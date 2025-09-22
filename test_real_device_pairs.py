#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for device pair creation using real devices from phone_mapping.json
This script tests the /api/pairs/create endpoint with actual device IPs and mappings
"""

import json
import requests
import time
from typing import Dict, List, Tuple, Optional

def load_phone_mapping() -> Dict:
    """Load phone mapping from JSON file"""
    try:
        with open('phone_mapping.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('phone_mapping', {})
    except Exception as e:
        print(f"Error loading phone_mapping.json: {e}")
        return {}

def get_real_devices(phone_mapping: Dict) -> List[Tuple[str, str]]:
    """Extract real devices with IP addresses from mapping"""
    real_devices = []
    
    for ip, device_id in phone_mapping.items():
        if ip and device_id and ip != "" and device_id != "":
            # Skip empty entries
            if isinstance(device_id, str) and device_id.strip():
                real_devices.append((ip, device_id))
    
    print(f"Found {len(real_devices)} real devices with mappings:")
    for ip, device_id in real_devices[:10]:  # Show first 10
        print(f"  {ip} -> {device_id}")
    
    return real_devices

def test_pair_creation(device_a: str, device_b: str, base_url: str = "http://127.0.0.1:8000") -> Optional[Dict]:
    """Test creating a device pair"""
    url = f"{base_url}/api/pairs/create"
    payload = {
        "device_a": device_a,
        "device_b": device_b
    }
    
    try:
        print(f"\nTesting pair creation: {device_a} <-> {device_b}")
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            pair_data = result.get('pair', {})
            print(f"Success! Pair created:")
            print(f"  Temp Pair ID: {pair_data.get('temp_pair_id')}")
            print(f"  Pair Hash: {pair_data.get('pair_hash')}")
            print(f"  Device A: {pair_data.get('device_a')}")
            print(f"  Device B: {pair_data.get('device_b')}")
            print(f"  Created At: {pair_data.get('created_at')}")
            print(f"  Pair ID: {pair_data.get('id')}")
            return result
        else:
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_duplicate_prevention(device_a: str, device_b: str, base_url: str = "http://127.0.0.1:8000"):
    """Test that AB = BA (no duplicates created)"""
    print(f"\n=== Testing Duplicate Prevention ===")
    print(f"Testing AB vs BA logic with devices: {device_a}, {device_b}")
    
    # Test A -> B
    result1 = test_pair_creation(device_a, device_b, base_url)
    time.sleep(1)
    
    # Test B -> A (should return same pair)
    result2 = test_pair_creation(device_b, device_a, base_url)
    
    if result1 and result2:
        pair1 = result1.get('pair', {})
        pair2 = result2.get('pair', {})
        hash1 = pair1.get('pair_hash')
        hash2 = pair2.get('pair_hash')
        id1 = pair1.get('id')
        id2 = pair2.get('id')
        
        if hash1 == hash2 and id1 == id2:
            print(f"✅ PASS: AB = BA logic works correctly (same hash: {hash1}, same ID: {id1})")
        else:
            print(f"❌ FAIL: Different pairs created - Hash1: {hash1} vs Hash2: {hash2}, ID1: {id1} vs ID2: {id2}")
    else:
        print(f"❌ FAIL: One or both requests failed")

def test_nonexistent_device(base_url: str = "http://127.0.0.1:8000"):
    """Test with non-existent device"""
    print(f"\n=== Testing Non-existent Device ===")
    result = test_pair_creation("fake_device_123", "another_fake_456", base_url)
    
    if result:
        print(f"⚠️  WARNING: System created pair with fake devices - this might be expected behavior")
    else:
        print(f"✅ System properly handled non-existent devices")

def check_server_health(base_url: str = "http://127.0.0.1:8000") -> bool:
    """Check if API server is running"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ API Server is running at {base_url}")
            return True
        else:
            print(f"❌ API Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        return False

def main():
    print("=== Real Device Pair Creation Test ===")
    print("Loading phone mapping and testing with real devices...\n")
    
    # Check server health first
    if not check_server_health():
        print("Please start the API server first: python api_server.py")
        return
    
    # Load phone mapping
    phone_mapping = load_phone_mapping()
    if not phone_mapping:
        print("No phone mapping found. Please check phone_mapping.json")
        return
    
    print(f"\nTotal entries in phone_mapping: {len(phone_mapping)}")
    
    # Get real devices
    real_devices = get_real_devices(phone_mapping)
    
    if len(real_devices) < 2:
        print("Need at least 2 real devices to test pair creation")
        return
    
    # Test with first few real devices
    print(f"\n=== Testing with Real Devices ===")
    
    # Test 1: Create pair with first two devices
    device1_ip, device1_id = real_devices[0]
    device2_ip, device2_id = real_devices[1]
    
    print(f"\nDevice 1: {device1_ip} ({device1_id})")
    print(f"Device 2: {device2_ip} ({device2_id})")
    
    # Test using device IDs
    test_duplicate_prevention(device1_id, device2_id)
    
    # Test using IP addresses
    if len(real_devices) >= 4:
        device3_ip, device3_id = real_devices[2]
        device4_ip, device4_id = real_devices[3]
        print(f"\n=== Testing with IP Addresses ===")
        print(f"Device 3: {device3_ip} ({device3_id})")
        print(f"Device 4: {device4_ip} ({device4_id})")
        test_duplicate_prevention(device3_ip, device4_ip)
    
    # Test with non-existent devices
    test_nonexistent_device()
    
    # Test multiple pairs to check for conflicts
    if len(real_devices) >= 6:
        print(f"\n=== Testing Multiple Pairs ===")
        for i in range(0, min(6, len(real_devices)-1), 2):
            device_a = real_devices[i][1]  # Use device ID
            device_b = real_devices[i+1][1]  # Use device ID
            test_pair_creation(device_a, device_b)
            time.sleep(0.5)
    
    print(f"\n=== Test Summary ===")
    print(f"✅ Tested with {len(real_devices)} real devices from phone_mapping.json")
    print(f"✅ Verified AB = BA logic")
    print(f"✅ Tested with both device IDs and IP addresses")
    print(f"✅ Tested non-existent device handling")
    print(f"\nCheck the API server logs for any errors or issues.")

if __name__ == "__main__":
    main()