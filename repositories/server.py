from typing import Optional
from models.server import DiscordServer
from infra.db import postgres

class ServerRepository:
    def __init__(self):
        self.table = postgres.get_table('discord_server')

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

    async def create_server(self, server_id: int, name: str) -> Optional[DiscordServer]:
        """Create new Discord server"""
        try:
            server = DiscordServer(server_id=server_id, name=name)
            response = self.table.insert(server.dict(exclude_none=True)).execute()
            return DiscordServer(**response.data[0])
        except Exception as e:
            print(f"Error creating server: {e}")
            return None

    async def update_server(self, server_id: int, name: str) -> Optional[DiscordServer]:
        """Update Discord server"""
        try:
            response = self.table.update({'name': name}).eq('server_id', server_id).execute()
            if response.data:
                return DiscordServer(**response.data[0])
            return None
        except Exception as e:
            print(f"Error updating server: {e}")
            return None 