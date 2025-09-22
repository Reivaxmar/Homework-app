"""
Tests for Homework model.
"""
import pytest
from datetime import date, time, datetime
from app.models.user import User
from app.models.classes import Class
from app.models.homework import Homework, Priority, Status

def test_create_homework(db):
    """Test creating a new homework assignment."""
    # Create user and class first
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    # Create homework
    homework = Homework(
        class_id=class_obj.id,
        user_id=user.id,
        title="Math Assignment 1",
        description="Complete exercises 1-10",
        due_date=date(2024, 1, 15),
        due_time=time(23, 59),
        priority=Priority.HIGH,
        status=Status.PENDING
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    assert homework.id is not None
    assert homework.class_id == class_obj.id
    assert homework.user_id == user.id
    assert homework.title == "Math Assignment 1"
    assert homework.description == "Complete exercises 1-10"
    assert homework.due_date == date(2024, 1, 15)
    assert homework.due_time == time(23, 59)
    assert homework.priority == Priority.HIGH
    assert homework.status == Status.PENDING
    assert homework.assigned_date == date.today()  # Default
    assert homework.created_at is not None
    assert homework.updated_at is not None

def test_homework_defaults(db):
    """Test homework default values."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    homework = Homework(
        class_id=class_obj.id,
        user_id=user.id,
        title="Test Assignment",
        due_date=date(2024, 1, 15)
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    assert homework.priority == Priority.MEDIUM  # Default priority
    assert homework.status == Status.PENDING     # Default status
    assert homework.due_time == time(23, 59)     # Default due time
    assert homework.assigned_date == date.today()  # Default assigned date
    assert homework.description is None          # Optional field
    assert homework.google_calendar_event_id is None  # Optional field
    assert homework.completed_at is None         # Optional field

def test_homework_priority_enum(db):
    """Test homework priority enum values."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    # Test all priority levels
    for priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH]:
        homework = Homework(
            class_id=class_obj.id,
            user_id=user.id,
            title=f"Assignment {priority.value}",
            due_date=date(2024, 1, 15),
            priority=priority
        )
        db.add(homework)
        db.commit()
        db.refresh(homework)
        
        assert homework.priority == priority

def test_homework_status_enum(db):
    """Test homework status enum values."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    # Test all status values
    for status in [Status.PENDING, Status.IN_PROGRESS, Status.COMPLETED]:
        homework = Homework(
            class_id=class_obj.id,
            user_id=user.id,
            title=f"Assignment {status.value}",
            due_date=date(2024, 1, 15),
            status=status
        )
        db.add(homework)
        db.commit()
        db.refresh(homework)
        
        assert homework.status == status

def test_homework_relationships(db):
    """Test homework relationships with user and class."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    homework = Homework(
        class_id=class_obj.id,
        user_id=user.id,
        title="Test Assignment",
        due_date=date(2024, 1, 15)
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    # Test relationships work both ways
    assert homework.user.id == user.id
    assert homework.class_.id == class_obj.id
    assert len(user.homework) == 1
    assert user.homework[0].id == homework.id
    assert len(class_obj.homework) == 1
    assert class_obj.homework[0].id == homework.id

def test_homework_repr(db):
    """Test homework string representation."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    homework = Homework(
        class_id=class_obj.id,
        user_id=user.id,
        title="Test Assignment",
        due_date=date(2024, 1, 15)
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    expected = "<Homework(title='Test Assignment', class='Mathematics', due='2024-01-15')>"
    assert repr(homework) == expected

def test_homework_google_calendar_integration(db):
    """Test Google Calendar integration fields."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    homework = Homework(
        class_id=class_obj.id,
        user_id=user.id,
        title="Test Assignment",
        due_date=date(2024, 1, 15),
        google_calendar_event_id="calendar_event_123"
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    assert homework.google_calendar_event_id == "calendar_event_123"

def test_homework_completion_tracking(db):
    """Test homework completion tracking."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    homework = Homework(
        class_id=class_obj.id,
        user_id=user.id,
        title="Test Assignment",
        due_date=date(2024, 1, 15),
        status=Status.COMPLETED,
        completed_at=datetime.utcnow()
    )
    db.add(homework)
    db.commit()
    db.refresh(homework)
    
    assert homework.status == Status.COMPLETED
    assert homework.completed_at is not None