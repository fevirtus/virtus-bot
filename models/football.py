from sqlalchemy import Column, Integer, String, BigInteger, DateTime, UniqueConstraint
from datetime import datetime
from infra.db.postgres import Base

class FootballSubscription(Base):
    __tablename__ = "football_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False)
    team_name = Column(String, nullable=False) # Storing name for easier user interaction/display, or mapped ID later
    team_id = Column(Integer, nullable=True) # Optional: Store API ID for reliability
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('guild_id', 'team_name', name='uix_guild_team'),
    )

    def __repr__(self):
        return f"<FootballSubscription(guild_id={self.guild_id}, team={self.team_name})>"
