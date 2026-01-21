from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home_or_tasks_endpoint():
    # since you don't have "/" endpoint, testing /tasks
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
