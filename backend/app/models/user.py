from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    # Google OAuth tokens
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expiry = Column(DateTime, nullable=True)
    
    # User preferences
    timezone = Column(String(50), nullable=True, default='UTC')  # IANA timezone identifier
    
    # Supabase auth
    supabase_user_id = Column(String(255), unique=True, index=True, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classes = relationship("Class", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    homework = relationship("Homework", back_populates="user")
    
    def get_timezone(self):
        """Get user's timezone, defaulting to UTC if not set"""
        return self.timezone or 'UTC'
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.full_name}')>"