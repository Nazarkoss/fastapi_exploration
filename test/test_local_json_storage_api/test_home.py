from fastapi.testclient import TestClient

from local_json_storage_api.carsharing_local_db import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text
