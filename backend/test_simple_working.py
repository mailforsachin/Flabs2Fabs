#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8008"

print("🎯 TESTING SIMPLE WORKING VERSION")
print("=" * 60)

# Get token
resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "sashy", "password": "Welcome2026!"}
)
token = resp.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# Test all endpoints
endpoints = [
    "/api/progress/strength-projections?days_back=30",
    "/api/progress/consistency-projections?days_back=30",
    "/api/progress/comprehensive-report?days_back=90",
    "/api/progress/motivational-insights?days_back=30",
    "/api/progress/missed-opportunities?days_back=30",
]

for endpoint in endpoints:
    print(f"\n🔍 Testing {endpoint}")
    resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS!")
        print(f"   User ID: {data.get('user_id')}")
        if 'projections' in data:
            print(f"   Knowledge Level: {data['projections'].get('knowledge_level', 'N/A')}")
    else:
        print(f"   ❌ FAILED: {resp.text[:200]}")

print("\n" + "=" * 60)
print("🎉 Phase D Progress Endpoints should now work!")
print(f"\n🌐 Server: {BASE_URL}")
print(f"📚 Docs: {BASE_URL}/docs")
