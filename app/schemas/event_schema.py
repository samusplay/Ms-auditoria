from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class EventCreate(BaseModel):
    event_type: str = Field(..., min_length=1, description="Tipo de evento")
    source_service: str = Field(..., min_length=1, description="Nombre del servicio de origen")
    reference_id: Optional[str] = Field(default="N/A", description="ID de referencia del objeto afectado")
    trace_id: str = Field(..., min_length=1, description="Identificador único de trazabilidad")
    details: Dict[str, Any] = Field(..., description="Contexto libre del evento en formato JSON")
    status: Optional[str] = Field(default="SUCCESS", description="Estado del proceso o evento")

class EventResponse(BaseModel):
    id: int
    created_at: datetime
    reference_id: str
    status: str

    class Config:
        from_attributes = True
