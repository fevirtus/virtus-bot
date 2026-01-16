from sqlalchemy import Column, Integer, BigInteger, String, UniqueConstraint
from infra.db.base import Base, TimestampMixin

class Score(Base, TimestampMixin):
    __tablename__ = "score"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, default=0)
    user_id = Column(BigInteger, nullable=False)
    user_name = Column(String(255), nullable=True)
    point = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', name='uq_score_guild_user'),
    )

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
