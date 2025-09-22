#!/usr/bin/env python3

import requests
import json

def test_api_direct():
    """Test API directly to see detailed responses"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing API Direct Responses")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("device_33", "device_10"),
        ("device_7", "device_3"),
        ("device_100", "device_5")
    ]
    
    for device1, device2 in test_cases:
        print(f"\nTesting: {device1} + {device2}")
        
        # Create pair
        create_data = {
            "device_a": device1,
            "device_b": device2
        }
        
        try:
            response = requests.post(f"{base_url}/api/pairs/create", json=create_data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_api_direct()