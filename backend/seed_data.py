"""
Seed the database with sample data for demonstration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.models import Base, Class, ScheduleSlot, Homework
from datetime import datetime, time, timedelta

# Create all tables
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_classes = db.query(Class).count()
        if existing_classes > 0:
            print("Database already has data. Skipping seed.")
            return
        
        # Create sample classes
        classes_data = [
            {"name": "Mathematics", "teacher": "Mr. Johnson", "year": "2024", "half_group": None},
            {"name": "English Literature", "teacher": "Ms. Smith", "year": "2024", "half_group": "A"},
            {"name": "Chemistry", "teacher": "Dr. Brown", "year": "2024", "half_group": None},
            {"name": "History", "teacher": "Mr. Davis", "year": "2024", "half_group": "B"},
            {"name": "Physics", "teacher": "Dr. Wilson", "year": "2024", "half_group": None},
            {"name": "Spanish", "teacher": "Señora Garcia", "year": "2024", "half_group": "A"},
        ]
        
        classes = []
        for class_data in classes_data:
            class_obj = Class(**class_data)
            db.add(class_obj)
            classes.append(class_obj)
        
        db.commit()
        
        # Refresh to get IDs
        for class_obj in classes:
            db.refresh(class_obj)
        
        # Create sample schedule slots
        schedule_data = [
            # Monday
            {"day_of_week": 0, "period": 1, "start_time": time(8, 0), "end_time": time(8, 50), "class_id": classes[0].id},  # Math
            {"day_of_week": 0, "period": 2, "start_time": time(9, 0), "end_time": time(9, 50), "class_id": classes[1].id},  # English
            {"day_of_week": 0, "period": 3, "start_time": time(10, 0), "end_time": time(10, 50), "class_id": classes[2].id},  # Chemistry
            {"day_of_week": 0, "period": 4, "start_time": time(11, 0), "end_time": time(11, 50), "class_id": classes[3].id},  # History
            {"day_of_week": 0, "period": 5, "start_time": time(13, 0), "end_time": time(13, 50), "class_id": classes[4].id},  # Physics
            {"day_of_week": 0, "period": 6, "start_time": time(14, 0), "end_time": time(14, 50), "class_id": classes[5].id},  # Spanish
            {"day_of_week": 0, "period": 7, "start_time": time(15, 0), "end_time": time(15, 30), "class_id": None, "is_reading_time": True},
            
            # Tuesday
            {"day_of_week": 1, "period": 1, "start_time": time(8, 0), "end_time": time(8, 50), "class_id": classes[4].id},  # Physics
            {"day_of_week": 1, "period": 2, "start_time": time(9, 0), "end_time": time(9, 50), "class_id": classes[0].id},  # Math
            {"day_of_week": 1, "period": 3, "start_time": time(10, 0), "end_time": time(10, 50), "class_id": classes[5].id},  # Spanish
            {"day_of_week": 1, "period": 4, "start_time": time(11, 0), "end_time": time(11, 50), "class_id": classes[2].id},  # Chemistry
            {"day_of_week": 1, "period": 5, "start_time": time(13, 0), "end_time": time(13, 50), "class_id": classes[1].id},  # English
            {"day_of_week": 1, "period": 6, "start_time": time(14, 0), "end_time": time(14, 50), "class_id": classes[3].id},  # History
            {"day_of_week": 1, "period": 7, "start_time": time(15, 0), "end_time": time(15, 30), "class_id": None, "is_reading_time": True},
            
            # Wednesday
            {"day_of_week": 2, "period": 1, "start_time": time(8, 0), "end_time": time(8, 50), "class_id": classes[1].id},  # English
            {"day_of_week": 2, "period": 2, "start_time": time(9, 0), "end_time": time(9, 50), "class_id": classes[3].id},  # History
            {"day_of_week": 2, "period": 3, "start_time": time(10, 0), "end_time": time(10, 50), "class_id": classes[0].id},  # Math
            {"day_of_week": 2, "period": 4, "start_time": time(11, 0), "end_time": time(11, 50), "class_id": classes[5].id},  # Spanish
            {"day_of_week": 2, "period": 5, "start_time": time(13, 0), "end_time": time(13, 50), "class_id": classes[2].id},  # Chemistry
            {"day_of_week": 2, "period": 6, "start_time": time(14, 0), "end_time": time(14, 50), "class_id": classes[4].id},  # Physics
            {"day_of_week": 2, "period": 7, "start_time": time(15, 0), "end_time": time(15, 30), "class_id": None, "is_reading_time": True},
            
            # Thursday
            {"day_of_week": 3, "period": 1, "start_time": time(8, 0), "end_time": time(8, 50), "class_id": classes[2].id},  # Chemistry
            {"day_of_week": 3, "period": 2, "start_time": time(9, 0), "end_time": time(9, 50), "class_id": classes[4].id},  # Physics
            {"day_of_week": 3, "period": 3, "start_time": time(10, 0), "end_time": time(10, 50), "class_id": classes[3].id},  # History
            {"day_of_week": 3, "period": 4, "start_time": time(11, 0), "end_time": time(11, 50), "class_id": classes[0].id},  # Math
            {"day_of_week": 3, "period": 5, "start_time": time(13, 0), "end_time": time(13, 50), "class_id": classes[5].id},  # Spanish
            {"day_of_week": 3, "period": 6, "start_time": time(14, 0), "end_time": time(14, 50), "class_id": classes[1].id},  # English
            {"day_of_week": 3, "period": 7, "start_time": time(15, 0), "end_time": time(15, 30), "class_id": None, "is_reading_time": True},
            
            # Friday
            {"day_of_week": 4, "period": 1, "start_time": time(8, 0), "end_time": time(8, 50), "class_id": classes[5].id},  # Spanish
            {"day_of_week": 4, "period": 2, "start_time": time(9, 0), "end_time": time(9, 50), "class_id": classes[2].id},  # Chemistry
            {"day_of_week": 4, "period": 3, "start_time": time(10, 0), "end_time": time(10, 50), "class_id": classes[4].id},  # Physics
            {"day_of_week": 4, "period": 4, "start_time": time(11, 0), "end_time": time(11, 50), "class_id": classes[1].id},  # English
            {"day_of_week": 4, "period": 5, "start_time": time(13, 0), "end_time": time(13, 50), "class_id": classes[3].id},  # History
            {"day_of_week": 4, "period": 6, "start_time": time(14, 0), "end_time": time(14, 50), "class_id": classes[0].id},  # Math
            {"day_of_week": 4, "period": 7, "start_time": time(15, 0), "end_time": time(15, 30), "class_id": None, "is_reading_time": True},
        ]
        
        for slot_data in schedule_data:
            slot = ScheduleSlot(**slot_data)
            db.add(slot)
        
        db.commit()
        
        # Create sample homework assignments
        homework_data = [
            {
                "title": "Algebra Practice Problems",
                "description": "Complete exercises 1-20 on page 85",
                "class_id": classes[0].id,  # Math
                "due_date": datetime.now() + timedelta(days=2),
                "priority": "medium"
            },
            {
                "title": "Essay on Shakespeare",
                "description": "Write a 500-word essay on Hamlet Act 1",
                "class_id": classes[1].id,  # English
                "due_date": datetime.now() + timedelta(days=5),
                "priority": "high"
            },
            {
                "title": "Chemistry Lab Report",
                "description": "Complete lab report for acid-base titration experiment",
                "class_id": classes[2].id,  # Chemistry
                "due_date": datetime.now() + timedelta(days=3),
                "priority": "high"
            },
            {
                "title": "History Timeline",
                "description": "Create timeline of WWI major events",
                "class_id": classes[3].id,  # History
                "due_date": datetime.now() + timedelta(days=7),
                "priority": "medium"
            },
            {
                "title": "Physics Problem Set",
                "description": "Solve problems on Newton's Laws (Chapter 4)",
                "class_id": classes[4].id,  # Physics
                "due_date": datetime.now() + timedelta(days=1),
                "priority": "high"
            }
        ]
        
        for hw_data in homework_data:
            homework = Homework(**hw_data)
            db.add(homework)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   Created {len(classes)} classes")
        print(f"   Created {len(schedule_data)} schedule slots")
        print(f"   Created {len(homework_data)} homework assignments")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()