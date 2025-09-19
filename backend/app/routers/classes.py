from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..models.classes import Class
from .. import schemas

router = APIRouter(prefix="/classes", tags=["classes"])

@router.get("/", response_model=List[schemas.Class])
def get_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all classes"""
    classes = db.query(Class).offset(skip).limit(limit).all()
    return classes

@router.get("/{class_id}", response_model=schemas.Class)
def get_class(class_id: int, db: Session = Depends(get_db)):
    """Get a specific class by ID"""
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.post("/", response_model=schemas.Class, status_code=status.HTTP_201_CREATED)
def create_class(class_data: schemas.ClassCreate, db: Session = Depends(get_db)):
    """Create a new class"""
    db_class = Class(**class_data.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.put("/{class_id}", response_model=schemas.Class)
def update_class(class_id: int, class_data: schemas.ClassUpdate, db: Session = Depends(get_db)):
    """Update a class"""
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    update_data = class_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_class, field, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(class_id: int, db: Session = Depends(get_db)):
    """Delete a class"""
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(db_class)
    db.commit()
    return None

@router.get("/{class_id}/homework", response_model=List[schemas.Homework])
def get_class_homework(class_id: int, db: Session = Depends(get_db)):
    """Get all homework for a specific class"""
    from ..models.homework import Homework
    
    class_ = db.query(Class).filter(Class.id == class_id).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    homework = db.query(Homework).filter(Homework.class_id == class_id).all()
    return homework