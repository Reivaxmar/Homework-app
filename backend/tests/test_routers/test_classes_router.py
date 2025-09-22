"""
Tests for classes router.
"""
import pytest

def test_get_classes_empty(authenticated_user):
    """Test getting classes when user has none."""
    client, token_data = authenticated_user
    
    response = client.get("/api/classes/")
    assert response.status_code == 200
    
    data = response.json()
    assert data == []

def test_create_class(authenticated_user):
    """Test creating a new class."""
    client, token_data = authenticated_user
    
    class_data = {
        "name": "Mathematics",
        "teacher": "Dr. Smith",
        "year": "2024",
        "half_group": "A",
        "color": "#FF5733"
    }
    
    response = client.post("/api/classes/", json=class_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Mathematics"
    assert data["teacher"] == "Dr. Smith"
    assert data["year"] == "2024"
    assert data["half_group"] == "A"
    assert data["color"] == "#FF5733"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data

def test_create_class_minimal_data(authenticated_user):
    """Test creating a class with minimal required data."""
    client, token_data = authenticated_user
    
    class_data = {
        "name": "Physics",
        "teacher": "Dr. Johnson",
        "year": "2024"
    }
    
    response = client.post("/api/classes/", json=class_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Physics"
    assert data["teacher"] == "Dr. Johnson"
    assert data["year"] == "2024"
    assert data["color"] == "#3B82F6"  # Default color
    assert data["half_group"] is None  # Optional field

def test_create_class_validation_error(authenticated_user):
    """Test creating a class with invalid data."""
    client, token_data = authenticated_user
    
    # Missing required fields
    invalid_data = {
        "name": "Math"
        # Missing teacher and year
    }
    
    response = client.post("/api/classes/", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_get_classes_with_data(authenticated_user):
    """Test getting classes when user has classes."""
    client, token_data = authenticated_user
    
    # Create a few classes
    classes_data = [
        {"name": "Math", "teacher": "Dr. A", "year": "2024"},
        {"name": "Science", "teacher": "Dr. B", "year": "2024"},
    ]
    
    created_classes = []
    for class_data in classes_data:
        response = client.post("/api/classes/", json=class_data)
        assert response.status_code == 201
        created_classes.append(response.json())
    
    # Get all classes
    response = client.get("/api/classes/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Verify class names
    class_names = [c["name"] for c in data]
    assert "Math" in class_names
    assert "Science" in class_names

def test_get_specific_class(authenticated_user):
    """Test getting a specific class by ID."""
    client, token_data = authenticated_user
    
    # Create a class
    class_data = {
        "name": "History",
        "teacher": "Prof. Williams",
        "year": "2024"
    }
    
    create_response = client.post("/api/classes/", json=class_data)
    assert create_response.status_code == 201
    class_id = create_response.json()["id"]
    
    # Get the specific class
    response = client.get(f"/api/classes/{class_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == class_id
    assert data["name"] == "History"
    assert data["teacher"] == "Prof. Williams"

def test_get_nonexistent_class(authenticated_user):
    """Test getting a class that doesn't exist."""
    client, token_data = authenticated_user
    
    response = client.get("/api/classes/99999")
    assert response.status_code == 404

def test_update_class(authenticated_user):
    """Test updating a class."""
    client, token_data = authenticated_user
    
    # Create a class
    class_data = {
        "name": "Biology",
        "teacher": "Dr. Green",
        "year": "2024"
    }
    
    create_response = client.post("/api/classes/", json=class_data)
    assert create_response.status_code == 201
    class_id = create_response.json()["id"]
    
    # Update the class
    update_data = {
        "name": "Advanced Biology",
        "teacher": "Dr. Green Jr.",
        "color": "#00FF00"
    }
    
    response = client.put(f"/api/classes/{class_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Advanced Biology"
    assert data["teacher"] == "Dr. Green Jr."
    assert data["color"] == "#00FF00"
    assert data["year"] == "2024"  # Should remain unchanged

def test_update_nonexistent_class(authenticated_user):
    """Test updating a class that doesn't exist."""
    client, token_data = authenticated_user
    
    update_data = {"name": "Updated Name"}
    
    response = client.put("/api/classes/99999", json=update_data)
    assert response.status_code == 404

def test_delete_class(authenticated_user):
    """Test deleting a class."""
    client, token_data = authenticated_user
    
    # Create a class
    class_data = {
        "name": "Chemistry",
        "teacher": "Dr. Blue",
        "year": "2024"
    }
    
    create_response = client.post("/api/classes/", json=class_data)
    assert create_response.status_code == 201
    class_id = create_response.json()["id"]
    
    # Delete the class
    response = client.delete(f"/api/classes/{class_id}")
    assert response.status_code in [200, 204]  # Accept both OK and No Content
    
    # Verify it's deleted
    get_response = client.get(f"/api/classes/{class_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_class(authenticated_user):
    """Test deleting a class that doesn't exist."""
    client, token_data = authenticated_user
    
    response = client.delete("/api/classes/99999")
    assert response.status_code == 404

def test_user_isolation(client, db):
    """Test that users can only see their own classes."""
    # Create two users
    user1_response = client.post(
        "/api/auth/google/callback",
        params={"supabase_user_id": "user-1"},
        json={}
    )
    user1_token = user1_response.json()["access_token"]
    
    user2_response = client.post(
        "/api/auth/google/callback", 
        params={"supabase_user_id": "user-2"},
        json={}
    )
    user2_token = user2_response.json()["access_token"]
    
    # User 1 creates a class
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    class_data = {"name": "User1 Class", "teacher": "Teacher1", "year": "2024"}
    user1_class_response = client.post("/api/classes/", json=class_data)
    assert user1_class_response.status_code == 201
    user1_class_id = user1_class_response.json()["id"]
    
    # User 2 creates a class
    client.headers.update({"Authorization": f"Bearer {user2_token}"})
    class_data = {"name": "User2 Class", "teacher": "Teacher2", "year": "2024"}
    user2_class_response = client.post("/api/classes/", json=class_data)
    assert user2_class_response.status_code == 201
    user2_class_id = user2_class_response.json()["id"]
    
    # User 1 should only see their own class
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    user1_classes = client.get("/api/classes/").json()
    assert len(user1_classes) == 1
    assert user1_classes[0]["name"] == "User1 Class"
    
    # User 2 should only see their own class
    client.headers.update({"Authorization": f"Bearer {user2_token}"})
    user2_classes = client.get("/api/classes/").json()
    assert len(user2_classes) == 1
    assert user2_classes[0]["name"] == "User2 Class"
    
    # User 1 should not be able to access User 2's class
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    response = client.get(f"/api/classes/{user2_class_id}")
    assert response.status_code == 404

def test_get_classes_unauthorized(client):
    """Test accessing classes without authentication."""
    response = client.get("/api/classes/")
    assert response.status_code in [401, 403]

def test_classes_pagination(authenticated_user):
    """Test pagination of classes list."""
    client, token_data = authenticated_user
    
    # Create multiple classes
    for i in range(5):
        class_data = {
            "name": f"Class {i}",
            "teacher": f"Teacher {i}",
            "year": "2024"
        }
        response = client.post("/api/classes/", json=class_data)
        assert response.status_code == 201
    
    # Test pagination parameters
    response = client.get("/api/classes/?skip=2&limit=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2  # Should return 2 classes due to limit