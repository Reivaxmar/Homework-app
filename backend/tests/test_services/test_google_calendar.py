"""
Tests for Google Calendar service.
"""
import pytest
import unittest.mock
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, time
from googleapiclient.errors import HttpError

from app.services.google_calendar import GoogleCalendarService
from app.models.user import User
from app.models.homework import Homework
from app.models.classes import Class

@pytest.fixture
def mock_user():
    """Create a mock user with Google tokens."""
    user = Mock(spec=User)
    user.id = 1
    user.google_access_token = "mock_access_token"
    user.google_refresh_token = "mock_refresh_token"
    user.email = "test@example.com"
    return user

@pytest.fixture
def mock_user_no_token():
    """Create a mock user without Google tokens."""
    user = Mock(spec=User)
    user.id = 1
    user.google_access_token = None
    user.google_refresh_token = None
    user.email = "test@example.com"
    return user

@pytest.fixture
def mock_homework():
    """Create a mock homework assignment."""
    homework = Mock(spec=Homework)
    homework.id = 1
    homework.title = "Math Assignment"
    homework.description = "Complete exercises 1-10"
    homework.due_date = date(2024, 3, 15)
    homework.due_time = time(23, 59)
    homework.google_calendar_event_id = None
    
    # Mock class relationship
    mock_class = Mock(spec=Class)
    mock_class.name = "Mathematics"
    homework.class_ = mock_class
    
    return homework

