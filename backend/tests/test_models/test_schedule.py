"""
Tests for Schedule and ScheduleSlot models.
"""
import pytest
from datetime import time
from app.models.user import User
from app.models.classes import Class
from app.models.schedule import Schedule, ScheduleSlot, WeekDay, SlotType

def test_create_schedule(db):
    """Test creating a new schedule."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Spring 2024 Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    assert schedule.id is not None
    assert schedule.user_id == user.id
    assert schedule.name == "Spring 2024 Schedule"
    assert schedule.year == "2024"
    assert schedule.is_active is True  # Default value
    assert schedule.created_at is not None
    assert schedule.updated_at is not None

def test_schedule_defaults(db):
    """Test schedule default values."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    assert schedule.name == "Default Schedule"  # Default name
    assert schedule.is_active is True          # Default active status

def test_schedule_user_relationship(db):
    """Test schedule-user relationship."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Test relationship works both ways
    assert schedule.user.id == user.id
    assert schedule.user.email == "test@example.com"
    assert len(user.schedules) == 1
    assert user.schedules[0].id == schedule.id

def test_schedule_repr(db):
    """Test schedule string representation."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    
    expected = "<Schedule(name='Test Schedule', year='2024')>"
    assert repr(schedule) == expected

def test_create_schedule_slot(db):
    """Test creating a schedule slot."""
    # Create user, class, and schedule
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Create schedule slot
    slot = ScheduleSlot(
        schedule_id=schedule.id,
        class_id=class_obj.id,
        day=WeekDay.MONDAY,
        slot_number=1,
        start_time=time(9, 0),
        end_time=time(10, 30),
        slot_type=SlotType.CLASS
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    
    assert slot.id is not None
    assert slot.schedule_id == schedule.id
    assert slot.class_id == class_obj.id
    assert slot.day == WeekDay.MONDAY
    assert slot.slot_number == 1
    assert slot.start_time == time(9, 0)
    assert slot.end_time == time(10, 30)
    assert slot.slot_type == SlotType.CLASS

def test_schedule_slot_defaults(db):
    """Test schedule slot default values."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    slot = ScheduleSlot(
        schedule_id=schedule.id,
        day=WeekDay.MONDAY,
        slot_number=1,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    
    assert slot.slot_type == SlotType.CLASS  # Default slot type
    assert slot.class_id is None             # Optional class

def test_schedule_slot_enums(db):
    """Test schedule slot enum values."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Test all weekdays
    for day in WeekDay:
        slot = ScheduleSlot(
            schedule_id=schedule.id,
            day=day,
            slot_number=1,
            start_time=time(9, 0),
            end_time=time(10, 30)
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)
        
        assert slot.day == day
    
    # Test all slot types
    for slot_type in SlotType:
        slot = ScheduleSlot(
            schedule_id=schedule.id,
            day=WeekDay.MONDAY,
            slot_number=2,
            start_time=time(11, 0),
            end_time=time(12, 30),
            slot_type=slot_type
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)
        
        assert slot.slot_type == slot_type

def test_schedule_slot_relationships(db):
    """Test schedule slot relationships."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    class_obj = Class(
        user_id=user.id,
        name="Mathematics",
        teacher="Dr. Smith",
        year="2024"
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    slot = ScheduleSlot(
        schedule_id=schedule.id,
        class_id=class_obj.id,
        day=WeekDay.MONDAY,
        slot_number=1,
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    
    # Test relationships work both ways
    assert slot.schedule.id == schedule.id
    assert slot.class_.id == class_obj.id
    assert len(schedule.slots) == 1
    assert schedule.slots[0].id == slot.id
    assert len(class_obj.schedule_slots) == 1
    assert class_obj.schedule_slots[0].id == slot.id

def test_schedule_slot_repr(db):
    """Test schedule slot string representation."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    slot = ScheduleSlot(
        schedule_id=schedule.id,
        day=WeekDay.MONDAY,
        slot_number=1,
        start_time=time(9, 0),
        end_time=time(10, 30),
        slot_type=SlotType.CLASS
    )
    db.add(slot)
    db.commit()
    
    expected = "<ScheduleSlot(day='WeekDay.MONDAY', slot=1, type='SlotType.CLASS')>"
    assert repr(slot) == expected

def test_free_period_slot(db):
    """Test creating a free period (no class assigned)."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        supabase_user_id="test-user-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    schedule = Schedule(
        user_id=user.id,
        name="Test Schedule",
        year="2024"
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    # Create a reading period with no class
    slot = ScheduleSlot(
        schedule_id=schedule.id,
        class_id=None,  # No class assigned
        day=WeekDay.MONDAY,
        slot_number=2,
        start_time=time(10, 30),
        end_time=time(11, 0),
        slot_type=SlotType.READING
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    
    assert slot.class_id is None
    assert slot.slot_type == SlotType.READING
    assert slot.class_ is None