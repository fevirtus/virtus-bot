from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.home_debt import HomeDebt
from infra.db import postgres

class HomeDebtRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def get(self, guild_id: int, discord_user_id: int) -> Optional[HomeDebt]:
        """Lấy thông tin thành viên"""
        try:
            async with self.Session() as session:
                stmt = select(HomeDebt).where(
                    HomeDebt.guild_id == guild_id,
                    HomeDebt.user_id == discord_user_id
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        
    async def get_other(self, guild_id: int, discord_user_id: int) -> Optional[HomeDebt]:
        """Lấy thông tin thành viên khác"""
        try:
            async with self.Session() as session:
                stmt = select(HomeDebt).where(
                    HomeDebt.guild_id == guild_id,
                    HomeDebt.user_id != discord_user_id
                ).limit(1)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error getting other member: {e}")
            return None

    async def create_home_debt(self, guild_id: int, user_id: int, value: int) -> Optional[HomeDebt]:
        """Tạo mới khoản nợ"""
        try:
            async with self.Session() as session:
                home_debt = HomeDebt(guild_id=guild_id, user_id=user_id, value=value)
                session.add(home_debt)
                await session.commit()
                await session.refresh(home_debt)
                return home_debt
        except Exception as e:
            print(f"Error creating home debt: {e}")
            return None

    async def update_home_debt(self, home_debt: HomeDebt) -> Optional[HomeDebt]:
        """Cập nhật khoản nợ"""
        try:
            async with self.Session() as session:
                # Merge object vào session để cập nhật
                merged_debt = await session.merge(home_debt)
                await session.commit()
                await session.refresh(merged_debt)
                return merged_debt
        except Exception as e:
            print(f"Error updating home debt: {e}")
            return None

    async def get_all(self, guild_id: int) -> List[HomeDebt]:
        """Lấy tất cả khoản nợ"""
        try:
            async with self.Session() as session:
                stmt = select(HomeDebt).where(HomeDebt.guild_id == guild_id)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            print(f"Error getting all home debts: {e}")
            return []