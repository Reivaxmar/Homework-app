"""
Integration tests for complete user workflows.
These tests verify that different parts of the application work together correctly.
"""

import pytest
from fastapi import status
from unittest.mock import patch


class TestUserWorkflows:
    """Test complete user workflows from start to finish."""
    
    @patch('app.auth.supabase')
    @patch('app.services.google_calendar.GoogleCalendarService')
    def test_complete_homework_workflow(self, mock_calendar_service, mock_supabase, 
                                       client, test_session, user_factory, class_factory):
        """Test complete workflow: auth -> create class -> create homework -> sync to calendar."""
        
        # Step 1: Authentication
        mock_user_data = {
            "user": {
                "id": "supabase-user-123",
                "email": "test@example.com",
                "user_metadata": {"full_name": "Test User"}
            }
        }
        mock_supabase.auth.get_user.return_value = type('obj', (object,), mock_user_data)
        
        # Mock session
        mock_session = type('obj', (object,), {
            "access_token": "mock_token",
            "refresh_token": "mock_refresh",
            "provider_token": "google_token",
            "provider_refresh_token": "google_refresh"
        })
        mock_supabase.auth.get_session.return_value = mock_session
        
        # Authenticate user
        auth_response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "supabase-user-123"}
        )
        assert auth_response.status_code == status.HTTP_200_OK
        
        auth_data = auth_response.json()
        access_token = auth_data["access_token"]
        user_id = auth_data["user"]["id"]
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Step 2: Create a class
        class_data = {
            "name": "Integration Test Class",
            "teacher": "Test Teacher",
            "year": "2024",
            "color": "#FF5733"
        }
        
        class_response = client.post("/api/classes/", json=class_data, headers=headers)
        assert class_response.status_code == status.HTTP_201_CREATED
        
        class_info = class_response.json()
        class_id = class_info["id"]
        
        # Step 3: Create homework for the class
        homework_data = {
            "title": "Integration Test Homework",
            "description": "Test homework for integration workflow",
            "due_date": "2024-12-31",
            "class_id": class_id,
            "priority": "HIGH"
        }
        
        homework_response = client.post("/api/homework/", json=homework_data, headers=headers)
        assert homework_response.status_code == status.HTTP_201_CREATED
        
        homework_info = homework_response.json()
        homework_id = homework_info["id"]
        
        # Step 4: Sync homework to Google Calendar
        mock_service_instance = mock_calendar_service.return_value
        mock_service_instance.create_homework_event.return_value = "calendar_event_123"
        
        sync_response = client.post(f"/api/calendar/sync/{homework_id}", headers=headers)
        assert sync_response.status_code == status.HTTP_200_OK
        
        sync_data = sync_response.json()
        assert sync_data["success"] is True
        assert sync_data["homework_id"] == homework_id
        
        # Step 5: Verify homework was updated with calendar event ID
        homework_get_response = client.get(f"/api/homework/{homework_id}", headers=headers)
        assert homework_get_response.status_code == status.HTTP_200_OK
        
        updated_homework = homework_get_response.json()
        assert updated_homework["google_calendar_event_id"] == "calendar_event_123"
        
        # Step 6: Update homework status
        status_update = {"status": "COMPLETED"}
        update_response = client.put(f"/api/homework/{homework_id}", json=status_update, headers=headers)
        assert update_response.status_code == status.HTTP_200_OK
        
        final_homework = update_response.json()
        assert final_homework["status"] == "COMPLETED"
    
    @patch('app.auth.supabase')
    def test_class_management_workflow(self, mock_supabase, client, test_session):
        """Test complete class management workflow."""
        
        # Setup authentication
        mock_user_data = {
            "user": {
                "id": "supabase-user-456",
                "email": "teacher@example.com",
                "user_metadata": {"full_name": "Teacher User"}
            }
        }
        mock_supabase.auth.get_user.return_value = type('obj', (object,), mock_user_data)
        
        mock_session = type('obj', (object,), {
            "access_token": "mock_token",
            "refresh_token": "mock_refresh",
            "provider_token": "google_token",
            "provider_refresh_token": "google_refresh"
        })
        mock_supabase.auth.get_session.return_value = mock_session
        
        # Authenticate
        auth_response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "supabase-user-456"}
        )
        assert auth_response.status_code == status.HTTP_200_OK
        
        headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
        
        # Create multiple classes
        classes_data = [
            {"name": "Mathematics", "teacher": "Dr. Math", "year": "2024", "color": "#FF0000"},
            {"name": "Physics", "teacher": "Dr. Physics", "year": "2024", "color": "#00FF00"},
            {"name": "Chemistry", "teacher": "Dr. Chemistry", "year": "2024", "color": "#0000FF"}
        ]
        
        created_classes = []
        for class_data in classes_data:
            response = client.post("/api/classes/", json=class_data, headers=headers)
            assert response.status_code == status.HTTP_201_CREATED
            created_classes.append(response.json())
        
        # Get all classes
        get_response = client.get("/api/classes/", headers=headers)
        assert get_response.status_code == status.HTTP_200_OK
        
        all_classes = get_response.json()
        assert len(all_classes) == 3
        
        # Update a class
        class_to_update = created_classes[0]
        update_data = {"name": "Advanced Mathematics", "color": "#FF00FF"}
        
        update_response = client.put(
            f"/api/classes/{class_to_update['id']}", 
            json=update_data, 
            headers=headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        updated_class = update_response.json()
        assert updated_class["name"] == "Advanced Mathematics"
        assert updated_class["color"] == "#FF00FF"
        
        # Delete a class
        class_to_delete = created_classes[1]
        delete_response = client.delete(f"/api/classes/{class_to_delete['id']}", headers=headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        get_deleted_response = client.get(f"/api/classes/{class_to_delete['id']}", headers=headers)
        assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND
        
        # Final verification - should have 2 classes left
        final_get_response = client.get("/api/classes/", headers=headers)
        final_classes = final_get_response.json()
        assert len(final_classes) == 2
    
    @patch('app.auth.supabase')
    def test_user_isolation_workflow(self, mock_supabase, client, test_session):
        """Test that users can only access their own data."""
        
        # Create first user
        mock_supabase.auth.get_user.return_value = type('obj', (object,), {
            "user": {
                "id": "user-1",
                "email": "user1@example.com",
                "user_metadata": {"full_name": "User One"}
            }
        })
        
        mock_supabase.auth.get_session.return_value = type('obj', (object,), {
            "access_token": "token1",
            "refresh_token": "refresh1",
            "provider_token": "google1",
            "provider_refresh_token": "google_refresh1"
        })
        
        # Authenticate first user
        auth1_response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "user-1"}
        )
        user1_token = auth1_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        # Create class for first user
        class_response = client.post(
            "/api/classes/",
            json={"name": "User1 Class", "teacher": "Teacher1", "year": "2024", "color": "#FF0000"},
            headers=user1_headers
        )
        user1_class_id = class_response.json()["id"]
        
        # Create second user
        mock_supabase.auth.get_user.return_value = type('obj', (object,), {
            "user": {
                "id": "user-2",
                "email": "user2@example.com",
                "user_metadata": {"full_name": "User Two"}
            }
        })
        
        mock_supabase.auth.get_session.return_value = type('obj', (object,), {
            "access_token": "token2",
            "refresh_token": "refresh2",
            "provider_token": "google2",
            "provider_refresh_token": "google_refresh2"
        })
        
        # Authenticate second user
        auth2_response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "user-2"}
        )
        user2_token = auth2_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User 2 should not see User 1's class
        get_classes_response = client.get("/api/classes/", headers=user2_headers)
        user2_classes = get_classes_response.json()
        assert len(user2_classes) == 0
        
        # User 2 should not be able to access User 1's class
        access_response = client.get(f"/api/classes/{user1_class_id}", headers=user2_headers)
        assert access_response.status_code == status.HTTP_404_NOT_FOUND
        
        # User 2 should not be able to modify User 1's class
        modify_response = client.put(
            f"/api/classes/{user1_class_id}",
            json={"name": "Hacked Class"},
            headers=user2_headers
        )
        assert modify_response.status_code == status.HTTP_404_NOT_FOUND
        
        # User 2 should not be able to delete User 1's class
        delete_response = client.delete(f"/api/classes/{user1_class_id}", headers=user2_headers)
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND
        
        # User 1 should still have access to their class
        user1_access_response = client.get(f"/api/classes/{user1_class_id}", headers=user1_headers)
        assert user1_access_response.status_code == status.HTTP_200_OK


