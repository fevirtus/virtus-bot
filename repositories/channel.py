from typing import Optional, List
from models.channel import DiscordChannel
from infra.db import postgres

class ChannelRepository:
    def __init__(self):
        self.table = postgres.get_table('discord_channel')

    async def get_channel(self, channel_id: int) -> Optional[DiscordChannel]:
        try:
            response = self.table.select('*').eq('channel_id', channel_id).execute()
            if response.data:
                return DiscordChannel.model_validate(response.data[0])
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

    async def create_channel(self, server_id: int, channel_id: int, app: str) -> Optional[DiscordChannel]:
        try:
            channel = DiscordChannel(server_id=server_id, channel_id=channel_id, app=app)
            response = self.table.insert(channel.dict(exclude_none=True)).execute()
            return DiscordChannel(**response.data[0])
        except Exception as e:
            print(f"Error creating channel: {e}")
            return None

    async def update_channel(self, channel_id: int, app: str) -> Optional[DiscordChannel]:
        try:
            response = self.table.update({'app': app}).eq('channel_id', channel_id).execute()
            if response.data:
                return DiscordChannel(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating channel: {e}")
            return None 