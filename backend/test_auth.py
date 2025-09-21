#!/usr/bin/env python3
"""
Simple test script to verify JWT authentication is working.
Run this after starting the backend server to test the auth flow.

Usage:
    python test_auth.py

Requirements:
    - Backend server running on http://localhost:8000
    - requests library: pip install requests
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_auth():
    print("🧪 Testing JWT Authentication Setup")
    print("=" * 40)
    
    try:
        # Test 1: Health check
        print("1. Testing server connection...")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            raise Exception(f"Server health check failed: {response.status_code}")
        print("✅ Backend server is running")
        
        # Test 2: Protected endpoint without token
        print("\n2. Testing authentication requirement...")
        response = requests.get(f"{BASE_URL}/api/auth/me")
        if response.status_code not in [401, 403]:
            raise Exception(f"Expected 401/403, got {response.status_code}")
        print("✅ Protected endpoints require authentication")
        
        # Test 3: Create test user and get JWT token
        print("\n3. Testing JWT token generation...")
        response = requests.post(
            f"{BASE_URL}/api/auth/google/callback",
            params={"supabase_user_id": "test-user-12345"},
            json={}
        )
        if response.status_code != 200:
            raise Exception(f"Token generation failed: {response.status_code} - {response.text}")
        
        data = response.json()
        if "access_token" not in data:
            raise Exception("No access token in response")
        
        token = data["access_token"]
        print(f"✅ JWT token generated successfully")
        
        # Test 4: Use token to access protected endpoint
        print("\n4. Testing JWT token validation...")
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise Exception(f"Token validation failed: {response.status_code} - {response.text}")
        
        user_data = response.json()
        print(f"✅ Successfully authenticated as: {user_data.get('full_name', 'User')}")
        
        print("\n🎉 All authentication tests passed!")
        print("\nYour JWT authentication setup is working correctly.")
        print("Users should now be able to authenticate and access the API.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
        print("Start it with: cd backend && python run.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check that JWT_SECRET_KEY is set in backend/.env")
        print("2. Make sure you're not using the default JWT_SECRET_KEY")
        print("3. Verify the backend server started without errors")
        sys.exit(1)

if __name__ == "__main__":
    test_auth()