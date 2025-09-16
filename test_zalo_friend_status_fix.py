#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho Zalo friend status fix
Test các trường hợp:
1. Device serial validation
2. Resource-id detection với 'in' comparison
3. Smart fallback UNKNOWN
4. Error handling và logging
"""

import sys
import os
from pathlib import Path
import xml.etree.ElementTree as ET

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_friend_status_fix import check_friend_status_from_dump, _has_resource_id, _parse_xml

def create_test_xml_dump(device_serial: str, scenario: str) -> Path:
    """Tạo test XML dump cho các scenario khác nhau"""
    dump_dir = Path("debug_dumps")
    dump_dir.mkdir(exist_ok=True)
    
    # Format filename theo pattern
    if ":" in device_serial:
        ip, port = device_serial.split(":", 1)
        filename = f"ui_dump_{ip.replace('.', '_')}_{port}_test.xml"
    else:
        filename = f"ui_dump_{device_serial.replace('.', '_')}_test.xml"
    
    filepath = dump_dir / filename
    
    if scenario == "already_friend":
        xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="" resource-id="com.zing.zalo:id/chatinput_text" class="android.widget.EditText" bounds="[100,800][900,900]" />
  </node>
</hierarchy>'''
    elif scenario == "need_friend_request":
        xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Kết bạn" resource-id="com.zing.zalo:id/btn_send_friend_request" class="android.widget.Button" bounds="[100,800][900,900]" />
  </node>
</hierarchy>'''
    elif scenario == "limited_profile":
        xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Bạn chưa thể xem nhật ký của người này" resource-id="" class="android.widget.TextView" bounds="[100,400][900,500]" />
  </node>
</hierarchy>'''
    else:  # unknown scenario
        xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Some random content" resource-id="com.zing.zalo:id/random_element" class="android.widget.TextView" bounds="[100,400][900,500]" />
  </node>
</hierarchy>'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    return filepath

def test_device_serial_validation():
    """Test validation của device_serial parameter"""
    print("\n=== Test Device Serial Validation ===")
    
    # Test None
    result = check_friend_status_from_dump(None)
    print(f"None device_serial: {result}")
    assert result == "UNKNOWN", f"Expected UNKNOWN, got {result}"
    
    # Test empty string
    result = check_friend_status_from_dump("")
    print(f"Empty device_serial: {result}")
    assert result == "UNKNOWN", f"Expected UNKNOWN, got {result}"
    
    # Test non-string
    result = check_friend_status_from_dump(123)
    print(f"Non-string device_serial: {result}")
    assert result == "UNKNOWN", f"Expected UNKNOWN, got {result}"
    
    print("✅ Device serial validation tests passed")

def test_resource_id_detection():
    """Test resource-id detection với 'in' comparison"""
    print("\n=== Test Resource-ID Detection ===")
    
    # Tạo test XML
    xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="" resource-id="com.zing.zalo:id/chatinput_text" class="android.widget.EditText" />
    <node index="2" text="" resource-id="com.zing.zalo:id/btn_send_friend_request" class="android.widget.Button" />
  </node>
</hierarchy>'''
    
    root = ET.fromstring(xml_content)
    
    # Test 'in' comparison
    assert _has_resource_id(root, "chatinput_text") == True, "Should find chatinput_text"
    assert _has_resource_id(root, "btn_send_friend_request") == True, "Should find btn_send_friend_request"
    assert _has_resource_id(root, "nonexistent") == False, "Should not find nonexistent"
    
    print("✅ Resource-ID detection tests passed")

def test_friend_status_scenarios():
    """Test các scenario khác nhau của friend status"""
    print("\n=== Test Friend Status Scenarios ===")
    
    test_device = "192.168.1.100:5555"
    
    # Test scenario: Already friend
    create_test_xml_dump(test_device, "already_friend")
    result = check_friend_status_from_dump(test_device)
    print(f"Already friend scenario: {result}")
    assert result == "ALREADY_FRIEND", f"Expected ALREADY_FRIEND, got {result}"
    
    # Test scenario: Need friend request
    create_test_xml_dump(test_device, "need_friend_request")
    result = check_friend_status_from_dump(test_device)
    print(f"Need friend request scenario: {result}")
    assert result == "NEED_FRIEND_REQUEST", f"Expected NEED_FRIEND_REQUEST, got {result}"
    
    # Test scenario: Limited profile
    create_test_xml_dump(test_device, "limited_profile")
    result = check_friend_status_from_dump(test_device)
    print(f"Limited profile scenario: {result}")
    assert result == "NEED_FRIEND_REQUEST", f"Expected NEED_FRIEND_REQUEST, got {result}"
    
    # Test scenario: Unknown (smart fallback)
    create_test_xml_dump(test_device, "unknown")
    result = check_friend_status_from_dump(test_device)
    print(f"Unknown scenario: {result}")
    assert result == "UNKNOWN", f"Expected UNKNOWN, got {result}"
    
    print("✅ Friend status scenario tests passed")

def test_no_dump_file():
    """Test trường hợp không có dump file"""
    print("\n=== Test No Dump File ===")
    
    # Test với device không có dump file
    nonexistent_device = "999.999.999.999:5555"
    result = check_friend_status_from_dump(nonexistent_device)
    print(f"No dump file scenario: {result}")
    assert result == "UNKNOWN", f"Expected UNKNOWN, got {result}"
    
    print("✅ No dump file test passed")

def cleanup_test_files():
    """Cleanup test files"""
    dump_dir = Path("debug_dumps")
    if dump_dir.exists():
        for file in dump_dir.glob("*_test.xml"):
            try:
                file.unlink()
                print(f"Cleaned up: {file}")
            except Exception as e:
                print(f"Failed to cleanup {file}: {e}")

def main():
    """Chạy tất cả tests"""
    print("🧪 Starting Zalo Friend Status Fix Tests")
    
    try:
        test_device_serial_validation()
        test_resource_id_detection()
        test_friend_status_scenarios()
        test_no_dump_file()
        
        print("\n🎉 All tests passed successfully!")
        print("\n📋 Summary of fixes implemented:")
        print("✅ Fixed device_serial parameter passing (use device_id)")
        print("✅ Upgraded resource-id detection logic ('==' -> 'in')")
        print("✅ Replaced hard fallback with smart fallback (UNKNOWN)")
        print("✅ Added proper error logging and validation")
        print("✅ Updated core1.py integration to handle UNKNOWN status")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False
    finally:
        cleanup_test_files()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)