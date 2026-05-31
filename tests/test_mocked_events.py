import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.routers.events import get_audit_service

# Creamos el mock para el servicio
mock_service = MagicMock()

def override_get_audit_service():
    return mock_service

@pytest.fixture(autouse=True)
def setup_dependency_override():
    # Establecer el override antes del test
    app.dependency_overrides[get_audit_service] = override_get_audit_service
    yield
    # Limpiar el override después del test
    app.dependency_overrides.pop(get_audit_service, None)
    mock_service.reset_mock()

def test_create_event_mocked():
    payload = {
        "event_type": "DATA_LOADED",
        "service_name": "ms-ingestion",
        "reference_id": "REF-123456",
        "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "event_summary": "Carga exitosa del dataset",
        "status": "SUCCESS"
    }
    
    mock_service.process_audit_event.return_value = {
        "id": 1,
        "event_type": "DATA_LOADED",
        "service_name": "ms-ingestion",
        "reference_id": "REF-123456",
        "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "event_summary": "Carga exitosa del dataset",
        "status": "SUCCESS",
        "created_at": "2026-05-28T00:00:00"
    }
    
    client = TestClient(app)
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["status"] == "SUCCESS"
    mock_service.process_audit_event.assert_called_once()

def test_get_events_mocked():
    mock_service.get_audit_events.return_value = [
        {
            "id": 1,
            "event_type": "DATA_LOADED",
            "service_name": "ms-ingestion",
            "reference_id": "REF-123456",
            "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "event_summary": "Carga exitosa del dataset",
            "status": "SUCCESS",
            "created_at": "2026-05-28T00:00:00"
        }
    ]
    
    client = TestClient(app)
    response = client.get("/api/v1/events?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 1
    mock_service.get_audit_events.assert_called_once_with(limit=10, offset=0)
