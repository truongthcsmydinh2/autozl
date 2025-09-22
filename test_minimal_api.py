#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test minimal Flask API
"""

import requests
import json

def test_minimal_api():
    """Test minimal Flask API endpoints"""
    base_url = "http://localhost:8001"
    
    print("=== Testing Minimal Flask API ===")
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/test/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("❌ Health endpoint failed")
            
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test pairs create endpoint
    print("\n2. Testing pairs create endpoint...")
    try:
        test_data = {
            "device_a": "test_device_a",
            "device_b": "test_device_b"
        }
        
        print(f"Sending data: {test_data}")
        
        response = requests.post(
            f"{base_url}/test/pairs/create",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                print("✅ Pairs create endpoint working")
            except Exception as json_error:
                print(f"❌ JSON parsing error: {json_error}")
        else:
            print("❌ Pairs create endpoint failed")
            
    except Exception as e:
        print(f"❌ Pairs create endpoint error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_minimal_api()