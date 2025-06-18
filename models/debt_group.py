from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DiscordDebtGroup:
    id: Optional[int]
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    members: List[DiscordHomeDebt]