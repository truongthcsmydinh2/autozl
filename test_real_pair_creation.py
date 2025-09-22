#!/usr/bin/env python3
"""
Test real pair creation with actual device IDs
"""

import requests
import json
from utils.pair_utils import generate_pair_id

def test_pair_creation():
    """Test creating pairs with real device IDs"""
    
    # Real device IDs from API
    real_devices = [
        "192.168.5.76:5555",  # Should extract 76
        "192.168.5.93:5555",  # Should extract 93
        "192.168.5.88:5555",  # Should extract 88
        "192.168.4.156:5555"  # Should extract 156
    ]
    
    print("=== TESTING REAL PAIR CREATION ===")
    print(f"Available devices: {real_devices}")
    print()
    
    # Test pair ID generation
    device1 = real_devices[0]  # 192.168.5.76:5555
    device2 = real_devices[1]  # 192.168.5.93:5555
    
    print(f"Testing pair creation:")
    print(f"Device 1: {device1}")
    print(f"Device 2: {device2}")
    
    # Generate pair ID using backend logic
    pair_id = generate_pair_id(device1, device2)
    print(f"Generated pair ID: {pair_id}")
    print()
    
    # Test creating pair via API
    try:
        print("Creating pair via API...")
        response = requests.post('http://localhost:8000/api/pairs/create', 
                               json={
                                   'device_a': device1,
                                   'device_b': device2
                               })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API Response: {json.dumps(result, indent=2)}")
            
            api_pair_id = result.get('pair', {}).get('id')
            print(f"API created pair ID: {api_pair_id}")
            print(f"Generated pair ID: {pair_id}")
            print(f"Match: {'✅' if api_pair_id == pair_id else '❌'}")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
    
    print()
    
    # Test with different device combinations
    print("=== TESTING MULTIPLE COMBINATIONS ===")
    combinations = [
        (real_devices[0], real_devices[1]),  # 76, 93
        (real_devices[2], real_devices[3]),  # 88, 156
        (real_devices[0], real_devices[2]),  # 76, 88
    ]
    
    for i, (dev1, dev2) in enumerate(combinations, 1):
        pair_id = generate_pair_id(dev1, dev2)
        print(f"{i}. {dev1} + {dev2} -> {pair_id}")

if __name__ == "__main__":
    test_pair_creation()