"""
API tests for classes endpoints.
"""

import pytest
from unittest.mock import patch
from fastapi import status


class TestClassesAPI:
    """Test classes API endpoints."""
    
    @patch('app.auth.get_current_user')
    def test_get_class_types(self, mock_get_current_user, client, mock_user):
        """Test getting available class types."""
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/classes/types")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        # Should contain class type enum values
        expected_types = ["MATH", "SCIENCE", "LANGUAGE", "HISTORY", "ART", "OTHER"]
        for class_type in expected_types:
            assert class_type in data
    
    @patch('app.auth.get_current_user')
    def test_get_classes_empty(self, mock_get_current_user, client, mock_user):
        """Test getting classes when user has none."""
        mock_get_current_user.return_value = mock_user
        
        response = client.get("/api/classes/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('app.auth.get_current_user')
    def test_get_classes_with_data(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test getting classes when user has classes."""
        mock_get_current_user.return_value = test_user
        
        response = client.get("/api/classes/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_class.id
        assert data[0]["name"] == test_class.name
        assert data[0]["teacher"] == test_class.teacher
        assert data[0]["color"] == test_class.color
    
    @patch('app.auth.get_current_user')
    def test_get_class_by_id(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test getting a specific class by ID."""
        mock_get_current_user.return_value = test_user
        
        response = client.get(f"/api/classes/{test_class.id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["id"] == test_class.id
        assert data["name"] == test_class.name
        assert data["teacher"] == test_class.teacher
        assert data["color"] == test_class.color
    
    @patch('app.auth.get_current_user')
    def test_get_class_not_found(self, mock_get_current_user, client, test_user):
        """Test getting a non-existent class."""
        mock_get_current_user.return_value = test_user
        
        response = client.get("/api/classes/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_get_class_different_user(self, mock_get_current_user, client, test_class, user_factory, test_session):
        """Test getting a class that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        response = client.get(f"/api/classes/{test_class.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_create_class(self, mock_get_current_user, client, test_user, test_session):
        """Test creating a new class."""
        mock_get_current_user.return_value = test_user
        
        class_data = {
            "name": "New Class",
            "teacher": "New Teacher",
            "color": "#ABCDEF"
        }
        
        response = client.post("/api/classes/", json=class_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == class_data["name"]
        assert data["teacher"] == class_data["teacher"]
        assert data["color"] == class_data["color"]
        assert data["user_id"] == test_user.id
        assert "id" in data
    
    @patch('app.auth.get_current_user')
    def test_create_class_with_all_fields(self, mock_get_current_user, client, test_user, test_session):
        """Test creating a class with all optional fields."""
        mock_get_current_user.return_value = test_user
        
        class_data = {
            "name": "Advanced Physics",
            "teacher": "Dr. Einstein",
            "color": "#FF00FF",
            "class_type": "SCIENCE",
            "group": "A",
            "year": 2024
        }
        
        response = client.post("/api/classes/", json=class_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["name"] == class_data["name"]
        assert data["teacher"] == class_data["teacher"]
        assert data["color"] == class_data["color"]
        assert data["class_type"] == class_data["class_type"]
        assert data["group"] == class_data["group"]
        assert data["year"] == class_data["year"]
    
    @patch('app.auth.get_current_user')
    def test_create_class_invalid_data(self, mock_get_current_user, client, test_user):
        """Test creating a class with invalid data."""
        mock_get_current_user.return_value = test_user
        
        # Missing required fields
        class_data = {
            "name": "Incomplete Class"
            # Missing teacher and color
        }
        
        response = client.post("/api/classes/", json=class_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('app.auth.get_current_user')
    def test_update_class(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test updating a class."""
        mock_get_current_user.return_value = test_user
        
        update_data = {
            "name": "Updated Class Name",
            "teacher": "Updated Teacher",
            "color": "#UPDATED"
        }
        
        response = client.put(f"/api/classes/{test_class.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["teacher"] == update_data["teacher"]
        assert data["color"] == update_data["color"]
        assert data["id"] == test_class.id
    
    @patch('app.auth.get_current_user')
    def test_update_class_not_found(self, mock_get_current_user, client, test_user):
        """Test updating a non-existent class."""
        mock_get_current_user.return_value = test_user
        
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put("/api/classes/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_update_class_different_user(self, mock_get_current_user, client, test_class, user_factory, test_session):
        """Test updating a class that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        update_data = {
            "name": "Hacked Name"
        }
        
        response = client.put(f"/api/classes/{test_class.id}", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_delete_class(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test deleting a class."""
        mock_get_current_user.return_value = test_user
        
        response = client.delete(f"/api/classes/{test_class.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify class is deleted
        response = client.get(f"/api/classes/{test_class.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_delete_class_not_found(self, mock_get_current_user, client, test_user):
        """Test deleting a non-existent class."""
        mock_get_current_user.return_value = test_user
        
        response = client.delete("/api/classes/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_delete_class_different_user(self, mock_get_current_user, client, test_class, user_factory, test_session):
        """Test deleting a class that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        response = client.delete(f"/api/classes/{test_class.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @patch('app.auth.get_current_user')
    def test_get_class_homework_empty(self, mock_get_current_user, client, test_user, test_class, test_session):
        """Test getting homework for a class with no homework."""
        mock_get_current_user.return_value = test_user
        
        response = client.get(f"/api/classes/{test_class.id}/homework")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('app.auth.get_current_user')
    def test_get_class_homework_with_data(self, mock_get_current_user, client, test_user, test_class, test_homework, test_session):
        """Test getting homework for a class with homework."""
        mock_get_current_user.return_value = test_user
        
        response = client.get(f"/api/classes/{test_class.id}/homework")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_homework.id
        assert data[0]["title"] == test_homework.title
        assert data[0]["class_id"] == test_class.id
    
    @patch('app.auth.get_current_user')
    def test_get_class_homework_different_user(self, mock_get_current_user, client, test_class, user_factory, test_session):
        """Test getting homework for a class that belongs to a different user."""
        # Create a different user
        different_user = user_factory.create(email="different@example.com")
        test_session.add(different_user)
        test_session.commit()
        test_session.refresh(different_user)
        
        mock_get_current_user.return_value = different_user
        
        response = client.get(f"/api/classes/{test_class.id}/homework")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_unauthenticated_requests(self, client):
        """Test that all endpoints require authentication."""
        endpoints = [
            ("GET", "/api/classes/types"),
            ("GET", "/api/classes/"),
            ("GET", "/api/classes/1"),
            ("POST", "/api/classes/"),
            ("PUT", "/api/classes/1"),
            ("DELETE", "/api/classes/1"),
            ("GET", "/api/classes/1/homework"),
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