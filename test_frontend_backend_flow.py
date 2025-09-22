#!/usr/bin/env python3
"""
Test complete frontend-backend flow for device pairing
Simulate frontend actions and verify backend responses
"""

import requests
import json
from utils.pair_utils import generate_pair_id

def test_complete_flow():
    """Test complete flow from device selection to pair lookup"""
    
    base_url = "http://localhost:8000"
    
    print("Testing complete frontend-backend flow:")
    print("=" * 60)
    
    # Step 1: Get available devices (simulate frontend device list)
    print("\n📱 Step 1: Getting available devices...")
    try:
        devices_response = requests.get(f"{base_url}/api/devices")
        print(f"   Status: {devices_response.status_code}")
        
        if devices_response.status_code == 200:
            devices_data = devices_response.json()
            if 'data' in devices_data:
                devices = devices_data['data']
                print(f"   ✅ Found {len(devices)} devices")
                
                # Show first few devices
                for i, device in enumerate(devices[:5]):
                    device_id = device.get('device_id', device.get('id', str(device)))
                    print(f"      {i+1}. {device_id}")
                if len(devices) > 5:
                    print(f"      ... and {len(devices) - 5} more")
            else:
                print(f"   ❌ No devices in response")
                print(f"   Response keys: {list(devices_data.keys())}")
                return
        else:
            print(f"   ❌ Failed to get devices: {devices_response.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Error getting devices: {e}")
        return
    
    # Step 2: Select two devices for pairing (simulate user selection)
    print("\n🔗 Step 2: Selecting devices for pairing...")
    
    if len(devices) >= 2:
        # Extract device IDs from device objects
        device_a = devices[0].get('device_id', devices[0].get('id', str(devices[0])))
        device_b = devices[1].get('device_id', devices[1].get('id', str(devices[1])))
        print(f"   Selected: {device_a} + {device_b}")
        
        # Generate expected pair ID
        expected_id = generate_pair_id(device_a, device_b)
        print(f"   Expected pair ID: {expected_id}")
        
        # Step 3: Create pair (simulate frontend "Ghép cặp" button)
        print("\n🎯 Step 3: Creating device pair...")
        try:
            create_response = requests.post(f"{base_url}/api/pairs/create", json={
                "device_a": device_a,
                "device_b": device_b
            })
            
            print(f"   Status: {create_response.status_code}")
            
            if create_response.status_code == 200:
                create_data = create_response.json()
                if 'pair' in create_data:
                    pair = create_data['pair']
                    actual_id = pair['id']
                    print(f"   ✅ Pair created: {actual_id}")
                    
                    # Verify ID consistency
                    if actual_id == expected_id:
                        print(f"   ✅ ID consistency: PASS")
                    else:
                        print(f"   ❌ ID consistency: FAIL")
                        print(f"      Expected: {expected_id}")
                        print(f"      Actual: {actual_id}")
                    
                    # Step 4: Lookup pair (simulate frontend pair verification)
                    print("\n🔍 Step 4: Looking up created pair...")
                    try:
                        lookup_response = requests.get(f"{base_url}/api/pairs/{actual_id}")
                        print(f"   Status: {lookup_response.status_code}")
                        
                        if lookup_response.status_code == 200:
                            lookup_data = lookup_response.json()
                            if 'pair' in lookup_data:
                                found_pair = lookup_data['pair']
                                print(f"   ✅ Pair found: {found_pair['id']}")
                                print(f"   Devices: {found_pair['device_a']} + {found_pair['device_b']}")
                                print(f"   Temp ID: {found_pair.get('temp_pair_id', 'N/A')}")
                                
                                # Final verification
                                if (found_pair['device_a'] == device_a and found_pair['device_b'] == device_b) or \
                                   (found_pair['device_a'] == device_b and found_pair['device_b'] == device_a):
                                    print(f"   ✅ Device mapping: CORRECT")
                                else:
                                    print(f"   ❌ Device mapping: INCORRECT")
                                    
                            else:
                                print(f"   ❌ Invalid lookup response format")
                        else:
                            print(f"   ❌ Lookup failed: {lookup_response.status_code}")
                            print(f"   Response: {lookup_response.text}")
                            
                    except Exception as e:
                        print(f"   ❌ Lookup error: {e}")
                        
                else:
                    print(f"   ❌ Invalid create response format")
            else:
                print(f"   ❌ Create failed: {create_response.status_code}")
                print(f"   Response: {create_response.text}")
                
        except Exception as e:
            print(f"   ❌ Create error: {e}")
            
    else:
        print(f"   ❌ Not enough devices for pairing (found {len(devices)})")
    
    print("\n" + "=" * 60)
    print("🏁 Complete flow test finished!")

if __name__ == "__main__":
    test_complete_flow()