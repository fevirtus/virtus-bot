from sqlalchemy import Column, String, Text, BigInteger, PrimaryKeyConstraint
from infra.db.base import Base, TimestampMixin

class BotConfig(Base, TimestampMixin):
    __tablename__ = "bot_configs"
    
    guild_id = Column(BigInteger, nullable=False, default=0) # 0 for Global/Template, real ID for specific
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('guild_id', 'key'),
    )

    def __str__(self):
        return f"Key: {self.key}, Value: {self.value}"
    
    def __repr__(self):
        return self.__str__()
