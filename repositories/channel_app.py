from typing import Optional, List
from models.channel_app import DiscordChannelApp
from infra.db import postgres

class ChannelAppRepository:
    def __init__(self):
        self.table = postgres.get_table('discord_channel_app')

    async def get_channel_app(self, name: str) -> Optional[DiscordChannelApp]:
        try:
            response = self.table.select('*').eq('name', name).execute()
            if response.data:
                return DiscordChannelApp(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting channel app: {e}")
            return None

    async def get_all_apps(self) -> List[DiscordChannelApp]:
        try:
            response = self.table.select('*').execute()
            return [DiscordChannelApp(**app) for app in response.data]
        except Exception as e:
            print(f"Error getting channel apps: {e}")
            return []

    async def create_channel_app(self, name: str, description: str) -> Optional[DiscordChannelApp]:
        try:
            app = DiscordChannelApp(name=name, description=description)
            response = self.table.insert(app.dict(exclude_none=True)).execute()
            return DiscordChannelApp(**response.data[0])
        except Exception as e:
            print(f"Error creating channel app: {e}")
            return None

    async def update_channel_app(self, name: str, description: str) -> Optional[DiscordChannelApp]:
        try:
            response = self.table.update({'description': description}).eq('name', name).execute()
            if response.data:
                return DiscordChannelApp(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating channel app: {e}")
            return None

    async def delete_channel_app(self, channel_id: int, app_name: str) -> bool:
        try:
            response = self.table.delete().eq('channel_id', channel_id).eq('app_name', app_name).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error deleting channel app: {e}")
            return False 