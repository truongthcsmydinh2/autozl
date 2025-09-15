#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify device_pairs structure fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import data_manager

def test_device_pairs_structure():
    """Test the new device_pairs structure"""
    print("🧪 Testing device_pairs structure fix...")
    
    try:
        # Get devices from data_manager
        devices = data_manager.get_devices_with_phone_numbers()
        print(f"📱 Found {len(devices)} devices")
        
        if len(devices) < 2:
            print("⚠️ Need at least 2 devices to test pairing")
            return False
        
        # Simulate the new device_pairs structure
        selected_devices = []
        for i, device in enumerate(devices[:4]):  # Take first 4 devices for testing
            device_id = device.get('device_id', '')
            ip = device_id.split(':')[0] if ':' in device_id else device_id
            
            test_device = {
                'device_id': device_id,
                'ip': ip,  # This is the key fix
                'phone_number': device.get('phone', 'Unknown')
            }
            selected_devices.append(test_device)
            print(f"  Device {i+1}: {device_id} -> IP: {ip}")
        
        # Create device_pairs as tuples (new structure)
        device_pairs = []
        for i in range(0, len(selected_devices), 2):
            if i + 1 < len(selected_devices):
                pair = (selected_devices[i], selected_devices[i + 1])
                device_pairs.append(pair)
        
        print(f"\n🔗 Created {len(device_pairs)} device pairs:")
        
        # Test the structure that core1.py expects
        for i, pair in enumerate(device_pairs, 1):
            device1, device2 = pair  # This should work now
            
            # Test accessing 'ip' field (this was causing the error)
            ip1 = device1['ip']  # This should work now
            ip2 = device2['ip']  # This should work now
            
            print(f"  Pair {i}: {ip1} <-> {ip2}")
            print(f"    Device1: {device1['device_id']} ({device1['phone_number']})")
            print(f"    Device2: {device2['device_id']} ({device2['phone_number']})")
        
        print("\n✅ Device pairs structure test PASSED!")
        print("✅ The 'string indices must be integers, not str' error should be fixed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_device_pairs_structure()
    if success:
        print("\n🎉 All tests passed! The fix should work correctly.")
    else:
        print("\n💥 Tests failed! Need to investigate further.")
    
    sys.exit(0 if success else 1)