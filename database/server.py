from typing import Optional
from .base import BaseRepository
from models.server import DiscordServer

class ServerRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.table = self.db.get_table('discord_server')

    async def get_server(self, server_id: int) -> Optional[DiscordServer]:
        """Get Discord server by ID"""
        try:
            response = self.table.select('*').eq('server_id', server_id).execute()
            if response.data:
                return DiscordServer(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting server: {e}")
            return None

    async def create_server(self, server_id: int, server_name: str) -> Optional[DiscordServer]:
        """Create new Discord server"""
        try:
            server = DiscordServer(server_id=server_id, server_name=server_name)
            response = self.table.insert(server.dict()).execute()
            return DiscordServer(**response.data[0])
        except Exception as e:
            print(f"Error creating server: {e}")
            return None

    async def update_server(self, server_id: int, server_name: str) -> Optional[DiscordServer]:
        """Update Discord server"""
        try:
            response = self.table.update({'server_name': server_name}).eq('server_id', server_id).execute()
            if response.data:
                return DiscordServer(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating server: {e}")
            return None 