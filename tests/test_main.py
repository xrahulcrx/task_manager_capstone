from fastapi.testclient import TestClient
from task_man.main import app

def test_list_tasks():
    with TestClient(app) as client:
        res = client.get("/tasks")
        assert res.status_code == 200
        assert isinstance(res.json(), list)
