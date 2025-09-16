#!/usr/bin/env python3
"""Debug script để test hàm send_friend_request với NAF element handling."""

import sys
import os
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui_friend_status_fix import send_friend_request, _latest_dump_file, _parse_xml, _get_element_bounds

def debug_naf_element_issue():
    """Debug chi tiết vấn đề NAF element với btn_send_friend_request."""
    print("[DEBUG] 🔍 Starting NAF element debug analysis...")
    
    # Test với device serial từ UI dumps
    device_serial = "192.168.5.76:5555"
    
    print(f"[DEBUG] 📱 Testing with device: {device_serial}")
    
    # 1. Kiểm tra UI dump mới nhất
    print("[DEBUG] 📂 Checking latest UI dump...")
    dump_path = _latest_dump_file(device_serial)
    
    if not dump_path or not dump_path.exists():
        print(f"[ERROR] ❌ No UI dump found for {device_serial}")
        return False
    
    print(f"[DEBUG] 📄 Found UI dump: {dump_path.name}")
    
    # 2. Parse XML và kiểm tra NAF element
    root = _parse_xml(dump_path)
    if root is None:
        print(f"[ERROR] ❌ Failed to parse XML: {dump_path}")
        return False
    
    # 3. Tìm btn_send_friend_request element
    print("[DEBUG] 🔎 Searching for btn_send_friend_request element...")
    
    found_element = False
    for node in root.iter("node"):
        resource_id = node.attrib.get('resource-id', '')
        if 'btn_send_friend_request' in resource_id:
            found_element = True
            naf_value = node.attrib.get('NAF', 'false')
            bounds = node.attrib.get('bounds', '')
            clickable = node.attrib.get('clickable', 'false')
            enabled = node.attrib.get('enabled', 'false')
            visible = node.attrib.get('visible-to-user', 'false')
            
            print(f"[DEBUG] ✅ Found element:")
            print(f"[DEBUG]   - resource-id: {resource_id}")
            print(f"[DEBUG]   - NAF: {naf_value}")
            print(f"[DEBUG]   - bounds: {bounds}")
            print(f"[DEBUG]   - clickable: {clickable}")
            print(f"[DEBUG]   - enabled: {enabled}")
            print(f"[DEBUG]   - visible-to-user: {visible}")
            
            # Parse bounds để lấy center coordinates
            bounds_tuple = _get_element_bounds(root, "btn_send_friend_request")
            if bounds_tuple:
                x1, y1, x2, y2 = bounds_tuple
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                print(f"[DEBUG]   - center coordinates: ({center_x}, {center_y})")
            
            break
    
    if not found_element:
        print("[ERROR] ❌ btn_send_friend_request element not found in UI dump")
        return False
    
    # 4. Test các strategies click
    print("[DEBUG] 🧪 Testing click strategies...")
    
    # Strategy 1: Normal element click (sẽ thất bại với NAF=true)
    print("[DEBUG] 📱 Testing Strategy 1: Normal element click")
    from ui_friend_status_fix import _click_element_by_resource_id
    result1 = _click_element_by_resource_id(device_serial, "btn_send_friend_request")
    print(f"[DEBUG] Strategy 1 result: {result1}")
    
    time.sleep(1)
    
    # Strategy 2: Coordinate click từ bounds
    print("[DEBUG] 📍 Testing Strategy 2: Coordinate click from bounds")
    bounds_tuple = _get_element_bounds(root, "btn_send_friend_request")
    if bounds_tuple:
        x1, y1, x2, y2 = bounds_tuple
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        from ui_friend_status_fix import _click_coordinates
        result2 = _click_coordinates(device_serial, center_x, center_y)
        print(f"[DEBUG] Strategy 2 result: {result2}")
    else:
        print("[DEBUG] ❌ Could not get bounds for Strategy 2")
        result2 = False
    
    time.sleep(1)
    
    # Strategy 3: Hardcoded coordinates
    print("[DEBUG] 🎯 Testing Strategy 3: Hardcoded coordinates")
    hardcoded_x = 933
    hardcoded_y = 1186
    result3 = _click_coordinates(device_serial, hardcoded_x, hardcoded_y)
    print(f"[DEBUG] Strategy 3 result: {result3}")
    
    # 5. Tổng kết
    print("[DEBUG] 📊 Summary:")
    print(f"[DEBUG]   - Strategy 1 (normal click): {result1}")
    print(f"[DEBUG]   - Strategy 2 (bounds click): {result2}")
    print(f"[DEBUG]   - Strategy 3 (hardcoded): {result3}")
    
    if any([result1, result2, result3]):
        print("[DEBUG] ✅ At least one strategy succeeded")
        return True
    else:
        print("[DEBUG] ❌ All strategies failed")
        return False

def test_full_send_friend_request():
    """Test hàm send_friend_request hoàn chỉnh."""
    print("[DEBUG] 🚀 Testing full send_friend_request function...")
    
    device_serial = "192.168.5.76:5555"
    result = send_friend_request(device_serial, max_retries=1, debug=True)
    
    print(f"[DEBUG] 📋 Final result: {result}")
    return result

if __name__ == "__main__":
    print("[DEBUG] 🔧 Friend Request NAF Element Debug Tool")
    print("[DEBUG] " + "="*50)
    
    # Test 1: Debug NAF element issue
    print("\n[DEBUG] 🧪 Test 1: NAF Element Analysis")
    debug_naf_element_issue()
    
    print("\n" + "="*50)
    
    # Test 2: Full function test
    print("\n[DEBUG] 🧪 Test 2: Full Function Test")
    test_full_send_friend_request()
    
    print("\n[DEBUG] ✅ Debug completed")