from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiscordServer(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    server_id: int
    name: str 

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'server_id': self.server_id,
            'name': self.name
        }