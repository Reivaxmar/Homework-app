"""
Tests for authentication router.
"""
import pytest
from unittest.mock import patch, MagicMock

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Homework Management API"
    assert data["version"] == "1.0.0"

def test_google_auth_callback_new_user(client, db):
    """Test Google OAuth callback with new user."""
    response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "test-user-123"},
        json={"access_token": None}  # Minimal data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["message"] == "Authentication successful"
    
    # Check user was created
    user_data = data["user"]
    assert user_data["supabase_user_id"] == "test-user-123"
    assert "@example.com" in user_data["email"]  # Default email format

@patch('requests.get')
def test_google_auth_callback_with_google_data(mock_get, client, db):
    """Test Google OAuth callback with Google user data."""
    # Mock Google API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "email": "test@gmail.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg"
    }
    mock_get.return_value = mock_response
    
    response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "google-user-123"},
        json={
            "access_token": "google_access_token_123",
            "refresh_token": "google_refresh_token_123",
            "expires_in": 3600
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify user data from Google
    user_data = data["user"]
    assert user_data["email"] == "test@gmail.com"
    assert user_data["full_name"] == "Test User"
    assert user_data["avatar_url"] == "https://example.com/photo.jpg"
    assert user_data["supabase_user_id"] == "google-user-123"

def test_google_auth_callback_existing_user(client, db, test_user_data):
    """Test Google OAuth callback with existing user."""
    # First, create a user
    first_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": test_user_data["supabase_user_id"]},
        json={}
    )
    assert first_response.status_code == 200
    
    # Now authenticate again with same user
    second_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": test_user_data["supabase_user_id"]},
        json={}
    )
    
    assert second_response.status_code == 200
    data = second_response.json()
    assert data["user"]["supabase_user_id"] == test_user_data["supabase_user_id"]

def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication."""
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]  # Should require authentication

def test_get_current_user_authorized(authenticated_user):
    """Test getting current user with authentication."""
    client, token_data = authenticated_user
    
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    
    user_data = response.json()
    assert "id" in user_data
    assert "email" in user_data
    assert "full_name" in user_data
    assert "supabase_user_id" in user_data

def test_update_current_user_unauthorized(client):
    """Test updating current user without authentication."""
    response = client.put("/api/auth/me", json={"full_name": "New Name"})
    assert response.status_code in [401, 403]

def test_update_current_user_authorized(authenticated_user):
    """Test updating current user with authentication."""
    client, token_data = authenticated_user
    
    response = client.put("/api/auth/me", json={"full_name": "Updated Name"})
    assert response.status_code == 200
    
    user_data = response.json()
    assert user_data["full_name"] == "Updated Name"

def test_login_endpoint_new_user(client, db):
    """Test simple login endpoint with new user."""
    login_data = {
        "email": "newuser@example.com",
        "full_name": "New User"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["message"] == "Login successful"
    
    user_data = data["user"]
    assert user_data["email"] == "newuser@example.com"
    assert user_data["full_name"] == "New User"

def test_login_endpoint_existing_user(client, db):
    """Test simple login endpoint with existing user."""
    # Create user first
    first_login = {
        "email": "existing@example.com",
        "full_name": "Original Name"
    }
    
    first_response = client.post("/api/auth/login", json=first_login)
    assert first_response.status_code == 200
    
    # Login again with updated info
    second_login = {
        "email": "existing@example.com",
        "full_name": "Updated Name"
    }
    
    second_response = client.post("/api/auth/login", json=second_login)
    assert second_response.status_code == 200
    
    data = second_response.json()
    user_data = data["user"]
    assert user_data["email"] == "existing@example.com"
    assert user_data["full_name"] == "Updated Name"  # Should be updated

@patch('requests.get')
def test_google_auth_callback_api_error(mock_get, client, db):
    """Test Google OAuth callback when Google API fails."""
    # Mock Google API error
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_get.return_value = mock_response
    
    # Should still work with fallback data
    response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "test-user-456"},
        json={"access_token": "invalid_token"}
    )
    
    assert response.status_code == 200  # Should handle gracefully
    data = response.json()
    assert "user" in data
    assert data["user"]["supabase_user_id"] == "test-user-456"

def test_auth_token_validation(authenticated_user):
    """Test that JWT token works for protected endpoints."""
    client, token_data = authenticated_user
    
    # Token should work for multiple requests
    for _ in range(3):
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        
        user_data = response.json()
        assert "id" in user_data

def test_invalid_token_format(client):
    """Test authentication with invalid token format."""
    # Set invalid authorization header
    client.headers.update({"Authorization": "Bearer invalid_token_format"})
    
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]

def test_missing_authorization_header(client):
    """Test authentication without authorization header."""
    # Clear any existing headers
    if "Authorization" in client.headers:
        del client.headers["Authorization"]
    
    response = client.get("/api/auth/me")
    assert response.status_code in [401, 403]