from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON
from app.infrastructure.database import Base

class AuditEventModel(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    source_service = Column(String, nullable=False)
    reference_id = Column(String, nullable=False, index=True)
    trace_id = Column(String, nullable=False, index=True)
    details = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="SUCCESS")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
