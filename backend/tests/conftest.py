"""
Test configuration and fixtures for the Homework Management App backend tests.
"""
import os
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base, get_db
from app.config import settings

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create a test client with a test database."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "supabase_user_id": "test-user-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "avatar_url": "https://example.com/avatar.jpg"
    }

@pytest.fixture
def test_class_data():
    """Sample class data for testing."""
    return {
        "name": "Mathematics",
        "description": "Advanced Mathematics Course",
        "teacher": "Dr. Smith",
        "room": "Room 101",
        "color": "#FF5733"
    }

@pytest.fixture
def test_homework_data():
    """Sample homework data for testing."""
    return {
        "title": "Math Assignment 1",
        "description": "Complete exercises 1-10",
        "due_date": "2024-01-15T23:59:00",
        "class_id": 1,
        "priority": "medium",
        "status": "pending"
    }

@pytest.fixture
def test_schedule_data():
    """Sample schedule data for testing."""
    return {
        "class_id": 1,
        "day_of_week": 1,  # Monday
        "start_time": "09:00",
        "end_time": "10:30"
    }

@pytest.fixture
def authenticated_user(client, test_user_data):
    """Create an authenticated user session."""
    # Create user via auth endpoint
    response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": test_user_data["supabase_user_id"]},
        json=test_user_data
    )
    assert response.status_code == 200
    token_data = response.json()
    
    # Return client with auth headers
    client.headers.update({"Authorization": f"Bearer {token_data['access_token']}"})
    return client, token_data

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-testing")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-google-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-google-client-secret")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-service-key")