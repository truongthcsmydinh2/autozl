#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra hàm dump_ui_and_log
"""

import sys
import os

# Add current directory to path để import core1
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core1 import Device, dump_ui_and_log

def test_ui_dump():
    """Test hàm dump_ui_and_log"""
    print("=== Testing UI Dump Function ===")
    
    # Tạo device object
    device_id = "192.168.5.74:5555"  # Thay đổi theo device thực tế
    dev = Device(device_id)
    
    print(f"Connecting to device: {device_id}")
    if not dev.connect():
        print("❌ Failed to connect to device")
        return False
    
    print("✅ Device connected successfully")
    
    # Test dump UI function
    print("Testing dump_ui_and_log function...")
    result = dump_ui_and_log(dev, debug=True)
    
    if result:
        print("✅ UI dump function works correctly")
        print("Check debug_dumps/ folder for output files")
    else:
        print("❌ UI dump function failed")
    
    dev.disconnect()
    return result

if __name__ == "__main__":
    test_ui_dump()