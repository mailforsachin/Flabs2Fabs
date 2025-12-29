#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8010"

def get_token():
    """Get authentication token"""
    print("🔑 Getting authentication token...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "sashy", "password": "Welcome2026!"},
            timeout=10
        )
        print(f"Login status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Token obtained: {token[:50]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_endpoint(name, endpoint, token, params=None):
    """Test a specific endpoint"""
    print(f"\n🔍 Testing {name} ({endpoint})...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        if params:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=10
            )
        else:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
        
        print(f"Status: {response.status_code}")
        try:
            data = response.json()
            print(f"✅ Success! Response preview:")
            print(json.dumps(data, indent=2)[:500] + "...")
        except json.JSONDecodeError:
            print(f"Response (not JSON): {response.text[:200]}")
        except Exception as e:
            print(f"Error parsing response: {e}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def main():
    print("🚀 Starting Progress Endpoints Test")
    print("=" * 50)
    
    # Get token
    token = get_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    # Test endpoints
    test_endpoint("Test endpoint", "/api/progress/test", token)
    test_endpoint("Strength projections", "/api/progress/strength-projections-simple", token, {"days_back": 30})
    test_endpoint("Consistency projections", "/api/progress/consistency-projections-simple", token, {"days_back": 30})
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
