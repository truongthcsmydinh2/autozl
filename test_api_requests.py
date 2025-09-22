#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API endpoints using requests library
"""

import requests
import json
import traceback

def test_api_endpoint():
    """Test API endpoint using requests"""
    try:
        url = "http://localhost:8000/api/pairs/create"
        data = {
            "device_a": "test_device_a",
            "device_b": "test_device_b"
        }
        
        print(f"Sending POST request to: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            print("✅ API call successful!")
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test health endpoint first"""
    try:
        url = "http://localhost:8000/health"
        print(f"Testing health endpoint: {url}")
        
        response = requests.get(url)
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test API Requests ===")
    
    # Test health first
    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    
    if health_ok:
        print("\n2. Testing pairs/create endpoint...")
        success = test_api_endpoint()
        
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ API test failed!")
    else:
        print("\n❌ Health check failed - server may not be running!")