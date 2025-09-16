#!/usr/bin/env python3
"""Debug script để kiểm tra device_serial format và integration issue."""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_friend_status_fix import _latest_dump_file

def check_device_serial_formats():
    """Kiểm tra các format device serial khác nhau."""
    print("[DEBUG] 🔍 Checking device serial formats...")
    
    # Các format có thể có
    possible_formats = [
        "192.168.5.76:5555",
        "192_168_5_76_5555",
        "192.168.5.76_5555", 
        "emulator-5554",
        "192.168.5.77:5555"
    ]
    
    print("[DEBUG] 📂 Checking debug_dumps directory for available UI dumps...")
    
    debug_dumps_dir = Path("debug_dumps")
    if not debug_dumps_dir.exists():
        print("[ERROR] ❌ debug_dumps directory not found")
        return
    
    # List all UI dump files
    ui_dumps = list(debug_dumps_dir.glob("ui_dump_*.xml"))
    print(f"[DEBUG] 📄 Found {len(ui_dumps)} UI dump files:")
    
    device_serials_found = set()
    for dump_file in ui_dumps:
        # Extract device serial from filename
        # Format: ui_dump_192_168_5_76_5555_timestamp.xml
        parts = dump_file.stem.split('_')
        if len(parts) >= 6:
            # Reconstruct device serial
            ip_parts = parts[2:6]  # 192, 168, 5, 76
            port = parts[6] if len(parts) > 6 else "5555"
            
            # Try different formats
            format1 = f"{'.'.join(ip_parts[0:4])}:{port}"  # 192.168.5.76:5555
            format2 = f"{'_'.join(ip_parts[0:4])}_{port}"   # 192_168_5_76_5555
            
            device_serials_found.add(format1)
            device_serials_found.add(format2)
            
            print(f"[DEBUG]   - {dump_file.name} -> {format1} or {format2}")
    
    print(f"\n[DEBUG] 🎯 Unique device serials found: {sorted(device_serials_found)}")
    
    # Test each format with _latest_dump_file
    print("\n[DEBUG] 🧪 Testing _latest_dump_file with different formats:")
    
    for device_serial in sorted(device_serials_found):
        try:
            dump_path = _latest_dump_file(device_serial)
            if dump_path and dump_path.exists():
                print(f"[DEBUG] ✅ {device_serial} -> {dump_path.name}")
            else:
                print(f"[DEBUG] ❌ {device_serial} -> No dump found")
        except Exception as e:
            print(f"[DEBUG] ❌ {device_serial} -> Error: {e}")

def simulate_core1_integration():
    """Simulate cách core1.py gọi send_friend_request_fix."""
    print("\n[DEBUG] 🔧 Simulating core1.py integration...")
    
    # Mock device object
    class MockDevice:
        def __init__(self, device_id):
            self.device_id = device_id
    
    # Test với các device_id formats khác nhau
    test_device_ids = [
        "192.168.5.76:5555",
        "192_168_5_76_5555",
        "emulator-5554"
    ]
    
    from ui_friend_status_fix import send_friend_request as send_friend_request_fix
    
    for device_id in test_device_ids:
        print(f"\n[DEBUG] 📱 Testing with device_id: {device_id}")
        
        # Simulate core1.py logic
        mock_dev = MockDevice(device_id)
        device_serial = mock_dev.device_id
        
        print(f"[DEBUG]   - device_serial passed to send_friend_request_fix: {device_serial}")
        
        try:
            result = send_friend_request_fix(device_serial, max_retries=1, debug=True)
            print(f"[DEBUG]   - Result: {result}")
        except Exception as e:
            print(f"[DEBUG]   - Error: {e}")

if __name__ == "__main__":
    print("[DEBUG] 🔧 Device Serial Format Debug Tool")
    print("[DEBUG] " + "="*50)
    
    # Test 1: Check device serial formats
    check_device_serial_formats()
    
    # Test 2: Simulate core1 integration
    simulate_core1_integration()
    
    print("\n[DEBUG] ✅ Debug completed")