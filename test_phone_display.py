#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra phone mapping display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import data_manager

def test_phone_mapping_display():
    """Test xem phone mapping có hiển thị đúng không"""
    print("=== Testing Phone Mapping Display ===")
    
    # Reload data
    data_manager.reload_data()
    
    # Test get_devices_with_phone_numbers
    devices = data_manager.get_devices_with_phone_numbers()
    print(f"\n📱 Found {len(devices)} devices:")
    
    for i, device in enumerate(devices, 1):
        print(f"{i}. Device ID: {device['device_id']}")
        print(f"   IP: {device['ip']}")
        print(f"   Phone: '{device['phone']}'")
        print(f"   Note: '{device['note']}'")
        print()
    
    # Test phone mapping directly
    phone_mapping = data_manager.get_phone_mapping()
    print(f"\n📞 Phone mapping ({len(phone_mapping)} entries):")
    for device_id, phone in phone_mapping.items():
        print(f"   {device_id} -> '{phone}'")
    
    # Test device data directly
    device_data = data_manager.get_device_data()
    print(f"\n📋 Device data ({len(device_data)} entries):")
    for device_id, data in device_data.items():
        print(f"   {device_id} -> phone: '{data.get('phone', '')}', note: '{data.get('note', '')}'")

if __name__ == "__main__":
    test_phone_mapping_display()