#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("🔍 Checking available endpoints...")

# Get OpenAPI spec to see all endpoints
try:
    response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
    if response.status_code == 200:
        spec = response.json()
        print("✅ OpenAPI spec loaded")
        
        # List all paths
        print("\n📋 Available endpoints:")
        for path, methods in spec.get('paths', {}).items():
            for method, details in methods.items():
                print(f"  {method.upper()} {path}")
                if 'summary' in details:
                    print(f"    - {details['summary']}")
    else:
        print("❌ Could not get OpenAPI spec")
except Exception as e:
    print(f"❌ Error getting OpenAPI: {e}")

print("\n🔑 Testing login endpoint directly...")
try:
    # Try different possible login endpoints
    endpoints = [
        "/api/auth/login",
        "/auth/login", 
        "/token",
        "/api/token"
    ]
    
    for endpoint in endpoints:
        print(f"\nTrying {endpoint}...")
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"username": "sashy", "password": "Welcome2026!"},
            timeout=5
        )
        print(f"  Status: {response.status_code}")
        if response.status_code < 400:
            print(f"  Response: {response.text[:200]}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'access_token' in data:
                        print(f"  ✅ Found working login endpoint!")
                        break
                except:
                    pass
except Exception as e:
    print(f"❌ Error: {e}")
