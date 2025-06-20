from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DiscordHomeDebt:
    id: Optional[int]
    user_id: int
    value: int
    created_at: datetime
    updated_at: datetime

    def __str__(self):
        return f"ID: {self.id}, User ID: {self.user_id}, Value: {self.value}, Created At: {self.created_at}, Updated At: {self.updated_at}"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "value": self.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }