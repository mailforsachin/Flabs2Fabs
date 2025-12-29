#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8008"

print("🎯 TESTING FIXED PROGRESS ENDPOINTS")
print("=" * 60)

# 1. Get token
print("\n1. Getting authentication token...")
try:
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "sashy", "password": "Welcome2026!"},
        timeout=5
    )
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.status_code}")
        print(f"Response: {resp.text}")
        exit(1)
    
    token = resp.json().get('access_token')
    if not token:
        print("❌ No token in response")
        exit(1)
    
    print(f"✅ Token obtained: {token[:50]}...")
    headers = {"Authorization": f"Bearer {token}"}
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# 2. Test all progress endpoints
print("\n2. Testing all Phase D endpoints:")

endpoints = [
    ("Strength Projections", "/api/progress/strength-projections?days_back=30"),
    ("Consistency Projections", "/api/progress/consistency-projections?days_back=30"),
    ("Comprehensive Report", "/api/progress/comprehensive-report?days_back=90"),
    ("Motivational Insights", "/api/progress/motivational-insights?days_back=30"),
    ("Missed Opportunities", "/api/progress/missed-opportunities?days_back=30"),
]

all_success = True
for name, endpoint in endpoints:
    print(f"\n🔍 {name}:")
    try:
        resp = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print(f"   ✅ SUCCESS!")
            data = resp.json()
            print(f"   User ID: {data.get('user_id', 'N/A')}")
            print(f"   Data Quality: {data.get('data_quality', 'N/A')}")
            
            # Show a brief preview of the response
            if 'projections' in data:
                proj = data['projections']
                if 'knowledge_level' in proj:
                    print(f"   Knowledge Level: {proj['knowledge_level']}")
            elif 'report' in data:
                print(f"   Report Summary: {data['report'].get('summary', 'N/A')[:50]}...")
            elif 'insights' in data:
                insights = data.get('insights', [])
                if insights:
                    print(f"   Insight: {insights[0][:50]}...")
        else:
            print(f"   ❌ FAILED")
            print(f"   Response: {resp.text[:200]}")
            all_success = False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        all_success = False

# 3. Summary
print("\n" + "=" * 60)
if all_success:
    print("🎉 ALL PHASE D PROGRESS ENDPOINTS ARE WORKING!")
else:
    print("⚠️ Some endpoints need attention")

print(f"\n📚 Documentation: {BASE_URL}/docs")
print("🔗 Direct test links:")
for name, endpoint in endpoints:
    print(f"   {name}: {BASE_URL}{endpoint}")
