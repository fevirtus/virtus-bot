from typing import List, Optional
from models.home_debt import DiscordHomeDebt
from infra.db import postgres

class HomeDebtRepository:
    def __init__(self):
        self.table = postgres.get_table('discord_home_debt')

    async def get(self, discord_user_id: int) -> Optional[DiscordHomeDebt]:
        """Lấy thông tin thành viên"""
        try:
            response = self.table.select('*').eq('user_id', discord_user_id).execute()
            if response.data:
                return DiscordHomeDebt(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        
    async def get_other(self, discord_user_id: int) -> Optional[DiscordHomeDebt]:
        """Lấy thông tin thành viên khác"""
        try:
            response = self.table.select('*').neq('user_id', discord_user_id).execute()
            if response.data:
                return DiscordHomeDebt(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting other member: {e}")
            return None

    async def create_home_debt(self, user_id: int, value: int) -> Optional[DiscordHomeDebt]:
        """Tạo mới khoản nợ"""
        try:
            home_debt = DiscordHomeDebt(user_id=user_id, value=value)
            response = self.table.insert(home_debt.dict(exclude_none=True)).execute()
            return DiscordHomeDebt(**response.data[0])
        except Exception as e:
            print(f"Error creating home debt: {e}")
            return None

    async def update_home_debt(self, home_debt: DiscordHomeDebt) -> Optional[DiscordHomeDebt]:
        """Cập nhật khoản nợ"""
        try:
            response = self.table.update(home_debt.dict(exclude_none=True)).eq('user_id', home_debt.user_id).execute()
            return DiscordHomeDebt(**response.data[0])
        except Exception as e:
            print(f"Error updating home debt: {e}")
            return None

    async def get_all(self) -> List[DiscordHomeDebt]:
        """Lấy tất cả khoản nợ"""
        try:
            response = self.table.select('*').execute()
            return [DiscordHomeDebt(**home_debt) for home_debt in response.data]
        except Exception as e:
            print(f"Error getting all home debts: {e}")
            return []