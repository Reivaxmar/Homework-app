from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .database import Base
from .classes import ClassType

class EducationLevel(PyEnum):
    # International grades (standardized backend storage)
    GRADE_1 = "GRADE_1"
    GRADE_2 = "GRADE_2"
    GRADE_3 = "GRADE_3"
    GRADE_4 = "GRADE_4"
    GRADE_5 = "GRADE_5"
    GRADE_6 = "GRADE_6"
    GRADE_7 = "GRADE_7"
    GRADE_8 = "GRADE_8"
    GRADE_9 = "GRADE_9"
    GRADE_10 = "GRADE_10"
    GRADE_11 = "GRADE_11"
    GRADE_12 = "GRADE_12"

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Using Text for longer content - now serves as description for Drive files
    class_type = Column(Enum(ClassType), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    year = Column(String(20), nullable=False)  # Automatically determined from user's classes
    school = Column(String(200), nullable=True)
    education_level = Column(Enum(EducationLevel), nullable=True)
    
    # Google Drive integration fields
    google_drive_file_id = Column(String(100), nullable=True)  # Google Drive file ID
    google_drive_file_url = Column(String(500), nullable=True)  # Direct link to the file
    google_drive_file_name = Column(String(255), nullable=True)  # Original file name
    google_drive_mime_type = Column(String(100), nullable=True)  # File MIME type
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    
    def __repr__(self):
        return f"<Note(title='{self.title}', class_type='{self.class_type}', is_public={self.is_public}, drive_file='{self.google_drive_file_id}')>"