#!/usr/bin/env python3
"""
Check existing pairs in database
"""

from utils.conversation_manager import ConversationManager
from utils.pair_utils import generate_pair_id

def check_existing_pairs():
    print("=== Checking Existing Pairs in Database ===")
    
    cm = ConversationManager()
    
    # Test what pair_id would be generated for our test devices
    test_devices = [
        ("device_1758355858_1", "device_1758355858_2"),
        ("device_33", "device_10"),
        ("device_7", "device_3")
    ]
    
    for device_a, device_b in test_devices:
        expected_pair_id = generate_pair_id(device_a, device_b)
        print(f"\nTesting: {device_a} + {device_b}")
        print(f"Expected pair_id: {expected_pair_id}")
        
        # Check if this pair_id already exists
        existing_pair = cm.pair_manager.get_pair_by_id(expected_pair_id)
        if existing_pair:
            print(f"❌ EXISTING PAIR FOUND:")
            print(f"  ID: {existing_pair.id}")
            print(f"  Device A: {existing_pair.device_a}")
            print(f"  Device B: {existing_pair.device_b}")
            print(f"  Temp ID: {existing_pair.temp_pair_id}")
        else:
            print(f"✅ No existing pair found - would create new")
    
    # Also check what happens with the problematic pair_1_2
    print(f"\n=== Checking problematic pair_1_2 ===")
    problematic_pair = cm.pair_manager.get_pair_by_id("pair_1_2")
    if problematic_pair:
        print(f"Found pair_1_2:")
        print(f"  Device A: {problematic_pair.device_a}")
        print(f"  Device B: {problematic_pair.device_b}")
        print(f"  Temp ID: {problematic_pair.temp_pair_id}")
        
        # Check what pair_id would be generated for these devices
        regenerated_id = generate_pair_id(problematic_pair.device_a, problematic_pair.device_b)
        print(f"  Regenerated ID: {regenerated_id}")
        
        if regenerated_id != "pair_1_2":
            print(f"  ❌ MISMATCH: Current ID 'pair_1_2' != Regenerated '{regenerated_id}'")
        else:
            print(f"  ✅ ID matches regenerated")
    else:
        print(f"No pair_1_2 found")

if __name__ == "__main__":
    check_existing_pairs()