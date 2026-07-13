from fastapi.testclient import TestClient
from app.gateway.main import app

client = TestClient(app)

def test_dashboard_returns_html():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Mini Greenlight Engine" in response.text
    assert response.headers["content-type"].startswith("text/html")