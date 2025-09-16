#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra parallel execution của multiple device pairs
"""

import sys
import os
import time
from threading import Event

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core1 import run_zalo_automation

def test_progress_callback(message):
    """Test progress callback function"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] PROGRESS: {message}")

def test_status_callback(event_type, device_id, status, details):
    """Test status callback function"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] STATUS: {event_type} | {device_id} | {status} | {details}")

def mock_flow(dev, all_devices=None, stop_event=None, status_callback=None):
    """Mock flow function để test"""
    device_id = dev.device_id
    print(f"🎯 Mock flow bắt đầu cho {device_id}")
    
    # Simulate some work
    for i in range(3):
        if stop_event and stop_event.is_set():
            return "STOPPED"
        
        if status_callback:
            status_callback('device_status', device_id, f'Bước {i+1}/3', f'Đang xử lý bước {i+1}')
        
        time.sleep(2)  # Simulate work
    
    print(f"✅ Mock flow hoàn thành cho {device_id}")
    return "SUCCESS"

def test_parallel_pairs():
    """Test parallel execution với multiple pairs"""
    print("🧪 Bắt đầu test parallel pairs execution...")
    
    # Tạo mock device pairs
    device_pairs = [
        (
            {'ip': '192.168.1.100', 'device_id': '192.168.1.100:5555'},
            {'ip': '192.168.1.101', 'device_id': '192.168.1.101:5555'}
        ),
        (
            {'ip': '192.168.1.102', 'device_id': '192.168.1.102:5555'},
            {'ip': '192.168.1.103', 'device_id': '192.168.1.103:5555'}
        ),
        (
            {'ip': '192.168.1.104', 'device_id': '192.168.1.104:5555'},
            {'ip': '192.168.1.105', 'device_id': '192.168.1.105:5555'}
        )
    ]
    
    print(f"📱 Test với {len(device_pairs)} cặp thiết bị:")
    for i, (dev1, dev2) in enumerate(device_pairs, 1):
        print(f"  Cặp {i}: {dev1['ip']} ↔ {dev2['ip']}")
    
    # Tạo stop event
    stop_event = Event()
    
    # Mock Device class để test
    class MockDevice:
        def __init__(self, device_id):
            self.device_id = device_id
            self.connected = False
        
        def connect(self):
            print(f"🔌 Mock kết nối {self.device_id}")
            time.sleep(0.5)  # Simulate connection time
            self.connected = True
            return True
        
        def disconnect(self):
            print(f"🔌 Mock ngắt kết nối {self.device_id}")
            self.connected = False
    
    # Patch Device class trong core1
    import core1
    original_device = core1.Device
    core1.Device = MockDevice
    
    try:
        # Chạy test
        start_time = time.time()
        
        # Tạo mock conversations và phone_mapping
        conversations = ["Xin chào! Test message từ automation."] * len(device_pairs)
        phone_mapping = {}
        for i, (dev1, dev2) in enumerate(device_pairs):
            phone_mapping[dev1['ip']] = f"090000000{i*2+1}"
            phone_mapping[dev2['ip']] = f"090000000{i*2+2}"
        
        results = run_zalo_automation(
            device_pairs=device_pairs,
            conversations=conversations,
            phone_mapping=phone_mapping,
            progress_callback=test_progress_callback,
            stop_event=stop_event,
            status_callback=test_status_callback
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🏁 Test hoàn thành sau {duration:.1f}s")
        print(f"📊 Kết quả: {len(results)} cặp đã xử lý")
        
        # Phân tích kết quả
        success_count = 0
        for pair_name, result in results.items():
            status = result.get('status', 'unknown')
            print(f"  {pair_name}: {status}")
            if status == 'completed':
                success_count += 1
        
        print(f"✅ Thành công: {success_count}/{len(results)} cặp")
        
        # Kiểm tra parallel execution
        expected_sequential_time = len(device_pairs) * 6  # 6s per pair (3 steps * 2s each)
        if duration < expected_sequential_time * 0.7:  # Nếu nhanh hơn 70% thời gian tuần tự
            print(f"✅ Parallel execution hoạt động tốt! ({duration:.1f}s vs {expected_sequential_time}s tuần tự)")
        else:
            print(f"⚠️ Có thể chưa parallel hoàn toàn ({duration:.1f}s vs {expected_sequential_time}s tuần tự)")
        
        return results
        
    finally:
        # Restore original Device class
        core1.Device = original_device

if __name__ == "__main__":
    try:
        test_parallel_pairs()
    except KeyboardInterrupt:
        print("\n⏹️ Test bị dừng bởi người dùng")
    except Exception as e:
        print(f"❌ Lỗi test: {e}")
        import traceback
        traceback.print_exc()