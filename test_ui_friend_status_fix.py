#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để verify hàm check_friend_status_from_dump
Chỉ trả về ALREADY_FRIEND hoặc NEED_FRIEND_REQUEST, không bao giờ UNSURE
"""

import os
import sys
import tempfile
from ui_friend_status_fix import check_friend_status_from_dump

def create_test_dump(content, device_ip="192.168.1.100"):
    """Tạo file dump test với nội dung XML"""
    # Tạo thư mục debug_dumps nếu chưa có (theo ui_friend_status_fix.py)
    dumps_dir = "debug_dumps"
    if not os.path.exists(dumps_dir):
        os.makedirs(dumps_dir)
    
    # Tạo file dump với format đúng: ui_dump_{ip}_{timestamp}.xml
    import time
    timestamp = int(time.time())
    ip_formatted = device_ip.replace('.', '_')
    filename = f"{dumps_dir}/ui_dump_{ip_formatted}_{timestamp}.xml"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def test_already_friend_case():
    """Test case: Đã kết bạn (có chatinput_text)"""
    print("\n🧪 Test case: ALREADY_FRIEND")
    
    xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="" resource-id="com.zing.zalo:id/chatinput_text" class="android.widget.EditText" />
    <node index="2" text="Gửi" resource-id="com.zing.zalo:id/btn_send" class="android.widget.Button" />
  </node>
</hierarchy>'''
    
    device_ip = "192.168.1.100"
    dump_file = create_test_dump(xml_content, device_ip)
    
    try:
        result = check_friend_status_from_dump(device_ip)
        print(f"✅ Kết quả: {result}")
        
        if result == "ALREADY_FRIEND":
            print("✅ PASS: Trả về đúng ALREADY_FRIEND")
            return True
        else:
            print(f"❌ FAIL: Mong đợi ALREADY_FRIEND, nhận được {result}")
            return False
    finally:
        # Cleanup
        if os.path.exists(dump_file):
            os.remove(dump_file)

def test_need_friend_request_case():
    """Test case: Cần gửi lời mời kết bạn (có btn_send_friend_request)"""
    print("\n🧪 Test case: NEED_FRIEND_REQUEST")
    
    xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Kết bạn" resource-id="com.zing.zalo:id/btn_send_friend_request" class="android.widget.Button" />
    <node index="2" text="Nhắn tin" resource-id="com.zing.zalo:id/btn_message" class="android.widget.Button" />
  </node>
</hierarchy>'''
    
    device_ip = "192.168.1.101"
    dump_file = create_test_dump(xml_content, device_ip)
    
    try:
        result = check_friend_status_from_dump(device_ip)
        print(f"✅ Kết quả: {result}")
        
        if result == "NEED_FRIEND_REQUEST":
            print("✅ PASS: Trả về đúng NEED_FRIEND_REQUEST")
            return True
        else:
            print(f"❌ FAIL: Mong đợi NEED_FRIEND_REQUEST, nhận được {result}")
            return False
    finally:
        # Cleanup
        if os.path.exists(dump_file):
            os.remove(dump_file)

def test_limited_profile_case():
    """Test case: Profile bị hạn chế (fallback to NEED_FRIEND_REQUEST)"""
    print("\n🧪 Test case: Limited Profile (fallback)")
    
    xml_content = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Người dùng này đã hạn chế thông tin cá nhân" class="android.widget.TextView" />
    <node index="2" text="Quay lại" resource-id="com.zing.zalo:id/btn_back" class="android.widget.Button" />
  </node>
</hierarchy>'''
    
    device_ip = "192.168.1.102"
    dump_file = create_test_dump(xml_content, device_ip)
    
    try:
        result = check_friend_status_from_dump(device_ip)
        print(f"✅ Kết quả: {result}")
        
        if result == "NEED_FRIEND_REQUEST":
            print("✅ PASS: Fallback đúng về NEED_FRIEND_REQUEST")
            return True
        else:
            print(f"❌ FAIL: Mong đợi NEED_FRIEND_REQUEST (fallback), nhận được {result}")
            return False
    finally:
        # Cleanup
        if os.path.exists(dump_file):
            os.remove(dump_file)

def test_no_dump_file_case():
    """Test case: Không có file dump (fallback to NEED_FRIEND_REQUEST)"""
    print("\n🧪 Test case: No dump file (fallback)")
    
    device_ip = "192.168.1.999"  # IP không có file dump
    
    result = check_friend_status_from_dump(device_ip)
    print(f"✅ Kết quả: {result}")
    
    if result == "NEED_FRIEND_REQUEST":
        print("✅ PASS: Fallback đúng về NEED_FRIEND_REQUEST khi không có dump")
        return True
    else:
        print(f"❌ FAIL: Mong đợi NEED_FRIEND_REQUEST (fallback), nhận được {result}")
        return False

def test_never_returns_unsure():
    """Test tổng hợp: Verify hàm không bao giờ trả về UNSURE"""
    print("\n🧪 Test tổng hợp: Verify không bao giờ trả về UNSURE")
    
    test_cases = [
        ("empty_dump", '<?xml version="1.0"?><hierarchy></hierarchy>'),
        ("invalid_xml", 'invalid xml content'),
        ("no_relevant_elements", '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout">
    <node index="1" text="Some random text" resource-id="com.zing.zalo:id/random" class="android.widget.TextView" />
  </node>
</hierarchy>''')
    ]
    
    all_passed = True
    
    for case_name, xml_content in test_cases:
        device_ip = f"192.168.1.{hash(case_name) % 200 + 10}"
        dump_file = create_test_dump(xml_content, device_ip)
        
        try:
            result = check_friend_status_from_dump(device_ip)
            print(f"  📝 {case_name}: {result}")
            
            if result == "UNSURE":
                print(f"  ❌ FAIL: {case_name} trả về UNSURE!")
                all_passed = False
            elif result in ["ALREADY_FRIEND", "NEED_FRIEND_REQUEST"]:
                print(f"  ✅ PASS: {case_name} trả về {result}")
            else:
                print(f"  ❌ FAIL: {case_name} trả về giá trị không hợp lệ: {result}")
                all_passed = False
        finally:
            # Cleanup
            if os.path.exists(dump_file):
                os.remove(dump_file)
    
    return all_passed

def main():
    """Chạy tất cả test cases"""
    print("🚀 Bắt đầu test ui_friend_status_fix.py")
    print("📋 Verify hàm chỉ trả về ALREADY_FRIEND hoặc NEED_FRIEND_REQUEST")
    
    tests = [
        test_already_friend_case,
        test_need_friend_request_case,
        test_limited_profile_case,
        test_no_dump_file_case,
        test_never_returns_unsure
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} gặp lỗi: {e}")
    
    print(f"\n📊 Kết quả test: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 TẤT CẢ TEST PASSED! Hàm hoạt động đúng như mong đợi.")
        print("✅ Xác nhận: Hàm chỉ trả về ALREADY_FRIEND hoặc NEED_FRIEND_REQUEST")
        print("✅ Xác nhận: Hàm không bao giờ trả về UNSURE")
        return True
    else:
        print("❌ CÓ TEST FAILED! Cần kiểm tra lại implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)