from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DiscordChannelApp(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: str
    description: str 