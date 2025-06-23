from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import json

class DiscordNoiTu(BaseModel):
    id: Optional[int] = None
    word: str
    meaning: Optional[str] = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'meaning': self.meaning,
        }
    
    def to_json(self):
        return json.dumps(self.to_dict())