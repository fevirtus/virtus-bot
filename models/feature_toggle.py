from sqlalchemy import Column, String, BigInteger, Boolean, ForeignKey, PrimaryKeyConstraint
from infra.db.base import Base, TimestampMixin

class FeatureToggle(Base, TimestampMixin):
    __tablename__ = "feature_toggles"
    
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=False)
    feature_name = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, default=False)

    __table_args__ = (
        PrimaryKeyConstraint('guild_id', 'feature_name'),
    )

    def __str__(self):
        return f"Guild: {self.guild_id}, Feature: {self.feature_name}, Enabled: {self.is_enabled}"
    
    def __repr__(self):
        return self.__str__()
