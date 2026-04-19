from pydantic import BaseModel, Field
from datetime import datetime

class EventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, description="Tipo de evento")
    service_name: str = Field(..., min_length=1, description="Nombre del servicio de origen")
    trace_id: str = Field(..., min_length=1, description="Identificador único de trazabilidad")
    event_summary: str = Field(..., min_length=1, description="Resumen descriptivo del evento")

class EventResponse(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
