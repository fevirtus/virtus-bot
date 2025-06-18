from typing import Optional
from infra.db import postgres

class UserRepository:
    def __init__(self):
        self.exp_table = postgres.get_table('user_exp')
        self.voice_table = postgres.get_table('voice_time')

    async def get_exp(self, user_id: int) -> int:
        """Get user's experience points from database"""
        try:
            response = self.exp_table.select('exp_points').eq('user_id', user_id).execute()
            if response.data:
                return response.data[0]['exp_points']
            return 0
        except Exception as e:
            print(f"Error getting user exp: {e}")
            return 0

    async def update_exp(self, user_id: int, exp_points: int) -> bool:
        """Update user's experience points in database"""
        try:
            response = self.exp_table.upsert({'user_id': user_id, 'exp_points': exp_points}).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating user exp: {e}")
            return False

    async def get_voice_time(self, user_id: int) -> Optional[str]:
        """Get user's voice time from database"""
        try:
            response = self.voice_table.select('last_join_time').eq('user_id', user_id).execute()
            if response.data:
                return response.data[0]['last_join_time']
            return None
        except Exception as e:
            print(f"Error getting user voice time: {e}")
            return None

    async def update_voice_time(self, user_id: int, join_time: str) -> bool:
        """Update user's voice time in database"""
        try:
            response = self.voice_table.upsert({'user_id': user_id, 'last_join_time': join_time}).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating user voice time: {e}")
            return False 