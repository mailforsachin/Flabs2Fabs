#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8010"

# Test root endpoint
print("Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test health endpoint
print("\nTesting health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
