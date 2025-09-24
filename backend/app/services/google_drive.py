from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict, Any
import logging

from ..models.user import User

logger = logging.getLogger(__name__)

class GoogleDriveService:
    def __init__(self, user: User):
        self.user = user
        self.service = None
    
    def _build_service(self):
        """Build Google Drive service with user credentials"""
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
        
        self.service = build('drive', 'v3', credentials=credentials)
        return self.service
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information from Google Drive"""
        try:
            if not self.service:
                self._build_service()
            
            # Get file metadata
            file_info = self.service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,webViewLink,permissions,owners'
            ).execute()
            
            logger.info(f"Retrieved file info for {file_id}: {file_info.get('name')}")
            return file_info
            
        except HttpError as error:
            if error.resp.status == 404:
                logger.error(f"File not found: {file_id}")
                return None
            logger.error(f"Failed to get file info for {file_id}: {error}")
            return None
        except Exception as error:
            logger.error(f"Unexpected error getting file info: {error}")
            return None
    
    def make_file_shareable(self, file_id: str) -> bool:
        """Make a Google Drive file publicly viewable"""
        try:
            if not self.service:
                self._build_service()
            
            # Check if file is already shared
            permissions = self.service.permissions().list(fileId=file_id).execute()
            
            # Check if there's already a public permission
            for permission in permissions.get('permissions', []):
                if permission.get('type') == 'anyone' and permission.get('role') == 'reader':
                    logger.info(f"File {file_id} is already publicly shared")
                    return True
            
            # Create a public read permission
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            logger.info(f"Made file {file_id} publicly shareable")
            return True
            
        except HttpError as error:
            logger.error(f"Failed to make file shareable {file_id}: {error}")
            return False
        except Exception as error:
            logger.error(f"Unexpected error making file shareable: {error}")
            return False
    
    def verify_file_access(self, file_id: str) -> bool:
        """Verify that the user has access to the file"""
        try:
            if not self.service:
                self._build_service()
            
            # Try to get basic file info - this will fail if user doesn't have access
            self.service.files().get(
                fileId=file_id,
                fields='id'
            ).execute()
            
            return True
            
        except HttpError as error:
            if error.resp.status in [403, 404]:
                logger.error(f"User does not have access to file {file_id}")
                return False
            logger.error(f"Failed to verify file access for {file_id}: {error}")
            return False
        except Exception as error:
            logger.error(f"Unexpected error verifying file access: {error}")
            return False
    
    def extract_file_id_from_url(self, drive_url: str) -> Optional[str]:
        """Extract Google Drive file ID from various URL formats"""
        import re
        
        # Pattern to match various Google Drive URL formats
        patterns = [
            r'/file/d/([a-zA-Z0-9-_]+)',  # https://drive.google.com/file/d/FILE_ID/view
            r'id=([a-zA-Z0-9-_]+)',       # https://drive.google.com/open?id=FILE_ID
            r'/document/d/([a-zA-Z0-9-_]+)',  # Google Docs
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',  # Google Sheets
            r'/presentation/d/([a-zA-Z0-9-_]+)',  # Google Slides
        ]
        
        for pattern in patterns:
            match = re.search(pattern, drive_url)
            if match:
                return match.group(1)
        
        # If it's already just a file ID (no URL structure)
        if re.match(r'^[a-zA-Z0-9-_]+$', drive_url):
            return drive_url
            
        return None