"""One locked aggregate per small guild; atomic state and durable action receipts.

Postgres serializes workers/retries. No read-modify-write through legacy repos
that swallow database errors. Separate tables leave legacy balances untouched.
"""
import copy
import hashlib
import random
import secrets
import time
from contextlib import asynccontextmanager

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from models.cultivation import CultivationGuild, CultivationReceipt
from . import engine as E


class GameStore:
    def __init__(self, sessions):
        self.sessions = sessions

    @asynccontextmanager
    async def locked(self, guild_id):
        async with self.sessions() as session:
            async with session.begin():
                await session.execute(insert(CultivationGuild).values(
                    guild_id=guild_id, state=E.initial(), resources={}).on_conflict_do_nothing())
                row = (await session.execute(select(CultivationGuild).where(
                    CultivationGuild.guild_id == guild_id).with_for_update())).scalar_one()
                # Always replace JSON values so SQLAlchemy observes nested mutations.
                row.state = copy.deepcopy(row.state)
                row.resources = copy.deepcopy(row.resources)
                E.upgrade_state(row.state, time.time())
                yield session, row
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(row, 'state')
                flag_modified(row, 'resources')

    async def snapshot(self, guild_id, user_id=None, name='Đạo hữu'):
        async with self.locked(guild_id) as (_, row):
            E.settle(row.state, time.time())
            if user_id is not None:
                E.player(row.state, user_id, name, time.time(), random.SystemRandom())
            return copy.deepcopy(row.state), copy.deepcopy(row.resources)

    async def act(self, guild_id, user_id, name, action_id, op, args=None):
        args = args or {}
        async with self.locked(guild_id) as (session, row):
            receipt = await session.get(CultivationReceipt, (guild_id, str(action_id)))
            if receipt:
                E.require(receipt.user_id == user_id, 'Mã thao tác đã được dùng bởi người khác.')
                return receipt.result['text']
            E.require(row.resources.get('enabled', True), 'Tu tiên đang tạm dừng trên server.')
            now = time.time()
            E.player(row.state, user_id, name, now, random.SystemRandom())
            E.settle(row.state, now)
            if '_quote' in args:
                E.require(E.quote(row.state, user_id, op, args) == args['_quote'],
                          'Chi phí hoặc điều kiện đã thay đổi. Mở lại thao tác để xác nhận.')
            result = E.execute(row.state, user_id, op, args, now,
                               random.Random(secrets.randbits(128)), str(action_id))
            session.add(CultivationReceipt(guild_id=guild_id, user_id=user_id,
                                          action_id=str(action_id), result={'text': result, 'op': op}))
            return result

    async def reward_chat(self, guild_id, user_id, name, message_id, content, channel_ids=()):
        async with self.locked(guild_id) as (session, row):
            if not row.resources.get('enabled', True) or set(channel_ids).intersection(row.resources.get('ignored_channels', [])):
                return
            now = time.time()
            p = E.player(row.state, user_id, name, now, random.SystemRandom())
            fingerprint = hashlib.sha256(' '.join(content.casefold().split()).encode()).hexdigest()
            hashes = [x for x in p.get('chat_hashes', []) if now-x[1] < 600]
            if now-p['last_chat'] < 60 or any(x[0] == fingerprint for x in hashes):
                return
            key = f'chat:{message_id}'
            if await session.get(CultivationReceipt, (guild_id, key)):
                return
            E.settle(row.state, now)
            p['last_chat'] = now
            p['last_content'] = fingerprint
            p['last_content_time'] = now
            p['chat_hashes'] = (hashes+[[fingerprint, now]])[-20:]
            gained = E.xp(p, 10, now, social=True)
            session.add(CultivationReceipt(guild_id=guild_id, user_id=user_id,
                                          action_id=key, result={'xp': gained}))

    async def reward_voice(self, guild_id, user_id, name, interval_id, seconds, end=None):
        async with self.locked(guild_id) as (session, row):
            if not row.resources.get('enabled', True):
                return
            key = 'voice:'+interval_id
            if await session.get(CultivationReceipt, (guild_id, key)):
                return
            now = time.time()
            E.settle(row.state, now)
            p = E.player(row.state, user_id, name, now, random.SystemRandom())
            end = now if end is None else min(now, end)
            start = max(end-max(0, min(seconds, 60)), p.get('voice_until', 0))
            seconds = max(0, end-start)
            p['voice_until'] = max(end, p.get('voice_until', 0))
            gained = E.xp(p, 20*seconds/300, now, social=True)
            session.add(CultivationReceipt(guild_id=guild_id, user_id=user_id,
                                          action_id=key, result={'xp': gained}))

    async def settle_all(self):
        async with self.sessions() as session:
            ids = (await session.execute(select(CultivationGuild.guild_id))).scalars().all()
        for guild_id in ids:
            async with self.locked(guild_id) as (_, row):
                E.settle(row.state, time.time())

    async def resource(self, guild_id, key, value):
        async with self.locked(guild_id) as (_, row):
            row.resources[key] = value

    @asynccontextmanager
    async def provisioning_lock(self, guild_id):
        # Session advisory lock survives per-resource commits; released on crash.
        async with self.sessions() as session:
            key = -int(guild_id)
            await session.execute(text('SELECT pg_advisory_lock(:key)'), {'key': key})
            try:
                yield
            finally:
                await session.execute(text('SELECT pg_advisory_unlock(:key)'), {'key': key})

    async def bind_room(self, guild_id, room_id, message_id):
        async with self.locked(guild_id) as (_, row):
            if room_id in row.state['rooms']:
                row.state['rooms'][room_id]['message_id'] = message_id

    async def pending_notices(self, guild_id):
        async with self.locked(guild_id) as (_, row):
            now = time.time()
            notices = row.state['outbox']
            # Keep pending messages for seven days, bounded history after delivery.
            for key, event in list(notices.items()):
                if event['created'] < now-7*86400:
                    del notices[key]
            return copy.deepcopy([(key, event) for key, event in notices.items()
                                  if event['status'] == 'pending'])[:20]

    async def notice_done(self, guild_id, key):
        async with self.locked(guild_id) as (_, row):
            row.state['outbox'].pop(key, None)

    async def configure(self, guild_id, values):
        allowed = {'enabled', 'ignored_channels', 'auto_setup', 'channel_mode'}
        E.require(set(values).issubset(allowed), 'Cấu hình không hợp lệ.')
        async with self.locked(guild_id) as (_, row):
            row.resources.update(values)
