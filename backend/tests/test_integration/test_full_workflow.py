"""
Integration tests for complete user workflows.
"""
import pytest
from datetime import date

def test_complete_homework_workflow(client, db):
    """Test complete workflow: auth -> create class -> create homework -> complete homework."""
    
    # 1. Authenticate user
    auth_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "integration-test-user"},
        json={}
    )
    assert auth_response.status_code == 200
    auth_data = auth_response.json()
    
    # Set auth token for subsequent requests
    token = auth_data["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 2. Create a class
    class_data = {
        "name": "Mathematics",
        "teacher": "Dr. Smith", 
        "year": "2024",
        "color": "#FF5733"
    }
    
    class_response = client.post("/api/classes/", json=class_data)
    assert class_response.status_code == 200
    class_info = class_response.json()
    class_id = class_info["id"]
    
    # 3. Create homework assignment
    homework_data = {
        "title": "Algebra Assignment",
        "description": "Complete exercises 1-20",
        "due_date": "2024-02-15",
        "class_id": class_id,
        "priority": "HIGH"
    }
    
    homework_response = client.post("/api/homework/", json=homework_data)
    assert homework_response.status_code == 200
    homework_info = homework_response.json()
    homework_id = homework_info["id"]
    
    # 4. Verify homework was created correctly
    assert homework_info["title"] == "Algebra Assignment"
    assert homework_info["class_id"] == class_id
    assert homework_info["status"] == "PENDING"
    
    # 5. Update homework status to in progress
    update_data = {"status": "IN_PROGRESS"}
    update_response = client.put(f"/api/homework/{homework_id}", json=update_data)
    assert update_response.status_code == 200
    updated_homework = update_response.json()
    assert updated_homework["status"] == "IN_PROGRESS"
    
    # 6. Complete the homework
    complete_data = {"status": "COMPLETED"}
    complete_response = client.put(f"/api/homework/{homework_id}", json=complete_data)
    assert complete_response.status_code == 200
    completed_homework = complete_response.json()
    assert completed_homework["status"] == "COMPLETED"
    
    # 7. Verify dashboard shows the completed homework
    dashboard_response = client.get("/api/dashboard/")
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.json()
    
    # Should have homework statistics
    assert "total_homework" in dashboard_data
    assert "completed_homework" in dashboard_data
    assert dashboard_data["completed_homework"] >= 1

def test_class_schedule_workflow(client, db):
    """Test workflow: auth -> create class -> create schedule -> add slots."""
    
    # 1. Authenticate
    auth_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "schedule-test-user"},
        json={}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 2. Create a class
    class_data = {
        "name": "Physics",
        "teacher": "Dr. Johnson",
        "year": "2024"
    }
    
    class_response = client.post("/api/classes/", json=class_data)
    assert class_response.status_code == 200
    class_info = class_response.json()
    
    # 3. Create a schedule
    schedule_data = {
        "name": "Spring 2024",
        "year": "2024"
    }
    
    schedule_response = client.post("/api/schedules/", json=schedule_data)
    assert schedule_response.status_code == 200
    schedule_info = schedule_response.json()
    
    # 4. Add schedule slots
    slot_data = {
        "class_id": class_info["id"],
        "day": "MONDAY",
        "slot_number": 1,
        "start_time": "09:00",
        "end_time": "10:30"
    }
    
    slot_response = client.post(f"/api/schedules/{schedule_info['id']}/slots", json=slot_data)
    assert slot_response.status_code == 200
    slot_info = slot_response.json()
    
    # 5. Verify schedule was created properly
    get_schedule_response = client.get(f"/api/schedules/{schedule_info['id']}")
    assert get_schedule_response.status_code == 200
    schedule_detail = get_schedule_response.json()
    
    assert len(schedule_detail["slots"]) == 1
    assert schedule_detail["slots"][0]["day"] == "MONDAY"

def test_user_profile_and_data_workflow(client, db):
    """Test user profile management and data consistency."""
    
    # 1. Create user through auth
    auth_response = client.post(
        "/api/auth/google/callback", 
        params={"supabase_user_id": "profile-test-user"},
        json={}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 2. Get user profile
    profile_response = client.get("/api/auth/me")
    assert profile_response.status_code == 200
    profile = profile_response.json()
    user_id = profile["id"]
    
    # 3. Update user profile
    update_data = {
        "full_name": "Updated Test User",
        "avatar_url": "https://example.com/new-avatar.jpg"
    }
    
    update_response = client.put("/api/auth/me", json=update_data)
    assert update_response.status_code == 200
    updated_profile = update_response.json()
    assert updated_profile["full_name"] == "Updated Test User"
    
    # 4. Create some data for the user
    class_response = client.post("/api/classes/", json={
        "name": "Chemistry",
        "teacher": "Dr. Brown",
        "year": "2024"
    })
    assert class_response.status_code == 200
    
    homework_response = client.post("/api/homework/", json={
        "title": "Lab Report",
        "due_date": "2024-03-01",
        "class_id": class_response.json()["id"]
    })
    assert homework_response.status_code == 200
    
    # 5. Verify data ownership
    classes_response = client.get("/api/classes/")
    assert classes_response.status_code == 200
    classes = classes_response.json()
    assert len(classes) == 1
    assert classes[0]["user_id"] == user_id
    
    homework_response = client.get("/api/homework/")
    assert homework_response.status_code == 200
    homework_list = homework_response.json()
    assert len(homework_list) == 1
    assert homework_list[0]["user_id"] == user_id

def test_error_handling_workflow(client, db):
    """Test error handling in various scenarios."""
    
    # 1. Try to access protected endpoint without auth
    no_auth_response = client.get("/api/auth/me")
    assert no_auth_response.status_code in [401, 403]
    
    # 2. Authenticate user
    auth_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "error-test-user"},
        json={}
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # 3. Try to create homework without class
    invalid_homework = {
        "title": "Orphan Homework",
        "due_date": "2024-03-01",
        "class_id": 99999  # Non-existent class
    }
    
    homework_response = client.post("/api/homework/", json=invalid_homework)
    assert homework_response.status_code in [400, 404, 422]
    
    # 4. Try to access someone else's data (should be filtered out)
    # First create a class
    class_response = client.post("/api/classes/", json={
        "name": "My Class",
        "teacher": "My Teacher",
        "year": "2024"
    })
    assert class_response.status_code == 200
    class_id = class_response.json()["id"]
    
    # Try to update with invalid data
    invalid_update = {"class_id": "not-a-number"}
    update_response = client.put(f"/api/classes/{class_id}", json=invalid_update)
    assert update_response.status_code in [400, 422]
    
    # 5. Try to delete non-existent resource
    delete_response = client.delete("/api/homework/99999")
    assert delete_response.status_code in [404, 422]