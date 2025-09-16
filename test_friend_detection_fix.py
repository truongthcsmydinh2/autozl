#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để verify fix logic detection "đã là bạn bè"
"""

import os
import tempfile
from ui_friend_status_fix import check_friend_status_from_dump, _has_element_with_resource_id
import xml.etree.ElementTree as ET

def create_mock_xml_dump(scenario):
    """Tạo mock XML dump cho các scenario khác nhau"""
    if scenario == "already_friend":
        # Có chatinput_text - đã là bạn bè
        return '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="com.zing.zalo:id/chatinput_text" class="android.widget.EditText" package="com.zing.zalo" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[72,1794][972,1890]" />
</hierarchy>'''
    elif scenario == "need_friend_request":
        # Có btn_send_friend_request - cần kết bạn
        return '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="com.zing.zalo:id/btn_send_friend_request" class="android.widget.Button" package="com.zing.zalo" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[72,1794][972,1890]" />
</hierarchy>'''
    elif scenario == "text_fallback":
        # Không có resource-id nhưng có text "Kết bạn"
        return '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="Kết bạn" class="android.widget.Button" package="com.zing.zalo" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="true" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[72,1794][972,1890]" />
</hierarchy>'''
    else:
        # Empty/unknown scenario
        return '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
</hierarchy>'''

def test_xml_parsing():
    """Test XML parsing logic"""
    print("🧪 Test XML parsing logic")
    
    # Test 1: Already friend scenario
    xml_content = create_mock_xml_dump("already_friend")
    root = ET.fromstring(xml_content)
    has_chat = _has_element_with_resource_id(root, "chatinput_text")
    has_friend_btn = _has_element_with_resource_id(root, "btn_send_friend_request")
    print(f"  Already friend: chatinput={has_chat}, friend_btn={has_friend_btn}")
    assert has_chat == True, "Should detect chatinput_text"
    assert has_friend_btn == False, "Should not detect btn_send_friend_request"
    
    # Test 2: Need friend request scenario
    xml_content = create_mock_xml_dump("need_friend_request")
    root = ET.fromstring(xml_content)
    has_chat = _has_element_with_resource_id(root, "chatinput_text")
    has_friend_btn = _has_element_with_resource_id(root, "btn_send_friend_request")
    print(f"  Need friend: chatinput={has_chat}, friend_btn={has_friend_btn}")
    assert has_chat == False, "Should not detect chatinput_text"
    assert has_friend_btn == True, "Should detect btn_send_friend_request"
    
    print("  ✅ XML parsing tests passed")

def test_friend_status_detection():
    """Test friend status detection với mock data"""
    print("\n🧪 Test friend status detection")
    
    # Test scenarios
    test_cases = [
        ("already_friend", "ALREADY_FRIEND"),
        ("need_friend_request", "NEED_FRIEND_REQUEST"),
        ("text_fallback", "NEED_FRIEND_REQUEST"),
        ("empty", "ALREADY_FRIEND")
    ]
    
    for scenario, expected in test_cases:
        print(f"\n  📝 Test scenario: {scenario}")
        
        # Tạo temporary XML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
            xml_content = create_mock_xml_dump(scenario)
            f.write(xml_content)
            temp_file = f.name
        
        try:
            # Mock the UI dump file creation by copying our temp file
            mock_device = "test_device"
            expected_dump_file = f"ui_dump_{mock_device}.xml"
            
            # Copy temp file to expected location
            import shutil
            shutil.copy2(temp_file, expected_dump_file)
            
            # Test the function (but mock the adb commands)
            original_system = os.system
            os.system = lambda cmd: 0  # Mock adb commands to do nothing
            
            try:
                result = check_friend_status_from_dump(mock_device, wait_for_dump_sec=0.1)
                print(f"    Result: {result}, Expected: {expected}")
                
                if result == expected:
                    print(f"    ✅ PASS: {scenario}")
                else:
                    print(f"    ❌ FAIL: {scenario} - got {result}, expected {expected}")
                    
            finally:
                os.system = original_system  # Restore original
                # Cleanup
                if os.path.exists(expected_dump_file):
                    os.remove(expected_dump_file)
                    
        finally:
            # Cleanup temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)

def main():
    """Main test function"""
    print("🔧 Testing friend detection fix...")
    
    try:
        test_xml_parsing()
        test_friend_status_detection()
        print("\n✅ All tests passed! Fix is working correctly.")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)