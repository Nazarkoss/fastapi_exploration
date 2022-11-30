from fastapi.testclient import TestClient

import os
import sys
sys.path.append("/".join(os.getcwd().split("/")[:-1]))

from  local_json_storage_api.carsharing_json import app

client = TestClient(app)


def test_get_cars():
    response = client.get("/api/cars")
    assert response.status_code == 200
    cars = response.json()
    assert all(["doors" in c for c in cars])
    assert all(["size" in c for c in cars])

