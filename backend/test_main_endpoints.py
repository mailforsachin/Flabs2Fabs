#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8008"

def test_main_endpoints():
    print("🚀 Testing Main Server Endpoints")
    print("=" * 50)
    
    # 1. Test root endpoint
    print("\n1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Message: {data.get('message', 'N/A')}")
            print(f"Version: {data.get('version', 'N/A')}")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Test health endpoint
    print("\n2️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Get token
    print("\n3️⃣ Testing authentication...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "sashy", "password": "Welcome2026!"},
            timeout=5
        )
        print(f"Login status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Authentication successful!")
            
            # 4. Test progress endpoints
            print("\n4️⃣ Testing progress endpoints...")
            headers = {"Authorization": f"Bearer {token}"}
            
            endpoints = [
                ("Strength projections", "/api/progress/strength-projections?days_back=30"),
                ("Consistency projections", "/api/progress/consistency-projections?days_back=30"),
                ("Comprehensive report", "/api/progress/comprehensive-report?days_back=90"),
                ("Motivational insights", "/api/progress/motivational-insights?days_back=30"),
                ("Missed opportunities", "/api/progress/missed-opportunities?days_back=30"),
            ]
            
            for name, endpoint in endpoints:
                print(f"\n  🔍 Testing {name}...")
                try:
                    response = requests.get(
                        f"{BASE_URL}{endpoint}",
                        headers=headers,
                        timeout=5
                    )
                    print(f"  Status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"  ✅ Success!")
                        try:
                            data = response.json()
                            # Print just a preview
                            preview = json.dumps(data)[:200]
                            print(f"  Preview: {preview}...")
                        except:
                            print(f"  Response: {response.text[:100]}")
                    else:
                        print(f"  Response: {response.text[:100]}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_main_endpoints()
