from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..models.schedule import Schedule, ScheduleSlot
from ..models.user import User
from .. import schemas
from ..auth import get_current_user

router = APIRouter(prefix="/schedules", tags=["schedules"])

@router.get("/", response_model=List[schemas.Schedule])
def get_schedules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all schedules"""
    schedules = db.query(Schedule).offset(skip).limit(limit).all()
    return schedules

@router.get("/{schedule_id}", response_model=schemas.ScheduleWithSlots)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Get a specific schedule with its slots"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.get("/active/{year}", response_model=schemas.ScheduleWithSlots)
def get_active_schedule(year: str, db: Session = Depends(get_db)):
    """Get the active schedule for a year"""
    schedule = db.query(Schedule).filter(
        Schedule.year == year,
        Schedule.is_active == True
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="No active schedule found for this year")
    return schedule

@router.post("/", response_model=schemas.Schedule, status_code=status.HTTP_201_CREATED)
def create_schedule(schedule_data: schemas.ScheduleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new schedule"""
    # Deactivate other schedules for the same year
    db.query(Schedule).filter(Schedule.year == schedule_data.year).update({"is_active": False})

    # Add user_id from the authenticated user
    db_schedule = Schedule(**schedule_data.dict(), user_id=current_user.id, is_active=True)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.put("/{schedule_id}/activate", response_model=schemas.Schedule)
def activate_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Activate a schedule (deactivates others in same year)"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Deactivate other schedules for the same year
    db.query(Schedule).filter(Schedule.year == schedule.year).update({"is_active": False})
    
    schedule.is_active = True
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Delete a schedule"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    return None

# Schedule Slots endpoints
@router.get("/{schedule_id}/slots", response_model=List[schemas.ScheduleSlot])
def get_schedule_slots(schedule_id: int, db: Session = Depends(get_db)):
    """Get all slots for a schedule"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    slots = db.query(ScheduleSlot).filter(ScheduleSlot.schedule_id == schedule_id).all()
    return slots

@router.post("/{schedule_id}/slots", response_model=schemas.ScheduleSlot, status_code=status.HTTP_201_CREATED)
def create_schedule_slot(schedule_id: int, slot_data: schemas.ScheduleSlotCreate, db: Session = Depends(get_db)):
    """Create a new schedule slot"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    slot_data.schedule_id = schedule_id
    db_slot = ScheduleSlot(**slot_data.dict())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.put("/{schedule_id}/slots/{slot_id}", response_model=schemas.ScheduleSlot)
def update_schedule_slot(schedule_id: int, slot_id: int, slot_data: schemas.ScheduleSlotUpdate, db: Session = Depends(get_db)):
    """Update a schedule slot"""
    slot = db.query(ScheduleSlot).filter(
        ScheduleSlot.id == slot_id,
        ScheduleSlot.schedule_id == schedule_id
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    
    update_data = slot_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(slot, field, value)
    
    db.commit()
    db.refresh(slot)
    return slot

@router.delete("/{schedule_id}/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule_slot(schedule_id: int, slot_id: int, db: Session = Depends(get_db)):
    """Delete a schedule slot"""
    slot = db.query(ScheduleSlot).filter(
        ScheduleSlot.id == slot_id,
        ScheduleSlot.schedule_id == schedule_id
    ).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    
    db.delete(slot)
    db.commit()
    return None