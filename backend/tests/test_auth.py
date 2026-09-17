def test_successful_registration(client):
    r = client.post("/api/v1/auth/register", json={"name": "John Doe", "email": "john@example.com", "password": "password123"})
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "john@example.com"
    assert "password" not in str(data).lower()
    assert "password_hash" not in data


def test_duplicate_email(client, user_factory):
    user_factory(email="dup@example.com")
    r = client.post("/api/v1/auth/register", json={"name": "Another", "email": "dup@example.com", "password": "password123"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    # Case insensitive
    r = client.post("/api/v1/auth/register", json={"name": "Another", "email": "DUP@example.com", "password": "password123"})
    assert r.status_code == 409


def test_invalid_email(client):
    r = client.post("/api/v1/auth/register", json={"name": "Test", "email": "invalid-email", "password": "password123"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_password(client):
    r = client.post("/api/v1/auth/register", json={"name": "Test", "email": "valid@example.com", "password": "short"})
    assert r.status_code == 422
    # Too short
    r = client.post("/api/v1/auth/register", json={"name": "Test", "email": "valid2@example.com", "password": ""})
    assert r.status_code == 422


def test_successful_login(client, user_factory):
    user_factory(email="login@example.com", password="password123")
    r = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_invalid_credentials(client, user_factory):
    user_factory(email="cred@example.com", password="password123")
    r = client.post("/api/v1/auth/login", json={"email": "cred@example.com", "password": "wrongpass"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_CREDENTIALS"
    r = client.post("/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "password123"})
    assert r.status_code == 401


def test_logout(client, user_factory):
    u = user_factory(email="logout@example.com")
    headers = u["headers"]
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200
    r = client.post("/api/v1/auth/logout", headers=headers)
    assert r.status_code == 204
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 401
    # Without auth also 401
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_protected_without_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
    r = client.get("/api/v1/tasks")
    assert r.status_code == 401
    r = client.post("/api/v1/tasks", json={"title": "test"})
    assert r.status_code == 401
    r = client.get("/api/v1/time-sessions")
    assert r.status_code == 401
    r = client.get("/api/v1/dashboard/today")
    assert r.status_code == 401


def test_current_user(client, user_factory):
    u = user_factory(name="Current", email="current@example.com")
    r = client.get("/api/v1/auth/me", headers=u["headers"])
    assert r.status_code == 200
    assert r.json()["email"] == "current@example.com"
    assert r.json()["name"] == "Current"


def test_email_normalization(client):
    r = client.post("/api/v1/auth/register", json={"name": "Norm", "email": "  TeSt@Example.COM  ", "password": "password123"})
    assert r.status_code == 201
    assert r.json()["email"] == "test@example.com"
    # Duplicate with normalized
    r = client.post("/api/v1/auth/register", json={"name": "Norm2", "email": "TEST@example.com", "password": "password123"})
    assert r.status_code == 409


def test_password_not_returned(client, user_factory):
    u = user_factory(email="nopass@example.com")
    r = client.get("/api/v1/auth/me", headers=u["headers"])
    assert "password" not in r.text.lower()
