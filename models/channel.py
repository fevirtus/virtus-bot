from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiscordChannel(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    server_id: int
    channel_id: int
    app: str 

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "server_id": self.server_id,
            "channel_id": self.channel_id,
            "app": self.app
        }