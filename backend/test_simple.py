#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("Testing server connectivity...")

# Test root endpoint first
try:
    print("1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! {data.get('message')}")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test health endpoint
try:
    print("\n2. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test authentication
try:
    print("\n3. Testing authentication...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "sashy", "password": "Welcome2026!"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"   ✅ Authentication successful!")
        print(f"   Token preview: {token[:50]}...")
        
        # Now test a progress endpoint
        print("\n4. Testing progress endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/progress/strength-projections?days_back=30",
            headers=headers,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Progress endpoint working!")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Data quality: {data.get('data_quality')}")
        else:
            print(f"   Response: {response.text[:200]}")
    else:
        print(f"   ❌ Authentication failed: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*50)
print("Test completed!")
