#!/usr/bin/env python3
import requests
import traceback

BASE_URL = "http://localhost:8008"

print("🔍 Debugging 500 errors...")

# Get token
try:
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "sashy", "password": "Welcome2026!"},
        timeout=5
    )
    token = resp.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Got token, testing one endpoint with full error capture...")
    
    # Test one endpoint and capture full error
    resp = requests.get(
        f"{BASE_URL}/api/progress/strength-projections?days_back=30",
        headers=headers,
        timeout=10
    )
    
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
