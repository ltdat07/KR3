import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    JSON,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from .schema import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_type = Column(String, nullable=False)       # e.g. "order"
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String, nullable=False)           # e.g. "order_created"
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)