#!/usr/bin/env python3
import requests
import time

BASE_URL = "http://localhost:8008"
MAX_RETRIES = 10
RETRY_DELAY = 2

print("🔍 Testing server connectivity...")

for i in range(MAX_RETRIES):
    try:
        print(f"Attempt {i+1}/{MAX_RETRIES}...")
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Server is responding! Status: {response.status_code}")
            print(f"Response: {response.json().get('message', 'No message')}")
            
            # Test authentication
            print("\n🔑 Testing authentication...")
            auth_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"username": "sashy", "password": "Welcome2026!"},
                timeout=5
            )
            
            if auth_response.status_code == 200:
                token = auth_response.json().get('access_token')
                print(f"✅ Authentication successful!")
                print(f"Token: {token[:50]}...")
                
                # Test a Phase D endpoint
                print("\n🎯 Testing Phase D endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                progress_response = requests.get(
                    f"{BASE_URL}/api/progress/strength-projections?days_back=30",
                    headers=headers,
                    timeout=5
                )
                print(f"Progress endpoint status: {progress_response.status_code}")
                if progress_response.status_code == 200:
                    print("✅ Phase D endpoint working!")
                else:
                    print(f"Response: {progress_response.text[:200]}")
            else:
                print(f"⚠️ Authentication failed: {auth_response.status_code}")
                print(f"Response: {auth_response.text[:200]}")
            
            break
            
    except requests.exceptions.ConnectionError:
        if i < MAX_RETRIES - 1:
            print(f"⏳ Server not ready yet, waiting {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            print("❌ Server never became available")
    except Exception as e:
        print(f"❌ Error: {e}")
        break
