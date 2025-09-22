"""
API tests for authentication endpoints.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi import status


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
    
    @patch('app.auth.supabase')
    def test_google_callback_success(self, mock_supabase, client, test_session):
        """Test successful Google OAuth callback."""
        # Mock Supabase response
        mock_user = Mock()
        mock_user.user.id = "supabase-user-123"
        mock_user.user.email = "test@example.com"
        mock_user.user.user_metadata = {
            "full_name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg"
        }
        mock_supabase.auth.get_user.return_value = mock_user
        
        # Mock session data
        mock_session = Mock()
        mock_session.access_token = "mock_access_token"
        mock_session.refresh_token = "mock_refresh_token"
        mock_session.provider_token = "google_access_token"
        mock_session.provider_refresh_token = "google_refresh_token"
        mock_supabase.auth.get_session.return_value = mock_session
        
        response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "supabase-user-123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
    
    @patch('app.auth.supabase')
    def test_google_callback_invalid_user(self, mock_supabase, client):
        """Test Google OAuth callback with invalid user."""
        mock_supabase.auth.get_user.side_effect = Exception("User not found")
        
        response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "invalid-user"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.auth.get_current_user')
    def test_get_current_user_success(self, mock_get_current_user, client, mock_user):
        """Test getting current user with valid token."""
        mock_get_current_user.return_value = mock_user
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == mock_user.email
        assert data["full_name"] == mock_user.full_name
    
    @patch('app.auth.get_current_user')
    def test_update_current_user(self, mock_get_current_user, client, test_user, test_session):
        """Test updating current user profile."""
        mock_get_current_user.return_value = test_user
        
        update_data = {
            "full_name": "Updated Name",
            "avatar_url": "https://example.com/new_avatar.jpg"
        }
        
        response = client.put(
            "/api/auth/me",
            json=update_data,
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["avatar_url"] == "https://example.com/new_avatar.jpg"
    
    @patch('app.auth.get_current_user')
    def test_update_user_invalid_data(self, mock_get_current_user, client, test_user):
        """Test updating user with invalid data."""
        mock_get_current_user.return_value = test_user
        
        # Try to update with invalid email format
        update_data = {
            "email": "invalid-email-format"
        }
        
        response = client.put(
            "/api/auth/me",
            json=update_data,
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_legacy_login_endpoint(self, client):
        """Test legacy login endpoint (should redirect to Google OAuth)."""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "full_name": "Test User"}
        )
        
        # This endpoint should return a response directing to use Google OAuth
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_302_FOUND]


class TestJWTAuthentication:
    """Test JWT token authentication functionality."""
    
    @patch('app.auth.jwt.decode')
    @patch('app.auth.supabase')
    def test_valid_jwt_token(self, mock_supabase, mock_jwt_decode, client, test_user, test_session):
        """Test authentication with valid JWT token."""
        # Mock JWT decode
        mock_jwt_decode.return_value = {"sub": test_user.supabase_user_id}
        
        # Mock Supabase user verification
        mock_user = Mock()
        mock_user.user.id = test_user.supabase_user_id
        mock_supabase.auth.get_user.return_value = mock_user
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer valid_jwt_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    @patch('app.auth.jwt.decode')
    def test_invalid_jwt_token(self, mock_jwt_decode, client):
        """Test authentication with invalid JWT token."""
        mock_jwt_decode.side_effect = Exception("Invalid token")
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_missing_authorization_header(self, client):
        """Test request without authorization header."""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_malformed_authorization_header(self, client):
        """Test request with malformed authorization header."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_bearer_token_without_token(self, client):
        """Test request with Bearer but no token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED