#!/usr/bin/env python3
"""
Test automation API endpoints
"""

import requests
import json

def test_automation_start():
    """Test automation start endpoint"""
    print("=== Testing Automation Start API ===")
    
    # Test data
    test_data = {
        "devices": [
            {
                "id": "192.168.1.100",
                "ip": "192.168.1.100",
                "name": "Test Device 1"
            },
            {
                "id": "192.168.1.101", 
                "ip": "192.168.1.101",
                "name": "Test Device 2"
            }
        ],
        "conversations": []
    }
    
    try:
        response = requests.post(
            'http://localhost:8001/api/automation/start',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Automation API working!")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_automation_stop():
    """Test automation stop endpoint"""
    print("\n=== Testing Automation Stop API ===")
    
    try:
        response = requests.post(
            'http://localhost:8001/api/automation/stop',
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Stop API working!")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_edge_cases():
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===")
    
    # Test 1: No devices
    print("\n1. Testing with no devices:")
    try:
        response = requests.post(
            'http://localhost:8001/api/automation/start',
            json={"devices": [], "conversations": []},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Invalid device format
    print("\n2. Testing with invalid device format:")
    try:
        response = requests.post(
            'http://localhost:8001/api/automation/start',
            json={"devices": ["invalid"], "conversations": []},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: With conversations
    print("\n3. Testing with conversations:")
    try:
        response = requests.post(
            'http://localhost:8001/api/automation/start',
            json={
                "devices": [{"ip": "192.168.1.100"}],
                "conversations": ["Hello", "How are you?"]
            },
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Automation API Endpoints\n")
    
    # Test basic functionality
    start_success = test_automation_start()
    stop_success = test_automation_stop()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n" + "="*50)
    if start_success and stop_success:
        print("🎉 ALL TESTS PASSED! Automation API is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("="*50)