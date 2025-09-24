#!/usr/bin/env python3
"""
Test script to verify pair ID synchronization between frontend and backend
"""

import requests
import json
from utils.pair_utils import generate_pair_id

def test_pair_id_generation():
    """Test pair ID generation with various device formats"""
    
    # Test cases with different device formats
    test_devices = [
        # Case 1: IP addresses
        ({'ip': '192.168.4.268', 'name': 'Device 268'}, {'ip': '192.168.4.269', 'name': 'Device 269'}),
        
        # Case 2: Device IDs
        ({'device_id': '268', 'name': 'Device 268'}, {'device_id': '269', 'name': 'Device 269'}),
        
        # Case 3: Mixed formats
        ({'ip': '192.168.4.268'}, {'device_id': '269'}),
        
        # Case 4: Only names with numbers
        ({'name': 'device_268'}, {'name': 'device_269'}),
        
        # Case 5: Complex device names
        ({'name': 'device_1758355653_268'}, {'name': 'device_1758355654_269'})
    ]
    
    print("Testing pair ID generation consistency:")
    print("=" * 50)
    
    for i, (device1, device2) in enumerate(test_devices, 1):
        print(f"\nTest Case {i}:")
        print(f"Device 1: {device1}")
        print(f"Device 2: {device2}")
        
        # Simulate backend logic
        def extract_device_id(device):
            """Extract device ID from device object, prioritizing ip, then device_id, then id"""
            if isinstance(device, dict):
                # Priority: ip > device_id > id > name
                return device.get('ip') or device.get('device_id') or device.get('id') or device.get('name') or 'unknown'
            else:
                # If it's already a string/number, use as-is
                return device
        
        device1_id = extract_device_id(device1)
        device2_id = extract_device_id(device2)
        
        backend_pair_id = generate_pair_id(device1_id, device2_id)
        
        # Simulate frontend logic (same as createPairIdFromDevices)
        device1_frontend_id = device1.get('ip') or device1.get('device_id') or device1.get('name') or 'unknown'
        device2_frontend_id = device2.get('ip') or device2.get('device_id') or device2.get('name') or 'unknown'
        
        frontend_pair_id = generate_pair_id(device1_frontend_id, device2_frontend_id)
        
        # Check consistency
        is_consistent = backend_pair_id == frontend_pair_id
        status = "✅ PASS" if is_consistent else "❌ FAIL"
        
        print(f"Backend pair ID:  {backend_pair_id}")
        print(f"Frontend pair ID: {frontend_pair_id}")
        print(f"Status: {status}")
        
        if not is_consistent:
            print(f"❌ MISMATCH DETECTED!")
            print(f"  Backend extracted: {device1_id}, {device2_id}")
            print(f"  Frontend extracted: {device1_frontend_id}, {device2_frontend_id}")

def test_api_endpoint():
    """Test the actual API endpoint"""
    
    print("\n" + "=" * 50)
    print("Testing API endpoint /api/devices/pair")
    print("=" * 50)
    
    # Test data
    test_data = {
        'devices': [
            {'ip': '192.168.4.268', 'name': 'Device 268'},
            {'ip': '192.168.4.269', 'name': 'Device 269'}
        ]
    }
    
    try:
        # Make API request
        response = requests.post('http://localhost:8001/api/devices/pair', 
                               json=test_data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                pairs = result.get('data', {}).get('pairs', [])
                if pairs:
                    pair = pairs[0]
                    api_pair_id = pair.get('pair_id')
                    
                    # Calculate expected pair ID
                    device1 = test_data['devices'][0]
                    device2 = test_data['devices'][1]
                    device1_id = device1.get('ip') or device1.get('device_id') or device1.get('name') or 'unknown'
                    device2_id = device2.get('ip') or device2.get('device_id') or device2.get('name') or 'unknown'
                    expected_pair_id = generate_pair_id(device1_id, device2_id)
                    
                    is_correct = api_pair_id == expected_pair_id
                    status = "✅ PASS" if is_correct else "❌ FAIL"
                    
                    print(f"API returned pair ID: {api_pair_id}")
                    print(f"Expected pair ID:   {expected_pair_id}")
                    print(f"Status: {status}")
                    
                    if is_correct:
                        print("🎉 API endpoint is working correctly!")
                    else:
                        print("❌ API endpoint has pair ID mismatch!")
                else:
                    print("❌ No pairs returned from API")
            else:
                print(f"❌ API returned error: {result.get('error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_pair_id_generation()
    test_api_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("If all tests pass, the pair ID synchronization issue should be fixed.")