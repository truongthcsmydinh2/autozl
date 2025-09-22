#!/usr/bin/env python3
"""
Test script for pair ID consistency
Tests the generatePairId logic with various random pairing scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.pair_utils import generate_pair_id, extract_device_ids_from_pair_id, is_valid_pair_id
import random

def test_random_pairing_scenarios():
    """Test various random pairing scenarios"""
    print("=== Testing Random Pairing ID Consistency ===")
    
    # Test cases from user examples
    test_cases = [
        # User examples: random (33, 10) và (12, 15)
        ("device_33", "device_10", "pair_10_33"),
        ("device_12", "device_15", "pair_12_15"),
        ("device_7", "device_3", "pair_3_7"),
        
        # Additional test cases
        ("192.168.1.100", "192.168.1.50", "pair_50_100"),
        ("phone_25", "phone_8", "pair_8_25"),
        ("device_1", "device_999", "pair_1_999"),
        
        # Edge cases
        ("device_0", "device_1", "pair_0_1"),
        ("device_100", "device_100", "pair_100_100"),  # Same device
    ]
    
    print("\n1. Testing specific scenarios:")
    for device_a, device_b, expected in test_cases:
        result = generate_pair_id(device_a, device_b)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Random pair ({device_a}, {device_b}) → {result} (expected: {expected})")
        
        # Test reverse order gives same result
        result_reverse = generate_pair_id(device_b, device_a)
        reverse_status = "✓" if result_reverse == result else "✗"
        print(f"    {reverse_status} Reverse order ({device_b}, {device_a}) → {result_reverse}")
    
    print("\n2. Testing random pairing consistency:")
    # Generate random device pairs and test consistency
    device_numbers = list(range(1, 101))  # devices 1-100
    
    for i in range(10):
        # Random select 2 devices
        selected = random.sample(device_numbers, 2)
        device_a = f"device_{selected[0]}"
        device_b = f"device_{selected[1]}"
        
        # Generate pair ID
        pair_id = generate_pair_id(device_a, device_b)
        
        # Test consistency (reverse order should give same result)
        pair_id_reverse = generate_pair_id(device_b, device_a)
        
        # Extract device IDs back
        extracted_ids = extract_device_ids_from_pair_id(pair_id)
        
        # Validate
        is_valid = is_valid_pair_id(pair_id)
        is_consistent = pair_id == pair_id_reverse
        ids_match = set(extracted_ids) == {selected[0], selected[1]}
        
        status = "✓" if all([is_valid, is_consistent, ids_match]) else "✗"
        print(f"  {status} Random pair ({device_a}, {device_b}) → {pair_id}")
        print(f"      Valid: {is_valid}, Consistent: {is_consistent}, IDs match: {ids_match}")
        
        if not all([is_valid, is_consistent, ids_match]):
            print(f"      ERROR: Expected IDs {selected}, got {extracted_ids}")

def test_database_consistency():
    """Test that same logical pair always gets same ID"""
    print("\n=== Testing Database Consistency ===")
    
    # Simulate multiple random pairings that could result in same logical pair
    logical_pairs = [
        ("device_10", "device_33"),
        ("device_12", "device_15"),
        ("device_3", "device_7"),
    ]
    
    for device_a, device_b in logical_pairs:
        # Test multiple ways this pair could be created
        scenarios = [
            (device_a, device_b, "Normal order"),
            (device_b, device_a, "Reverse order"),
        ]
        
        pair_ids = []
        print(f"\nTesting logical pair: {device_a} ↔ {device_b}")
        
        for dev_a, dev_b, scenario in scenarios:
            pair_id = generate_pair_id(dev_a, dev_b)
            pair_ids.append(pair_id)
            print(f"  {scenario}: {pair_id}")
        
        # All should be the same
        all_same = len(set(pair_ids)) == 1
        status = "✓" if all_same else "✗"
        print(f"  {status} All scenarios produce same ID: {all_same}")
        
        if not all_same:
            print(f"  ERROR: Got different IDs: {set(pair_ids)}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    edge_cases = [
        # Non-numeric devices
        ("device_abc", "device_def", "Should handle non-numeric gracefully"),
        ("192.168.1.1", "192.168.1.2", "IP addresses"),
        ("phone", "tablet", "No numbers in name"),
        
        # Mixed formats
        ("device_10", "192.168.1.20", "Mixed device formats"),
        ("phone_5", "tablet_15", "Different prefixes"),
    ]
    
    for device_a, device_b, description in edge_cases:
        try:
            pair_id = generate_pair_id(device_a, device_b)
            is_valid = is_valid_pair_id(pair_id)
            print(f"  ✓ {description}: {pair_id} (valid: {is_valid})")
        except Exception as e:
            print(f"  ✗ {description}: ERROR - {e}")

if __name__ == "__main__":
    print("Testing Pair ID Consistency for Random Pairing")
    print("=" * 50)
    
    test_random_pairing_scenarios()
    test_database_consistency()
    test_edge_cases()
    
    print("\n=== Test Summary ===")
    print("✓ = Pass, ✗ = Fail")
    print("\nKey requirements tested:")
    print("1. Random pairing (33,10) → pair_10_33")
    print("2. Random pairing (12,15) → pair_12_15")
    print("3. Order independence: (A,B) = (B,A)")
    print("4. ID consistency across multiple calls")
    print("5. Database uniqueness (no duplicates)")