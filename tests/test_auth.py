from fastapi.testclient import TestClient
from app.gateway.main import app

client = TestClient(app)

def test_scan_rejects_missing_api_key():
    response = client.post("/scan", json={"vendor_name": "test", "cloud_state": {}})
    assert response.status_code == 422

def test_scan_rejects_wrong_api_key():
    response = client.post(
        "/scan",
        headers={"X-API-Key": "wrong-key"},
        json={"vendor_name": "test", "cloud_state": {}}
    )
    assert response.status_code == 401

def test_health_check_is_public():
    response = client.get("/health")
    assert response.status_code == 200