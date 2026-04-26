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
        "source_service": "ms-ingestion",
        "reference_id": "REF-123456",
        "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "details": {"rows_processed": 15420, "file_name": "ventas_q3.csv"},
        "status": "SUCCESS"
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "created_at" in data

    assert "status" in data
    assert "reference_id" in data

    # Verify trace_id in DB (isolated check)
    db = TestingSessionLocal()
    from app.infrastructure.models.audit_event import AuditEventModel
    event_in_db = db.query(AuditEventModel).filter(AuditEventModel.id == data["id"]).first()
    assert event_in_db is not None
    assert event_in_db.trace_id == payload["trace_id"]
    assert event_in_db.reference_id == payload["reference_id"]
    assert event_in_db.status == payload["status"]
    db.close()

def test_create_event_missing_fields():
    payload = {
        "event_type": "DATA_LOADED",
        "source_service": "ms-ingestion"
        # missing trace_id and details
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "Validation failed"
    assert "trace_id" in data["missing_fields"]
    assert "details" in data["missing_fields"]

def test_method_not_allowed():
    payload = {"event_type": "TEST", "source_service": "test", "trace_id": "123", "details": {"test": True}}
    
    response = client.put("/api/v1/events", json=payload)
    assert response.status_code == 405
    
    response = client.patch("/api/v1/events", json=payload)
    assert response.status_code == 405
    
    response = client.delete("/api/v1/events")
    assert response.status_code == 405
