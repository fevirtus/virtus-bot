from typing import List, Optional
from sqlalchemy import select
from models.guild import Guild
from infra.db import postgres

class GuildRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def get(self, guild_id: int) -> Optional[Guild]:
        try:
            async with self.Session() as session:
                stmt = select(Guild).where(Guild.id == guild_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error getting guild {guild_id}: {e}")
            return None

    async def create_or_update(self, guild_id: int, name: str) -> Optional[Guild]:
        try:
            async with self.Session() as session:
                stmt = select(Guild).where(Guild.id == guild_id)
                result = await session.execute(stmt)
                guild = result.scalar_one_or_none()
                
                if guild:
                    guild.name = name
                    guild.is_active = True
                else:
                    guild = Guild(id=guild_id, name=name, is_active=True)
                    session.add(guild)
                
                await session.commit()
                await session.refresh(guild)
                return guild
        except Exception as e:
            print(f"Error upserting guild {guild_id}: {e}")
            return None

    async def get_all(self) -> List[Guild]:
        try:
            async with self.Session() as session:
                stmt = select(Guild).where(Guild.is_active == True)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Error getting all guilds: {e}")
            return []
