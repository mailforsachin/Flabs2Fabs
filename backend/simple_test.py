#!/usr/bin/env python3
import requests
import time

def test_server():
    BASE_URL = "http://localhost:8008"
    
    print("🔍 Testing server step by step...")
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   ✅ Success: {resp.json().get('message', 'No message')}")
        else:
            print(f"   Response: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Login
    print("\n2. Testing login...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "sashy", "password": "Welcome2026!"},
            timeout=5
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            token = resp.json().get('access_token')
            if token:
                print(f"   ✅ Login successful! Token: {token[:50]}...")
                
                # Test 3: Progress endpoint
                print("\n3. Testing Phase D progress endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.get(
                    f"{BASE_URL}/api/progress/strength-projections?days_back=30",
                    headers=headers,
                    timeout=5
                )
                print(f"   Status: {resp.status_code}")
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"   ✅ Progress endpoint working!")
                    print(f"   User ID: {data.get('user_id', 'N/A')}")
                    print(f"   Data Quality: {data.get('data_quality', 'N/A')}")
                    return True
                else:
                    print(f"   Response: {resp.text[:200]}")
            else:
                print("   ❌ No token in response")
                print(f"   Response: {resp.text[:200]}")
        else:
            print(f"   Response: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 FLAB2FABS API TEST")
    print("=" * 50)
    
    # Give server time to start
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_server()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print(f"\n🌐 Server URL: http://localhost:8008")
        print(f"📚 Docs: http://localhost:8008/docs")
    else:
        print("⚠️ Some tests failed")
        print("\n🔧 Check logs: tail -f debug_server.log")
