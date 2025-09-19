from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date

from ..models.database import get_db
from ..models.homework import Homework, Status
from ..models.classes import Class
from .. import schemas

router = APIRouter(prefix="/homework", tags=["homework"])

@router.get("/", response_model=List[schemas.Homework])
def get_homework(
    skip: int = 0,
    limit: int = 100,
    class_id: Optional[int] = Query(None),
    status: Optional[schemas.Status] = Query(None),
    due_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get homework with optional filters"""
    query = db.query(Homework)
    
    if class_id:
        query = query.filter(Homework.class_id == class_id)
    if status:
        query = query.filter(Homework.status == status)
    if due_date:
        query = query.filter(Homework.due_date == due_date)
    
    homework = query.offset(skip).limit(limit).all()
    return homework

@router.get("/due-today", response_model=List[schemas.Homework])
def get_homework_due_today(db: Session = Depends(get_db)):
    """Get homework due today"""
    today = date.today()
    homework = db.query(Homework).filter(
        and_(
            Homework.due_date == today,
            Homework.status != Status.COMPLETED
        )
    ).all()
    return homework

@router.get("/overdue", response_model=List[schemas.Homework])
def get_overdue_homework(db: Session = Depends(get_db)):
    """Get overdue homework"""
    today = date.today()
    homework = db.query(Homework).filter(
        and_(
            Homework.due_date < today,
            Homework.status != Status.COMPLETED
        )
    ).all()
    return homework

@router.get("/upcoming", response_model=List[schemas.Homework])
def get_upcoming_homework(days: int = 7, db: Session = Depends(get_db)):
    """Get homework due in the next N days"""
    from datetime import timedelta
    today = date.today()
    future_date = today + timedelta(days=days)
    
    homework = db.query(Homework).filter(
        and_(
            Homework.due_date >= today,
            Homework.due_date <= future_date,
            Homework.status != Status.COMPLETED
        )
    ).all()
    return homework

@router.get("/{homework_id}", response_model=schemas.Homework)
def get_homework_item(homework_id: int, db: Session = Depends(get_db)):
    """Get a specific homework item"""
    homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    return homework

@router.post("/", response_model=schemas.Homework, status_code=status.HTTP_201_CREATED)
def create_homework(homework_data: schemas.HomeworkCreate, db: Session = Depends(get_db)):
    """Create a new homework item"""
    # Verify class exists
    class_ = db.query(Class).filter(Class.id == homework_data.class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db_homework = Homework(**homework_data.dict())
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)
    return db_homework

@router.put("/{homework_id}", response_model=schemas.Homework)
def update_homework(homework_id: int, homework_data: schemas.HomeworkUpdate, db: Session = Depends(get_db)):
    """Update a homework item"""
    db_homework = db.query(Homework).filter(Homework.id == homework_id).first()
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
    return db_homework

@router.put("/{homework_id}/complete", response_model=schemas.Homework)
def complete_homework(homework_id: int, db: Session = Depends(get_db)):
    """Mark homework as completed"""
    db_homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    db_homework.status = Status.COMPLETED
    db_homework.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_homework)
    return db_homework

@router.put("/{homework_id}/reopen", response_model=schemas.Homework)
def reopen_homework(homework_id: int, db: Session = Depends(get_db)):
    """Reopen completed homework"""
    db_homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    db_homework.status = Status.PENDING
    db_homework.completed_at = None
    
    db.commit()
    db.refresh(db_homework)
    return db_homework

@router.delete("/{homework_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_homework(homework_id: int, db: Session = Depends(get_db)):
    """Delete a homework item"""
    db_homework = db.query(Homework).filter(Homework.id == homework_id).first()
    if not db_homework:
        raise HTTPException(status_code=404, detail="Homework not found")
    
    db.delete(db_homework)
    db.commit()
    return None