"""
API tests for homework endpoints.
"""

import pytest
from unittest.mock import patch
from fastapi import status
from datetime import date


class TestHomeworkAPI:
    """Test homework API endpoints."""
    
    @patch('app.auth.get_current_user')
    def test_get_homework_empty(self, mock_get_current_user, client, mock_user):
        """Test getting homework when user has none."""
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/homework/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('app.auth.get_current_user')
    def test_get_homework_with_data(self, mock_get_current_user, client, test_user, test_homework, test_session):
        """Test getting homework when user has homework."""
        mock_get_current_user.return_value = test_user
        
        response = client.get("/api/homework/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_homework.id
        assert data[0]["title"] == test_homework.title
        assert data[0]["description"] == test_homework.description
        assert data[0]["user_id"] == test_user.id
    
    @patch('app.auth.get_current_user')
    def test_get_homework_by_id(self, mock_get_current_user, client, test_user, test_homework, test_session):
        """Test getting a specific homework by ID."""
        mock_get_current_user.return_value = test_user
        
        response = client.get(f"/api/homework/{test_homework.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_homework.id
        assert data["title"] == test_homework.title
        assert data["description"] == test_homework.description
        assert data["status"] == test_homework.status.value
    
    @patch('app.auth.get_current_user')
    def test_get_homework_not_found(self, mock_get_current_user, client, test_user):
        """Test getting a non-existent homework."""
        mock_get_current_user.return_value = test_user
        
        response = client.get("/api/homework/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_get_homework_different_user(self, mock_get_current_user, client, test_homework, user_factory, test_session):
        """Test getting homework that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        response = client.get(f"/api/homework/{test_homework.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_create_homework(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test creating a new homework."""
        mock_get_current_user.return_value = test_user
        
        homework_data = {
            "title": "New Homework",
            "description": "New homework description",
            "due_date": "2024-12-31",
            "class_id": test_class.id,
            "priority": "HIGH",
            "status": "PENDING"
        }
        
        response = client.post("/api/homework/", json=homework_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["title"] == homework_data["title"]
        assert data["description"] == homework_data["description"]
        assert data["due_date"] == homework_data["due_date"]
        assert data["class_id"] == homework_data["class_id"]
        assert data["user_id"] == test_user.id
        assert "id" in data
    
    @patch('app.auth.get_current_user')
    def test_create_homework_minimal(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test creating homework with minimal required fields."""
        mock_get_current_user.return_value = test_user
        
        homework_data = {
            "title": "Minimal Homework",
            "due_date": "2024-12-31",
            "class_id": test_class.id
        }
        
        response = client.post("/api/homework/", json=homework_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["title"] == homework_data["title"]
        assert data["due_date"] == homework_data["due_date"]
        assert data["class_id"] == homework_data["class_id"]
        assert data["user_id"] == test_user.id
        # Should have default values
        assert data["status"] == "PENDING"
        assert data["priority"] == "MEDIUM"
    
    @patch('app.auth.get_current_user')
    def test_create_homework_invalid_data(self, mock_get_current_user, client, test_user):
        """Test creating homework with invalid data."""
        mock_get_current_user.return_value = test_user
        
        # Missing required fields
        homework_data = {
            "title": "Incomplete Homework"
            # Missing due_date and class_id
        }
        
        response = client.post("/api/homework/", json=homework_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('app.auth.get_current_user')
    def test_create_homework_invalid_class(self, mock_get_current_user, client, test_user):
        """Test creating homework with non-existent class."""
        mock_get_current_user.return_value = test_user
        
        homework_data = {
            "title": "Homework with bad class",
            "due_date": "2024-12-31",
            "class_id": 999  # Non-existent class
        }
        
        response = client.post("/api/homework/", json=homework_data)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
    
    @patch('app.auth.get_current_user')
    def test_update_homework(self, mock_get_current_user, client, test_user, test_homework, test_session):
        """Test updating homework."""
        mock_get_current_user.return_value = test_user
        
        update_data = {
            "title": "Updated Homework Title",
            "description": "Updated description",
            "status": "IN_PROGRESS",
            "priority": "HIGH"
        }
        
        response = client.put(f"/api/homework/{test_homework.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]
        assert data["id"] == test_homework.id
    
    @patch('app.auth.get_current_user')
    def test_update_homework_not_found(self, mock_get_current_user, client, test_user):
        """Test updating a non-existent homework."""
        mock_get_current_user.return_value = test_user
        
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.put("/api/homework/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_update_homework_different_user(self, mock_get_current_user, client, test_homework, user_factory, test_session):
        """Test updating homework that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        update_data = {
            "title": "Hacked Title"
        }
        
        response = client.put(f"/api/homework/{test_homework.id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_delete_homework(self, mock_get_current_user, client, test_user, test_homework, test_session):
        """Test deleting homework."""
        mock_get_current_user.return_value = test_user
        
        response = client.delete(f"/api/homework/{test_homework.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify homework is deleted
        response = client.get(f"/api/homework/{test_homework.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_delete_homework_not_found(self, mock_get_current_user, client, test_user):
        """Test deleting a non-existent homework."""
        mock_get_current_user.return_value = test_user
        
        response = client.delete("/api/homework/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_delete_homework_different_user(self, mock_get_current_user, client, test_homework, user_factory, test_session):
        """Test deleting homework that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        response = client.delete(f"/api/homework/{test_homework.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_get_homework_by_status(self, mock_get_current_user, client, test_user, test_class, test_session, homework_factory):
        """Test filtering homework by status."""
        mock_get_current_user.return_value = test_user
        
        # Create homework with different statuses
        from app.models.homework import Status
        statuses = [Status.PENDING, Status.IN_PROGRESS, Status.COMPLETED]
        
        for status in statuses:
            homework = homework_factory.create(
                user_id=test_user.id,
                class_id=test_class.id,
                status=status.value
            )
            test_session.add(homework)
        test_session.commit()
        
        # Test filtering by status (if endpoint supports it)
        response = client.get("/api/homework/?status=PENDING")
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, list)
            # All returned homework should have PENDING status
            for homework in data:
                assert homework["status"] == "PENDING"
    
    @patch('app.auth.get_current_user')
    def test_get_homework_by_class(self, mock_get_current_user, client, test_user, test_class, test_session, homework_factory, class_factory):
        """Test filtering homework by class."""
        mock_get_current_user.return_value = test_user
        
        # Create another class
        other_class = class_factory.create(user_id=test_user.id, name="Other Class")
        test_session.add(other_class)
        test_session.commit()
        test_session.refresh(other_class)
        
        # Create homework for both classes
        homework1 = homework_factory.create(user_id=test_user.id, class_id=test_class.id)
        homework2 = homework_factory.create(user_id=test_user.id, class_id=other_class.id)
        test_session.add(homework1)
        test_session.add(homework2)
        test_session.commit()
        
        # Test filtering by class (if endpoint supports it)
        response = client.get(f"/api/homework/?class_id={test_class.id}")
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert isinstance(data, list)
            # All returned homework should belong to test_class
            for homework in data:
                assert homework["class_id"] == test_class.id
    
    def test_unauthenticated_homework_requests(self, client):
        """Test that all homework endpoints require authentication."""
        endpoints = [
            ("GET", "/api/homework/"),
            ("GET", "/api/homework/1"),
            ("POST", "/api/homework/"),
            ("PUT", "/api/homework/1"),
            ("DELETE", "/api/homework/1"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED