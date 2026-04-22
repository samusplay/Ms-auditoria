from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AuditEvent:
    id: Optional[int]
    event_type: str
    service_name: str
    reference_id: str
    trace_id: str
    event_summary: str
    status: str
    created_at: Optional[datetime] = None
