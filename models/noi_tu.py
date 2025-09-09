from sqlalchemy import Column, Integer, String
from infra.db.base import Base

class DiscordNoiTu(Base):
    __tablename__ = "dictionary_vietnamese_two_words"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(255), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
        }
    
    def to_json(self):
        import json
        return json.dumps(self.to_dict())