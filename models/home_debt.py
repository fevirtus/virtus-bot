from sqlalchemy import Column, Integer, BigInteger, UniqueConstraint
from infra.db.base import Base, TimestampMixin

class HomeDebt(Base, TimestampMixin):
    __tablename__ = "home_debt"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, default=0)
    user_id = Column(BigInteger, nullable=False)
    value = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('guild_id', 'user_id', name='uq_home_debt_guild_user'),
    )

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