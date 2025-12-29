#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8008"

print("🔧 Testing Phase D Progress Endpoint Fix")
print("=" * 50)

# 1. Get token
print("\n1. Getting token...")
try:
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "sashy", "password": "Welcome2026!"},
        timeout=5
    )
    if resp.status_code == 200:
        token = resp.json().get('access_token')
        print(f"✅ Token: {token[:50]}...")
    else:
        print(f"❌ Login failed: {resp.status_code}")
        print(f"Response: {resp.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 2. Test ALL Phase D endpoints
print("\n2. Testing Phase D endpoints...")
headers = {"Authorization": f"Bearer {token}"}

endpoints = [
    "/api/progress/strength-projections?days_back=30",
    "/api/progress/consistency-projections?days_back=30",
    "/api/progress/comprehensive-report?days_back=90",
    "/api/progress/motivational-insights?days_back=30",
    "/api/progress/missed-opportunities?days_back=30",
]

for endpoint in endpoints:
    print(f"\n🔍 Testing: {endpoint}")
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"   ✅ Success!")
            data = resp.json()
            if "user_id" in data:
                print(f"   User ID: {data['user_id']}")
            if "data_quality" in data:
                print(f"   Data Quality: {data['data_quality']}")
        elif resp.status_code == 404:
            print(f"   ❌ 404 Not Found - Router not configured properly")
        else:
            print(f"   Response: {resp.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Test complete!")
print(f"\n🌐 Server: {BASE_URL}")
print(f"📚 Docs: {BASE_URL}/docs")
