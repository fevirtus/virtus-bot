from sqlalchemy import Column, String, BigInteger, Boolean
from infra.db.base import Base, TimestampMixin

class Guild(Base, TimestampMixin):
    __tablename__ = "guilds"
    
    id = Column(BigInteger, primary_key=True) # Discord Guild ID
    name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    def __str__(self):
        return f"Guild ID: {self.id}, Name: {self.name}"
    
    def __repr__(self):
        return self.__str__()
