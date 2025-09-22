#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để thêm devices vào phone mapping để có đủ 10 máy
"""

import json
import os
from typing import Dict

def generate_phone_numbers(count: int) -> list:
    """Tạo danh sách số điện thoại giả cho test"""
    base_numbers = [
        "583563439", "567513830", "921948994", "921003813", 
        "924648008", "582160135", "582043409", "587191813",
        "924454352", "928903551", "569924311", "924981260"
    ]
    
    # Tạo thêm số nếu cần
    phones = base_numbers[:]
    for i in range(len(base_numbers), count):
        # Tạo số điện thoại giả với format 9xxxxxxxx
        phone = f"9{str(i+20).zfill(8)}"
        phones.append(phone)
    
    return phones[:count]

def add_devices_to_mapping():
    """Thêm devices vào phone mapping"""
    
    # Load phone mapping hiện tại
    phone_mapping_file = "phone_mapping.json"
    
    if os.path.exists(phone_mapping_file):
        with open(phone_mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"phone_mapping": {}, "timestamp": 0, "created_by": "add_devices_script"}
    
    phone_mapping = data.get('phone_mapping', {})
    
    # Danh sách IP cần thêm (loại trừ .88 và .74)
    excluded_ips = ['192.168.5.88', '192.168.5.74']
    target_ips = []
    
    # Tạo danh sách IP từ .70 đến .95
    for i in range(70, 96):
        ip = f"192.168.5.{i}"
        if ip not in excluded_ips:
            target_ips.append(ip)
    
    # Lấy 10 IP đầu tiên chưa có trong mapping
    new_ips = []
    for ip in target_ips:
        if ip not in phone_mapping and len(new_ips) < 10:
            new_ips.append(ip)
    
    # Tạo số điện thoại cho các IP mới
    new_phones = generate_phone_numbers(len(new_ips))
    
    print(f"🔧 THÊM {len(new_ips)} DEVICES VÀO PHONE MAPPING")
    print("=" * 50)
    
    # Thêm vào mapping
    for i, ip in enumerate(new_ips):
        phone = new_phones[i]
        phone_mapping[ip] = phone
        phone_mapping[f"{ip}:5555"] = phone  # Thêm cả format có port
        print(f"  ✅ {ip} -> {phone}")
    
    # Cập nhật timestamp
    import time
    data['phone_mapping'] = phone_mapping
    data['timestamp'] = time.time()
    data['created_by'] = "add_devices_script"
    
    # Lưu lại file
    with open(phone_mapping_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Đã cập nhật {phone_mapping_file}")
    print(f"📊 Tổng devices trong mapping: {len([k for k in phone_mapping.keys() if ':' not in k and k.startswith('192.168.5.')])}") 
    
    return new_ips

def main():
    print("📱 THÊM DEVICES VÀO PHONE MAPPING")
    print("=" * 40)
    
    new_devices = add_devices_to_mapping()
    
    if new_devices:
        print(f"\n🎯 Đã thêm {len(new_devices)} devices mới")
        print("📋 Danh sách devices mới:")
        for i, ip in enumerate(new_devices, 1):
            print(f"  {i:2d}. {ip}")
    else:
        print("ℹ️  Không có devices mới nào được thêm")
    
    print("\n✅ Hoàn thành!")

if __name__ == "__main__":
    main()