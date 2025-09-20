from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Time, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, time
from enum import Enum as PyEnum
from .database import Base

class WeekDay(PyEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"

class SlotType(PyEnum):
    CLASS = "CLASS"
    READING = "READING"
    RECESS = "RECESS"

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False, default="Default Schedule")
    year = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    slots = relationship("ScheduleSlot", back_populates="schedule")
    user = relationship("User", back_populates="schedules")
    
    def __repr__(self):
        return f"<Schedule(name='{self.name}', year='{self.year}')>"

class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)  # Null for reading/free time
    
    day = Column(Enum(WeekDay), nullable=False)
    slot_number = Column(Integer, nullable=False)  # 1-6 for 6 classes per day
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_type = Column(Enum(SlotType), nullable=False, default=SlotType.CLASS)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="slots")
    class_ = relationship("Class", back_populates="schedule_slots")
    
    def __repr__(self):
        return f"<ScheduleSlot(day='{self.day}', slot={self.slot_number}, type='{self.slot_type}')>"