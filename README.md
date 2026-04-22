# Microservicio de Auditoría e Historial (ms-auditoria)

Este microservicio se encarga de recibir, procesar y persistir eventos de auditoría y logueo relevantes para todo el clúster de la solución. 

## 🏗️ Arquitectura Hexagonal y Principio de Responsabilidad Única (SRP)

El proyecto ha sido rediseñado rigurosamente bajo el patrón de **Arquitectura Hexagonal (Puertos y Adaptadores)**. Ninguna capa conoce lógica de persistencia directamente excepto la de infraestructura. 

### 1. Capa de Dominio (`app/domain`)
Contiene reglas puras de negocio que no dependen de la base de datos (SQLAlchemy) ni del framework web (FastAPI).
- **Entidad `AuditEvent`:** (Dataclass de Python pura) Modela la estructura lógica de un evento.
- **Puerto de Repositorio `AuditRepositoryPort`:** Una interfaz (`ABC`) que define el contrato de métodos que cualquier adaptador de base de datos deberá cumplir.

### 2. Capa de Aplicación (`app/application`)
Se encarga de orquestar los procesos mediante **Servicios de Casos de Uso**.
- **`AuditService`**: Recibe datos, instancia la clase pura del dominio `AuditEvent` y se los pasa al repositorio (Dependencia Inyectada) para persistirlos y procesarlos.

### 3. Capa de Infraestructura (`app/infrastructure`)
Todo aquello que tiene un acoplamiento a una librería concreta o hardware se maneja aquí.
- **Modelos (`audit_event.py`):** Define el modelo físico de la tabla `audit_events` asociado de manera exclusiva a **SQLAlchemy**.
- **Repositorios Concretos (`audit_repository_impl.py`):** Adaptador que cumple con `AuditRepositoryPort`. Contiene la lógica transaccional de conectar modelo a objeto de base de datos (`add`, `commit`, etc.).
- **Base de Datos (`database.py`):** Instancias de configuración del gestor de Postgres.

### 4. Capa de Presentación o Routers (`app/routers`)
- Archivos como `events.py` solo reciben la petición HTTP de FastAPI, ejecutan los validadores de Pydantic (`EventCreate`) e inyectan el *Repository Impl* en `AuditService`. No tienen interacción directa con `session.commit()` para respetar rigurosamente la responsabilidad separada.

## 💾 Creación Dinámica de Tablas en Base de Datos

Las tablas de `ms-auditoria` se **autoconstruyen** programáticamente cada vez que el microservicio arranca, si ellas aún no existen.
Esta labor se realiza a la altura del constructor de vida (`lifespan`) en `app/main.py`:
```python
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de AUDITORÍA sincronizadas")
```
Esto descarta la necesidad de scripts o queries manuales para inicializar el contenedor recién levantando en Docker Compose.

## 📝 Estructura del Evento de Auditoría

Cada evento procesado consta de los siguientes atributos clave:

- `id`: Identificador interno (Autogenerado).
- `event_type`: Tipo del evento (ej. "TRANSFORMATION_COMPLETED").
- `service_name`: Nombre del componente de software que originó el mensaje.
- `reference_id`: ID del Dataset o Elemento de negocio de interés que provocó el evento (novedad añadida).
- `trace_id`: ID de Trazabilidad distribuida para seguir un flujo largo a través de múltiples APIs.
- `event_summary`: Resumen de la acción o suceso descriptivo.
- `status`: Estado semántico de confirmación (Se define como "SUCCESS" por defecto en caso de no especificarse).
- `created_at`: Marca temporal persistida autogenerada por el DB.
