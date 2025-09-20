from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from ..models.database import get_db
from ..models.homework import Homework
from ..auth import get_current_user
from ..services.google_calendar import GoogleCalendarService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.post("/sync")
async def sync_google_calendar(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync existing homework with Google Calendar"""
    try:
        if not current_user.google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Google Calendar access. Please sign in with Google."
            )
        
        # Get user's homework
        homework_list = db.query(Homework).filter(
            Homework.user_id == current_user.id,
            Homework.status != "completed"
        ).all()
        
        # Initialize Google Calendar service
        calendar_service = GoogleCalendarService(current_user)
        
        synced_count = 0
        for homework in homework_list:
            if not homework.google_calendar_event_id:
                # Create calendar event for homework without one
                event_id = calendar_service.create_homework_event(homework)
                if event_id:
                    homework.google_calendar_event_id = event_id
                    synced_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully synced {synced_count} homework assignments with Google Calendar",
            "synced_count": synced_count,
            "total_homework": len(homework_list)
        }
        
    except Exception as e:
        logger.error(f"Calendar sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync with Google Calendar"
        )

@router.post("/sync/{homework_id}")
async def sync_homework_to_calendar(
    homework_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync a specific homework assignment to Google Calendar"""
    try:
        if not current_user.google_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Google Calendar access. Please sign in with Google."
            )
        
        # Get the specific homework
        homework = db.query(Homework).filter(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        ).first()
        
        if not homework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Homework assignment not found"
            )
        
        # Initialize Google Calendar service
        calendar_service = GoogleCalendarService(current_user)
        
        if homework.google_calendar_event_id:
            # Update existing event
            success = calendar_service.update_homework_event(homework)
            action = "updated"
        else:
            # Create new event
            event_id = calendar_service.create_homework_event(homework)
            if event_id:
                homework.google_calendar_event_id = event_id
                success = True
                action = "created"
            else:
                success = False
        
        if success:
            db.commit()
            return {
                "message": f"Successfully {action} calendar event for homework: {homework.title}",
                "homework_id": homework_id,
                "event_id": homework.google_calendar_event_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync homework with Google Calendar"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Homework calendar sync error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync homework with Google Calendar"
        )