# Simplified UI Friend Status Fix
# Loại bỏ logic phức tạp - flow kết bạn đã được xử lý trong core1.py

import time
import os
import xml.etree.ElementTree as ET
from typing import Optional

def check_friend_status_from_dump(device_serial: str, wait_for_dump_sec: float = 1.5) -> str:
    """
    Phân tích UI dump để xác định trạng thái bạn bè.
    
    Args:
        device_serial: Serial của device
        wait_for_dump_sec: Thời gian chờ dump
    Returns:
        str: 'ALREADY_FRIEND' nếu đã là bạn bè, 'NEED_FRIEND_REQUEST' nếu chưa
    """
    try:
        # Tạo UI dump
        dump_file = f"ui_dump_{device_serial}.xml"
        os.system(f'adb -s {device_serial} shell uiautomator dump /sdcard/{dump_file}')
        time.sleep(wait_for_dump_sec)
        os.system(f'adb -s {device_serial} pull /sdcard/{dump_file} .')
        
        if not os.path.exists(dump_file):
            print(f"[WARNING] Không tìm thấy UI dump file: {dump_file}")
            return "ALREADY_FRIEND"  # Fallback
            
        # Phân tích XML
        with open(dump_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
            
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Kiểm tra các indicator
        has_send_friend_btn = _has_element_with_resource_id(root, "btn_send_friend_request")
        has_chat_input = _has_element_with_resource_id(root, "chatinput_text")
        
        # Kiểm tra thêm các elements khác để debug
        has_profile_elements = _count_elements_with_text_pattern(root, ["Xem trang cá nhân", "View Profile"])
        has_friend_text = _count_elements_with_text_pattern(root, ["Kết bạn", "Add Friend", "Send Friend Request"])
        
        print(f"[DEBUG] UI Analysis for {device_serial}:")
        print(f"  - btn_send_friend_request: {has_send_friend_btn}")
        print(f"  - chatinput_text: {has_chat_input}")
        print(f"  - profile_elements: {has_profile_elements}")
        print(f"  - friend_text_patterns: {has_friend_text}")
        print(f"  - xml_length: {len(xml_content)} chars")
        
        # Logic quyết định với logging chi tiết
        if has_send_friend_btn:
            print(f"[DEBUG] Decision: NEED_FRIEND_REQUEST (found btn_send_friend_request)")
            return "NEED_FRIEND_REQUEST"
        elif has_chat_input:
            print(f"[DEBUG] Decision: ALREADY_FRIEND (found chatinput_text)")
            return "ALREADY_FRIEND"
        else:
            # Fallback: kiểm tra text patterns
            if has_friend_text > 0:
                print(f"[DEBUG] Decision: NEED_FRIEND_REQUEST (found {has_friend_text} friend text patterns)")
                return "NEED_FRIEND_REQUEST"
            else:
                print(f"[DEBUG] Decision: ALREADY_FRIEND (fallback - no clear indicators)")
                return "ALREADY_FRIEND"
                
    except Exception as e:
        print(f"[ERROR] Lỗi phân tích UI dump: {e}")
        return "ALREADY_FRIEND"  # Fallback safe
    finally:
        # Cleanup
        if 'dump_file' in locals() and os.path.exists(dump_file):
            try:
                os.remove(dump_file)
            except:
                pass

def _has_element_with_resource_id(root, resource_id: str) -> bool:
    """
    Kiểm tra xem có element với resource-id cụ thể không.
    Sử dụng string search để xử lý cả NAF elements.
    """
    # Convert XML tree back to string để search
    import xml.etree.ElementTree as ET
    xml_string = ET.tostring(root, encoding='unicode')
    
    # Sử dụng string search như trong core1.py để xử lý NAF elements
    target_resource_id = f'com.zing.zalo:id/{resource_id}'
    has_element = target_resource_id in xml_string
    
    return has_element

def _count_elements_with_text_pattern(root, patterns: list) -> int:
    """
    Đếm số lượng elements có chứa text patterns.
    """
    count = 0
    for elem in root.iter():
        text = elem.get('text', '')
        content_desc = elem.get('content-desc', '')
        for pattern in patterns:
            if pattern in text or pattern in content_desc:
                count += 1
                break  # Chỉ đếm 1 lần cho mỗi element
    return count

# File này chỉ giữ lại hàm check_friend_status_from_dump để tương thích