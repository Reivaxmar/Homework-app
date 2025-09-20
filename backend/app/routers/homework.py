from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
import logging

from ..models.database import get_db
from ..models.homework import Homework, Status
from ..models.classes import Class
from ..models.user import User
from ..auth import get_current_user
from ..services.google_calendar import GoogleCalendarService
from .. import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/homework", tags=["homework"])

@router.get("/", response_model=List[schemas.Homework])
def get_homework(
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[int] = Query(None),
    status: Optional[schemas.Status] = Query(None),
    due_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get homework with optional filters (user-specific)"""
    query = db.query(Homework).filter(Homework.user_id == current_user.id)
    
    if class_id:
        query = query.filter(Homework.class_id == class_id)
    if status:
        query = query.filter(Homework.status == status)
    if due_date:
        query = query.filter(Homework.due_date == due_date)
    
    homework = query.offset(skip).limit(limit).all()
    return homework

@router.get("/due-today", response_model=List[schemas.Homework])
def get_homework_due_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get homework due today (considering both date and time) - user-specific"""
    from datetime import datetime, time
    today = date.today()
    now = datetime.now()
    current_time = now.time()
    
    # Get homework due today that is either:
    # 1. Due today with time later than current time
    # 2. Due today and it's already past the due time (still show as due today)
    homework = db.query(Homework).filter(
        and_(
            Homework.user_id == current_user.id,
            Homework.due_date == today,
            Homework.status != Status.COMPLETED
        )
    ).all()
    return homework

@router.get("/overdue", response_model=List[schemas.Homework])
def get_overdue_homework(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overdue homework - user-specific"""
    from datetime import datetime, time
    now = datetime.now()
    today = now.date()
    current_time = now.time()
    
    homework = db.query(Homework).filter(
        and_(
            Homework.user_id == current_user.id,
            or_(
                # Tasks due before today are overdue
                Homework.due_date < today,
                # Tasks due today but past their due time are overdue
                and_(
                    Homework.due_date == today,
                    Homework.due_time < current_time
                )
            ),
            Homework.status != Status.COMPLETED
        )
    ).all()
    return homework

@router.get("/upcoming", response_model=List[schemas.Homework])
def get_upcoming_homework(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get homework due in the next N days - user-specific"""
    from datetime import timedelta
    today = date.today()
    future_date = today + timedelta(days=days)
    
    homework = db.query(Homework).filter(
        and_(
            Homework.user_id == current_user.id,
            Homework.due_date >= today,
            Homework.due_date <= future_date,
            Homework.status != Status.COMPLETED
        )
    ).all()
    return homework

@router.get("/{homework_id}", response_model=schemas.Homework)
def get_homework_item(
    homework_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific homework item - user-specific"""
    homework = db.query(Homework).filter(
        and_(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        )
    ).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    return homework

@router.post("/", response_model=schemas.Homework, status_code=status.HTTP_201_CREATED)
def create_homework(
    homework_data: schemas.HomeworkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new homework item with Google Calendar integration"""
    # Verify class exists and belongs to user
    class_ = db.query(Class).filter(
        and_(
            Class.id == homework_data.class_id,
            Class.user_id == current_user.id
        )
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    # Create homework
    homework_dict = homework_data.dict()
    homework_dict["user_id"] = current_user.id
    db_homework = Homework(**homework_dict)
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)
    
    # Create Google Calendar event if user has tokens
    if current_user.google_access_token:
        try:
            calendar_service = GoogleCalendarService(current_user)
            event_id = calendar_service.create_homework_event(db_homework)
            if event_id:
                db_homework.google_calendar_event_id = event_id
                db.commit()
                db.refresh(db_homework)
        except Exception as e:
            logger.error(f"Failed to create calendar event for homework {db_homework.id}: {e}")
    
    return db_homework

@router.put("/{homework_id}", response_model=schemas.Homework)
def update_homework(
    homework_id: int,
    homework_data: schemas.HomeworkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a homework item with Google Calendar sync"""
    db_homework = db.query(Homework).filter(
        and_(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        )
    ).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    update_data = homework_data.dict(exclude_unset=True)
    
    # Handle status completion
    if "status" in update_data and update_data["status"] == Status.COMPLETED:
        update_data["completed_at"] = datetime.utcnow()
    elif "status" in update_data and update_data["status"] != Status.COMPLETED:
        update_data["completed_at"] = None
    
    for field, value in update_data.items():
        setattr(db_homework, field, value)
    
    db.commit()
    db.refresh(db_homework)
    
    # Update Google Calendar event if it exists and user has tokens
    if (current_user.google_access_token and 
        db_homework.google_calendar_event_id and
        any(field in update_data for field in ["title", "description", "due_date", "due_time", "priority"])):
        try:
            calendar_service = GoogleCalendarService(current_user)
            calendar_service.update_homework_event(db_homework)
        except Exception as e:
            logger.error(f"Failed to update calendar event for homework {db_homework.id}: {e}")
    
    return db_homework

@router.put("/{homework_id}/complete", response_model=schemas.Homework)
def complete_homework(
    homework_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark homework as completed - user-specific"""
    db_homework = db.query(Homework).filter(
        and_(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        )
    ).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    db_homework.status = Status.COMPLETED
    db_homework.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_homework)
    return db_homework

@router.put("/{homework_id}/reopen", response_model=schemas.Homework)
def reopen_homework(
    homework_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reopen completed homework - user-specific"""
    db_homework = db.query(Homework).filter(
        and_(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        )
    ).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    db_homework.status = Status.PENDING
    db_homework.completed_at = None
    
    db.commit()
    db.refresh(db_homework)
    return db_homework

@router.delete("/{homework_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_homework(
    homework_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a homework item - user-specific"""
    db_homework = db.query(Homework).filter(
        and_(
            Homework.id == homework_id,
            Homework.user_id == current_user.id
        )
    ).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    # Delete Google Calendar event if it exists
    if (current_user.google_access_token and 
        db_homework.google_calendar_event_id):
        try:
            calendar_service = GoogleCalendarService(current_user)
            calendar_service.delete_homework_event(db_homework.google_calendar_event_id)
        except Exception as e:
            logger.error(f"Failed to delete calendar event for homework {db_homework.id}: {e}")
    
    db.delete(db_homework)
    db.commit()
    return None