from typing import Optional, List
from .base import BaseRepository
from models.channel_app import DiscordChannelApp

class ChannelAppRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.table = self.db.get_table('discord_channel_app')

    async def get_channel_app(self, channel_id: int, app_name: str) -> Optional[DiscordChannelApp]:
        try:
            response = self.table.select('*').eq('channel_id', channel_id).eq('app_name', app_name).execute()
            if response.data:
                return DiscordChannelApp(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting channel app: {e}")
            return None

    async def get_channel_apps(self, channel_id: int) -> List[DiscordChannelApp]:
        try:
            response = self.table.select('*').eq('channel_id', channel_id).execute()
            return [DiscordChannelApp(**app) for app in response.data]
        except Exception as e:
            print(f"Error getting channel apps: {e}")
            return []

    async def create_channel_app(self, channel_id: int, app_name: str) -> Optional[DiscordChannelApp]:
        try:
            app = DiscordChannelApp(channel_id=channel_id, app_name=app_name)
            response = self.table.insert(app.dict()).execute()
            return DiscordChannelApp(**response.data[0])
        except Exception as e:
            print(f"Error creating channel app: {e}")
            return None

    async def delete_channel_app(self, channel_id: int, app_name: str) -> bool:
        try:
            response = self.table.delete().eq('channel_id', channel_id).eq('app_name', app_name).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting channel app: {e}")
            return False 