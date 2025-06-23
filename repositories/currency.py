from typing import List, Optional
from models.currency import DiscordCurrency
from infra.db import postgres
from datetime import datetime

class CurrencyRepository:
    def __init__(self):
        self.table = postgres.get_table('discord_currency')

    async def get(self, user_id: int) -> Optional[DiscordCurrency]:
        """Lấy thông tin thành viên"""
        try:
            response = self.table.select('*').eq('user_id', user_id).execute()
            if response.data:
                data = response.data[0]
                return DiscordCurrency(
                    id=data.get('id'),
                    user_id=data['user_id'],
                    balance=data['balance'],
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data['updated_at'] else datetime.now()
                )
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        
    async def create(self, user_id: int, balance: int) -> Optional[DiscordCurrency]:
        """Tạo thông tin thành viên"""
        try:
            response = self.table.insert({'user_id': user_id, 'balance': balance}).execute()
            if response.data:
                data = response.data[0]
                return DiscordCurrency(
                    id=data.get('id'),
                    user_id=data['user_id'],
                    balance=data['balance'],
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data['updated_at'] else datetime.now()
                )
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        
    async def update(self, user_id: int, balance: int) -> Optional[DiscordCurrency]:
        """Cập nhật thông tin thành viên"""
        try:
            response = self.table.update({'balance': balance}).eq('user_id', user_id).execute()
            if response.data:
                data = response.data[0]
                return DiscordCurrency(
                    id=data.get('id'),
                    user_id=data['user_id'],
                    balance=data['balance'],
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data['updated_at'] else datetime.now()
                )
            return None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
        
    async def get_all(self) -> List[DiscordCurrency]:
        """Lấy tất cả thông tin thành viên"""
        try:
            response = self.table.select('*').execute()
            currencies = []
            for data in response.data:
                currencies.append(DiscordCurrency(
                    id=data.get('id'),
                    user_id=data['user_id'],
                    balance=data['balance'],
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data['updated_at'] else datetime.now()
                ))
            return currencies
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
        
    async def get_all_with_balance(self) -> List[DiscordCurrency]:
        """Lấy tất cả thông tin thành viên và số dư"""
        try:
            response = self.table.select('*').execute()
            currencies = []
            for data in response.data:
                currencies.append(DiscordCurrency(
                    id=data.get('id'),
                    user_id=data['user_id'],
                    balance=data['balance'],
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data['updated_at'] else datetime.now()
                ))
            return currencies
        except Exception as e:
            print(f"Error getting all users with balance: {e}")
            return []
            
    # Get all with sort by balance
    async def get_all_with_sort_by_balance(self) -> List[DiscordCurrency]:
        """Lấy tất cả thông tin thành viên và sắp xếp theo số dư"""
        try:
            response = self.table.select('*').order('balance', desc=True).execute()
            currencies = []
            for data in response.data:
                currencies.append(DiscordCurrency(
                    id=data.get('id'),
                    user_id=data['user_id'],
                    balance=data['balance'],
                    updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data['updated_at'] else datetime.now()
                ))
            return currencies
        except Exception as e:
            print(f"Error getting all users with sort by balance: {e}")
            return []