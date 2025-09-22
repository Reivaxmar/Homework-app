from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base

class ClassType(PyEnum):
    MATHS = "MATHS"
    ENGLISH = "ENGLISH"
    SCIENCE = "SCIENCE"
    HISTORY = "HISTORY"
    GEOGRAPHY = "GEOGRAPHY"
    ART = "ART"
    MUSIC = "MUSIC"
    PHYSICAL_EDUCATION = "PHYSICAL_EDUCATION"
    COMPUTER_SCIENCE = "COMPUTER_SCIENCE"
    FOREIGN_LANGUAGE = "FOREIGN_LANGUAGE"
    LITERATURE = "LITERATURE"
    CHEMISTRY = "CHEMISTRY"
    PHYSICS = "PHYSICS"
    BIOLOGY = "BIOLOGY"
    OTHER = "OTHER"

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    teacher = Column(String(100), nullable=False)
    year = Column(String(20), nullable=False)
    half_group = Column(String(10), nullable=True)  # Optional half-group (A, B, etc.)
    color = Column(String(7), default="#3B82F6")  # Hex color for UI
    class_type = Column(Enum(ClassType), nullable=False, default=ClassType.OTHER)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedule_slots = relationship("ScheduleSlot", back_populates="class_")
    homework = relationship("Homework", back_populates="class_")
    user = relationship("User", back_populates="classes")
    
    def __repr__(self):
        return f"<Class(name='{self.name}', teacher='{self.teacher}', year='{self.year}', type='{self.class_type}')>"