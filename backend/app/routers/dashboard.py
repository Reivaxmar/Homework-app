from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, date, timedelta

from ..models.database import get_db
from ..models.homework import Homework, Status
from ..models.classes import Class
from ..models.schedule import Schedule, ScheduleSlot
from .. import schemas

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Total classes
    total_classes = db.query(Class).count()
    
    # Pending homework
    pending_homework = db.query(Homework).filter(
        Homework.status != Status.COMPLETED
    ).count()
    
    # Due today
    due_today = db.query(Homework).filter(
        and_(
            Homework.due_date == today,
            Homework.status != Status.COMPLETED
        )
    ).count()
    
    # Overdue
    overdue = db.query(Homework).filter(
        and_(
            Homework.due_date < today,
            Homework.status != Status.COMPLETED
        )
    ).count()
    
    # Completed this week
    completed_this_week = db.query(Homework).filter(
        and_(
            Homework.status == Status.COMPLETED,
            Homework.completed_at >= week_start,
            Homework.completed_at <= week_end
        )
    ).count()
    
    return schemas.DashboardSummary(
        total_classes=total_classes,
        pending_homework=pending_homework,
        due_today=due_today,
        overdue=overdue,
        completed_this_week=completed_this_week
    )

@router.delete("/clear-all-data")
def clear_all_data(db: Session = Depends(get_db)):
    """Clear all data from the database - homework, classes, and schedules"""
    try:
        # Delete in order to respect foreign key constraints
        # First delete schedule slots, then schedules
        db.query(ScheduleSlot).delete()
        db.query(Schedule).delete()
        
        # Delete homework (which references classes)
        db.query(Homework).delete()
        
        # Delete classes
        db.query(Class).delete()
        
        db.commit()
        return {"message": "All data cleared successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")