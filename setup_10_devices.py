#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để cấu hình 10 devices cho automation test
Loại trừ 192.168.5.88 và 192.168.5.74
"""

import json
import os
from typing import List, Dict

def get_available_devices() -> List[str]:
    """Lấy danh sách 10 devices từ phone mapping, loại trừ .5.88 và .5.74"""
    
    # Load phone mapping hiện tại
    phone_mapping_file = "phone_mapping.json"
    if not os.path.exists(phone_mapping_file):
        print(f"❌ Không tìm thấy file {phone_mapping_file}")
        return []
    
    with open(phone_mapping_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    phone_mapping = data.get('phone_mapping', {})
    
    # Lọc devices có IP 192.168.5.x và có phone number
    available_devices = []
    excluded_ips = ['192.168.5.88', '192.168.5.74']
    
    for device_ip, phone in phone_mapping.items():
        # Chỉ lấy IP không có port
        if ':' not in device_ip and device_ip.startswith('192.168.5.'):
            if device_ip not in excluded_ips and phone and phone.strip():
                available_devices.append(device_ip)
    
    # Lấy tối đa 10 devices
    return available_devices[:10]

def create_device_config(devices: List[str]) -> Dict:
    """Tạo cấu hình cho 10 devices"""
    
    # Load phone mapping
    with open("phone_mapping.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    phone_mapping = data.get('phone_mapping', {})
    
    config = {
        "devices": [],
        "phone_mapping": {},
        "total_devices": len(devices)
    }
    
    for i, device_ip in enumerate(devices, 1):
        phone = phone_mapping.get(device_ip, '')
        
        device_config = {
            "id": i,
            "ip": device_ip,
            "port": "5555",
            "phone": phone,
            "status": "ready"
        }
        
        config["devices"].append(device_config)
        config["phone_mapping"][f"{device_ip}:5555"] = phone
    
    return config

def save_test_config(config: Dict):
    """Lưu cấu hình test"""
    config_file = "test_10_devices_config.json"
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Đã lưu cấu hình test vào {config_file}")
    return config_file

def main():
    print("🔧 THIẾT LẬP 10 DEVICES CHO AUTOMATION TEST")
    print("=" * 50)
    
    # Lấy danh sách devices
    devices = get_available_devices()
    
    if len(devices) < 10:
        print(f"⚠️  Chỉ tìm thấy {len(devices)} devices khả dụng (cần 10)")
        print("📋 Devices khả dụng:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device}")
    else:
        print(f"✅ Tìm thấy {len(devices)} devices khả dụng")
    
    # Hiển thị danh sách 10 devices sẽ sử dụng
    selected_devices = devices[:10]
    print(f"\n📱 10 DEVICES SẼ SỬ DỤNG:")
    print("-" * 30)
    
    for i, device in enumerate(selected_devices, 1):
        print(f"  {i:2d}. {device}")
    
    # Tạo cấu hình
    config = create_device_config(selected_devices)
    
    # Lưu cấu hình
    config_file = save_test_config(config)
    
    print(f"\n📊 THỐNG KÊ:")
    print(f"  - Tổng devices: {config['total_devices']}")
    print(f"  - Loại trừ: 192.168.5.88, 192.168.5.74")
    print(f"  - File cấu hình: {config_file}")
    
    return config

if __name__ == "__main__":
    main()