from app.domain.repository.audit_repository import AuditRepositoryPort
from app.domain.entity.audit_event import AuditEvent

class AuditService:
    def __init__(self, repository: AuditRepositoryPort):
        self.repository = repository

    def process_audit_event(self, event_data: dict) -> AuditEvent:
        event = AuditEvent(
            id=None,
            event_type=event_data["event_type"],
            service_name=event_data["service_name"],
            reference_id=event_data.get("reference_id", "N/A"),
            trace_id=event_data["trace_id"],
            event_summary=event_data["event_summary"],
            status=event_data.get("status", "SUCCESS")
        )
        return self.repository.save(event)
