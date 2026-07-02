"""
Pytest fixtures — Temporary SQLite DB for testing

- Uses an in-memory SQLite database (via StaticPool so the same
  connection is reused across requests).
- Tables are created/dropped fresh for every test function.
- The real `get_session` dependency is overridden so the app never
  touches the production database.
- The lifespan's `create_db_and_tables()` call is patched out so
  startup doesn't also try to hit the production DB.
"""

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_session
from app.models.user import User

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session", autouse=True)
def session_fixture():
    """Create fresh tables before each test, drop them afterwards."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session):
    """TestClient wired to the temporary DB instead of the real one."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    # Prevent the app's lifespan from creating/touching the production DB
    with patch("app.main.init_db"):
        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_login_user")
def test_login_user_fixture(client):
    """Registers and logs in a normal (non-admin) user."""
    client.post(
        "/auth/register",
        json={"username": "testuser", "password": "testpass123"},
    )

    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpass123"},
    )
    token = response.json()["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_data = me.json()

    return {"token": token, "id": user_data["id"], "username": "testuser"}


@pytest.fixture(name="test_admin")
def test_admin_fixture(client, session):
    """Registers a user, promotes it to admin directly in the DB, then logs in."""
    # Register admin user
    register_response = client.post(
        "/auth/register",
        json={"username": "adminuser", "password": "adminpass123"},
    )
    assert register_response.status_code == 201, f"Failed to register admin: {register_response.text}"
    user_data = register_response.json()
    
    # Promote to admin in database
    user = session.get(User, user_data["id"])
    assert user is not None, "User not found in database"
    user.is_admin = True
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Login to get token
    response = client.post(
        "/auth/login",
        data={"username": "adminuser", "password": "adminpass123"},
    )
    assert response.status_code == 200, f"Failed to login admin: {response.text}"
    token = response.json()["access_token"]
    
    # Verify user is admin
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    me_data = me.json()
    assert me_data["is_admin"] == True, "User was not promoted to admin"

    return {"token": token, "id": user_data["id"], "username": "adminuser"}


@pytest.fixture(name="test_hero")
def test_hero_fixture(client, test_login_user):
    """Creates a hero (named 'Test Hero') owned/created by test_login_user."""
    response = client.post(
        "/heroes/",
        json={"name": "Test Hero", "power": "Test Power"},
        headers={"Authorization": f"Bearer {test_login_user['token']}"},
    )
    assert response.status_code == 201, f"Failed to create hero: {response.text}"
    return response.json()

@pytest.fixture(name="test_hero_id")
def test_hero_id_fixture(client, test_login_user):
    """Creates a hero and returns just the ID."""
    response = client.post(
        "/heroes/",
        json={"name": "Hero By ID", "power": "Power By ID"},
        headers={"Authorization": f"Bearer {test_login_user['token']}"},
    )
    assert response.status_code == 201, f"Failed to create hero: {response.text}"
    return response.json()["id"]