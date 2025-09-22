"""
Unit tests for database models.
"""

import pytest
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.classes import Class, ClassType
from app.models.homework import Homework, Status as HomeworkStatus, Priority
from app.models.schedule import Schedule, ScheduleSlot, WeekDay, SlotType


class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user(self, test_session):
        """Test creating a user."""
        user = User(
            email="test@example.com",
            full_name="Test User",
            supabase_user_id="test-123"
        )
        test_session.add(user)
        test_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.supabase_user_id == "test-123"
        assert user.google_access_token is None
        assert user.google_refresh_token is None
    
    def test_user_with_google_tokens(self, test_session):
        """Test user with Google OAuth tokens."""
        user = User(
            email="test_google@example.com",
            full_name="Test Google User",
            supabase_user_id="test-google-123",
            google_access_token="access_token",
            google_refresh_token="refresh_token"
        )
        test_session.add(user)
        test_session.commit()
        
        assert user.google_access_token == "access_token"
        assert user.google_refresh_token == "refresh_token"
    
    def test_user_email_uniqueness(self, test_session):
        """Test that user emails must be unique."""
        user1 = User(
            email="unique_test@example.com",
            full_name="Test User 1",
            supabase_user_id="unique-test-123"
        )
        user2 = User(
            email="unique_test@example.com",
            full_name="Test User 2",
            supabase_user_id="unique-test-456"
        )
        
        test_session.add(user1)
        test_session.commit()
        
        test_session.add(user2)
        with pytest.raises(IntegrityError):
            test_session.commit()


class TestClassModel:
    """Test Class model functionality."""
    
    def test_create_class(self, test_session, test_user):
        """Test creating a class."""
        class_obj = Class(
            name="Mathematics",
            teacher="Dr. Smith",
            year="2024",
            color="#FF5733",
            user_id=test_user.id
        )
        test_session.add(class_obj)
        test_session.commit()
        
        assert class_obj.id is not None
        assert class_obj.name == "Mathematics"
        assert class_obj.teacher == "Dr. Smith"
        assert class_obj.color == "#FF5733"
        assert class_obj.year == "2024"
        assert class_obj.user_id == test_user.id
        assert class_obj.class_type == ClassType.OTHER  # default value
        assert class_obj.half_group is None
    
    def test_class_with_all_fields(self, test_session, test_user):
        """Test creating a class with all optional fields."""
        class_obj = Class(
            name="Physics",
            teacher="Prof. Johnson",
            year="2024",
            color="#33FF57",
            class_type=ClassType.PHYSICS,
            half_group="A",
            user_id=test_user.id
        )
        test_session.add(class_obj)
        test_session.commit()
        
        assert class_obj.class_type == ClassType.PHYSICS
        assert class_obj.half_group == "A"
        assert class_obj.year == "2024"
    
    def test_class_user_relationship(self, test_session, test_user):
        """Test class-user relationship."""
        class_obj = Class(
            name="History",
            teacher="Ms. Brown",
            year="2024",
            color="#5733FF",
            user_id=test_user.id
        )
        test_session.add(class_obj)
        test_session.commit()
        
        # Test relationship
        assert class_obj.user == test_user
        assert class_obj in test_user.classes


class TestHomeworkModel:
    """Test Homework model functionality."""
    
    def test_create_homework(self, test_session, test_user, test_class):
        """Test creating homework."""
        homework = Homework(
            title="Math Assignment 1",
            description="Complete exercises 1-10",
            due_date="2024-12-31",
            status=HomeworkStatus.PENDING,
            priority=Priority.MEDIUM,
            user_id=test_user.id,
            class_id=test_class.id
        )
        test_session.add(homework)
        test_session.commit()
        
        assert homework.id is not None
        assert homework.title == "Math Assignment 1"
        assert homework.description == "Complete exercises 1-10"
        assert str(homework.due_date) == "2024-12-31"
        assert homework.status == HomeworkStatus.PENDING
        assert homework.priority == Priority.MEDIUM
        assert homework.user_id == test_user.id
        assert homework.class_id == test_class.id
        assert homework.google_calendar_event_id is None
    
    def test_homework_with_calendar_event(self, test_session, test_user, test_class):
        """Test homework with Google Calendar event ID."""
        homework = Homework(
            title="Science Lab Report",
            description="Write lab report",
            due_date="2024-11-15",
            status=HomeworkStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            google_calendar_event_id="calendar_event_123",
            user_id=test_user.id,
            class_id=test_class.id
        )
        test_session.add(homework)
        test_session.commit()
        
        assert homework.google_calendar_event_id == "calendar_event_123"
        assert homework.status == HomeworkStatus.IN_PROGRESS
        assert homework.priority == Priority.HIGH
    
    def test_homework_relationships(self, test_session, test_user, test_class):
        """Test homework relationships."""
        homework = Homework(
            title="English Essay",
            description="Write 500-word essay",
            due_date="2024-12-01",
            status=HomeworkStatus.PENDING,
            user_id=test_user.id,
            class_id=test_class.id
        )
        test_session.add(homework)
        test_session.commit()
        
        # Test relationships
        assert homework.user == test_user
        assert homework.class_ == test_class
        assert homework in test_user.homework
        assert homework in test_class.homework
    
    def test_homework_status_values(self, test_session, test_user, test_class):
        """Test different homework status values."""
        statuses = [
            HomeworkStatus.PENDING,
            HomeworkStatus.IN_PROGRESS,
            HomeworkStatus.COMPLETED
        ]
        
        for i, status in enumerate(statuses):
            homework = Homework(
                title=f"Test Homework {i}",
                description="Test description",
                due_date="2024-12-31",
                status=status,
                user_id=test_user.id,
                class_id=test_class.id
            )
            test_session.add(homework)
        
        test_session.commit()
        
        # Verify all homework were created with correct statuses
        all_homework = test_session.query(Homework).all()
        assert len(all_homework) == len(statuses)
        for homework in all_homework:
            assert homework.status in statuses


