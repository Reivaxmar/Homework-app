"""
Tests for Class model.
"""
import pytest
from app.models.user import User
from app.models.classes import Class

def test_create_class(db):
    """Test creating a new class."""
    # First create a user
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create a class
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024",
        half_group="A",
        color="#FF5733"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    assert class_obj.id is not None
    assert class_obj.user_id == user.id
    assert class_obj.name == "Mathematics"
    assert class_obj.teacher == "Dr. Smith"
    assert class_obj.year == "2024"
    assert class_obj.half_group == "A"
    assert class_obj.color == "#FF5733"
    assert class_obj.created_at is not None
    assert class_obj.updated_at is not None

def test_class_default_color(db):
    """Test that class has default color."""
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
    
    assert class_obj.color == "#3B82F6"  # Default blue color

def test_class_optional_half_group(db):
    """Test that half_group is optional."""
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
    
    assert class_obj.half_group is None

def test_class_user_relationship(db):
    """Test class-user relationship."""
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
    
    # Test relationship works both ways
    assert class_obj.user.id == user.id
    assert class_obj.user.email == "test@example.com"
    assert len(user.classes) == 1
    assert user.classes[0].id == class_obj.id

def test_class_repr(db):
    """Test class string representation."""
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
    
    expected = "<Class(name='Mathematics', teacher='Dr. Smith', year='2024')>"
    assert repr(class_obj) == expected

def test_class_relationships_exist(db):
    """Test that class has proper relationships defined."""
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
    
    # Test relationships exist (should be empty lists initially)
    assert hasattr(class_obj, 'schedule_slots')
    assert hasattr(class_obj, 'homework')
    assert hasattr(class_obj, 'user')
    assert class_obj.schedule_slots == []
    assert class_obj.homework == []