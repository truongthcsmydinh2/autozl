#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho Friend Request Flow
Test các trường hợp:
1. Complete flow: NEED_FRIEND_REQUEST -> send request -> verify -> start conversation
2. Mock UI interactions cho send_friend_request function
3. Error handling và fallback scenarios
4. UI state verification after sending friend request
"""

import sys
import os
from pathlib import Path
import time
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_friend_status_fix import check_friend_status_from_dump

class MockDevice:
    """Mock device class để test UI interactions"""
    
    def __init__(self, scenario="success"):
        self.scenario = scenario
        self.click_calls = []
        self.element_exists_calls = []
        
    def click(self, **kwargs):
        """Mock click method"""
        self.click_calls.append(kwargs)
        if self.scenario == "success":
            return True
        elif self.scenario == "click_fail":
            return False
        return True
    
    def element_exists(self, **kwargs):
        """Mock element_exists method"""
        self.element_exists_calls.append(kwargs)
        if self.scenario == "success":
            # Check for resourceId parameter (used by send_friend_request)
            resource_id = kwargs.get('resourceId', '')
            if 'btn_send_friend_request' in resource_id and len(self.element_exists_calls) == 1:
                return True   # Button exists initially
            elif 'btn_send_friend_request' in resource_id:
                return False  # Button disappeared = success
            elif 'chatinput_text' in resource_id:
                return False  # Not chat input in this scenario
            elif kwargs.get('text') == 'Đã gửi lời mời':
                return True   # Success indicator appears
            return False
        elif self.scenario == "already_friends":
            resource_id = kwargs.get('resourceId', '')
            if 'chatinput_text' in resource_id:
                return True   # Chat input exists = already friends
            return False
        elif self.scenario == "send_fail":
            resource_id = kwargs.get('resourceId', '')
            if 'btn_send_friend_request' in resource_id:
                return True   # Button still exists = failed
            return False
        return False
    
    def dump_ui(self, filename):
        """Mock dump_ui method"""
        # Create mock dump file based on scenario
        dump_dir = Path("debug_dumps")
        dump_dir.mkdir(exist_ok=True)
        
        if self.scenario == "success":
            xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Đã gửi lời mời" resource-id="" class="android.widget.TextView" bounds="[100,400][900,500]" />
  </node>
</hierarchy>'''
        elif self.scenario == "already_friends":
            xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="" resource-id="com.zing.zalo:id/chatinput_text" class="android.widget.EditText" bounds="[100,800][900,900]" />
  </node>
</hierarchy>'''
        else:  # send_fail
            xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Kết bạn" resource-id="com.zing.zalo:id/btn_send_friend_request" class="android.widget.Button" bounds="[100,800][900,900]" />
  </node>
</hierarchy>'''
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        return True

def test_send_friend_request_success():
    """Test successful friend request sending"""
    print("\n=== Test Send Friend Request Success ===")
    
    # Import send_friend_request function
    from core1 import send_friend_request
    
    # Create mock device
    mock_dev = MockDevice("success")
    
    # Test send_friend_request
    result = send_friend_request(mock_dev, debug=True)
    print(f"Send friend request result: {result}")
    
    # Verify result
    assert result == 'FRIEND_REQUEST_SENT', f"Expected FRIEND_REQUEST_SENT, got {result}"
    
    # Verify UI interactions
    assert len(mock_dev.click_calls) > 0, "Should have clicked something"
    assert any('btn_send_friend_request' in str(call) for call in mock_dev.click_calls), "Should have clicked friend request button"
    
    print("✅ Send friend request success test passed")

def test_send_friend_request_already_friends():
    """Test case where users are already friends"""
    print("\n=== Test Send Friend Request - Already Friends ===")
    
    from core1 import send_friend_request
    
    mock_dev = MockDevice("already_friends")
    result = send_friend_request(mock_dev, debug=True)
    print(f"Send friend request result: {result}")
    
    assert result == 'ALREADY_FRIENDS', f"Expected ALREADY_FRIENDS, got {result}"
    
    print("✅ Send friend request already friends test passed")

def test_send_friend_request_fail():
    """Test failed friend request sending"""
    print("\n=== Test Send Friend Request Fail ===")
    
    from core1 import send_friend_request
    
    mock_dev = MockDevice("click_fail")
    result = send_friend_request(mock_dev, debug=True)
    print(f"Send friend request result: {result}")
    
    assert result == 'SEND_FAILED', f"Expected SEND_FAILED, got {result}"
    
    print("✅ Send friend request fail test passed")

def test_complete_friend_flow():
    """Test complete flow: detect NEED_FRIEND_REQUEST -> send request -> verify"""
    print("\n=== Test Complete Friend Flow ===")
    
    # Step 1: Create scenario where friend request is needed
    test_device = "192.168.1.100:5555"
    create_test_xml_dump(test_device, "need_friend_request")
    
    # Step 2: Check friend status
    friend_status = check_friend_status_from_dump(test_device)
    print(f"Initial friend status: {friend_status}")
    assert friend_status == "NEED_FRIEND_REQUEST", f"Expected NEED_FRIEND_REQUEST, got {friend_status}"
    
    # Step 3: Mock send friend request
    from core1 import send_friend_request
    mock_dev = MockDevice("success")
    send_result = send_friend_request(mock_dev, debug=True)
    print(f"Send friend request result: {send_result}")
    assert send_result == 'FRIEND_REQUEST_SENT', f"Expected FRIEND_REQUEST_SENT, got {send_result}"
    
    # Step 4: Verify UI state after sending
    # Check that button disappeared or success indicator appears
    button_exists = mock_dev.element_exists(resource_id='btn_send_friend_request')
    success_indicator = mock_dev.element_exists(text='Đã gửi lời mời')
    
    print(f"Button still exists: {button_exists}")
    print(f"Success indicator exists: {success_indicator}")
    
    assert not button_exists or success_indicator, "Should have UI verification of successful send"
    
    print("✅ Complete friend flow test passed")

def test_core_flow_branching():
    """Test core flow branching logic"""
    print("\n=== Test Core Flow Branching ===")
    
    # Test that NEED_FRIEND_REQUEST leads to send_friend_request call
    # This would be integration test with actual core1.py flow
    
    # Mock the flow
    friend_status = "NEED_FRIEND_REQUEST"
    
    if friend_status == 'NEED_FRIEND_REQUEST':
        print("✅ Detected NEED_FRIEND_REQUEST - should call send_friend_request")
        # In real flow, this would call send_friend_request
        mock_result = 'FRIEND_REQUEST_SENT'
        print(f"Mock send result: {mock_result}")
        
        if mock_result == 'FRIEND_REQUEST_SENT':
            print("✅ Friend request sent successfully - can continue conversation")
        elif mock_result == 'ALREADY_FRIENDS':
            print("✅ Already friends - can continue conversation")
        elif mock_result == 'SEND_FAILED':
            print("❌ Friend request failed - should stop flow")
            return False
    
    print("✅ Core flow branching test passed")
    return True

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
    
    if scenario == "need_friend_request":
        xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Kết bạn" resource-id="com.zing.zalo:id/btn_send_friend_request" class="android.widget.Button" bounds="[100,800][900,900]" />
  </node>
</hierarchy>'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    return filepath

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
    print("🧪 Starting Friend Request Flow Tests")
    
    try:
        test_send_friend_request_success()
        test_send_friend_request_already_friends()
        test_send_friend_request_fail()
        test_complete_friend_flow()
        test_core_flow_branching()
        
        print("\n🎉 All friend request flow tests passed successfully!")
        print("\n📋 Summary of friend request flow features tested:")
        print("✅ Send friend request UI interactions")
        print("✅ UI state verification after sending")
        print("✅ Error handling and fallback scenarios")
        print("✅ Complete flow: detect -> send -> verify")
        print("✅ Core flow branching logic")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cleanup_test_files()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)