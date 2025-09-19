from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models.models import ScheduleSlot
from ..schemas.schemas import ScheduleSlotCreate, ScheduleSlotUpdate, ScheduleSlotResponse, WeeklyScheduleResponse

router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.get("/", response_model=WeeklyScheduleResponse)
def get_weekly_schedule(db: Session = Depends(get_db)):
    """Get the complete weekly schedule"""
    schedule_slots = db.query(ScheduleSlot).options(joinedload(ScheduleSlot.class_ref)).all()
    
    # Organize by day of week
    weekly_schedule = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": []
    }
    
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday"]
    
    for slot in schedule_slots:
        if 0 <= slot.day_of_week <= 4:
            day_name = day_names[slot.day_of_week]
            weekly_schedule[day_name].append(slot)
    
    # Sort each day's slots by period
    for day in weekly_schedule:
        weekly_schedule[day].sort(key=lambda x: x.period)
    
    return weekly_schedule

@router.get("/slots", response_model=List[ScheduleSlotResponse])
def get_schedule_slots(db: Session = Depends(get_db)):
    """Get all schedule slots"""
    slots = db.query(ScheduleSlot).options(joinedload(ScheduleSlot.class_ref)).all()
    return slots

@router.post("/slots", response_model=ScheduleSlotResponse)
def create_schedule_slot(slot_data: ScheduleSlotCreate, db: Session = Depends(get_db)):
    """Create a new schedule slot"""
    db_slot = ScheduleSlot(**slot_data.model_dump())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.put("/slots/{slot_id}", response_model=ScheduleSlotResponse)
def update_schedule_slot(slot_id: int, slot_data: ScheduleSlotUpdate, db: Session = Depends(get_db)):
    """Update an existing schedule slot"""
    slot_obj = db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).first()
    if not slot_obj:
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    
    for field, value in slot_data.model_dump().items():
        setattr(slot_obj, field, value)
    
    db.commit()
    db.refresh(slot_obj)
    return slot_obj

@router.delete("/slots/{slot_id}")
def delete_schedule_slot(slot_id: int, db: Session = Depends(get_db)):
    """Delete a schedule slot"""
    slot_obj = db.query(ScheduleSlot).filter(ScheduleSlot.id == slot_id).first()
    if not slot_obj:
        raise HTTPException(status_code=404, detail="Schedule slot not found")
    
    db.delete(slot_obj)
    db.commit()
    return {"message": "Schedule slot deleted successfully"}