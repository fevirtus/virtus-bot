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