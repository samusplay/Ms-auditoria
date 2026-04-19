import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.database import get_db
from app.infrastructure.models.audit_event import AuditEvent
from app.schemas.event_schema import EventCreate, EventResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/events", tags=["Events"])

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Recibe un evento de auditoría y lo persiste de forma inmutable.
    """
    try:
        new_event = AuditEvent(
            event_type=event.event_type,
            service_name=event.service_name,
            trace_id=event.trace_id,
            event_summary=event.event_summary
        )
        
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        return new_event
        
    except SQLAlchemyError as e:
        db.rollback()
        # Log estructurado interno, nunca exponer stack trace al cliente
        logger.error(f"Database error while saving audit event: {str(e)} - trace_id: {event.trace_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al persistir el evento."
        )
