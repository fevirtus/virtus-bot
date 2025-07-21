from dataclasses import dataclass
from typing import Optional

@dataclass
class CMCDebt:
    id: Optional[int]
    name: str
    amount: int

    def to_dict(self):
        if self.id is None:
            return {
                "name": self.name,
                "amount": self.amount
            }
        
        return {
            "id": self.id,
            "name": self.name,
            "amount": self.amount
        } 