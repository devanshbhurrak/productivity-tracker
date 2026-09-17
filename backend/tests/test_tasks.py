import pytest
import time


def test_create_task(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": " follow up with designer "}, headers=alice["headers"])
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "follow up with designer"  # trimmed
    assert data["status"] == "PENDING"
    assert "id" in data


def test_read_task(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Task Read"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.get(f"/api/v1/tasks/{tid}", headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["title"] == "Task Read"


def test_update_task(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Original"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.patch(f"/api/v1/tasks/{tid}", json={"title": "Updated", "description": "New desc"}, headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["title"] == "Updated"
    assert r.json()["description"] == "New desc"


def test_delete_task(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "To Delete"}, headers=alice["headers"])
    tid = r.json()["id"]
    # Also create a time session
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=alice["headers"])
    sid = r.json()["id"]
    time.sleep(0.5)
    client.post(f"/api/v1/time-sessions/{sid}/stop", headers=alice["headers"])
    r = client.delete(f"/api/v1/tasks/{tid}", headers=alice["headers"])
    assert r.status_code == 204
    r = client.get(f"/api/v1/tasks/{tid}", headers=alice["headers"])
    assert r.status_code == 404
    # Time sessions should be cascade deleted
    r = client.get("/api/v1/time-sessions", headers=alice["headers"])
    assert r.json()["pagination"]["total"] == 0


def test_status_changes(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Status Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    assert r.json()["status"] == "PENDING"
    # PENDING -> IN_PROGRESS
    r = client.patch(f"/api/v1/tasks/{tid}", json={"status": "IN_PROGRESS"}, headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"
    assert r.json()["completed_at"] is None
    # IN_PROGRESS -> COMPLETED
    r = client.patch(f"/api/v1/tasks/{tid}", json={"status": "COMPLETED"}, headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["status"] == "COMPLETED"
    assert r.json()["completed_at"] is not None
    # COMPLETED -> IN_PROGRESS (reopen)
    r = client.patch(f"/api/v1/tasks/{tid}", json={"status": "IN_PROGRESS"}, headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"
    assert r.json()["completed_at"] is None  # cleared on reopen


def test_invalid_status(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Invalid Status"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.patch(f"/api/v1/tasks/{tid}", json={"status": "NOT_A_STATUS"}, headers=alice["headers"])
    assert r.status_code == 422
    # Create with invalid status also fails
    r = client.post("/api/v1/tasks", json={"title": "Bad", "status": "WRONG"}, headers=alice["headers"])
    assert r.status_code == 422


def test_search(client, user_factory):
    alice = user_factory()
    client.post("/api/v1/tasks", json={"title": "Build Authentication", "description": "OAuth flow"}, headers=alice["headers"])
    client.post("/api/v1/tasks", json={"title": "Write Docs", "description": "authentication guide"}, headers=alice["headers"])
    client.post("/api/v1/tasks", json={"title": "Fix Bug", "description": " unrelated"}, headers=alice["headers"])
    # Search title
    r = client.get("/api/v1/tasks", params={"search": "Authentication"}, headers=alice["headers"])
    assert r.status_code == 200
    assert r.json()["pagination"]["total"] == 2
    # Search description case insensitive
    r = client.get("/api/v1/tasks", params={"search": "oauth"}, headers=alice["headers"])
    assert r.json()["pagination"]["total"] == 1


def test_filtering(client, user_factory):
    alice = user_factory()
    r = client.post("/api/v1/tasks", json={"title": "Filter PENDING"}, headers=alice["headers"])
    tid_pending = r.json()["id"]
    r = client.post("/api/v1/tasks", json={"title": "Filter COMPLETED"}, headers=alice["headers"])
    tid_completed = r.json()["id"]
    client.patch(f"/api/v1/tasks/{tid_completed}", json={"status": "COMPLETED"}, headers=alice["headers"])
    # Filter by status
    r = client.get("/api/v1/tasks", params={"status": "COMPLETED"}, headers=alice["headers"])
    assert r.json()["pagination"]["total"] == 1
    assert r.json()["items"][0]["id"] == tid_completed
    r = client.get("/api/v1/tasks", params={"status": "PENDING"}, headers=alice["headers"])
    # Should include at least the pending one (plus maybe others)
    ids = [i["id"] for i in r.json()["items"]]
    assert tid_pending in ids


def test_sorting(client, user_factory):
    alice = user_factory()
    client.post("/api/v1/tasks", json={"title": "B Title"}, headers=alice["headers"])
    time.sleep(0.01)
    client.post("/api/v1/tasks", json={"title": "A Title"}, headers=alice["headers"])
    time.sleep(0.01)
    client.post("/api/v1/tasks", json={"title": "C Title"}, headers=alice["headers"])
    r = client.get("/api/v1/tasks", params={"sort_by": "title", "sort_order": "asc"}, headers=alice["headers"])
    titles = [t["title"] for t in r.json()["items"]]
    assert titles == sorted(titles)
    r = client.get("/api/v1/tasks", params={"sort_by": "title", "sort_order": "desc"}, headers=alice["headers"])
    titles_desc = [t["title"] for t in r.json()["items"]]
    assert titles_desc == sorted(titles, reverse=True)
    # Created_at sort
    r = client.get("/api/v1/tasks", params={"sort_by": "created_at", "sort_order": "desc"}, headers=alice["headers"])
    assert r.status_code == 200
    # Invalid sort defaults to created_at
    r = client.get("/api/v1/tasks", params={"sort_by": "invalid_column"}, headers=alice["headers"])
    assert r.status_code == 200


def test_pagination(client, user_factory):
    alice = user_factory()
    for i in range(5):
        client.post("/api/v1/tasks", json={"title": f"Paginate {i}"}, headers=alice["headers"])
    r = client.get("/api/v1/tasks", params={"page": 1, "page_size": 2}, headers=alice["headers"])
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2
    assert data["pagination"]["total"] == 5
    assert data["pagination"]["total_pages"] == 3
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_previous"] is False
    r = client.get("/api/v1/tasks", params={"page": 3, "page_size": 2}, headers=alice["headers"])
    assert len(r.json()["items"]) == 1
    assert r.json()["pagination"]["has_next"] is False
    assert r.json()["pagination"]["has_previous"] is True


def test_task_validation(client, user_factory):
    alice = user_factory()
    # Empty title
    r = client.post("/api/v1/tasks", json={"title": "   "}, headers=alice["headers"])
    assert r.status_code == 422
    # Title too long
    r = client.post("/api/v1/tasks", json={"title": "a" * 256}, headers=alice["headers"])
    assert r.status_code == 422
    # Description too long
    r = client.post("/api/v1/tasks", json={"title": "Valid", "description": "x" * 2001}, headers=alice["headers"])
    assert r.status_code == 422


def test_pagination_max_size(client, user_factory):
    alice = user_factory()
    r = client.get("/api/v1/tasks", params={"page_size": 200}, headers=alice["headers"])
    # Should be 422 due to le=100 validation
    assert r.status_code == 422
