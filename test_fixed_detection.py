#!/usr/bin/env python3
# Test script để kiểm tra fix cho hàm _has_element_with_resource_id

import xml.etree.ElementTree as ET
import sys
import os

# Import hàm đã fix
sys.path.append('.')
from ui_friend_status_fix import _has_element_with_resource_id, _count_elements_with_text_pattern

def test_ui_dump_detection(dump_file_path):
    """
    Test detection logic với UI dump file
    """
    print(f"\n🧪 Testing detection với file: {dump_file_path}")
    
    if not os.path.exists(dump_file_path):
        print(f"❌ File không tồn tại: {dump_file_path}")
        return False
    
    try:
        # Đọc và parse XML
        with open(dump_file_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        root = ET.fromstring(xml_content)
        
        # Test các hàm detection
        has_send_friend_btn = _has_element_with_resource_id(root, "btn_send_friend_request")
        has_chat_input = _has_element_with_resource_id(root, "chatinput_text")
        has_friend_text = _count_elements_with_text_pattern(root, ["Bạn chưa thể xem nhật ký", "chưa là bạn bè"])
        
        print(f"📊 Kết quả detection:")
        print(f"  - btn_send_friend_request: {has_send_friend_btn}")
        print(f"  - chatinput_text: {has_chat_input}")
        print(f"  - friend_text_patterns: {has_friend_text}")
        
        # Kiểm tra string search trực tiếp
        has_btn_string_search = 'com.zing.zalo:id/btn_send_friend_request' in xml_content
        print(f"  - string_search_verification: {has_btn_string_search}")
        
        # Logic quyết định
        if has_send_friend_btn:
            decision = "NEED_FRIEND_REQUEST"
        elif has_chat_input:
            decision = "ALREADY_FRIEND"
        else:
            decision = "ALREADY_FRIEND (fallback)"
        
        print(f"🎯 Decision: {decision}")
        
        # Verify với expected result
        expected_decision = "NEED_FRIEND_REQUEST"  # Cả 2 dumps đều có btn_send_friend_request
        if decision.startswith(expected_decision):
            print(f"✅ PASS: Detection chính xác")
            return True
        else:
            print(f"❌ FAIL: Expected {expected_decision}, got {decision}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi test: {e}")
        return False

def main():
    print("🚀 Bắt đầu test fixed detection logic")
    
    # Test với 2 UI dumps
    dump_files = [
        "y:\\tool auto\\debug_dumps\\ui_dump_192_168_5_77_5555_1757993760.xml",
        "y:\\tool auto\\debug_dumps\\ui_dump_192_168_5_77_5555_1757993758.xml"
    ]
    
    all_passed = True
    
    for dump_file in dump_files:
        result = test_ui_dump_detection(dump_file)
        if not result:
            all_passed = False
    
    print(f"\n🏁 Kết quả tổng thể:")
    if all_passed:
        print(f"✅ TẤT CẢ TESTS PASSED - Fix hoạt động chính xác!")
    else:
        print(f"❌ CÓ TESTS FAILED - Cần kiểm tra thêm")
    
    return all_passed

if __name__ == "__main__":
    main()