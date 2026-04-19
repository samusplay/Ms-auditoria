from pydantic import BaseModel
from typing import Dict, Any


class AuditEventCreate(BaseModel):
    event_type: str
    source_service: str
    trace_id: str
    details: Dict[str, Any]