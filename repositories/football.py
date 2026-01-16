from typing import List, Optional
from sqlalchemy import select, delete
from models.football import FootballSubscription
from infra.db import postgres

class FootballRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def add_subscription(self, guild_id: int, channel_id: int, team_name: str, team_id: int = None) -> bool:
        try:
            async with self.Session() as session:
                # Check exist
                stmt = select(FootballSubscription).where(
                    FootballSubscription.guild_id == guild_id,
                    FootballSubscription.team_name == team_name
                )
                existing = await session.execute(stmt)
                if existing.scalar_one_or_none():
                    return False

                sub = FootballSubscription(
                    guild_id=guild_id,
                    channel_id=channel_id,
                    team_name=team_name,
                    team_id=team_id
                )
                session.add(sub)
                await session.commit()
                return True
        except Exception as e:
            print(f"Error adding subscription: {e}")
            return False

    async def remove_subscription(self, guild_id: int, team_name: str) -> bool:
        try:
            async with self.Session() as session:
                stmt = delete(FootballSubscription).where(
                    FootballSubscription.guild_id == guild_id,
                    FootballSubscription.team_name == team_name
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error removing subscription: {e}")
            return False

    async def get_all_subscriptions(self) -> List[FootballSubscription]:
        try:
            async with self.Session() as session:
                stmt = select(FootballSubscription)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Error getting subscriptions: {e}")
            return []

    async def get_guild_subscriptions(self, guild_id: int) -> List[FootballSubscription]:
        try:
            async with self.Session() as session:
                stmt = select(FootballSubscription).where(FootballSubscription.guild_id == guild_id)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Error getting guild subscriptions: {e}")
            return []
