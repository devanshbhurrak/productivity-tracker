def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert "version" in r.json()

def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code == 200
    r = client.get("/openapi.json")
    assert r.status_code == 200
    data = r.json()
    assert "paths" in data
    # Check some expected paths
    assert "/api/v1/auth/register" in data["paths"]
    assert "/api/v1/tasks" in data["paths"]
    assert "/api/v1/time-sessions/start" in data["paths"]
    assert "/api/v1/dashboard/today" in data["paths"]
