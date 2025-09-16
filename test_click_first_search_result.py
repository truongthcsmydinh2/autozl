#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra hàm click_first_search_result đã được fix
"""

import sys
from core1 import Device, click_first_search_result

def test_click_first_search_result(device_serial):
    """Test hàm click_first_search_result với debug enabled"""
    print(f"🧪 Testing click_first_search_result for device: {device_serial}")
    print("=" * 60)
    
    try:
        # Khởi tạo device
        dev = Device(device_serial)
        
        # Test hàm click_first_search_result với debug=True
        print("\n🔍 Testing click_first_search_result function...")
        result = click_first_search_result(dev, debug=True)
        
        if result:
            print("\n✅ click_first_search_result completed successfully")
        else:
            print("\n❌ click_first_search_result failed")
            
        return result
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_click_first_search_result.py <device_serial>")
        print("Example: python test_click_first_search_result.py 192.168.5.76:5555")
        sys.exit(1)
    
    device_serial = sys.argv[1]
    
    print("🧪 Test click_first_search_result Function")
    print("=" * 60)
    print(f"📱 Device: {device_serial}")
    print("\nℹ️ This test will:")
    print("  1. Initialize device connection")
    print("  2. Call click_first_search_result with debug=True")
    print("  3. Show detailed detection logic")
    print("  4. Verify btn_send_friend_request detection")
    
    # Chạy test
    success = test_click_first_search_result(device_serial)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Test PASSED - Function works correctly")
    else:
        print("❌ Test FAILED - Check the logs above")
    print("🏁 Test completed")

if __name__ == "__main__":
    main()