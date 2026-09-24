"""Create only owned resources. Persist intent before each Discord creation.

An uncertain role/category creation is stopped for reconciliation rather than
guessing ownership of a same-name resource and modifying somebody else's role.
"""
import discord

from .rules import REALMS


class SetupError(RuntimeError):
    pass


async def provision(bot, guild, store, panel_view):
    async with store.provisioning_lock(guild.id):
        _, resources = await store.snapshot(guild.id)
        if resources.get('auto_setup', True) is False:
            return resources
        me = guild.me
        if not me or not me.guild_permissions.manage_channels or not me.guild_permissions.manage_roles:
            raise SetupError('Bot cần Manage Channels và Manage Roles để tự thiết lập.')
        reason = 'Virtus cultivation automatic setup'

        async def saved(key, value):
            resources[key] = value
            await store.resource(guild.id, key, value)

        async def create(key, factory):
            # If API succeeded and response/DB write failed, do not blindly repeat.
            if resources.get('pending') == key:
                raise SetupError(f'Thiết lập {key} có kết quả chưa xác định. Dùng /tutien_setup để xem và đối soát; bot không tạo trùng.')
            await saved('pending', key)
            try:
                resource = await factory()
            except discord.HTTPException as error:
                # Explicit client rejection means Discord did not create it.
                # Timeouts/5xx remain uncertain and need reconciliation.
                if 400 <= error.status < 500:
                    await saved('pending', None)
                raise
            await saved(key, resource.id)
            await saved('pending', None)
            return resource

        # If the ID was saved before a crash, it is safe to clear that intent.
        pending = resources.get('pending')
        if pending and resources.get(pending):
            await saved('pending', None)
        category = guild.get_channel(resources.get('category_id', 0))
        if category is None:
            category = await create('category_id', lambda: guild.create_category('Virtus · Tu Tiên', reason=reason))
        if not isinstance(category, discord.CategoryChannel):
            raise SetupError('ID danh mục đã lưu không còn là category; không sửa tài nguyên khác.')
        channels = [('game_channel', 'tu-tien'), ('achievement_channel', 'thanh-tuu'), ('sect_channel', 'tong-mon')]
        for key, name in channels:
            if resources.get('channel_mode') == 'merged' and key != 'game_channel':
                # Preserve old physical channels; only redirect future bot output.
                if resources.get(key) and resources[key] != resources['game_channel']:
                    await saved(key+'_separate', resources[key])
                await saved(key, resources['game_channel'])
                continue
            if key != 'game_channel' and resources.get(key) == resources.get('game_channel'):
                await saved(key, resources.get(key+'_separate', 0))
            channel = guild.get_channel(resources.get(key, 0))
            if channel is None:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=key != 'achievement_channel'),
                    me: discord.PermissionOverwrite(view_channel=True, send_messages=True, embed_links=True, read_message_history=True),
                }
                channel = await create(key, lambda name=name, key=key, overwrites=overwrites: guild.create_text_channel(
                    name, category=category, topic=f'virtus:{bot.user.id}:{guild.id}:{key}',
                    overwrites=overwrites, reason=reason))
            if not isinstance(channel, discord.TextChannel):
                raise SetupError(f'{key} không phải text channel.')
        for index, name in enumerate(REALMS):
            key = f'realm_role_{index}'
            role = guild.get_role(resources.get(key, 0))
            if role is None:
                role = await create(key, lambda name=name: guild.create_role(
                    name=f'Tu Tiên · {name}', permissions=discord.Permissions.none(),
                    mentionable=False, hoist=False, reason=reason))
            if role >= me.top_role:
                raise SetupError(f'Role bot phải cao hơn role {role.name}.')
        channel = guild.get_channel(resources['game_channel'])
        message = None
        if resources.get('panel_message'):
            try:
                message = await channel.fetch_message(resources['panel_message'])
            except discord.NotFound:
                pass
        if message is None:
            # Reconcile a message created before a process crash, by author/custom_id.
            async for old in channel.history(limit=100):
                if old.author.id == bot.user.id and any(
                    getattr(child, 'custom_id', '') == 'virtus:open'
                    for row in old.components for child in row.children):
                    message = old
                    break
            if message is None:
                message = await channel.send(
                    'Tu tiên cùng cả hội. Mở hồ sơ để luyện đan, thám hiểm và xuất chiến auto. '
                    'Chat/voice hợp lệ trên server tự tích lũy tu vi.', view=panel_view,
                    allowed_mentions=discord.AllowedMentions.none())
            await saved('panel_message', message.id)
        await saved('status', 'ready')
        return resources
