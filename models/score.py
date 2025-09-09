from sqlalchemy import Column, Integer, BigInteger, String
from infra.db.base import Base

class Score(Base):
    __tablename__ = "score"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    user_name = Column(String(255), nullable=True)
    point = Column(Integer, nullable=False, default=0)

    def __str__(self):
        return f"ID: {self.id}, User ID: {self.user_id}, User Name: {self.user_name}, point: {self.point}"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "point": self.point
        }
