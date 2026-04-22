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

# Guía de Pruebas de Microservicios vía API Gateway

Esta guía detalla los pasos para validar que los nuevos microservicios (`ms-analytics` y `ms-configuration`) están correctamente integrados al **API Gateway** y respondiendo a través del puerto central `8000`.

---

## 📋 Requisitos Previos

1.  **Levantar Infraestructura:** Asegúrate de que los contenedores estén corriendo:
    ```bash
    docker compose up -d
    ```
    *(O si estás probando localmente, asegúrate de que cada servicio esté iniciado en su respectivo puerto: Gateway: 8000, Configuration: 8004, Analytics: 8005).*

2.  **Postman:** Tener instalado Postman o una herramienta similar (Thunder Client, Insomnia).

---

## 🚦 Paso 1: Validar Conectividad (Health Checks)

Antes de probar lógica de negocio, verificamos que el Gateway puede llegar a los microservicios.

### A. Probar ms-analytics vía Gateway
- **Método:** `GET`
- **URL:** `http://localhost:8000/api/v1/analytics/health`
- **Respuesta esperada (200 OK):**
  ```json
  {
      "status": "ok",
      "service": "ms-ANALYTICS"
  }
  ```

### B. Probar ms-configuration vía Gateway
- **Método:** `GET`
- **URL:** `http://localhost:8000/api/v1/configuration/health`
- **Respuesta esperada (200 OK):**
  ```json
  {
      "status": "ok",
      "service": "ms-CONFIGURATION"
  }
  ```

---

## 📊 Paso 2: Probar Sincronización de Analítica

El microservicio de analítica recibe datos transformados. Vamos a simular un envío desde el Gateway.

- **Método:** `POST`
- **URL:** `http://localhost:8000/api/v1/analytics/internal/sync/DATASET_001`
- **Headers:** `Content-Type: application/json`
- **Body (Raw JSON):**
  ```json
  {
    "data": [
      {
        "zone_code": "Z01",
        "zone_name": "Zona Norte",
        "region": "Capital",
        "metrics": {
          "poverty_index": 0.25,
          "population": 1200
        }
      },
      {
        "zone_code": "Z02",
        "zone_name": "Zona Sur",
        "region": "Periferia",
        "metrics": {
          "poverty_index": 0.45,
          "population": 850
        }
      }
    ]
  }
  ```
- **Respuesta esperada:** Un JSON indicando el éxito de la operación.

---

## 🛠️ Solución de Problemas (Troubleshooting)

### ❌ Error 503 Service Unavailable
Si el Gateway responde con:
`"detail": "Error: El ms-analytics (Puerto 8005) está apagado o no responde."`
**Solución:** Verifica que el microservicio esté encendido. Si estás usando Docker, revisa que el nombre del servicio en `docker-compose.yml` coincida con la URL configurada en el Gateway.

### ❌ Error 404 Not Found
**Solución:** Asegúrate de que la URL en Postman incluya exactamente los prefijos correctos:
- `/api/v1/analytics/...`
- `/api/v1/configuration/...`

### 🔍 Prueba Directa (Bypass Gateway)
Si sospechas que el problema es el Gateway, intenta llamar al microservicio directamente:
- **Analytics:** `http://localhost:8005/api/v1/analytics/health`
- **Configuration:** `http://localhost:8004/api/v1/configuration/health`

---

## 🛡️ Paso 3: Probar Auditoría Automática desde Ingestión

Hemos configurado `ms-ingestion` para que dispare un evento de auditoría de forma asíncrona cada vez que cargue un dataset con éxito. Para probar este flujo integral, sigue estos pasos:

### Opción A: Prueba de Ingesta desde el API Gateway (Recomendado)
- **Método:** `POST`
- **URL:** `http://localhost:8000/api/v1/ingesta/datasets`
- **Body:** `form-data` con un archivo `file` válido (ej. un CSV o JSON).
- **Flujo Esperado:** 
  1. El Gateway recibe y transfiere el archivo a `ms-ingestion`.
  2. `ms-ingestion` responde con éxito y su `dataset_load_id`.
  3. En background, `ms-ingestion` emitirá de inmediato el evento `DATA_INGESTION_COMPLETED` hacia `ms-auditoria`.

### Opción B: Prueba Directa en el puerto del Microservicio
Puedes saltarte el Gateway e invocar el microservicio directo usando su puerto nativo, típicamente `8001`:
- **Método:** `POST`
- **URL:** `http://localhost:8001/api/v1/ingesta/datasets`
- **Body:** `form-data` -> `file`

### ✅ Verificación del Evento Creado
Tras enviar cualquiera de las dos peticiones anteriores sin error, comprueba tu base de datos de auditoría (`db-audit` ubicada típicamente en el puerto local `5438`) y verás registrado el nuevo evento, confirmando así que el flujo entre **Ingesta -> Auditoría** funciona a la perfección.
