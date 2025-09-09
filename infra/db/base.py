from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from datetime import datetime

# Tạo Base class cho tất cả ORM models
Base = declarative_base()

class TimestampMixin:
    """Mixin để tự động thêm created_at và updated_at"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
