from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional, List

# Class schemas
class ClassBase(BaseModel):
    name: str
    teacher: str
    year: str
    half_group: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassUpdate(ClassBase):
    pass

class ClassResponse(ClassBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schedule schemas
class ScheduleSlotBase(BaseModel):
    day_of_week: int  # 0=Monday, 1=Tuesday, etc.
    period: int       # 1-6 for classes, 7 for reading/free time
    start_time: time
    end_time: time
    class_id: Optional[int] = None
    is_reading_time: bool = False

class ScheduleSlotCreate(ScheduleSlotBase):
    pass

class ScheduleSlotUpdate(ScheduleSlotBase):
    pass

class ScheduleSlotResponse(ScheduleSlotBase):
    id: int
    class_ref: Optional[ClassResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Homework schemas
class HomeworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    class_id: int
    due_date: datetime
    completed: bool = False
    priority: str = "medium"

class HomeworkCreate(HomeworkBase):
    pass

class HomeworkUpdate(HomeworkBase):
    pass

class HomeworkResponse(HomeworkBase):
    id: int
    class_ref: ClassResponse
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Weekly schedule response
class WeeklyScheduleResponse(BaseModel):
    monday: List[ScheduleSlotResponse]
    tuesday: List[ScheduleSlotResponse]
    wednesday: List[ScheduleSlotResponse]
    thursday: List[ScheduleSlotResponse]
    friday: List[ScheduleSlotResponse]