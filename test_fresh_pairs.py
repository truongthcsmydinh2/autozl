#!/usr/bin/env python3

import requests
import json
import time
import random

# API Configuration
API_BASE = "http://localhost:8000"

def test_fresh_pair_creation():
    """Test pair creation with completely new device IDs"""
    print("=== Testing Fresh Pair Creation with Standardized IDs ===")
    
    # Use random device IDs to ensure fresh data
    timestamp = int(time.time())
    device_a = f"device_{timestamp}_1"
    device_b = f"device_{timestamp}_2"
    
    print(f"Testing with fresh devices: {device_a} + {device_b}")
    
    # Expected standardized pair_id (sorted order)
    expected_pair_id = f"pair_{timestamp}_1_{timestamp}_2"
    print(f"Expected pair_id: {expected_pair_id}")
    
    # Test pair creation
    try:
        response = requests.post(f"{API_BASE}/api/pairs/create", json={
            "device_a": device_a,
            "device_b": device_b
        })
        
        if response.status_code == 200:
            response_data = response.json()
            pair_data = response_data.get('pair', {})
            actual_pair_id = pair_data.get('id')
            temp_pair_id = pair_data.get('temp_pair_id')
            
            print(f"✓ Created pair: {actual_pair_id} (temp: {temp_pair_id})")
            
            if actual_pair_id == expected_pair_id:
                print(f"✅ SUCCESS: Pair ID matches expected standardized format!")
                return True
            else:
                print(f"❌ FAIL: Expected {expected_pair_id}, got {actual_pair_id}")
                return False
        else:
            print(f"❌ Failed to create pair: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing pair creation: {e}")
        return False

def test_reverse_order():
    """Test that reverse order produces same pair_id"""
    print("\n=== Testing Reverse Order Consistency ===")
    
    # Use random device IDs
    timestamp = int(time.time()) + 1
    device_a = f"device_{timestamp}_5"
    device_b = f"device_{timestamp}_3"
    
    print(f"Testing reverse order: {device_b} + {device_a}")
    
    # Expected standardized pair_id (always sorted)
    expected_pair_id = f"pair_{timestamp}_3_{timestamp}_5"
    print(f"Expected pair_id: {expected_pair_id}")
    
    # Test pair creation with reverse order
    try:
        response = requests.post(f"{API_BASE}/api/pairs/create", json={
            "device_a": device_b,  # Reverse order
            "device_b": device_a
        })
        
        if response.status_code == 200:
            response_data = response.json()
            pair_data = response_data.get('pair', {})
            actual_pair_id = pair_data.get('id')
            temp_pair_id = pair_data.get('temp_pair_id')
            
            print(f"✓ Created pair: {actual_pair_id} (temp: {temp_pair_id})")
            
            if actual_pair_id == expected_pair_id:
                print(f"✅ SUCCESS: Reverse order produces same standardized ID!")
                return True
            else:
                print(f"❌ FAIL: Expected {expected_pair_id}, got {actual_pair_id}")
                return False
        else:
            print(f"❌ Failed to create pair: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing reverse order: {e}")
        return False

def test_numeric_extraction():
    """Test numeric extraction from device names"""
    print("\n=== Testing Numeric Extraction ===")
    
    test_cases = [
        ("device_33", "device_10", "pair_10_33"),
        ("device_7", "device_3", "pair_3_7"),
        ("device_100", "device_5", "pair_5_100")
    ]
    
    success_count = 0
    
    for device_a, device_b, expected in test_cases:
        print(f"\nTesting: {device_a} + {device_b} → {expected}")
        
        try:
            response = requests.post(f"{API_BASE}/api/pairs/create", json={
                "device_a": device_a,
                "device_b": device_b
            })
            
            if response.status_code == 200:
                response_data = response.json()
                pair_data = response_data.get('pair', {})
                actual_pair_id = pair_data.get('id')
                
                print(f"  Result: {actual_pair_id}")
                
                if actual_pair_id == expected:
                    print(f"  ✅ SUCCESS")
                    success_count += 1
                else:
                    print(f"  ❌ FAIL: Expected {expected}")
            else:
                print(f"  ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\nNumeric extraction tests: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

if __name__ == "__main__":
    print("Testing Standardized Pair ID Implementation")
    print("=" * 50)
    
    # Check if API server is running
    try:
        response = requests.get(f"{API_BASE}/api/pairs")
        if response.status_code != 200:
            print("❌ API server is not running or not accessible")
            exit(1)
    except:
        print("❌ API server is not running or not accessible")
        exit(1)
    
    results = []
    results.append(test_fresh_pair_creation())
    results.append(test_reverse_order())
    results.append(test_numeric_extraction())
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 ALL TESTS PASSED! Standardized pair_id is working correctly!")
    else:
        print("❌ Some tests failed. Standardized pair_id needs fixes.")