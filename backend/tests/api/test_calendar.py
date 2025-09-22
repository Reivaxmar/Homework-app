"""
API tests for calendar integration endpoints.
Note: These tests mock Google Calendar API to avoid external dependencies.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi import status


class TestCalendarAPI:
    """Test calendar integration API endpoints."""
    
    @patch('app.auth.get_current_user')
    @patch('app.services.google_calendar.GoogleCalendarService')
    def test_sync_google_calendar_success(self, mock_calendar_service, mock_get_current_user, 
                                        client, authenticated_user, test_homework, test_session):
        """Test successful Google Calendar sync."""
        mock_get_current_user.return_value = authenticated_user
        
        # Mock calendar service
        mock_service_instance = Mock()
        mock_service_instance.create_homework_event.return_value = "calendar_event_123"
        mock_calendar_service.return_value = mock_service_instance
        
        response = client.post(
            "/api/calendar/sync",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "synced_count" in data
        assert data["synced_count"] >= 0
        assert "message" in data
    
    @patch('app.auth.get_current_user')
    def test_sync_calendar_no_google_token(self, mock_get_current_user, client, test_user):
        """Test calendar sync without Google access token."""
        # User without Google tokens
        mock_get_current_user.return_value = test_user
        
        response = client.post(
            "/api/calendar/sync",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Google Calendar access" in data["detail"]
    
    @patch('app.auth.get_current_user')
    @patch('app.services.google_calendar.GoogleCalendarService')
    def test_sync_calendar_service_error(self, mock_calendar_service, mock_get_current_user,
                                       client, authenticated_user, test_homework, test_session):
        """Test calendar sync when Google Calendar service fails."""
        mock_get_current_user.return_value = authenticated_user
        
        # Mock calendar service to raise exception
        mock_calendar_service.side_effect = Exception("Google Calendar API error")
        
        response = client.post(
            "/api/calendar/sync",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @patch('app.auth.get_current_user')
    @patch('app.services.google_calendar.GoogleCalendarService')
    def test_sync_specific_homework_success(self, mock_calendar_service, mock_get_current_user,
                                          client, authenticated_user, test_homework, test_session):
        """Test syncing a specific homework to calendar."""
        mock_get_current_user.return_value = authenticated_user
        
        # Mock calendar service
        mock_service_instance = Mock()
        mock_service_instance.create_homework_event.return_value = "calendar_event_456"
        mock_calendar_service.return_value = mock_service_instance
        
        response = client.post(
            f"/api/calendar/sync/{test_homework.id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        assert "message" in data
        assert "homework_id" in data
        assert data["homework_id"] == test_homework.id
    
    @patch('app.auth.get_current_user')
    @patch('app.services.google_calendar.GoogleCalendarService')
    def test_sync_homework_update_existing(self, mock_calendar_service, mock_get_current_user,
                                         client, authenticated_user, test_homework, test_session):
        """Test updating existing calendar event for homework."""
        mock_get_current_user.return_value = authenticated_user
        
        # Set homework to have existing calendar event
        test_homework.google_calendar_event_id = "existing_event_123"
        test_session.commit()
        
        # Mock calendar service
        mock_service_instance = Mock()
        mock_service_instance.update_homework_event.return_value = True
        mock_calendar_service.return_value = mock_service_instance
        
        response = client.post(
            f"/api/calendar/sync/{test_homework.id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "updated" in data["message"]
    
    @patch('app.auth.get_current_user')
    def test_sync_homework_not_found(self, mock_get_current_user, client, authenticated_user):
        """Test syncing non-existent homework."""
        mock_get_current_user.return_value = authenticated_user
        
        response = client.post(
            "/api/calendar/sync/999",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "not found" in data["detail"]
    
    @patch('app.auth.get_current_user')
    def test_sync_homework_different_user(self, mock_get_current_user, client, 
                                        test_homework, user_factory, test_session):
        """Test syncing homework that belongs to different user."""
        # Create different user with Google tokens
        different_user = user_factory.create(
            email="different@example.com",
            google_access_token="different_token"
        )
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        response = client.post(
            f"/api/calendar/sync/{test_homework.id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_sync_homework_no_google_token(self, mock_get_current_user, client, 
                                         test_user, test_homework, test_session):
        """Test syncing homework without Google access token."""
        mock_get_current_user.return_value = test_user
        
        response = client.post(
            f"/api/calendar/sync/{test_homework.id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Google Calendar access" in data["detail"]
    
    @patch('app.auth.get_current_user')
    @patch('app.services.google_calendar.GoogleCalendarService')
    def test_sync_homework_calendar_service_error(self, mock_calendar_service, mock_get_current_user,
                                                 client, authenticated_user, test_homework, test_session):
        """Test syncing homework when calendar service fails."""
        mock_get_current_user.return_value = authenticated_user
        
        # Mock calendar service to fail
        mock_service_instance = Mock()
        mock_service_instance.create_homework_event.return_value = None  # Failed to create
        mock_calendar_service.return_value = mock_service_instance
        
        response = client.post(
            f"/api/calendar/sync/{test_homework.id}",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Failed to sync" in data["detail"]
    
    def test_unauthenticated_calendar_requests(self, client):
        """Test that calendar endpoints require authentication."""
        endpoints = [
            ("POST", "/api/calendar/sync"),
            ("POST", "/api/calendar/sync/1"),
        ]
        
        for method, endpoint in endpoints:
            response = client.post(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGoogleCalendarServiceMocking:
    """Test that Google Calendar service is properly mocked and doesn't make real API calls."""
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_calendar_service_initialization(self, mock_credentials, mock_build, authenticated_user):
        """Test that GoogleCalendarService initializes without real Google API calls."""
        from app.services.google_calendar import GoogleCalendarService
        
        service = GoogleCalendarService(authenticated_user)
        service._build_service()
        
        # Verify mocks were called
        mock_credentials.assert_called_once()
        mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_credentials.return_value)
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_calendar_service_no_tokens(self, mock_credentials, mock_build, test_user):
        """Test GoogleCalendarService with user without Google tokens."""
        from app.services.google_calendar import GoogleCalendarService
        
        service = GoogleCalendarService(test_user)
        
        with pytest.raises(ValueError, match="User has no Google access token"):
            service._build_service()
    
    @patch('app.services.google_calendar.GoogleCalendarService.create_homework_event')
    def test_mock_create_homework_event(self, mock_create_event, authenticated_user, test_homework):
        """Test that homework event creation is properly mocked."""
        from app.services.google_calendar import GoogleCalendarService
        
        mock_create_event.return_value = "mock_event_id"
        
        service = GoogleCalendarService(authenticated_user)
        event_id = service.create_homework_event(test_homework)
        
        assert event_id == "mock_event_id"
        mock_create_event.assert_called_once_with(test_homework)
    
    @patch('app.services.google_calendar.GoogleCalendarService.update_homework_event')
    def test_mock_update_homework_event(self, mock_update_event, authenticated_user, test_homework):
        """Test that homework event update is properly mocked."""
        from app.services.google_calendar import GoogleCalendarService
        
        mock_update_event.return_value = True
        
        service = GoogleCalendarService(authenticated_user)
        result = service.update_homework_event(test_homework)
        
        assert result is True
        mock_update_event.assert_called_once_with(test_homework)
    
    @patch('app.services.google_calendar.GoogleCalendarService.delete_homework_event')
    def test_mock_delete_homework_event(self, mock_delete_event, authenticated_user):
        """Test that homework event deletion is properly mocked.""" 
        from app.services.google_calendar import GoogleCalendarService
        
        mock_delete_event.return_value = True
        
        service = GoogleCalendarService(authenticated_user)
        result = service.delete_homework_event("event_id_123")
        
        assert result is True
        mock_delete_event.assert_called_once_with("event_id_123")