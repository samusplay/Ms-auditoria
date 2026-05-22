# Resumen del Microservicio: ms-auditoria

El microservicio `ms-auditoria` es un componente central diseñado para la **gestión, registro y persistencia de eventos de auditoría y trazabilidad** en todo el ecosistema del proyecto. Su función principal es actuar como un "libro mayor" inmutable donde todos los demás microservicios reportan sus actividades y estados.

## 🏗️ Arquitectura Técnica
El proyecto sigue rigurosamente el patrón de **Arquitectura Hexagonal (Puertos y Adaptadores)**:

1.  **Capa de Dominio (`app/domain`):** Contiene las reglas puras de negocio y definiciones de interfaz (Repositorio).
2.  **Capa de Aplicación (`app/application`):** Orquestra los procesos mediante servicios de casos de uso (`AuditService`).
3.  **Capa de Infraestructura (`app/infrastructure`):** Gestiona la persistencia (PostgreSQL/SQLAlchemy) y configuraciones externas.
4.  **Capa de Presentación (`app/routers`):** Expone los endpoints de la API mediante FastAPI.

## 💾 Persistencia de Datos

### Información de la Tabla
- **Nombre de la tabla:** `audit_events`
- **Estructura del registro (JSON):**

```json
{
  "id": 1,
  "event_type": "TRANSFORMATION_COMPLETED",
  "service_name": "ms-transform",
  "reference_id": "DS-99823",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_summary": "La transformación del dataset de ventas finalizó exitosamente.",
  "status": "SUCCESS",
  "created_at": "2024-05-03T19:10:00Z"
}
```

## 🚀 Características Principales
- **Trazabilidad Distribuida:** Uso de `trace_id` para vincular acciones entre múltiples microservicios.
- **Inmutabilidad:** Los eventos se registran como hechos históricos que no deben ser modificados.
- **Sincronización Automática:** Las tablas se crean automáticamente al arrancar el servicio si no existen.
- **Validación Estricta:** Implementación de esquemas Pydantic para asegurar la integridad de los datos recibidos.

## 🛠️ Stack Tecnológico
- **Lenguaje:** Python 3.12+
- **Framework Web:** FastAPI
- **ORM:** SQLAlchemy
- **Base de Datos:** PostgreSQL
- **Contenedores:** Docker
