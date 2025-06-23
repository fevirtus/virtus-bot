from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DiscordCurrency:
    id: Optional[int]
    user_id: int
    balance: int
    updated_at: datetime

    def __str__(self):
        return f"ID: {self.id}, User ID: {self.user_id}, Balance: {self.balance}, Updated At: {self.updated_at}"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "balance": self.balance,
            "updated_at": self.updated_at
        }