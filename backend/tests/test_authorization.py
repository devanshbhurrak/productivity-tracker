import pytest


def test_user_a_cannot_read_user_b_task(client, user_factory):
    alice = user_factory(email="alice_auth@example.com")
    bob = user_factory(email="bob_auth@example.com")
    # Alice creates task
    r = client.post("/api/v1/tasks", json={"title": "Alice Secret"}, headers=alice["headers"])
    tid = r.json()["id"]
    # Bob tries to read
    r = client.get(f"/api/v1/tasks/{tid}", headers=bob["headers"])
    assert r.status_code == 404
    # Bob list should not contain alice task
    r = client.get("/api/v1/tasks", headers=bob["headers"])
    assert r.json()["pagination"]["total"] == 0


def test_user_a_cannot_update_user_b_task(client, user_factory):
    alice = user_factory(email="alice_up@example.com")
    bob = user_factory(email="bob_up@example.com")
    r = client.post("/api/v1/tasks", json={"title": "Alice Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.patch(f"/api/v1/tasks/{tid}", json={"title": "Hacked"}, headers=bob["headers"])
    assert r.status_code == 404
    # Verify not updated
    r = client.get(f"/api/v1/tasks/{tid}", headers=alice["headers"])
    assert r.json()["title"] == "Alice Task"


def test_user_a_cannot_delete_user_b_task(client, user_factory):
    alice = user_factory(email="alice_del@example.com")
    bob = user_factory(email="bob_del@example.com")
    r = client.post("/api/v1/tasks", json={"title": "Alice Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.delete(f"/api/v1/tasks/{tid}", headers=bob["headers"])
    assert r.status_code == 404
    # Still exists for alice
    r = client.get(f"/api/v1/tasks/{tid}", headers=alice["headers"])
    assert r.status_code == 200


def test_user_a_cannot_read_user_b_time_session(client, user_factory):
    alice = user_factory(email="alice_sess@example.com")
    bob = user_factory(email="bob_sess@example.com")
    # Alice creates task and session
    r = client.post("/api/v1/tasks", json={"title": "Alice Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=alice["headers"])
    sid = r.json()["id"]
    # Bob tries to list task sessions for alice task (should 404 because task not owned)
    r = client.get(f"/api/v1/tasks/{tid}/time-sessions", headers=bob["headers"])
    assert r.status_code == 404
    # Bob tries to stop alice session
    r = client.post(f"/api/v1/time-sessions/{sid}/stop", headers=bob["headers"])
    assert r.status_code == 404
    # Bob's own time-sessions list should be empty
    r = client.get("/api/v1/time-sessions", headers=bob["headers"])
    assert r.json()["pagination"]["total"] == 0
    # Summary also blocked
    r = client.get(f"/api/v1/tasks/{tid}/time-summary", headers=bob["headers"])
    assert r.status_code == 404


def test_user_a_cannot_start_user_b_task_timer(client, user_factory):
    alice = user_factory(email="alice_start@example.com")
    bob = user_factory(email="bob_start@example.com")
    r = client.post("/api/v1/tasks", json={"title": "Alice Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=bob["headers"])
    assert r.status_code == 404


def test_user_a_cannot_stop_user_b_timer(client, user_factory):
    alice = user_factory(email="alice_stop@example.com")
    bob = user_factory(email="bob_stop@example.com")
    # Bob creates and starts
    r = client.post("/api/v1/tasks", json={"title": "Bob Task"}, headers=bob["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=bob["headers"])
    sid = r.json()["id"]
    # Alice tries to stop
    r = client.post(f"/api/v1/time-sessions/{sid}/stop", headers=alice["headers"])
    assert r.status_code == 404
    # Bob can still stop
    r = client.post(f"/api/v1/time-sessions/{sid}/stop", headers=bob["headers"])
    assert r.status_code == 200


def test_dashboard_isolation(client, user_factory):
    alice = user_factory(email="alice_dash@example.com")
    bob = user_factory(email="bob_dash@example.com")
    # Alice creates task and tracks time
    r = client.post("/api/v1/tasks", json={"title": "Alice Task"}, headers=alice["headers"])
    tid = r.json()["id"]
    r = client.post("/api/v1/time-sessions/start", json={"task_id": tid}, headers=alice["headers"])
    sid = r.json()["id"]
    import time; time.sleep(1)
    client.post(f"/api/v1/time-sessions/{sid}/stop", headers=alice["headers"])
    # Bob dashboard should be empty
    r = client.get("/api/v1/dashboard/today", headers=bob["headers"])
    assert r.status_code == 200
    assert r.json()["total_tracked_seconds"] == 0
    assert r.json()["tasks_worked_on"] == 0
    # Alice dashboard has data
    r = client.get("/api/v1/dashboard/today", headers=alice["headers"])
    assert r.json()["total_tracked_seconds"] > 0
    assert r.json()["tasks_worked_on"] == 1
