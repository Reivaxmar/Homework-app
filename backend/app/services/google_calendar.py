from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import Optional
import logging

from ..models.user import User
from ..models.homework import Homework

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self, user: User):
        self.user = user
        self.service = None
        
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
            
            # Combine due date and time for event start
            due_datetime = datetime.combine(homework.due_date, homework.due_time)
            
            # Create event that lasts 1 hour before due time
            start_time = due_datetime - timedelta(hours=1)
            
            event = {
                'summary': f'Homework: {homework.title}',
                'description': f'Class: {homework.class_.name if homework.class_ else "Unknown"}\n'
                              f'Description: {homework.description or "No description"}\n'
                              f'Priority: {homework.priority.value}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': due_datetime.isoformat(),
                    'timeZone': 'UTC',
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
            logger.info(f"Created calendar event {result.get('id')} for homework {homework.id}")
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
            
            # Update event details
            due_datetime = datetime.combine(homework.due_date, homework.due_time)
            start_time = due_datetime - timedelta(hours=1)
            
            event['summary'] = f'Homework: {homework.title}'
            event['description'] = f'Class: {homework.class_.name if homework.class_ else "Unknown"}\n' \
                                  f'Description: {homework.description or "No description"}\n' \
                                  f'Priority: {homework.priority.value}'
            event['start']['dateTime'] = start_time.isoformat()
            event['end']['dateTime'] = due_datetime.isoformat()
            
            self.service.events().update(
                calendarId='primary',
                eventId=homework.google_calendar_event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated calendar event {homework.google_calendar_event_id} for homework {homework.id}")
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
            if not event_id:
                return False
                
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