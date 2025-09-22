#!/usr/bin/env python3
"""
Test script to verify pair ID generation fix
"""

from utils.pair_utils import generate_pair_id

def test_pair_id_generation():
    """Test pair ID generation with various device formats"""
    
    print("Testing pair ID generation fix:")
    print("=" * 50)
    
    # Test cases that were problematic
    test_cases = [
        # Old format devices (should extract the ID part, not timestamp)
        ("device_1758355653_1", "device_1758355653_2", "pair_1_2"),
        ("device_1758356565_3", "device_1758356565_5", "pair_3_5"),
        ("device_1758356560_1", "device_1758356560_2", "pair_1_2"),
        
        # IP format devices (should work as before)
        ("192.168.4.158:8080", "192.168.4.81", "pair_81_158"),
        ("192.168.5.82:5555", "192.168.5.88:5555", "pair_82_88"),
        
        # Simple device format
        ("device_33", "device_10", "pair_10_33"),
        ("device_7", "device_3", "pair_3_7"),
        
        # Mixed formats
        ("device_1758355653_1", "192.168.4.81", "pair_1_81"),
    ]
    
    print("\n1. Testing generate_pair_id function:")
    

    for device1, device2, expected in test_cases:
        result = generate_pair_id(device1, device2)
        status = "✅" if result == expected else "❌"
        print(f"{status} generate_pair_id('{device1}', '{device2}')")
        print(f"   Result: {result}")
        print(f"   Expected: {expected}")
        print()
    
    print("\n3. Testing problematic cases from database:")
    problematic_cases = [
        # These should now generate consistent IDs
        ("device_1758356565_3", "device_1758356565_5"),
        ("device_1758356560_1", "device_1758356560_2"),
        ("device_1758356487_3", "device_1758356487_5"),
        ("device_1758356482_1", "device_1758356482_2"),
    ]
    
    for device1, device2 in problematic_cases:
        result = generate_pair_id(device1, device2)
        print(f"generate_pair_id('{device1}', '{device2}') = {result}")

if __name__ == "__main__":
    # Import the function we need to test
    import sys
    sys.path.append('.')
    
    # Test the public API only
    
    test_pair_id_generation()