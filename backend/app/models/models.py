from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    teacher = Column(String(100), nullable=False)
    year = Column(String(20), nullable=False)
    half_group = Column(String(10), nullable=True)  # Optional: A, B, or None
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    schedule_slots = relationship("ScheduleSlot", back_populates="class_ref")
    homework_assignments = relationship("Homework", back_populates="class_ref")

class ScheduleSlot(Base):
    __tablename__ = "schedule_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc.
    period = Column(Integer, nullable=False)  # 1-6 for classes, 7 for reading/free time
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)  # Null for reading/free periods
    is_reading_time = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    class_ref = relationship("Class", back_populates="schedule_slots")

class Homework(Base):
    __tablename__ = "homework"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    completed = Column(Boolean, default=False)
    priority = Column(String(10), default="medium")  # low, medium, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    class_ref = relationship("Class", back_populates="homework_assignments")