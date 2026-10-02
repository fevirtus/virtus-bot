from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    ForeignKeyConstraint, Index, Integer, JSON, String,
)
from infra.db.base import Base, TimestampMixin


class DebtGroup(Base, TimestampMixin):
    __tablename__ = "group_debt_groups"
    guild_id = Column(BigInteger, primary_key=True)
    channel_id = Column(BigInteger, primary_key=True)
    owner_id = Column(BigInteger, nullable=False)
    member_ids = Column(JSON, nullable=False)
    revision = Column(Integer, nullable=False, default=1)


class DebtTransaction(Base, TimestampMixin):
    __tablename__ = "group_debt_transactions"
    # Original Discord interaction ID makes repeated confirmations idempotent.
    id = Column(BigInteger, primary_key=True, autoincrement=False)
    guild_id = Column(BigInteger, nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    actor_id = Column(BigInteger, nullable=False)
    kind = Column(String(10), nullable=False)
    amount = Column(BigInteger, nullable=False)
    recipient_id = Column(BigInteger, nullable=True)
    note = Column(String(100), nullable=False, default="")
    shares = Column(JSON, nullable=False, default=dict)
    reversed = Column(Boolean, nullable=False, default=False)
    reversed_by = Column(BigInteger, nullable=True)
    reversed_at = Column(DateTime(timezone=True), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['guild_id', 'channel_id'], ['group_debt_groups.guild_id', 'group_debt_groups.channel_id']),
        CheckConstraint("amount > 0", name="ck_group_debt_positive_amount"),
        CheckConstraint("kind IN ('expense', 'payment')", name="ck_group_debt_kind"),
        Index('ix_group_debt_channel_history', 'guild_id', 'channel_id', 'id'),
    )


class DebtEntry(Base):
    __tablename__ = "group_debt_entries"
    transaction_id = Column(BigInteger, ForeignKey('group_debt_transactions.id'), primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    delta = Column(BigInteger, nullable=False)
