#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test real API with detailed logging
"""

import requests
import json
import time

def test_api_with_detailed_logs():
    """Test API with detailed request/response logging"""
    base_url = "http://localhost:8000"
    
    print("=== Test Real API with Detailed Logs ===")
    
    # Test health first
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health status: {response.status_code}")
        print(f"Health response: {response.text}")
        print(f"Health headers: {dict(response.headers)}")
    except Exception as e:
        print(f"Health error: {e}")
        return False
    
    # Test pairs/create with detailed logging
    print("\n2. Testing /api/pairs/create endpoint...")
    
    test_data = {
        'device_a': 'detailed_test_a',
        'device_b': 'detailed_test_b'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Python-Test-Client/1.0'
    }
    
    print(f"Request URL: {base_url}/api/pairs/create")
    print(f"Request method: POST")
    print(f"Request headers: {headers}")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        print("\nSending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/api/pairs/create",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nResponse received in {duration:.2f} seconds")
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content-type: {response.headers.get('content-type', 'N/A')}")
        print(f"Response content-length: {response.headers.get('content-length', 'N/A')}")
        print(f"Response text length: {len(response.text)}")
        print(f"Response text: {response.text}")
        
        # Try to parse JSON
        try:
            json_data = response.json()
            print(f"Response JSON: {json.dumps(json_data, indent=2)}")
        except Exception as json_error:
            print(f"JSON parse error: {json_error}")
        
        # Check if successful
        if response.status_code == 200:
            print("✅ API test successful")
            return True
        else:
            print(f"❌ API test failed with status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_multiple_requests():
    """Test multiple requests to see if it's consistent"""
    print("\n=== Test Multiple Requests ===")
    
    base_url = "http://localhost:8000"
    success_count = 0
    total_requests = 3
    
    for i in range(total_requests):
        print(f"\nRequest {i+1}/{total_requests}:")
        
        test_data = {
            'device_a': f'multi_test_a_{i}',
            'device_b': f'multi_test_b_{i}'
        }
        
        try:
            response = requests.post(
                f"{base_url}/api/pairs/create",
                json=test_data,
                timeout=10
            )
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                success_count += 1
                print("  ✅ Success")
            else:
                print(f"  ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\nSuccess rate: {success_count}/{total_requests} ({success_count/total_requests*100:.1f}%)")
    return success_count == total_requests

if __name__ == "__main__":
    success1 = test_api_with_detailed_logs()
    success2 = test_multiple_requests()
    
    if success1 and success2:
        print("\n🎉 All API tests passed!")
    else:
        print("\n💥 Some API tests failed!")