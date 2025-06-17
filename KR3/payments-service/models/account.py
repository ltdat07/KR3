import uuid
from sqlalchemy import Column, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from .schema import Base

class Account(Base):
    __tablename__ = "accounts"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = Column(Numeric(12,2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
