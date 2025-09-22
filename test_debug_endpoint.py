#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test debug endpoint
"""

import requests
import json

def test_debug_endpoint():
    """Test the debug endpoint"""
    base_url = "http://localhost:8000"
    
    print("=== Test Debug Endpoint ===")
    
    # Test debug endpoint
    print("\n1. Testing /api/debug/test-pair endpoint...")
    try:
        response = requests.get(f"{base_url}/api/debug/test-pair", timeout=10)
        print(f"Debug endpoint status: {response.status_code}")
        print(f"Debug response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nParsed response:")
            print(f"  Success: {data.get('success')}")
            print(f"  Pair type: {data.get('pair_type')}")
            print(f"  Has await: {data.get('has_await')}")
            print(f"  Pair data: {data.get('pair_data')}")
            return True
        else:
            print(f"❌ Debug endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")
        return False

    # Test original endpoint for comparison
    print("\n2. Testing /api/pairs/create endpoint for comparison...")
    try:
        test_data = {
            'device_a': 'compare_test_a',
            'device_b': 'compare_test_b'
        }
        
        response = requests.post(
            f"{base_url}/api/pairs/create",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Original endpoint status: {response.status_code}")
        print(f"Original response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Original endpoint works")
        else:
            print(f"❌ Original endpoint failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Original endpoint error: {e}")

if __name__ == "__main__":
    test_debug_endpoint()