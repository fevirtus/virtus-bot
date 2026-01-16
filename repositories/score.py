from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, update, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

from models.score import Score
from infra.db import postgres

class ScoreRepository:
    def __init__(self):
        self.Session = postgres.get_sessionmaker()

    async def get(self, guild_id: int, user_id: int) -> Optional[Score]:
        """Lấy thông tin thành viên"""
        try:
            async with self.Session() as session:
                stmt = select(Score).where(
                    Score.guild_id == guild_id,
                    Score.user_id == user_id
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        
    async def create(self, guild_id: int, user_id: int, point: int) -> Optional[Score]:
        """Tạo thông tin thành viên"""
        try:
            async with self.Session() as session:
                currency = Score(guild_id=guild_id, user_id=user_id, point=point)
                session.add(currency)
                await session.commit()
                await session.refresh(currency)
                return currency
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        
    async def update(self, guild_id: int, user_id: int, point: int) -> Optional[Score]:
        """Cập nhật thông tin thành viên"""
        try:
            async with self.Session() as session:
                stmt = (
                    update(Score)
                    .where(
                        Score.guild_id == guild_id,
                        Score.user_id == user_id
                    )
                    .values(point=point)
                    .returning(Score)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
        
    async def get_all(self, guild_id: int) -> List[Score]:
        """Lấy tất cả thông tin thành viên"""
        try:
            async with self.Session() as session:
                stmt = select(Score).where(Score.guild_id == guild_id).order_by(Score.point.desc())
                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        
    async def get_all_with_point(self, guild_id: int) -> List[Score]:
        """Lấy tất cả thông tin thành viên và số dư"""
        try:
            async with self.Session() as session:
                stmt = select(Score).where(Score.guild_id == guild_id)
                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            print(f"Error getting all users with point: {e}")
            return []
            
    # Get all with sort by point
    async def get_all_with_sort_by_point(self, guild_id: int) -> List[Score]:
        """Lấy tất cả thông tin thành viên và sắp xếp theo số dư"""
        try:
            async with self.Session() as session:
                stmt = select(Score).where(Score.guild_id == guild_id).order_by(Score.point.desc())
                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            print(f"Error getting all users with sort by point: {e}")
            return []

    async def upsert_or_increment_point(self, guild_id: int, user_id: str, user_name: str, amount: int) -> Optional[int]:
        try:
            async with self.Session() as session:
                # Sử dụng PostgreSQL UPSERT (ON CONFLICT)
                stmt = pg_insert(Score).values(
                    guild_id=int(guild_id),
                    user_id=int(user_id),
                    user_name=str(user_name),
                    point=amount
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=['guild_id', 'user_id'], # Must match UniqueConstraint/Index
                    set_=dict(
                        point=Score.point + amount,
                        user_name=stmt.excluded.user_name
                    )
                ).returning(Score.point)
                
                result = await session.execute(stmt)
                await session.commit()
                row = result.first()
                return row[0] if row else None
        except Exception as e:
            print(f"Error upserting point for user {user_id}: {e}")
            return None
