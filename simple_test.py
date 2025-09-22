#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script đơn giản để test automation với 10 devices và conversation từ demo.json
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def load_demo_conversations():
    """Load conversations từ demo.json"""
    try:
        with open('demo.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Load được {len(data)} conversations từ demo.json")
        return data
    except Exception as e:
        print(f"❌ Lỗi load demo.json: {e}")
        return None

def create_simple_conversation_data():
    """Tạo conversation data đơn giản từ demo.json"""
    demo_data = load_demo_conversations()
    if not demo_data:
        return None
    
    # Lấy conversation đầu tiên từ demo
    conversations_list = demo_data.get('conversations', [])
    if not conversations_list:
        print("❌ Không tìm thấy conversations trong demo.json")
        return None
        
    first_conversation = conversations_list[0]
    messages = first_conversation.get('conversation', [])
    
    print(f"📝 Sử dụng conversation đầu tiên với {len(messages)} messages")
    
    # Tạo conversation data format đơn giản
    conversation_data = {
        "timestamp": datetime.now().timestamp(),
        "total_pairs": 5,
        "conversations": {}
    }
    
    # Devices list (10 máy trừ .88 và .74)
    devices = [
        "192.168.5.86", "192.168.5.81", "192.168.5.70", "192.168.5.71", "192.168.5.72",
        "192.168.5.73", "192.168.5.75", "192.168.5.76", "192.168.5.77", "192.168.5.78"
    ]
    
    # Phone mapping từ phone_mapping.json
    phone_map = {
        "192.168.5.86": "924648008",
        "192.168.5.81": "924454352",
        "192.168.5.70": "583563439",
        "192.168.5.71": "567513830",
        "192.168.5.72": "921948994",
        "192.168.5.73": "921003813",
        "192.168.5.75": "924648008",
        "192.168.5.76": "582160135",
        "192.168.5.77": "582043409",
        "192.168.5.78": "587191813"
    }
    
    # Tạo 5 pairs
    for i in range(5):
        pair_name = f"pair_{i+1}"
        device_a = devices[i*2]
        device_b = devices[i*2+1]
        
        conversation_data["conversations"][pair_name] = {
            "devices": [
                {
                    "device_id": device_a,
                    "phone": phone_map.get(device_a, "000000000"),
                    "role": "device_a"
                },
                {
                    "device_id": device_b,
                    "phone": phone_map.get(device_b, "000000000"),
                    "role": "device_b"
                }
            ],
            "messages": messages  # Sử dụng messages từ demo.json
        }
    
    return conversation_data

def save_conversation_data(data):
    """Lưu conversation data"""
    try:
        with open('conversation_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ Đã lưu conversation_data.json")
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu conversation data: {e}")
        return False

def run_core1_with_devices():
    """Chạy core1.py với DEVICES environment"""
    devices_list = [
        "192.168.5.86", "192.168.5.81", "192.168.5.70", "192.168.5.71", "192.168.5.72",
        "192.168.5.73", "192.168.5.75", "192.168.5.76", "192.168.5.77", "192.168.5.78"
    ]
    devices_env = ",".join(devices_list)
    
    print(f"🚀 Chạy automation với {len(devices_list)} devices")
    print(f"📱 Devices: {devices_env}")
    
    try:
        # Thiết lập environment
        env = os.environ.copy()
        env['DEVICES'] = devices_env
        
        # Chạy core1.py
        cmd = ["python", "core1.py"]
        print(f"📝 Command: {' '.join(cmd)}")
        
        # Chạy với timeout 300s (5 phút)
        result = subprocess.run(
            cmd, 
            env=env, 
            cwd="y:\\tool auto",
            timeout=300,
            capture_output=True,
            text=True
        )
        
        print(f"📊 Exit code: {result.returncode}")
        
        if result.stdout:
            print("📤 STDOUT:")
            print(result.stdout[-1000:])  # Chỉ hiển thị 1000 ký tự cuối
            
        if result.stderr:
            print("📥 STDERR:")
            print(result.stderr[-1000:])  # Chỉ hiển thị 1000 ký tự cuối
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - automation chạy quá 5 phút")
        return False
    except Exception as e:
        print(f"❌ Lỗi chạy automation: {e}")
        return False

def main():
    """Main function"""
    print("🤖 SIMPLE AUTOMATION TEST")
    print("=" * 30)
    
    # 1. Tạo conversation data từ demo.json
    print("\n📝 BƯỚC 1: TẠO CONVERSATION DATA")
    conversation_data = create_simple_conversation_data()
    if not conversation_data:
        print("❌ Không thể tạo conversation data")
        return False
    
    # 2. Lưu conversation data
    print("\n💾 BƯỚC 2: LƯU CONVERSATION DATA")
    if not save_conversation_data(conversation_data):
        print("❌ Không thể lưu conversation data")
        return False
    
    # 3. Chạy automation
    print("\n🚀 BƯỚC 3: CHẠY AUTOMATION")
    success = run_core1_with_devices()
    
    if success:
        print("\n✅ AUTOMATION HOÀN THÀNH THÀNH CÔNG!")
    else:
        print("\n❌ AUTOMATION THẤT BẠI!")
    
    return success

if __name__ == "__main__":
    main()