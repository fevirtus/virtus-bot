from sqlalchemy import BigInteger, Column, DateTime, JSON, String, func
from infra.db.base import Base


class CultivationGuild(Base):
    __tablename__ = 'cultivation_guilds'
    guild_id = Column(BigInteger, primary_key=True)
    state = Column(JSON, nullable=False)
    resources = Column(JSON, nullable=False, default=dict)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CultivationReceipt(Base):
    __tablename__ = 'cultivation_receipts'
    guild_id = Column(BigInteger, primary_key=True)
    action_id = Column(String(160), primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
