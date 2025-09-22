"""
Tests for User model.
"""
import pytest
from datetime import datetime
from app.models.user import User

def test_create_user(db):
    """Test creating a new user."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        avatar_url="https://example.com/avatar.jpg",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.avatar_url == "https://example.com/avatar.jpg"
    assert user.supabase_user_id == "test-user-123"
    assert user.created_at is not None
    assert user.updated_at is not None

def test_user_unique_email(db):
    """Test that user email must be unique."""
    user1 = User(
        email="test@example.com",
        full_name="Test User 1",
        supabase_user_id="test-user-1"
    )
    user2 = User(
        email="test@example.com",
        full_name="Test User 2",
        supabase_user_id="test-user-2"
    )
    
    db.add(user1)
    db.commit()
    
    db.add(user2)
    with pytest.raises(Exception):  # Should raise IntegrityError
        db.commit()

def test_user_unique_supabase_id(db):
    """Test that supabase_user_id must be unique."""
    user1 = User(
        email="test1@example.com",
        full_name="Test User 1",
        supabase_user_id="test-user-123"
    )
    user2 = User(
        email="test2@example.com",
        full_name="Test User 2",
        supabase_user_id="test-user-123"
    )
    
    db.add(user1)
    db.commit()
    
    db.add(user2)
    with pytest.raises(Exception):  # Should raise IntegrityError
        db.commit()

def test_user_repr(db):
    """Test user string representation."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    
    expected = "<User(email='test@example.com', name='Test User')>"
    assert repr(user) == expected

def test_user_google_tokens(db):
    """Test user Google OAuth token storage."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123",
        google_access_token="access_token_123",
        google_refresh_token="refresh_token_123",
        google_token_expiry=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.google_access_token == "access_token_123"
    assert user.google_refresh_token == "refresh_token_123"
    assert user.google_token_expiry is not None

def test_user_relationships(db):
    """Test that user has proper relationships defined."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Test relationships exist (should be empty lists initially) 
    assert hasattr(user, 'classes')
    assert hasattr(user, 'schedules')
    assert hasattr(user, 'homework')
    assert user.classes == []
    assert user.schedules == []
    assert user.homework == []