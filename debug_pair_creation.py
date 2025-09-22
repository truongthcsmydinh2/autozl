#!/usr/bin/env python3
"""
Debug script to understand pair ID creation flow
"""

import requests
import json
from utils.pair_utils import generate_pair_id, extract_device_ids_from_pair_id, is_valid_pair_id

def test_pair_creation_flow():
    print("=== DEBUG PAIR CREATION FLOW ===")
    
    # 1. Get current devices
    print("\n1. Getting current devices...")
    try:
        response = requests.get('http://localhost:8000/api/devices')
        data = response.json()
        print(f"Raw API response type: {type(data)}")
        print(f"Raw API response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
        
        # Handle different response formats
        if isinstance(data, dict):
            if 'data' in data:
                devices = data['data']
            elif 'devices' in data:
                devices = data['devices']
            else:
                print(f"Dict keys available: {list(data.keys())}")
                return
        elif isinstance(data, list):
            devices = data
        else:
            print(f"Unexpected response format: {type(data)}")
            return
            
        print(f"Found {len(devices)} devices:")
        for i, device in enumerate(devices):
            if i >= 3:  # Show first 3
                break
            print(f"  {i+1}. ID: {device['device_id']}, Name: {device.get('name', 'N/A')}")
    except Exception as e:
        print(f"Error getting devices: {e}")
        return
    
    if len(devices) < 2:
        print("Need at least 2 devices for testing")
        return
    
    # 2. Test pair ID generation with real devices
    device_a = devices[0]['device_id']
    device_b = devices[1]['device_id']
    
    print(f"\n2. Testing pair ID generation:")
    print(f"  Device A: {device_a}")
    print(f"  Device B: {device_b}")
    
    # Generate pair ID using utils
    generated_pair_id = generate_pair_id(device_a, device_b)
    print(f"  Generated pair ID: {generated_pair_id}")
    
    # Test reverse extraction
    extracted_ids = extract_device_ids_from_pair_id(generated_pair_id)
    print(f"  Extracted IDs: {extracted_ids}")
    
    # Validate
    is_valid = is_valid_pair_id(generated_pair_id)
    print(f"  Is valid: {is_valid}")
    
    # 3. Test API pair creation
    print(f"\n3. Testing API pair creation:")
    try:
        payload = {
            'device_a': device_a,
            'device_b': device_b
        }
        response = requests.post('http://localhost:8000/api/pairs/create', json=payload)
        result = response.json()
        
        if response.status_code == 200:
            print(f"  API Response: {json.dumps(result, indent=2)}")
            # Check different possible locations for pair ID
            api_pair_id = result.get('id') or (result.get('pair', {}).get('id') if result.get('pair') else None)
            print(f"  API created pair ID: {api_pair_id}")
            print(f"  Matches generated ID: {api_pair_id == generated_pair_id}")
            
            # Check if API used correct devices
            if result.get('pair'):
                pair_data = result['pair']
                print(f"  API used devices: {pair_data.get('device_a')} + {pair_data.get('device_b')}")
                print(f"  Expected devices: {device_a} + {device_b}")
        else:
            print(f"  API Error: {result}")
    except Exception as e:
        print(f"  Error calling API: {e}")
    
    # 4. Check existing pairs in database
    print(f"\n4. Checking existing pairs:")
    try:
        response = requests.get('http://localhost:8000/api/pairs')
        pairs = response.json()
        print(f"  Found {len(pairs)} existing pairs:")
        for i, pair in enumerate(pairs):
            if i >= 5:  # Show last 5
                break
            print(f"    ID: {pair['id']}, Devices: {pair['device_a']} + {pair['device_b']}")
    except Exception as e:
        print(f"  Error getting pairs: {e}")
    
    # 5. Test finding the pair we just created
    print(f"\n5. Testing pair lookup:")
    try:
        # Try to find by generated ID
        response = requests.get(f'http://localhost:8000/api/pairs/{generated_pair_id}')
        if response.status_code == 200:
            pair_data = response.json()
            print(f"  Found pair by generated ID: {pair_data['id']}")
        else:
            print(f"  Pair not found by generated ID: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error looking up pair: {e}")

if __name__ == '__main__':
    test_pair_creation_flow()