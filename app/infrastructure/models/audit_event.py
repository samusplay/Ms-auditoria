from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.infrastructure.database import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary key=True, index=True)
    event_type = Column(String, nullable=False)
    service_name = Column(String, nullable=False)
    trace_id = Column(String, nullable=False, index=True)
    event_summary = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
