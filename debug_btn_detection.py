#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script để kiểm tra btn_send_friend_request detection
"""

import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core1 import *

def dump_and_analyze_ui(device_serial, debug=True):
    """Dump UI và phân tích có btn_send_friend_request không - sử dụng hàm mới"""
    try:
        if debug: print(f"[DEBUG] 🔍 Analyzing UI for device: {device_serial}")
        
        # Sử dụng hàm check_btn_send_friend_request_in_dump đã được fix
        has_btn = check_btn_send_friend_request_in_dump(device_serial, debug=True)
        
        if has_btn:
            if debug: print(f"[DEBUG] ✅ btn_send_friend_request detected successfully")
            return {
                'has_btn': True,
                'detection_method': 'check_btn_send_friend_request_in_dump'
            }
        else:
            if debug: print(f"[DEBUG] ❌ btn_send_friend_request NOT detected")
            return {
                'has_btn': False,
                'detection_method': 'check_btn_send_friend_request_in_dump'
            }
            
    except Exception as e:
        if debug: print(f"[DEBUG] ❌ Error in dump_and_analyze_ui: {e}")
        return None

def test_element_detection_methods(device_serial, debug=True):
    """Test các methods detection khác nhau"""
    try:
        if debug: print(f"[DEBUG] 🧪 Testing detection methods for: {device_serial}")
        
        # Method 1: uiautomator2 element_exists
        try:
            import uiautomator2 as u2
            dev = u2.connect(device_serial)
            
            method1_result = dev(resourceId="com.zing.zalo:id/btn_send_friend_request").exists(timeout=3)
            if debug: print(f"[DEBUG] Method 1 (u2.element_exists): {method1_result}")
            
            # Method 2: uiautomator2 with different timeout
            method2_result = dev(resourceId="com.zing.zalo:id/btn_send_friend_request").exists(timeout=0.5)
            if debug: print(f"[DEBUG] Method 2 (u2.quick_check): {method2_result}")
            
            # Method 3: Check all elements
            all_elements = dev.dump_hierarchy()
            method3_result = 'btn_send_friend_request' in all_elements
            if debug: print(f"[DEBUG] Method 3 (dump_hierarchy): {method3_result}")
            
        except Exception as e:
            if debug: print(f"[DEBUG] ❌ uiautomator2 methods failed: {e}")
        
        # Method 4: Direct adb command
        try:
            adb_cmd = f'adb -s {device_serial} shell uiautomator dump && adb -s {device_serial} shell cat /sdcard/window_dump.xml'
            result = os.popen(adb_cmd).read()
            method4_result = 'btn_send_friend_request' in result
            if debug: print(f"[DEBUG] Method 4 (direct_adb): {method4_result}")
        except Exception as e:
            if debug: print(f"[DEBUG] ❌ Direct adb method failed: {e}")
            
    except Exception as e:
        if debug: print(f"[DEBUG] ❌ Error in test_element_detection_methods: {e}")

def main():
    """Main function để test detection"""
    print("🔍 Debug btn_send_friend_request Detection")
    print("=" * 50)
    
    # Lấy device serial từ args hoặc default
    device_serial = sys.argv[1] if len(sys.argv) > 1 else "192.168.5.76:5555"
    print(f"📱 Device: {device_serial}")
    
    # 1. Dump và analyze UI
    print("\n1. UI Dump Analysis:")
    dump_result = dump_and_analyze_ui(device_serial)
    
    if dump_result:
        if dump_result['has_btn']:
            print(f"✅ btn_send_friend_request detected using {dump_result['detection_method']}")
        else:
            print(f"❌ btn_send_friend_request NOT detected using {dump_result['detection_method']}")
    else:
        print("❌ UI dump analysis failed")
    
    # 2. Test detection methods
    print("\n2. Detection Methods Test:")
    test_element_detection_methods(device_serial)
    
    # 3. Recommendations
    print("\n3. Recommendations:")
    if dump_result and dump_result['has_btn']:
        print("✅ btn_send_friend_request found - should proceed with friend request flow")
        print("💡 The element was detected using improved UI dump analysis")
        print("📝 Check core1.py click_first_search_result function for implementation")
    else:
        print("❌ No btn_send_friend_request found - check UI state")
        print("💡 Possible reasons:")
        print("   - User is already friends")
        print("   - UI is in different state")
        print("   - Element is not visible/loaded yet")
    
    print("\n" + "=" * 50)
    print("🏁 Debug completed")

if __name__ == "__main__":
    main()