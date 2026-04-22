from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.domain.repository.audit_repository import AuditRepositoryPort
from app.domain.entity.audit_event import AuditEvent
from app.infrastructure.models.audit_event import AuditEventModel

class AuditRepositoryImpl(AuditRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def save(self, event: AuditEvent) -> AuditEvent:
        try:
            db_event = AuditEventModel(
                event_type=event.event_type,
                service_name=event.service_name,
                reference_id=event.reference_id,
                trace_id=event.trace_id,
                event_summary=event.event_summary,
                status=event.status
            )
            self.db.add(db_event)
            self.db.commit()
            self.db.refresh(db_event)
            
            # Map back to domain model
            event.id = db_event.id
            event.created_at = db_event.created_at
            return event
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
