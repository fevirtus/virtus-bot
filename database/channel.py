from typing import Optional, List
from .base import BaseRepository
from models.channel import DiscordChannel

class ChannelRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.table = self.db.get_table('discord_channel')

    async def get_channel(self, channel_id: int) -> Optional[DiscordChannel]:
        try:
            response = self.table.select('*').eq('channel_id', channel_id).execute()
            if response.data:
                return DiscordChannel(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting channel: {e}")
            return None

    async def get_channels_by_server(self, server_id: int) -> List[DiscordChannel]:
        try:
            response = self.table.select('*').eq('server_id', server_id).execute()
            return [DiscordChannel(**channel) for channel in response.data]
        except Exception as e:
            print(f"Error getting channels: {e}")
            return []

    async def create_channel(self, channel_id: int, server_id: int, channel_name: str) -> Optional[DiscordChannel]:
        try:
            channel = DiscordChannel(channel_id=channel_id, server_id=server_id, channel_name=channel_name)
            response = self.table.insert(channel.dict()).execute()
            return DiscordChannel(**response.data[0])
        except Exception as e:
            print(f"Error creating channel: {e}")
            return None

    async def update_channel(self, channel_id: int, channel_name: str) -> Optional[DiscordChannel]:
        try:
            response = self.table.update({'channel_name': channel_name}).eq('channel_id', channel_id).execute()
            if response.data:
                return DiscordChannel(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating channel: {e}")
            return None 