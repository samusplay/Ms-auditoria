import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database import Base, get_db

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_event_success():
    payload = {
        "event_type": "DATA_LOADED",
        "service_name": "ms-ingestion",
        "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "event_summary": "Carga exitosa del dataset ventas_q3.csv con 15420 registros."
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "created_at" in data

    # Verify trace_id in DB (isolated check)
    db = TestingSessionLocal()
    from app.infrastructure.models.audit_event import AuditEvent
    event_in_db = db.query(AuditEvent).filter(AuditEvent.id == data["id"]).first()
    assert event_in_db is not None
    assert event_in_db.trace_id == payload["trace_id"]
    db.close()

def test_create_event_missing_fields():
    payload = {
        "event_type": "DATA_LOADED",
        "service_name": "ms-ingestion"
        # missing trace_id and event_summary
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Validation failed"
    assert "trace_id" in data["missing_fields"]
    assert "event_summary" in data["missing_fields"]

def test_method_not_allowed():
    payload = {"event_type": "TEST", "service_name": "test", "trace_id": "123", "event_summary": "test"}
    
    response = client.put("/api/v1/events", json=payload)
    assert response.status_code == 405
    
    response = client.patch("/api/v1/events", json=payload)
    assert response.status_code == 405
    
    response = client.delete("/api/v1/events")
    assert response.status_code == 405
