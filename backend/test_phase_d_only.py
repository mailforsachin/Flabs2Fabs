#!/usr/bin/env python3
"""
Test ONLY Phase D progress endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8008"

def test_progress_endpoints():
    print("🎯 PHASE D - PROGRESS ENDPOINTS TEST")
    print("=" * 60)
    
    # 1. Get token
    print("\n1. Getting authentication token...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "sashy", "password": "Welcome2026!"},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
        token = response.json().get("access_token")
        if not token:
            print("❌ No token in response")
            return False
            
        print(f"✅ Token obtained: {token[:50]}...")
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # 2. Test each Phase D endpoint
    print("\n2. Testing Phase D Progress Endpoints:")
    
    endpoints = [
        ("Strength Projections", "/api/progress/strength-projections?days_back=30"),
        ("Consistency Projections", "/api/progress/consistency-projections?days_back=30"),
        ("Comprehensive Report", "/api/progress/comprehensive-report?days_back=90"),
        ("Motivational Insights", "/api/progress/motivational-insights?days_back=30"),
        ("Missed Opportunities", "/api/progress/missed-opportunities?days_back=30"),
    ]
    
    all_passed = True
    for name, endpoint in endpoints:
        print(f"\n   🔍 Testing: {name}")
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ {name}: SUCCESS (Status: {response.status_code})")
                try:
                    data = response.json()
                    # Show brief info
                    if "user_id" in data:
                        print(f"      User ID: {data['user_id']}")
                    if "data_quality" in data:
                        print(f"      Data Quality: {data['data_quality']}")
                except:
                    print(f"      Response: {response.text[:100]}")
            else:
                print(f"   ❌ {name}: FAILED (Status: {response.status_code})")
                print(f"      Response: {response.text[:200]}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ {name}: ERROR - {e}")
            all_passed = False
    
    # 3. Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL PHASE D ENDPOINTS ARE WORKING!")
    else:
        print("⚠️ Some endpoints need attention")
    
    print(f"\n📚 API Documentation: {BASE_URL}/docs")
    print("🔗 Direct links to test:")
    for name, endpoint in endpoints:
        print(f"   {name}: {BASE_URL}{endpoint}")
    
    return all_passed

if __name__ == "__main__":
    success = test_progress_endpoints()
    sys.exit(0 if success else 1)
