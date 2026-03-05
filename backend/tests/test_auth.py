import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# In-memory SQLite for tests
TEST_DB_URL = "sqlite:///./test_healing_bot.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_register_and_login(client):
    # Register
    resp = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "testuser"

    # Login
    resp2 = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "secret123",
    })
    assert resp2.status_code == 200
    token = resp2.json()["access_token"]
    assert token

    # Wrong password
    resp3 = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert resp3.status_code == 401


def test_duplicate_register(client):
    client.post("/api/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "abc123",
    })
    resp = client.post("/api/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "abc123",
    })
    assert resp.status_code == 400
