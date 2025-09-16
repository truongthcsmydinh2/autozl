#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script chỉ để kiểm tra logic detection btn_send_friend_request
"""

import sys
from core1 import Device, check_btn_send_friend_request_in_dump

def test_detection_logic(device_serial):
    """Test chỉ logic detection không click gì cả"""
    print(f"🧪 Testing detection logic for device: {device_serial}")
    print("=" * 60)
    
    try:
        # Khởi tạo device
        dev = Device(device_serial)
        print(f"✅ Device initialized: {device_serial}")
        print(f"📱 Device ID: {getattr(dev, 'device_id', 'Not found')}")
        
        # Test UI dump analysis
        print("\n🔍 Testing UI dump analysis...")
        has_friend_btn = check_btn_send_friend_request_in_dump(device_serial, debug=True)
        
        if has_friend_btn:
            print("\n✅ btn_send_friend_request detected successfully")
        else:
            print("\n❌ btn_send_friend_request NOT detected")
            
        # Test element_exists fallback
        print("\n🔍 Testing element_exists fallback...")
        exists_result = dev.element_exists(resourceId="com.zing.zalo:id/btn_send_friend_request", timeout=3)
        
        if exists_result:
            print("✅ btn_send_friend_request found via element_exists")
        else:
            print("❌ btn_send_friend_request NOT found via element_exists")
            
        return has_friend_btn
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_detection_only.py <device_serial>")
        print("Example: python test_detection_only.py 192.168.5.76:5555")
        sys.exit(1)
    
    device_serial = sys.argv[1]
    
    print("🧪 Test Detection Logic Only")
    print("=" * 60)
    print(f"📱 Device: {device_serial}")
    print("\nℹ️ This test will:")
    print("  1. Initialize device connection")
    print("  2. Test UI dump analysis")
    print("  3. Test element_exists fallback")
    print("  4. Compare results")
    
    # Chạy test
    success = test_detection_logic(device_serial)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Detection WORKS - btn_send_friend_request found")
    else:
        print("❌ Detection FAILED - btn_send_friend_request not found")
    print("🏁 Test completed")

if __name__ == "__main__":
    main()