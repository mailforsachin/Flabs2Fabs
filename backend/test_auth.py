#!/usr/bin/env python3
"""
Simple authentication test
"""

import requests
import json

BASE_URL = "http://localhost:8010"

def test_login():
    """Test login endpoint"""
    print("Testing login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "sashy", "password": "Welcome2026!"},
            timeout=10
        )
        print(f"Status code: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful! Token: {data.get('access_token', '')[:50]}...")
            return data.get('access_token')
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_progress_endpoint(token):
    """Test progress endpoint"""
    print("\nTesting progress endpoint...")
    if not token:
        print("❌ No token available")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/progress/test",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔐 Starting authentication test...")
    token = test_login()
    if token:
        test_progress_endpoint(token)
