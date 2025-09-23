"""
Test configuration and fixtures for the Homework App backend tests.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from faker import Faker

from app.main import app
from app.models.database import get_db, Base
from app.models.user import User
from app.models.classes import Class
from app.models.homework import Homework
from app.models.schedule import Schedule, ScheduleSlot, ScheduleSlot

fake = Faker()

# Test database setup
@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    # Clean up any existing data
    session.execute(text("DELETE FROM homework"))
    session.execute(text("DELETE FROM schedule_slots"))
    session.execute(text("DELETE FROM schedules"))
    session.execute(text("DELETE FROM classes"))
    session.execute(text("DELETE FROM users"))
    session.commit()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(test_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield test_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

# User fixtures
@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123",
        google_access_token="mock_access_token",
        google_refresh_token="mock_refresh_token"
    )

@pytest.fixture
def test_user(test_session):
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)
    return user

@pytest.fixture
def authenticated_user(test_user):
    """Create an authenticated user with tokens."""
    test_user.google_access_token = "mock_access_token"
    test_user.google_refresh_token = "mock_refresh_token"
    return test_user

# Class fixtures
@pytest.fixture
def test_class(test_session, test_user):
    """Create a test class in the database."""
    class_obj = Class(
        name="Test Class",
        teacher="Test Teacher",
        year="2024",
        color="#FF5733",
        user_id=test_user.id
    )
    test_session.add(class_obj)
    test_session.commit()
    test_session.refresh(class_obj)
    return class_obj

# Homework fixtures
@pytest.fixture
def test_homework(test_session, test_user, test_class):
    """Create a test homework in the database."""
    homework = Homework(
        title="Test Homework",
        description="Test Description",
        due_date="2024-12-31",
        status="pending",
        user_id=test_user.id,
        class_id=test_class.id
    )
    test_session.add(homework)
    test_session.commit()
    test_session.refresh(homework)
    return homework

# Schedule fixtures
@pytest.fixture
def test_schedule(test_session, test_user):
    """Create a test schedule in the database."""
    schedule = Schedule(
        name="Test Schedule",
        year="2024",
        user_id=test_user.id
    )
    test_session.add(schedule)
    test_session.commit()
    test_session.refresh(schedule)
    return schedule

# Auth mocking fixtures
@pytest.fixture
def mock_current_user(mock_user):
    """Mock the get_current_user dependency."""
    with patch('app.auth.get_current_user', return_value=mock_user):
        yield mock_user

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('app.auth.supabase') as mock_supabase:
        mock_supabase.auth.get_user.return_value = Mock(
            user=Mock(
                id="test-user-123",
                email="test@example.com",
                user_metadata={"full_name": "Test User"}
            )
        )
        yield mock_supabase

@pytest.fixture
def mock_google_calendar():
    """Mock Google Calendar service."""
    with patch('app.services.google_calendar.GoogleCalendarService') as mock_service:
        mock_instance = Mock()
        mock_instance.create_homework_event.return_value = "mock_event_id"
        mock_instance.update_homework_event.return_value = True
        mock_instance.delete_homework_event.return_value = True
        mock_service.return_value = mock_instance
        yield mock_service

# JWT Token fixtures
@pytest.fixture
def auth_headers(mock_user):
    """Create authorization headers for authenticated requests."""
    # Create a mock JWT token (in real app this would be generated properly)
    token = "mock_jwt_token"
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def valid_jwt_token():
    """Create a valid JWT token for testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock_signature"

# Data factories for generating test data
class UserFactory:
    @staticmethod
    def create(**kwargs):
        defaults = {
            "email": fake.email(),
            "full_name": fake.name(),
            "supabase_user_id": fake.uuid4(),
        }
        defaults.update(kwargs)
        return User(**defaults)

class ClassFactory:
    @staticmethod
    def create(user_id, **kwargs):
        defaults = {
            "name": fake.word().title() + " Class",
            "teacher": fake.name(),
            "year": "2024",
            "color": fake.color(),
            "user_id": user_id,
        }
        defaults.update(kwargs)
        return Class(**defaults)

class HomeworkFactory:
    @staticmethod
    def create(user_id, class_id, **kwargs):
        defaults = {
            "title": fake.sentence(nb_words=3),
            "description": fake.text(max_nb_chars=200),
            "due_date": fake.date_between(start_date="today", end_date="+30d").isoformat(),
            "status": "pending",
            "user_id": user_id,
            "class_id": class_id,
        }
        defaults.update(kwargs)
        return Homework(**defaults)

@pytest.fixture
def user_factory():
    return UserFactory

@pytest.fixture
def class_factory():
    return ClassFactory

@pytest.fixture
def homework_factory():
    return HomeworkFactory