class TestScheduleModel:
    """Test Schedule and ScheduleSlot model functionality."""
    
    def test_create_schedule(self, test_session, test_user):
        """Test creating a schedule."""
        schedule = Schedule(
            name="Fall Schedule",
            year="2024",
            user_id=test_user.id
        )
        test_session.add(schedule)
        test_session.commit()
        
        assert schedule.id is not None
        assert schedule.name == "Fall Schedule"
        assert schedule.year == "2024"
        assert schedule.user_id == test_user.id
        assert schedule.is_active is True  # default value
    
    def test_create_schedule_slot(self, test_session, test_user, test_class):
        """Test creating a schedule slot."""
        schedule = Schedule(
            name="Test Schedule",
            year="2024",
            user_id=test_user.id
        )
        test_session.add(schedule)
        test_session.commit()
        
        schedule_slot = ScheduleSlot(
            schedule_id=schedule.id,
            class_id=test_class.id,
            day=WeekDay.MONDAY,
            slot_number=1,
            start_time="08:00",
            end_time="09:00",
            slot_type=SlotType.CLASS
        )
        test_session.add(schedule_slot)
        test_session.commit()
        
        assert schedule_slot.id is not None
        assert schedule_slot.schedule_id == schedule.id
        assert schedule_slot.class_id == test_class.id
        assert schedule_slot.day == WeekDay.MONDAY
        assert schedule_slot.slot_number == 1
        assert schedule_slot.slot_type == SlotType.CLASS
    
    def test_schedule_relationships(self, test_session, test_user, test_class):
        """Test schedule relationships."""
        schedule = Schedule(
            name="Test Schedule",
            year="2024",
            user_id=test_user.id
        )
        test_session.add(schedule)
        test_session.commit()
        
        schedule_slot = ScheduleSlot(
            schedule_id=schedule.id,
            class_id=test_class.id,
            day=WeekDay.TUESDAY,
            slot_number=2,
            start_time="09:00",
            end_time="10:00",
            slot_type=SlotType.CLASS
        )
        test_session.add(schedule_slot)
        test_session.commit()
        
        # Test relationships
        assert schedule.user == test_user
        assert schedule in test_user.schedules
        assert schedule_slot.schedule == schedule
        assert schedule_slot.class_ == test_class
        assert schedule_slot in schedule.slots
        assert schedule_slot in test_class.schedule_slots
    
    def test_different_slot_types(self, test_session, test_user):
        """Test different schedule slot types."""
        schedule = Schedule(
            name="Test Schedule",
            year="2024",
            user_id=test_user.id
        )
        test_session.add(schedule)
        test_session.commit()
        
        slot_types = [SlotType.CLASS, SlotType.READING, SlotType.RECESS]
        
        for i, slot_type in enumerate(slot_types):
            schedule_slot = ScheduleSlot(
                schedule_id=schedule.id,
                class_id=None if slot_type != SlotType.CLASS else None,  # No class for reading/recess
                day=WeekDay.MONDAY,
                slot_number=i + 1,
                start_time=f"0{8+i}:00",
                end_time=f"0{9+i}:00",
                slot_type=slot_type
            )
            test_session.add(schedule_slot)
        
        test_session.commit()
        
        # Verify all slots were created
        slots = test_session.query(ScheduleSlot).all()
        assert len(slots) == len(slot_types)
        for slot in slots:
            assert slot.slot_type in slot_types