class TestGoogleCalendarService:
    
    def test_init(self, mock_user):
        """Test GoogleCalendarService initialization."""
        service = GoogleCalendarService(mock_user)
        assert service.user == mock_user
        assert service.service is None
    
    def test_build_service_success(self, mock_user):
        """Test successful service building."""
        with patch('app.services.google_calendar.build') as mock_build, \
             patch('app.services.google_calendar.Credentials') as mock_credentials:
            
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            service = GoogleCalendarService(mock_user)
            result = service._build_service()
            
            assert result == mock_service
            assert service.service == mock_service
            
            # Verify credentials were created correctly
            mock_credentials.assert_called_once_with(
                token=mock_user.google_access_token,
                refresh_token=mock_user.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=unittest.mock.ANY,
                client_secret=unittest.mock.ANY,
            )
            
            # Verify service was built
            mock_build.assert_called_once_with('calendar', 'v3', credentials=mock_credentials.return_value)
    
    def test_build_service_no_token(self, mock_user_no_token):
        """Test service building fails without access token."""
        service = GoogleCalendarService(mock_user_no_token)
        
        with pytest.raises(ValueError, match="User has no Google access token"):
            service._build_service()
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_create_homework_event_success(self, mock_credentials, mock_build, mock_user, mock_homework):
        """Test successful homework event creation."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        mock_insert = Mock()
        mock_events.insert.return_value = mock_insert
        mock_execute = Mock()
        mock_insert.execute.return_value = {"id": "mock_event_id"}
        mock_execute.return_value = {"id": "mock_event_id"}
        
        service = GoogleCalendarService(mock_user)
        
        # Test event creation
        event_id = service.create_homework_event(mock_homework)
        
        assert event_id == "mock_event_id"
        
        # Verify service was built
        mock_build.assert_called_once()
        
        # Verify event was created with correct data
        mock_events.insert.assert_called_once()
        call_args = mock_events.insert.call_args
        
        assert call_args[1]['calendarId'] == 'primary'
        event_data = call_args[1]['body']
        
        assert event_data['summary'] == 'Homework: Math Assignment'
        assert 'Class: Mathematics' in event_data['description']
        assert 'Complete exercises 1-10' in event_data['description']
        assert 'start' in event_data
        assert 'end' in event_data
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_create_homework_event_http_error(self, mock_credentials, mock_build, mock_user, mock_homework):
        """Test homework event creation with HTTP error."""
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        mock_insert = Mock()
        mock_events.insert.return_value = mock_insert
        
        # Mock HTTP error
        http_error = HttpError(Mock(status=400), b'Bad Request')
        mock_insert.execute.side_effect = http_error
        
        service = GoogleCalendarService(mock_user)
        
        # Test event creation fails gracefully
        event_id = service.create_homework_event(mock_homework)
        
        assert event_id is None
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_update_homework_event(self, mock_credentials, mock_build, mock_user, mock_homework):
        """Test updating an existing homework event."""
        # Setup homework with existing event ID
        mock_homework.google_calendar_event_id = "existing_event_id"
        
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        
        # Mock the get call for existing event
        mock_get = Mock()
        mock_events.get.return_value = mock_get
        mock_get.execute.return_value = {
            "id": "existing_event_id",
            "summary": "Old title",
            "description": "Old description",
            "start": {"dateTime": "2024-03-15T13:00:00"},
            "end": {"dateTime": "2024-03-15T14:00:00"}
        }
        
        # Mock the update call
        mock_update = Mock()
        mock_events.update.return_value = mock_update
        mock_update.execute.return_value = {"id": "existing_event_id"}
        
        service = GoogleCalendarService(mock_user)
        
        # Test event update
        result = service.update_homework_event(mock_homework)
        
        assert result is True
        
        # Verify update was called with correct parameters
        mock_events.update.assert_called_once()
        call_args = mock_events.update.call_args
        
        assert call_args[1]['calendarId'] == 'primary'
        assert call_args[1]['eventId'] == 'existing_event_id'
        assert 'body' in call_args[1]
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_delete_homework_event(self, mock_credentials, mock_build, mock_user):
        """Test deleting a homework event."""
        event_id_to_delete = "event_to_delete"
        
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        mock_delete = Mock()
        mock_events.delete.return_value = mock_delete
        mock_delete.execute.return_value = None
        
        service = GoogleCalendarService(mock_user)
        
        # Test event deletion
        result = service.delete_homework_event(event_id_to_delete)
        
        assert result is True
        
        # Verify delete was called with correct parameters
        mock_events.delete.assert_called_once_with(
            calendarId='primary',
            eventId='event_to_delete'
        )
    
    def test_delete_homework_event_no_event_id(self, mock_user):
        """Test deleting homework event when no event ID exists."""
        service = GoogleCalendarService(mock_user)
        
        # Should handle empty event ID gracefully
        result = service.delete_homework_event(None)
        
        assert result is False
    
    @patch('app.services.google_calendar.build')
    @patch('app.services.google_calendar.Credentials')
    def test_delete_homework_event_http_error(self, mock_credentials, mock_build, mock_user):
        """Test deleting homework event with HTTP error."""
        event_id_to_delete = "event_to_delete"
        
        # Setup mocks
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        mock_events = Mock()
        mock_service.events.return_value = mock_events
        mock_delete = Mock()
        mock_events.delete.return_value = mock_delete
        
        # Mock HTTP error
        http_error = HttpError(Mock(status=404), b'Not Found')
        mock_delete.execute.side_effect = http_error
        
        service = GoogleCalendarService(mock_user)
        
        # Should handle error gracefully (404 is treated as success)
        result = service.delete_homework_event(event_id_to_delete)
        
        assert result is True  # 404 errors are treated as success
    
    def test_event_datetime_calculation(self, mock_user, mock_homework):
        """Test that event datetime calculations are correct."""
        # Set specific due date and time
        mock_homework.due_date = date(2024, 3, 15)
        mock_homework.due_time = time(14, 30)  # 2:30 PM
        
        with patch('app.services.google_calendar.build') as mock_build, \
             patch('app.services.google_calendar.Credentials'):
            
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_events = Mock()
            mock_service.events.return_value = mock_events
            mock_insert = Mock()
            mock_events.insert.return_value = mock_insert
            mock_insert.execute.return_value = {"id": "test_event_id"}
            
            service = GoogleCalendarService(mock_user)
            service.create_homework_event(mock_homework)
            
            # Get the event data that was sent
            call_args = mock_events.insert.call_args
            event_data = call_args[1]['body']
            
            # Verify the start time is 1 hour before due time
            start_time = event_data['start']['dateTime']
            end_time = event_data['end']['dateTime']
            
            # Should be set to 1:30 PM (1 hour before 2:30 PM due time)
            assert '13:30:00' in start_time  # 1:30 PM
            assert '14:30:00' in end_time    # 2:30 PM (due time)
    
    def test_event_description_formatting(self, mock_user, mock_homework):
        """Test that event description is formatted correctly."""
        mock_homework.description = "Complete exercises 1-20 and review chapter 5"
        
        with patch('app.services.google_calendar.build') as mock_build, \
             patch('app.services.google_calendar.Credentials'):
            
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_events = Mock()
            mock_service.events.return_value = mock_events
            mock_insert = Mock()
            mock_events.insert.return_value = mock_insert
            mock_insert.execute.return_value = {"id": "test_event_id"}
            
            service = GoogleCalendarService(mock_user)
            service.create_homework_event(mock_homework)
            
            # Get the event data that was sent
            call_args = mock_events.insert.call_args
            event_data = call_args[1]['body']
            
            description = event_data['description']
            
            # Verify description contains class name and homework description
            assert 'Class: Mathematics' in description
            assert 'Complete exercises 1-20 and review chapter 5' in description
    
    def test_homework_without_class(self, mock_user):
        """Test creating event for homework without associated class."""
        # Create homework without class
        homework = Mock(spec=Homework)
        homework.id = 1
        homework.title = "Independent Study"
        homework.description = "Self-directed learning"
        homework.due_date = date(2024, 3, 15)
        homework.due_time = time(23, 59)
        homework.google_calendar_event_id = None
        homework.class_ = None  # No associated class
        
        with patch('app.services.google_calendar.build') as mock_build, \
             patch('app.services.google_calendar.Credentials'):
            
            mock_service = Mock()
            mock_build.return_value = mock_service
            
            mock_events = Mock()
            mock_service.events.return_value = mock_events
            mock_insert = Mock()
            mock_events.insert.return_value = mock_insert
            mock_insert.execute.return_value = {"id": "test_event_id"}
            
            service = GoogleCalendarService(mock_user)
            service.create_homework_event(homework)
            
            # Get the event data that was sent
            call_args = mock_events.insert.call_args
            event_data = call_args[1]['body']
            
            description = event_data['description']
            
            # Should handle missing class gracefully
            assert 'Class: Unknown' in description or 'Class: None' in description
            assert 'Self-directed learning' in description