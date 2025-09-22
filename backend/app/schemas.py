from pydantic import BaseModel, Field
from datetime import datetime, date, time
from enum import Enum
from typing import Optional, List

# User schemas
class UserBase(BaseModel):
    email: str
    full_name: str
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    supabase_user_id: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    google_access_token: Optional[str] = None
    google_refresh_token: Optional[str] = None
    google_token_expiry: Optional[datetime] = None

class User(UserBase):
    id: int
    supabase_user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Enums
class WeekDay(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"

class SlotType(str, Enum):
    CLASS = "CLASS"
    READING = "READING"
    RECESS = "RECESS"

class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Status(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ClassType(str, Enum):
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

# Class schemas
class ClassBase(BaseModel):
    name: str = Field(..., max_length=100)
    teacher: str = Field(..., max_length=100)
    year: str = Field(..., max_length=20)
    half_group: Optional[str] = Field(None, max_length=10)
    color: str = Field("#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    class_type: ClassType = Field(..., description="Predefined class type")

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    teacher: Optional[str] = Field(None, max_length=100)
    year: Optional[str] = Field(None, max_length=20)
    half_group: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    class_type: Optional[ClassType] = Field(None, description="Predefined class type")

class Class(ClassBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True

# Schedule schemas
class ScheduleBase(BaseModel):
    name: str = Field(..., max_length=100)
    year: str = Field(..., max_length=20)

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True

# Schedule Slot schemas
class ScheduleSlotBase(BaseModel):
    day: WeekDay
    slot_number: int = Field(..., ge=1, le=8)
    start_time: time
    end_time: time
    slot_type: SlotType = SlotType.CLASS

class ScheduleSlotCreate(ScheduleSlotBase):
    schedule_id: int
    class_id: Optional[int] = None

class ScheduleSlotUpdate(BaseModel):
    class_id: Optional[int] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_type: Optional[SlotType] = None

class ScheduleSlot(ScheduleSlotBase):
    id: int
    schedule_id: int
    class_id: Optional[int] = None
    class_: Optional[Class] = None

    class Config:
        from_attributes = True

# Homework schemas
class HomeworkBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: date
    due_time: time = time(23, 59)  # Default to 23:59
    priority: Priority = Priority.MEDIUM

class HomeworkCreate(HomeworkBase):
    class_id: int
    assigned_date: date = Field(default_factory=date.today)

class HomeworkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None

class Homework(HomeworkBase):
    id: int
    class_id: int
    user_id: int
    assigned_date: date
    status: Status
    google_calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    class_: Optional[Class] = None
    user: Optional[User] = None

    class Config:
        from_attributes = True

# Response schemas
class ScheduleWithSlots(Schedule):
    slots: List[ScheduleSlot] = []

class ClassWithHomework(Class):
    homework: List[Homework] = []

# Dashboard summary
class DashboardSummary(BaseModel):
    total_classes: int
    pending_homework: int
    due_today: int
    overdue: int
    completed_this_week: int