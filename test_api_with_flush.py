#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API with forced output flush
"""

import requests
import json
import time
import sys

def test_api_with_flush():
    """Test API and force server to flush output"""
    base_url = "http://localhost:8000"
    
    print("=== Test API with Flush ===")
    
    # Test health first
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health status: {response.status_code}")
        if response.status_code != 200:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"Health error: {e}")
        return False
    
    # Test pairs/create with small delay to allow server processing
    print("\n2. Testing /api/pairs/create endpoint...")
    
    test_data = {
        'device_a': 'flush_test_a',
        'device_b': 'flush_test_b'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"Sending request to {base_url}/api/pairs/create...")
    print(f"Data: {json.dumps(test_data)}")
    
    try:
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
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Give server time to flush debug output
        print("\nWaiting 2 seconds for server debug output...")
        time.sleep(2)
        
        if response.status_code == 200:
            print("✅ API test successful")
            return True
        else:
            print(f"❌ API test failed with status {response.status_code}")
            
            # Try to parse error
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_server_logs_endpoint():
    """Test if we can get server logs via a special endpoint"""
    base_url = "http://localhost:8000"
    
    print("\n=== Test Server Logs ===")
    
    # Try to access a non-existent endpoint to see error handling
    try:
        response = requests.get(f"{base_url}/api/debug/test", timeout=10)
        print(f"Debug endpoint status: {response.status_code}")
        print(f"Debug response: {response.text}")
    except Exception as e:
        print(f"Debug endpoint error: {e}")
    
    return True

if __name__ == "__main__":
    print("Starting API test with flush...")
    sys.stdout.flush()
    
    success1 = test_api_with_flush()
    success2 = test_server_logs_endpoint()
    
    if success1:
        print("\n🎉 API test passed!")
    else:
        print("\n💥 API test failed!")
    
    sys.stdout.flush()