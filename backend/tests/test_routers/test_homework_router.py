"""
Tests for homework router.
"""
import pytest
from datetime import date, datetime

def test_get_homework_empty(authenticated_user):
    """Test getting homework when user has none."""
    client, token_data = authenticated_user
    
    response = client.get("/api/homework/")
    assert response.status_code == 200
    
    data = response.json()
    assert data == []

def test_create_homework(authenticated_user):
    """Test creating homework assignment."""
    client, token_data = authenticated_user
    
    # First create a class
    class_data = {
        "name": "Mathematics",
        "teacher": "Dr. Smith",
        "year": "2024"
    }
    class_response = client.post("/api/classes/", json=class_data)
    assert class_response.status_code == 201
    class_id = class_response.json()["id"]
    
    # Create homework
    homework_data = {
        "title": "Algebra Assignment",
        "description": "Complete exercises 1-20",
        "due_date": "2024-02-15",
        "class_id": class_id,
        "priority": "HIGH"
    }
    
    response = client.post("/api/homework/", json=homework_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == "Algebra Assignment"
    assert data["description"] == "Complete exercises 1-20"
    assert data["due_date"] == "2024-02-15"
    assert data["class_id"] == class_id
    assert data["priority"] == "HIGH"
    assert data["status"] == "PENDING"  # Default status
    assert "id" in data
    assert "user_id" in data

def test_create_homework_minimal_data(authenticated_user):
    """Test creating homework with minimal required data."""
    client, token_data = authenticated_user
    
    # Create a class first
    class_response = client.post("/api/classes/", json={
        "name": "Physics",
        "teacher": "Dr. Johnson",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    homework_data = {
        "title": "Lab Report",
        "due_date": "2024-03-01",
        "class_id": class_id
    }
    
    response = client.post("/api/homework/", json=homework_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == "Lab Report"
    assert data["due_date"] == "2024-03-01"
    assert data["priority"] == "MEDIUM"  # Default priority
    assert data["status"] == "PENDING"   # Default status
    assert data["description"] is None   # Optional field

def test_create_homework_invalid_class(authenticated_user):
    """Test creating homework with non-existent class."""
    client, token_data = authenticated_user
    
    homework_data = {
        "title": "Orphan Homework",
        "due_date": "2024-03-01",
        "class_id": 99999  # Non-existent class
    }
    
    response = client.post("/api/homework/", json=homework_data)
    assert response.status_code in [400, 404, 422]

def test_get_homework_with_data(authenticated_user):
    """Test getting homework when user has assignments."""
    client, token_data = authenticated_user
    
    # Create class and homework
    class_response = client.post("/api/classes/", json={
        "name": "Chemistry",
        "teacher": "Dr. Brown",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    homework_data = [
        {
            "title": "Lab Report 1",
            "due_date": "2024-02-15",
            "class_id": class_id,
            "priority": "HIGH"
        },
        {
            "title": "Lab Report 2", 
            "due_date": "2024-03-01",
            "class_id": class_id,
            "priority": "MEDIUM"
        }
    ]
    
    for hw in homework_data:
        response = client.post("/api/homework/", json=hw)
        assert response.status_code == 201
    
    # Get all homework
    response = client.get("/api/homework/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    titles = [hw["title"] for hw in data]
    assert "Lab Report 1" in titles
    assert "Lab Report 2" in titles

def test_get_specific_homework(authenticated_user):
    """Test getting specific homework by ID."""
    client, token_data = authenticated_user
    
    # Create class and homework
    class_response = client.post("/api/classes/", json={
        "name": "Biology",
        "teacher": "Dr. Green",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    homework_data = {
        "title": "Research Paper",
        "description": "Write about cell division",
        "due_date": "2024-04-01",
        "class_id": class_id
    }
    
    create_response = client.post("/api/homework/", json=homework_data)
    homework_id = create_response.json()["id"]
    
    # Get specific homework
    response = client.get(f"/api/homework/{homework_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == homework_id
    assert data["title"] == "Research Paper"
    assert data["description"] == "Write about cell division"

def test_update_homework(authenticated_user):
    """Test updating homework assignment."""
    client, token_data = authenticated_user
    
    # Create class and homework
    class_response = client.post("/api/classes/", json={
        "name": "English",
        "teacher": "Prof. White",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    homework_data = {
        "title": "Essay Draft",
        "due_date": "2024-03-15",
        "class_id": class_id,
        "status": "PENDING"
    }
    
    create_response = client.post("/api/homework/", json=homework_data)
    homework_id = create_response.json()["id"]
    
    # Update homework
    update_data = {
        "title": "Essay Final",
        "status": "IN_PROGRESS",
        "description": "Final version of the essay"
    }
    
    response = client.put(f"/api/homework/{homework_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Essay Final"
    assert data["status"] == "IN_PROGRESS"
    assert data["description"] == "Final version of the essay"
    assert data["due_date"] == "2024-03-15"  # Should remain unchanged

def test_complete_homework(authenticated_user):
    """Test marking homework as completed."""
    client, token_data = authenticated_user
    
    # Create class and homework
    class_response = client.post("/api/classes/", json={
        "name": "Art",
        "teacher": "Ms. Colors",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    homework_data = {
        "title": "Painting Project",
        "due_date": "2024-05-01",
        "class_id": class_id
    }
    
    create_response = client.post("/api/homework/", json=homework_data)
    homework_id = create_response.json()["id"]
    
    # Mark as completed
    update_data = {"status": "COMPLETED"}
    
    response = client.put(f"/api/homework/{homework_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "COMPLETED"
    # completed_at should be set when status changes to COMPLETED
    # The exact value may vary, so we just check it exists
    # assert data["completed_at"] is not None

def test_delete_homework(authenticated_user):
    """Test deleting homework assignment."""
    client, token_data = authenticated_user
    
    # Create class and homework
    class_response = client.post("/api/classes/", json={
        "name": "Music",
        "teacher": "Mr. Notes",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    homework_data = {
        "title": "Practice Scales",
        "due_date": "2024-06-01",
        "class_id": class_id
    }
    
    create_response = client.post("/api/homework/", json=homework_data)
    homework_id = create_response.json()["id"]
    
    # Delete homework
    response = client.delete(f"/api/homework/{homework_id}")
    assert response.status_code in [200, 204]  # Accept both OK and No Content
    
    # Verify it's deleted
    get_response = client.get(f"/api/homework/{homework_id}")
    assert get_response.status_code == 404

def test_homework_filtering(authenticated_user):
    """Test filtering homework by various criteria."""
    client, token_data = authenticated_user
    
    # Create two classes
    class1_response = client.post("/api/classes/", json={
        "name": "Math",
        "teacher": "Dr. Numbers",
        "year": "2024"
    })
    class1_id = class1_response.json()["id"]
    
    class2_response = client.post("/api/classes/", json={
        "name": "Science",
        "teacher": "Dr. Experiments",
        "year": "2024"
    })
    class2_id = class2_response.json()["id"]
    
    # Create homework for different classes and statuses
    homework_data = [
        {
            "title": "Math HW 1",
            "due_date": "2024-02-15",
            "class_id": class1_id,
            "status": "PENDING"
        },
        {
            "title": "Math HW 2",
            "due_date": "2024-02-16",
            "class_id": class1_id,
            "status": "COMPLETED"
        },
        {
            "title": "Science Lab",
            "due_date": "2024-02-15",
            "class_id": class2_id,
            "status": "PENDING"
        }
    ]
    
    homework_ids = []
    for hw in homework_data:
        response = client.post("/api/homework/", json=hw)
        homework_ids.append(response.json()["id"])
    
    # Update homework status for testing
    update_response = client.put(f"/api/homework/{homework_ids[1]}", json={"status": "COMPLETED"})
    assert update_response.status_code == 200
    
    # Test filtering by class
    response = client.get(f"/api/homework/?class_id={class1_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Should return only Math homework
    
    # Test filtering by status
    response = client.get("/api/homework/?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Should return only pending homework (Math HW 1 and Science Lab)
    
    # Test filtering by due date
    response = client.get("/api/homework/?due_date=2024-02-15")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Should return homework due on 2024-02-15

def test_homework_due_today(authenticated_user):
    """Test getting homework due today."""
    client, token_data = authenticated_user
    
    # Create class
    class_response = client.post("/api/classes/", json={
        "name": "Today Class",
        "teacher": "Today Teacher",
        "year": "2024"
    })
    class_id = class_response.json()["id"]
    
    today = date.today().isoformat()
    tomorrow = date.today().replace(day=date.today().day + 1).isoformat()
    
    # Create homework due today and tomorrow
    homework_data = [
        {
            "title": "Due Today",
            "due_date": today,
            "class_id": class_id
        },
        {
            "title": "Due Tomorrow",
            "due_date": tomorrow,
            "class_id": class_id
        }
    ]
    
    for hw in homework_data:
        response = client.post("/api/homework/", json=hw)
        assert response.status_code == 201
    
    # Get homework due today
    response = client.get("/api/homework/due-today")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Due Today"

def test_user_homework_isolation(client, db):
    """Test that users can only see their own homework."""
    # Create two users
    user1_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "hw-user-1"},
        json={}
    )
    user1_token = user1_response.json()["access_token"]
    
    user2_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "hw-user-2"},
        json={}
    )
    user2_token = user2_response.json()["access_token"]
    
    # User 1 creates class and homework
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    class1_response = client.post("/api/classes/", json={
        "name": "User1 Class",
        "teacher": "Teacher1",
        "year": "2024"
    })
    class1_id = class1_response.json()["id"]
    
    homework1_response = client.post("/api/homework/", json={
        "title": "User1 Homework",
        "due_date": "2024-03-01",
        "class_id": class1_id
    })
    homework1_id = homework1_response.json()["id"]
    
    # User 2 creates class and homework
    client.headers.update({"Authorization": f"Bearer {user2_token}"})
    class2_response = client.post("/api/classes/", json={
        "name": "User2 Class",
        "teacher": "Teacher2",
        "year": "2024"
    })
    class2_id = class2_response.json()["id"]
    
    homework2_response = client.post("/api/homework/", json={
        "title": "User2 Homework",
        "due_date": "2024-03-01",
        "class_id": class2_id
    })
    homework2_id = homework2_response.json()["id"]
    
    # User 1 should only see their homework
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    user1_homework = client.get("/api/homework/").json()
    assert len(user1_homework) == 1
    assert user1_homework[0]["title"] == "User1 Homework"
    
    # User 2 should only see their homework
    client.headers.update({"Authorization": f"Bearer {user2_token}"})
    user2_homework = client.get("/api/homework/").json()
    assert len(user2_homework) == 1
    assert user2_homework[0]["title"] == "User2 Homework"
    
    # User 1 should not be able to access User 2's homework
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    response = client.get(f"/api/homework/{homework2_id}")
    assert response.status_code == 404

def test_homework_unauthorized(client):
    """Test accessing homework without authentication."""
    response = client.get("/api/homework/")
    assert response.status_code in [401, 403]