class TestErrorHandling:
    """Test error handling in workflows."""
    
    def test_unauthenticated_access(self, client):
        """Test that unauthenticated requests are properly rejected."""
        endpoints = [
            ("GET", "/api/classes/"),
            ("POST", "/api/classes/"),
            ("GET", "/api/homework/"),
            ("POST", "/api/homework/"),
            ("POST", "/api/calendar/sync"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @patch('app.auth.supabase')
    def test_invalid_data_handling(self, mock_supabase, client):
        """Test handling of invalid data in requests."""
        
        # Setup authentication
        mock_supabase.auth.get_user.return_value = type('obj', (object,), {
            "user": {
                "id": "test-user",
                "email": "test@example.com",
                "user_metadata": {"full_name": "Test User"}
            }
        })
        
        mock_supabase.auth.get_session.return_value = type('obj', (object,), {
            "access_token": "mock_token",
            "refresh_token": "mock_refresh",
            "provider_token": "google_token",
            "provider_refresh_token": "google_refresh"
        })
        
        auth_response = client.post(
            "/api/auth/google/callback",
            params={"supabase_user_id": "test-user"}
        )
        headers = {"Authorization": f"Bearer {auth_response.json()['access_token']}"}
        
        # Test invalid class data
        invalid_class_data = [
            {},  # Missing required fields
            {"name": "Test"},  # Missing teacher, year, color
            {"name": "", "teacher": "Teacher", "year": "2024", "color": "#FF0000"},  # Empty name
            {"name": "Test", "teacher": "", "year": "2024", "color": "#FF0000"},  # Empty teacher
        ]
        
        for invalid_data in invalid_class_data:
            response = client.post("/api/classes/", json=invalid_data, headers=headers)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test invalid homework data
        invalid_homework_data = [
            {},  # Missing required fields
            {"title": "Test"},  # Missing due_date, class_id
            {"title": "", "due_date": "2024-12-31", "class_id": 1},  # Empty title
            {"title": "Test", "due_date": "invalid-date", "class_id": 1},  # Invalid date
        ]
        
        for invalid_data in invalid_homework_data:
            response = client.post("/api/homework/", json=invalid_data, headers=headers)
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_400_BAD_REQUEST
            ]