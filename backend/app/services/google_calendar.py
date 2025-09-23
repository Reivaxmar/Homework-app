from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import Optional
import logging
import pytz

from ..models.user import User
from ..models.homework import Homework

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self, user: User):
        self.user = user
        self.service = None
        
    def _get_user_timezone(self):
        """Get user's timezone, defaulting to UTC"""
        try:
            tz = pytz.timezone(self.user.get_timezone())
            return tz
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone {self.user.get_timezone()}, falling back to UTC")
            return pytz.UTC
    
    def _localize_datetime(self, dt):
        """Convert naive datetime to user's timezone"""
        user_tz = self._get_user_timezone()
        if dt.tzinfo is None:
            # Assume naive datetime is in user's timezone
            return user_tz.localize(dt)
        return dt.astimezone(user_tz)
        
    def _build_service(self):
        """Build Google Calendar service with user credentials"""
        if not self.user.google_access_token:
            raise ValueError("User has no Google access token")
            
        from ..config import settings
            
        credentials = Credentials(
            token=self.user.google_access_token,
            refresh_token=self.user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
        )
        
        self.service = build('calendar', 'v3', credentials=credentials)
        return self.service
    
    def create_homework_event(self, homework: Homework) -> Optional[str]:
        """Create a Google Calendar event for homework"""
        try:
            if not self.service:
                self._build_service()
            
            # Combine due date and time, treating as user's local time
            due_datetime = datetime.combine(homework.due_date, homework.due_time)
            
            # Localize to user's timezone
            due_datetime_localized = self._localize_datetime(due_datetime)
            
            # Create event that lasts 1 hour before due time
            start_time = due_datetime_localized - timedelta(hours=1)
            
            # Get timezone string for the user
            user_timezone = self.user.get_timezone()
            
            event = {
                'summary': f'Homework: {homework.title}',
                'description': f'Class: {homework.class_.name if homework.class_ else "Unknown"}\n'
                              f'Description: {homework.description or "No description"}\n'
                              f'Priority: {homework.priority.value}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': user_timezone,
                },
                'end': {
                    'dateTime': due_datetime_localized.isoformat(),
                    'timeZone': user_timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                        {'method': 'popup', 'minutes': 60},        # 1 hour before
                    ],
                },
            }
            
            result = self.service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Created calendar event {result.get('id')} for homework {homework.id} in timezone {user_timezone}")
            return result.get('id')
            
        except HttpError as error:
            logger.error(f"Failed to create calendar event for homework {homework.id}: {error}")
            return None
        except Exception as error:
            logger.error(f"Unexpected error creating calendar event: {error}")
            return None
    
    def update_homework_event(self, homework: Homework) -> bool:
        """Update existing Google Calendar event for homework"""
        try:
            if not homework.google_calendar_event_id:
                return False
                
            if not self.service:
                self._build_service()
            
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=homework.google_calendar_event_id
            ).execute()
            
            # Update event details with proper timezone handling
            due_datetime = datetime.combine(homework.due_date, homework.due_time)
            due_datetime_localized = self._localize_datetime(due_datetime)
            start_time = due_datetime_localized - timedelta(hours=1)
            
            user_timezone = self.user.get_timezone()
            
            event['summary'] = f'Homework: {homework.title}'
            event['description'] = f'Class: {homework.class_.name if homework.class_ else "Unknown"}\n' \
                                  f'Description: {homework.description or "No description"}\n' \
                                  f'Priority: {homework.priority.value}'
            event['start']['dateTime'] = start_time.isoformat()
            event['start']['timeZone'] = user_timezone
            event['end']['dateTime'] = due_datetime_localized.isoformat()
            event['end']['timeZone'] = user_timezone
            
            self.service.events().update(
                calendarId='primary',
                eventId=homework.google_calendar_event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated calendar event {homework.google_calendar_event_id} for homework {homework.id} in timezone {user_timezone}")
            return True
            
        except HttpError as error:
            logger.error(f"Failed to update calendar event for homework {homework.id}: {error}")
            return False
        except Exception as error:
            logger.error(f"Unexpected error updating calendar event: {error}")
            return False
    
    def delete_homework_event(self, event_id: str) -> bool:
        """Delete Google Calendar event"""
        try:
            if not self.service:
                self._build_service()
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted calendar event {event_id}")
            return True
            
        except HttpError as error:
            if error.resp.status == 404:
                logger.warning(f"Calendar event {event_id} not found (already deleted?)")
                return True
            logger.error(f"Failed to delete calendar event {event_id}: {error}")
            return False
        except Exception as error:
            logger.error(f"Unexpected error deleting calendar event: {error}")
            return False