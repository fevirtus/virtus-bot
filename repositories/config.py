from typing import List, Optional, Any
from sqlalchemy import select
from models.config import BotConfig
from infra.db import postgres

class ConfigRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def get(self, guild_id: int, key: str, default: Any = None) -> Any:
        """Lấy giá trị config theo key"""
        try:
            async with self.Session() as session:
                stmt = select(BotConfig).where(
                    BotConfig.guild_id == guild_id,
                    BotConfig.key == key
                )
                result = await session.execute(stmt)
                config = result.scalar_one_or_none()
                return config.value if config else default
        except Exception as e:
            print(f"Error getting config {key} for guild {guild_id}: {e}")
            return default

    async def set(self, guild_id: int, key: str, value: str, description: str = None) -> Optional[BotConfig]:
        """Cập nhật hoặc tạo mới config"""
        try:
            async with self.Session() as session:
                stmt = select(BotConfig).where(
                    BotConfig.guild_id == guild_id,
                    BotConfig.key == key
                )
                result = await session.execute(stmt)
                config = result.scalar_one_or_none()
                
                if config:
                    config.value = str(value)
                    if description:
                        config.description = description
                else:
                    config = BotConfig(guild_id=guild_id, key=key, value=str(value), description=description)
                    session.add(config)
                
                await session.commit()
                await session.refresh(config)
                return config
        except Exception as e:
            print(f"Error setting config {key} for guild {guild_id}: {e}")
            return None

    async def get_all(self, guild_id: int) -> List[BotConfig]:
        """Lấy tất cả config"""
        try:
            async with self.Session() as session:
                stmt = select(BotConfig).where(BotConfig.guild_id == guild_id)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Error getting all configs for guild {guild_id}: {e}")
            return []

    async def delete(self, guild_id: int, key: str) -> bool:
        """Xóa config"""
        try:
            async with self.Session() as session:
                stmt = select(BotConfig).where(
                    BotConfig.guild_id == guild_id,
                    BotConfig.key == key
                )
                result = await session.execute(stmt)
                config = result.scalar_one_or_none()
                
                if config:
                    await session.delete(config)
                    await session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error deleting config {key} for guild {guild_id}: {e}")
            return False
