#!/usr/bin/env python3
"""Test script để verify fix device serial format conversion."""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_device_serial_conversion():
    """Test device serial format conversion logic."""
    print("[DEBUG] 🧪 Testing device serial format conversion...")
    
    # Test cases
    test_cases = [
        ("192_168_5_76_5555", "192.168.5.76:5555"),
        ("192_168_1_100_8080", "192.168.1.100:8080"),
        ("10_0_0_1_5555", "10.0.0.1:5555"),
        ("emulator-5554", "emulator-5554"),  # Should remain unchanged
        ("192.168.5.76:5555", "192.168.5.76:5555"),  # Already correct format
    ]
    
    for input_serial, expected_output in test_cases:
        print(f"\n[DEBUG] 📱 Testing: {input_serial}")
        
        # Apply conversion logic
        device_serial = input_serial
        
        # Fix device serial format conversion
        # Convert from 192_168_5_76_5555 to 192.168.5.76:5555
        if '_' in device_serial and device_serial.count('_') >= 4:
            parts = device_serial.split('_')
            if len(parts) >= 5:
                # Reconstruct IP:PORT format
                ip_parts = parts[:4]  # First 4 parts are IP
                port = parts[4] if len(parts) > 4 else '5555'
                device_serial = ".".join(ip_parts) + ":" + port
                print(f"[DEBUG] 🔧 Converted: {input_serial} -> {device_serial}")
        
        # Verify result
        if device_serial == expected_output:
            print(f"[DEBUG] ✅ PASS: {device_serial}")
        else:
            print(f"[DEBUG] ❌ FAIL: Expected {expected_output}, got {device_serial}")

def test_integration_with_send_friend_request():
    """Test integration với send_friend_request_fix."""
    print("\n[DEBUG] 🔧 Testing integration with send_friend_request_fix...")
    
    from ui_friend_status_fix import send_friend_request as send_friend_request_fix
    
    # Mock device_id từ core1.py
    mock_device_id = "192_168_5_76_5555"
    
    # Apply conversion logic (same as in core1.py)
    device_serial = mock_device_id
    
    if '_' in device_serial and device_serial.count('_') >= 4:
        parts = device_serial.split('_')
        if len(parts) >= 5:
            ip_parts = parts[:4]
            port = parts[4] if len(parts) > 4 else '5555'
            device_serial = ".".join(ip_parts) + ":" + port
            print(f"[DEBUG] 🔧 Converted device_serial: {mock_device_id} -> {device_serial}")
    
    # Test với converted device_serial
    print(f"[DEBUG] 📞 Calling send_friend_request_fix with: {device_serial}")
    
    try:
        result = send_friend_request_fix(device_serial, max_retries=1, debug=True)
        print(f"[DEBUG] 📋 Result: {result}")
        
        if result:
            print(f"[DEBUG] ✅ SUCCESS: Friend request sent successfully")
        else:
            print(f"[DEBUG] ❌ FAILED: Friend request failed")
            
    except Exception as e:
        print(f"[DEBUG] ❌ ERROR: {e}")

if __name__ == "__main__":
    print("[DEBUG] 🔧 Device Serial Fix Test Tool")
    print("[DEBUG] " + "="*50)
    
    # Test 1: Device serial conversion logic
    test_device_serial_conversion()
    
    # Test 2: Integration test
    test_integration_with_send_friend_request()
    
    print("\n[DEBUG] ✅ All tests completed")