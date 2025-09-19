from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models.models import Homework
from ..schemas.schemas import HomeworkCreate, HomeworkUpdate, HomeworkResponse

router = APIRouter(prefix="/api/homework", tags=["homework"])

@router.get("/", response_model=List[HomeworkResponse])
def get_homework_assignments(
    completed: Optional[bool] = None,
    class_id: Optional[int] = None,
    due_before: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get homework assignments with optional filters"""
    query = db.query(Homework).options(joinedload(Homework.class_ref))
    
    if completed is not None:
        query = query.filter(Homework.completed == completed)
    
    if class_id is not None:
        query = query.filter(Homework.class_id == class_id)
    
    if due_before is not None:
        query = query.filter(Homework.due_date <= due_before)
    
    homework_list = query.order_by(Homework.due_date).all()
    return homework_list

@router.get("/{homework_id}", response_model=HomeworkResponse)
def get_homework(homework_id: int, db: Session = Depends(get_db)):
    """Get a specific homework assignment by ID"""
    homework_obj = db.query(Homework).options(joinedload(Homework.class_ref)).filter(Homework.id == homework_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    return homework_obj

@router.post("/", response_model=HomeworkResponse)
def create_homework(homework_data: HomeworkCreate, db: Session = Depends(get_db)):
    """Create a new homework assignment"""
    db_homework = Homework(**homework_data.model_dump())
    db.add(db_homework)
    db.commit()
    db.refresh(db_homework)
    
    # Load the class relationship
    db.refresh(db_homework)
    homework_with_class = db.query(Homework).options(joinedload(Homework.class_ref)).filter(Homework.id == db_homework.id).first()
    return homework_with_class

@router.put("/{homework_id}", response_model=HomeworkResponse)
def update_homework(homework_id: int, homework_data: HomeworkUpdate, db: Session = Depends(get_db)):
    """Update an existing homework assignment"""
    homework_obj = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    
    for field, value in homework_data.model_dump().items():
        setattr(homework_obj, field, value)
    
    db.commit()
    db.refresh(homework_obj)
    
    # Load the class relationship
    homework_with_class = db.query(Homework).options(joinedload(Homework.class_ref)).filter(Homework.id == homework_id).first()
    return homework_with_class

@router.delete("/{homework_id}")
def delete_homework(homework_id: int, db: Session = Depends(get_db)):
    """Delete a homework assignment"""
    homework_obj = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    
    db.delete(homework_obj)
    db.commit()
    return {"message": "Homework assignment deleted successfully"}

@router.put("/{homework_id}/complete", response_model=HomeworkResponse)
def toggle_homework_completion(homework_id: int, db: Session = Depends(get_db)):
    """Toggle completion status of a homework assignment"""
    homework_obj = db.query(Homework).filter(Homework.id == homework_id).first()
    if not homework_obj:
        raise HTTPException(status_code=404, detail="Homework assignment not found")
    
    homework_obj.completed = not homework_obj.completed
    db.commit()
    db.refresh(homework_obj)
    
    # Load the class relationship
    homework_with_class = db.query(Homework).options(joinedload(Homework.class_ref)).filter(Homework.id == homework_id).first()
    return homework_with_class