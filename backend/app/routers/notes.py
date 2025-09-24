from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
import logging

from ..models.database import get_db
from ..models.notes import Note, EducationLevel
from ..models.classes import Class, ClassType
from ..models.user import User
from ..auth import get_current_user
from .. import schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notes", tags=["notes"])

def get_user_current_year(user_id: int, db: Session) -> str:
    """Get the most common year from user's classes"""
    classes = db.query(Class).filter(Class.user_id == user_id).all()
    if not classes:
        # Default to current academic year if no classes
        from datetime import datetime
        current_year = datetime.now().year
        return f"{current_year}-{current_year + 1}"
    
    # Get the most common year from user's classes
    years = [cls.year for cls in classes]
    most_common_year = max(set(years), key=years.count) if years else f"{datetime.now().year}-{datetime.now().year + 1}"
    return most_common_year

@router.get("/", response_model=List[schemas.Note])
def get_user_notes(
    skip: int = 0,
    limit: int = 100,
    class_type: Optional[schemas.ClassType] = Query(None),
    is_public: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's notes with optional filters"""
    query = db.query(Note).filter(Note.user_id == current_user.id)
    
    if class_type:
        query = query.filter(Note.class_type == class_type)
    if is_public is not None:
        query = query.filter(Note.is_public == is_public)
    
    notes = query.order_by(desc(Note.updated_at)).offset(skip).limit(limit).all()
    return notes

@router.get("/public", response_model=List[schemas.PublicNote])
def get_public_notes(
    skip: int = 0,
    limit: int = 100,
    class_type: Optional[schemas.ClassType] = Query(None),
    education_level: Optional[schemas.EducationLevel] = Query(None),
    year: Optional[str] = Query(None),
    school: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get public notes from all users with optional filters"""
    query = db.query(Note).filter(Note.is_public == True)
    
    if class_type:
        query = query.filter(Note.class_type == class_type)
    if education_level:
        query = query.filter(Note.education_level == education_level)
    if year:
        query = query.filter(Note.year == year)
    if school:
        query = query.filter(Note.school.ilike(f"%{school}%"))
    
    notes = query.order_by(desc(Note.updated_at)).offset(skip).limit(limit).all()
    
    # Convert to PublicNote schema (excludes user details)
    public_notes = []
    for note in notes:
        public_notes.append(schemas.PublicNote(
            id=note.id,
            title=note.title,
            content=note.content,
            class_type=note.class_type,
            year=note.year,
            school=note.school,
            education_level=note.education_level,
            created_at=note.created_at,
            updated_at=note.updated_at
        ))
    
    return public_notes

@router.get("/education-levels", response_model=List[str])
def get_education_levels(lang: Optional[str] = Query(None)):
    """Get available education levels, optionally filtered by language"""
    if lang == "en":
        # Return international grades for English
        international_levels = [
            EducationLevel.GRADE_1, EducationLevel.GRADE_2, EducationLevel.GRADE_3,
            EducationLevel.GRADE_4, EducationLevel.GRADE_5, EducationLevel.GRADE_6,
            EducationLevel.GRADE_7, EducationLevel.GRADE_8, EducationLevel.GRADE_9,
            EducationLevel.GRADE_10, EducationLevel.GRADE_11, EducationLevel.GRADE_12
        ]
        return [level.value for level in international_levels]
    elif lang == "es":
        # Return Spanish education system levels for Spanish
        spanish_levels = [
            EducationLevel.PRIMARIA, EducationLevel.ESO, EducationLevel.BACHILLERATO
        ]
        return [level.value for level in spanish_levels]
    else:
        # Return all levels if no language specified (backward compatibility)
        return [level.value for level in EducationLevel]

@router.get("/{note_id}", response_model=schemas.Note)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific note by ID - user-specific"""
    note = db.query(Note).filter(
        and_(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/", response_model=schemas.Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: schemas.NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new note for current user"""
    # Get current year from user's classes
    current_year = get_user_current_year(current_user.id, db)
    
    note_dict = note_data.dict()
    note_dict["user_id"] = current_user.id
    note_dict["year"] = current_year
    
    db_note = Note(**note_dict)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.put("/{note_id}", response_model=schemas.Note)
def update_note(
    note_id: int,
    note_data: schemas.NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a note - user-specific"""
    note = db.query(Note).filter(
        and_(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update note fields
    update_data = note_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a note - user-specific"""
    note = db.query(Note).filter(
        and_(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return None