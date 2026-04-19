# Pruebas del Endpoint de Auditoría con Postman

Este documento explica cómo probar el nuevo endpoint de registro de eventos de auditoría utilizando Postman.

## Pre-requisitos
Asegúrate de que tus contenedores de Docker estén corriendo, especialmente `db-audit` y `ms-auditoria`:
```bash
docker compose up -d ms-auditoria
```

---

## Endpoint: Registrar Evento de Auditoría

El microservicio de Auditoría recibe los eventos directamente en su puerto expuesto (o a través del gateway si estuviera mapeado). Asumiendo que atacas directamente al microservicio o a través del proxy:

**URL (Directa si está expuesto):** `http://localhost:8000/api/v1/events`
*(Nota: Si pasas por el API Gateway, la URL dependerá del ruteo que tengas configurado, por ejemplo `http://localhost:8000/api/v1/auditoria/events`)*

**Método:** `POST`

### Prueba 1: Petición Exitosa (Payload Completo)

1. En Postman, selecciona el método **POST**.
2. Ingresa la URL: `http://localhost:8000/api/v1/events`.
3. Ve a la pestaña **Body** y selecciona **raw**.
4. A la derecha, asegúrate de que el formato diga **JSON**.
5. Pega el siguiente JSON:

```json
{
  "event_type": "DATA_LOADED",
  "service_name": "ms-ingestion",
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_summary": "Carga exitosa del dataset ventas_q3.csv con 15420 registros."
}
```

6. Presiona **Send**.

**Respuesta Esperada:**
Deberías recibir un código `201 Created` y un cuerpo similar a:
```json
{
  "id": 1,
  "created_at": "2026-04-18T22:50:00.000Z"
}
```

---

### Prueba 2: Validación de Campos Faltantes

1. Usa la misma pestaña de Postman.
2. Borra los campos `trace_id` y `event_summary` del JSON. Déjalo así:

```json
{
  "event_type": "DATA_LOADED",
  "service_name": "ms-ingestion"
}
```

3. Presiona **Send**.

**Respuesta Esperada:**
Deberías recibir un código `400 Bad Request` y este cuerpo:
```json
{
    "error": "Validation failed",
    "missing_fields": [
        "trace_id",
        "event_summary"
    ]
}
```
Esto confirma que la validación estricta funciona correctamente.

---

### Prueba 3: Patrón Append-Only (Solo Insertar)

La tabla de auditoría es inmutable. El controlador no permite actualizaciones ni borrados.

1. Cambia el método en Postman de **POST** a **PUT** o **DELETE**.
2. Presiona **Send**.

**Respuesta Esperada:**
Deberías recibir un código `405 Method Not Allowed`, lo que garantiza el cumplimiento del CA 4 (Aislamiento y no modificación).

---

## Verificación en Base de Datos (pgAdmin)

Para confirmar que el evento persistió correctamente, abre **pgAdmin**:
1. Conéctate a la base de datos `db_audit` en `localhost:5438`.
2. Ve a **Schemas > public > Tables > audit_events**.
3. Haz clic derecho y selecciona **View/Edit Data > All Rows**.
4. Deberías ver la fila insertada con el `trace_id` intacto y el `created_at` generado por el servidor.

## Script Table AuditEvent

CREATE TABLE AuditEvent (
id SERIAL PRIMARY KEY,
event_type VARCHAR(100) NOT NULL,
service_name VARCHAR(100) NOT NULL,
reference_id VARCHAR(255),
event_summary TEXT,
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
status VARCHAR(50)
);