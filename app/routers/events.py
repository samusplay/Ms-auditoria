import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.application.service.audit_service import AuditService
from app.infrastructure.repositories.audit_repository_impl import AuditRepositoryImpl
from app.schemas.event_schema import EventCreate, EventResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/events", tags=["Events"])

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    repository = AuditRepositoryImpl(db)
    return AuditService(repository)

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, service: AuditService = Depends(get_audit_service)):
    """
    Recibe un evento de auditoría y lo persiste de forma inmutable delegando al AuditService (Hexagonal).
    """
    try:
        # Usamos dict() o model_dump() (Pydantic v2)
        saved_event = service.process_audit_event(event.dict() if hasattr(event, "dict") else event.model_dump())
        return saved_event
    except Exception as e:
        logger.error(f"Error while saving audit event: {str(e)} - trace_id: {event.trace_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al persistir el evento."
        )
