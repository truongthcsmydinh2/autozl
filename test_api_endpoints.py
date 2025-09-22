#!/usr/bin/env python3
"""
Test API endpoints with standardized pair IDs
Tests the actual API endpoints to ensure they work with the new ID system
"""

import requests
import json
import time
import sys
import os

# API base URL
API_BASE = "http://localhost:8000"

def test_pair_creation():
    """Test creating device pairs with standardized IDs"""
    print("=== Testing Pair Creation API ===")
    
    test_cases = [
        # User examples
        {"device_a": "device_33", "device_b": "device_10", "expected_id": "pair_10_33"},
        {"device_a": "device_12", "device_b": "device_15", "expected_id": "pair_12_15"},
        {"device_a": "device_7", "device_b": "device_3", "expected_id": "pair_3_7"},
    ]
    
    for case in test_cases:
        print(f"\nTesting pair creation: {case['device_a']} + {case['device_b']}")
        
        # Test both orders
        for order in ["normal", "reverse"]:
            if order == "normal":
                device_a, device_b = case["device_a"], case["device_b"]
            else:
                device_a, device_b = case["device_b"], case["device_a"]
            
            try:
                # Create pair via API
                response = requests.post(f"{API_BASE}/api/pairs/create", 
                                       json={
                                           "device_a": device_a,
                                           "device_b": device_b
                                       },
                                       timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    pair_data = data.get("pair", {})
                    pair_id = pair_data.get("id")
                    temp_pair_id = pair_data.get("temp_pair_id")
                    
                    # Check if standardized pair_id matches expected
                    id_correct = pair_id == case["expected_id"]
                    status = "✓" if id_correct else "✗"
                    
                    print(f"  {status} {order.capitalize()} order: pair_id = {pair_id}")
                    print(f"      temp_pair_id = {temp_pair_id}")
                    
                    if not id_correct:
                        print(f"      ERROR: Expected {case['expected_id']}, got {pair_id}")
                        
                else:
                    print(f"  ✗ {order.capitalize()} order: API error {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"  ✗ {order.capitalize()} order: Exception - {e}")

def test_summary_retrieval():
    """Test retrieving summaries with standardized pair IDs"""
    print("\n=== Testing Summary Retrieval API ===")
    
    # First create some pairs and conversations
    test_pairs = [
        {"device_a": "device_33", "device_b": "device_10", "pair_id": "pair_10_33"},
        {"device_a": "device_12", "device_b": "device_15", "pair_id": "pair_12_15"},
    ]
    
    created_pairs = []
    
    for pair_info in test_pairs:
        print(f"\nSetting up pair: {pair_info['device_a']} + {pair_info['device_b']}")
        
        try:
            # Create pair
            response = requests.post(f"{API_BASE}/api/pairs/create", 
                                   json={
                                       "device_a": pair_info["device_a"],
                                       "device_b": pair_info["device_b"]
                                   },
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pair_data = data.get("pair", {})
                pair_info["temp_pair_id"] = pair_data.get("temp_pair_id")
                created_pairs.append(pair_info)
                print(f"  ✓ Created pair: {pair_data.get('id')} (temp: {pair_data.get('temp_pair_id')})")
                
                # Add some conversation input
                input_response = requests.post(f"{API_BASE}/api/conversations/input",
                                             json={
                                                 "device_a": pair_info["device_a"],
                                                 "device_b": pair_info["device_b"],
                                                 "conversation_data": {
                                                     "content": {
                                                         "messages": [{
                                                             "sender": pair_info["device_a"],
                                                             "text": f"Test message from {pair_info['device_a']}"
                                                         }]
                                                     }
                                                 }
                                             },
                                             timeout=10)
                
                if input_response.status_code == 200:
                    print(f"  ✓ Added conversation input")
                else:
                    print(f"  ✗ Failed to add conversation input: {input_response.status_code}")
                    
            else:
                print(f"  ✗ Failed to create pair: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Exception during setup: {e}")
    
    # Wait a bit for processing
    time.sleep(2)
    
    # Now test summary retrieval with different ID formats
    for pair_info in created_pairs:
        print(f"\nTesting summary retrieval for {pair_info['pair_id']}:")
        
        # Test with standardized pair_id
        test_ids = [
            (pair_info["pair_id"], "standardized pair_id"),
            (pair_info["temp_pair_id"], "temp_pair_id"),
        ]
        
        for test_id, id_type in test_ids:
            try:
                response = requests.get(f"{API_BASE}/api/summaries/latest/{test_id}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✓ {id_type}: Retrieved summary successfully")
                    print(f"      Summary length: {len(data.get('summary', ''))} chars")
                elif response.status_code == 404:
                    print(f"  - {id_type}: No summary found (expected for new pairs)")
                else:
                    print(f"  ✗ {id_type}: API error {response.status_code}")
                    
            except Exception as e:
                print(f"  ✗ {id_type}: Exception - {e}")

def test_conversation_endpoints():
    """Test conversation-related endpoints"""
    print("\n=== Testing Conversation Endpoints ===")
    
    try:
        # Test getting all pairs
        response = requests.get(f"{API_BASE}/api/pairs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])
            print(f"  ✓ Retrieved {len(pairs)} device pairs")
            
            # Show some pairs with their IDs
            for i, pair in enumerate(pairs[:3]):
                pair_id = pair.get('id', 'N/A')
                temp_pair_id = pair.get('temp_pair_id', 'N/A')
                device_a = pair.get('device_a', 'N/A')
                device_b = pair.get('device_b', 'N/A')
                print(f"    Pair {i+1}: {device_a} + {device_b} → {pair_id} (temp: {temp_pair_id})")
                
        else:
            print(f"  ✗ Failed to get pairs: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")

def check_api_server():
    """Check if API server is running"""
    try:
        response = requests.get(f"{API_BASE}/api/pairs", timeout=5)
        return response.status_code in [200, 404]  # Either works or no data yet
    except:
        return False

def main():
    print("Testing API Endpoints with Standardized Pair IDs")
    print("=" * 55)
    
    # Check if API server is running
    if not check_api_server():
        print("✗ API server is not running or not accessible at http://localhost:5000")
        print("Please make sure the API server is running with: python api_server.py")
        return
    
    print("✓ API server is accessible")
    
    # Run tests
    test_pair_creation()
    test_summary_retrieval()
    test_conversation_endpoints()
    
    print("\n=== Test Summary ===")
    print("Key API features tested:")
    print("1. Pair creation with standardized IDs")
    print("2. Order independence in pair creation")
    print("3. Summary retrieval with both standardized and temp IDs")
    print("4. Conversation endpoints compatibility")
    print("5. Database consistency across API calls")

if __name__ == "__main__":
    main()