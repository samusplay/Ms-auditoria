from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, description="Tipo de evento")
    service_name: str = Field(..., min_length=1, description="Nombre del servicio de origen")
    reference_id: Optional[str] = Field(default="N/A", description="ID de referencia del objeto afectado")
    trace_id: str = Field(..., min_length=1, description="Identificador único de trazabilidad")
    event_summary: str = Field(..., min_length=1, description="Resumen descriptivo del evento")
    status: Optional[str] = Field(default="SUCCESS", description="Estado del proceso o evento")

class EventResponse(BaseModel):
    id: int
    event_type: str
    service_name: str
    trace_id: str
    event_summary: str
    created_at: datetime
    reference_id: str
    status: str

    class Config:
        from_attributes = True
