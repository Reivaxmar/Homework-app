from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
from .database import Base

class Priority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Homework(Base):
    __tablename__ = "homework"
    
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    status = Column(Enum(Status), default=Status.PENDING)
    
    # Google Calendar integration
    google_calendar_event_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    class_ = relationship("Class", back_populates="homework")
    
    def __repr__(self):
        return f"<Homework(title='{self.title}', class='{self.class_.name if self.class_ else 'N/A'}', due='{self.due_date}')>"