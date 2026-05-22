from abc import ABC, abstractmethod
from app.domain.entity.audit_event import AuditEvent

class AuditRepositoryPort(ABC):
    """
    Puerto de Dominio: Define los métodos requeridos para persistir eventos de auditoría,
    independientemente de la tecnología subyacente.
    """
    
    @abstractmethod
    def save(self, event: AuditEvent) -> AuditEvent:
        """Persiste un evento en la base de datos y retorna la entidad con su ID y fecha de creación."""
        pass

    @abstractmethod
    def get_all(self, limit: int = 50, offset: int = 0) -> list[AuditEvent]:
        """Obtiene un listado paginado de eventos de auditoría."""
        pass
