from typing import List, Optional
from sqlalchemy import select
from models.feature_toggle import FeatureToggle
from infra.db import postgres

class FeatureToggleRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def get(self, guild_id: int, feature_name: str) -> bool:
        """Check if feature is enabled for guild"""
        try:
            async with self.Session() as session:
                stmt = select(FeatureToggle).where(
                    FeatureToggle.guild_id == guild_id,
                    FeatureToggle.feature_name == feature_name
                )
                result = await session.execute(stmt)
                toggle = result.scalar_one_or_none()
                return toggle.is_enabled if toggle else False # Default Disabled
        except Exception as e:
            print(f"Error getting feature {feature_name} for guild {guild_id}: {e}")
            return False

    async def set(self, guild_id: int, feature_name: str, is_enabled: bool) -> Optional[FeatureToggle]:
        try:
            async with self.Session() as session:
                stmt = select(FeatureToggle).where(
                    FeatureToggle.guild_id == guild_id,
                    FeatureToggle.feature_name == feature_name
                )
                result = await session.execute(stmt)
                toggle = result.scalar_one_or_none()
                
                if toggle:
                    toggle.is_enabled = is_enabled
                else:
                    toggle = FeatureToggle(guild_id=guild_id, feature_name=feature_name, is_enabled=is_enabled)
                    session.add(toggle)
                
                await session.commit()
                await session.refresh(toggle)
                return toggle
        except Exception as e:
            print(f"Error setting feature {feature_name} for guild {guild_id}: {e}")
            return None
        
    async def get_all_for_guild(self, guild_id: int) -> List[FeatureToggle]:
        try:
            async with self.Session() as session:
                stmt = select(FeatureToggle).where(FeatureToggle.guild_id == guild_id)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Error getting all features for guild {guild_id}: {e}")
            return []
