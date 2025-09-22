#!/usr/bin/env python3
"""
Test script to create new device pair and verify ID consistency
"""

import requests
import json
from utils.pair_utils import generate_pair_id

def test_create_new_pair():
    """Test creating a new device pair and verify ID mapping"""
    
    base_url = "http://localhost:8000"
    
    print("Testing new pair creation and ID consistency:")
    print("=" * 60)
    
    # Test devices
    test_devices = [
        ("192.168.1.100:5555", "192.168.1.200:5555"),
        ("device_999", "device_888"),
        ("device_1758999999_7", "device_1758999999_9"),
    ]
    
    for device_a, device_b in test_devices:
        print(f"\n🧪 Testing pair creation: {device_a} + {device_b}")
        
        # 1. Generate expected pair ID
        expected_id = generate_pair_id(device_a, device_b)
        print(f"   Expected ID: {expected_id}")
        
        # 2. Create pair via API
        try:
            create_response = requests.post(f"{base_url}/api/pairs/create", json={
                "device_a": device_a,
                "device_b": device_b
            })
            
            print(f"   Create API status: {create_response.status_code}")
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                print(f"   Create response: {create_data}")
                
                # Extract pair ID from response
                if 'pair' in create_data and 'id' in create_data['pair']:
                    actual_id = create_data['pair']['id']
                elif 'pair_id' in create_data:
                    actual_id = create_data['pair_id']
                elif 'id' in create_data:
                    actual_id = create_data['id']
                else:
                    print(f"   ❌ Could not extract pair ID from response")
                    continue
                
                print(f"   Actual ID: {actual_id}")
                
                # 3. Verify ID consistency
                if actual_id == expected_id:
                    print(f"   ✅ ID consistency: PASS")
                else:
                    print(f"   ❌ ID consistency: FAIL")
                    print(f"      Expected: {expected_id}")
                    print(f"      Actual: {actual_id}")
                
                # 4. Test lookup via new endpoint
                try:
                    lookup_response = requests.get(f"{base_url}/api/pairs/{actual_id}")
                    print(f"   Lookup API status: {lookup_response.status_code}")
                    
                    if lookup_response.status_code == 200:
                        lookup_data = lookup_response.json()
                        print(f"   ✅ Lookup: SUCCESS")
                        print(f"   Lookup data: {lookup_data['pair']['id']}")
                    else:
                        print(f"   ❌ Lookup: FAILED - {lookup_response.status_code}")
                        print(f"   Response: {lookup_response.text}")
                        
                except Exception as e:
                    print(f"   ❌ Lookup error: {e}")
                
            else:
                print(f"   ❌ Create failed: {create_response.status_code}")
                print(f"   Response: {create_response.text}")
                
        except Exception as e:
            print(f"   ❌ Create error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_create_new_pair()