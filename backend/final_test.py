#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8008"

def test_endpoint(method, path, expected_status=200, **kwargs):
    """Test a single endpoint"""
    print(f"\n🔍 {method.upper()} {path}")
    try:
        response = requests.request(method, f"{BASE_URL}{path}", **kwargs, timeout=10)
        status_ok = response.status_code == expected_status
        icon = "✅" if status_ok else "❌"
        print(f"{icon} Status: {response.status_code}")
        
        if not status_ok:
            print(f"   Expected: {expected_status}")
            if response.text:
                print(f"   Response: {response.text[:200]}")
        
        # Try to return JSON
        try:
            return response.json() if response.text else None
        except:
            return response.text[:200] if response.text else None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

print("🚀 COMPREHENSIVE API TEST")
print("=" * 60)

# 1. Test basic endpoints
print("\n1️⃣ Basic Server Tests")
test_endpoint("GET", "/")
test_endpoint("GET", "/health")

# 2. Test authentication
print("\n2️⃣ Authentication Test")
login_result = test_endpoint(
    "POST", "/api/auth/login",
    json={"username": "sashy", "password": "Welcome2026!"}
)

if login_result and isinstance(login_result, dict) and "access_token" in login_result:
    token = login_result["access_token"]
    print(f"✅ Token obtained: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test Phase D Progress Endpoints
    print("\n3️⃣ Phase D Progress Endpoints")
    
    progress_tests = [
        ("GET", "/api/progress/strength-projections?days_back=30"),
        ("GET", "/api/progress/consistency-projections?days_back=30"),
        ("GET", "/api/progress/comprehensive-report?days_back=90"),
        ("GET", "/api/progress/motivational-insights?days_back=30"),
        ("GET", "/api/progress/missed-opportunities?days_back=30"),
    ]
    
    for method, endpoint in progress_tests:
        result = test_endpoint(method, endpoint, headers=headers)
        if result and isinstance(result, dict):
            print(f"   User ID: {result.get('user_id', 'N/A')}")
            print(f"   Data Quality: {result.get('data_quality', 'N/A')}")
    
    # 4. Test other endpoints to ensure they still work
    print("\n4️⃣ Other Critical Endpoints")
    test_endpoint("GET", "/api/exercises/", headers=headers)
    test_endpoint("GET", "/api/workouts/", headers=headers)
    test_endpoint("GET", "/api/recommendations/quick", headers=headers)
    
else:
    print("❌ Cannot proceed - authentication failed")

print("\n" + "=" * 60)
print("🎯 Test Complete!")
print(f"\n📚 Documentation: {BASE_URL}/docs")
print("🔑 Test with: curl -X POST http://localhost:8008/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"sashy\",\"password\":\"Welcome2026!\"}'")
