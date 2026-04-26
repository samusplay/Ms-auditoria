from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class AuditEvent:
    id: Optional[int]
    event_type: str
    source_service: str
    reference_id: str
    trace_id: str
    details: Dict[str, Any]
    status: str
    created_at: Optional[datetime] = None
