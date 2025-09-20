from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from ..models.database import get_db
from ..models.classes import Class
from ..models.user import User
from ..auth import get_current_user
from .. import schemas

router = APIRouter(prefix="/classes", tags=["classes"])

@router.get("/", response_model=List[schemas.Class])
def get_classes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all classes for current user"""
    classes = db.query(Class).filter(Class.user_id == current_user.id).offset(skip).limit(limit).all()
    return classes

@router.get("/{class_id}", response_model=schemas.Class)
def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific class by ID - user-specific"""
    class_ = db.query(Class).filter(
        and_(
            Class.id == class_id,
            Class.user_id == current_user.id
        )
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_

@router.post("/", response_model=schemas.Class, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: schemas.ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new class for current user"""
    class_dict = class_data.dict()
    class_dict["user_id"] = current_user.id
    db_class = Class(**class_dict)
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.put("/{class_id}", response_model=schemas.Class)
def update_class(
    class_id: int,
    class_data: schemas.ClassUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a class - user-specific"""
    db_class = db.query(Class).filter(
        and_(
            Class.id == class_id,
            Class.user_id == current_user.id
        )
    ).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    update_data = class_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_class, field, value)
    
    db.commit()
    db.refresh(db_class)
    return db_class

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a class - user-specific"""
    db_class = db.query(Class).filter(
        and_(
            Class.id == class_id,
            Class.user_id == current_user.id
        )
    ).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(db_class)
    db.commit()
    return None

@router.get("/{class_id}/homework", response_model=List[schemas.Homework])
def get_class_homework(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all homework for a specific class - user-specific"""
    from ..models.homework import Homework
    
    class_ = db.query(Class).filter(
        and_(
            Class.id == class_id,
            Class.user_id == current_user.id
        )
    ).first()
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    
    homework = db.query(Homework).filter(
        and_(
            Homework.class_id == class_id,
            Homework.user_id == current_user.id
        )
    ).all()
    return homework