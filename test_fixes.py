#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra các fix đã implement
"""

import os
import sys
import json
import time
import threading
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_shared_status_creation():
    """Test tạo shared status file"""
    print("\n=== Test Shared Status Creation ===")
    
    # Import core1 để test
    try:
        import core1
        print("✓ Import core1 thành công")
        
        # Test tạo shared status
        test_status = {
            "device_id": "test_device",
            "status": "running",
            "progress": 50,
            "timestamp": datetime.now().isoformat(),
            "message": "Test message"
        }
        
        core1.update_shared_status("test_device", test_status)
        print("✓ Tạo shared status thành công")
        
        # Kiểm tra file được tạo
        if os.path.exists("shared_status.json"):
            with open("shared_status.json", 'r', encoding='utf-8') as f:
                loaded_status = json.load(f)
                print(f"✓ Đọc shared status: {loaded_status['status']} - {loaded_status['progress']}%")
        else:
            print("✗ Shared status file không được tạo")
            
    except Exception as e:
        print(f"✗ Lỗi test shared status: {e}")

def test_thread_barrier():
    """Test thread barrier functionality"""
    print("\n=== Test Thread Barrier ===")
    
    try:
        import core1
        
        # Test với 3 threads
        num_threads = 3
        barrier = threading.Barrier(num_threads)
        results = []
        
        def worker(thread_id):
            print(f"Thread {thread_id} bắt đầu")
            time.sleep(thread_id * 0.5)  # Simulate different start times
            
            print(f"Thread {thread_id} chờ barrier")
            barrier.wait()  # Wait for all threads
            
            timestamp = time.time()
            results.append((thread_id, timestamp))
            print(f"Thread {thread_id} hoàn thành tại {timestamp}")
        
        # Start threads
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Check synchronization
        if len(results) == num_threads:
            timestamps = [r[1] for r in results]
            time_diff = max(timestamps) - min(timestamps)
            if time_diff < 0.1:  # Within 100ms
                print(f"✓ Thread barrier hoạt động tốt (time diff: {time_diff:.3f}s)")
            else:
                print(f"⚠ Thread barrier có độ trễ: {time_diff:.3f}s")
        else:
            print("✗ Không đủ threads hoàn thành")
            
    except Exception as e:
        print(f"✗ Lỗi test thread barrier: {e}")

def test_ui_checks():
    """Test UI check functions"""
    print("\n=== Test UI Checks ===")
    
    try:
        import core1
        
        # Test các hàm UI check (mock)
        print("Testing UI check functions...")
        
        # Kiểm tra hàm wait_for_ui_ready có tồn tại
        if hasattr(core1, 'wait_for_ui_ready'):
            print("✓ Hàm wait_for_ui_ready tồn tại")
        else:
            print("✗ Hàm wait_for_ui_ready không tồn tại")
            
        # Kiểm tra hàm verify_message_sent có tồn tại
        if hasattr(core1, 'verify_message_sent'):
            print("✓ Hàm verify_message_sent tồn tại")
        else:
            print("✗ Hàm verify_message_sent không tồn tại")
            
        # Kiểm tra hàm capture_error_state có tồn tại
        if hasattr(core1, 'capture_error_state'):
            print("✓ Hàm capture_error_state tồn tại")
        else:
            print("✗ Hàm capture_error_state không tồn tại")
            
        # Kiểm tra hàm safe_ui_operation có tồn tại
        if hasattr(core1, 'safe_ui_operation'):
            print("✓ Hàm safe_ui_operation tồn tại")
        else:
            print("✗ Hàm safe_ui_operation không tồn tại")
            
    except Exception as e:
        print(f"✗ Lỗi test UI checks: {e}")

def test_gui_integration():
    """Test GUI integration với shared status"""
    print("\n=== Test GUI Integration ===")
    
    try:
        # Test import GUI components
        from ui.main_window import MainWindow
        from ui.execution_control import ExecutionStatusWidget
        
        print("✓ Import GUI components thành công")
        
        # Kiểm tra MainWindow có hàm read_shared_status
        if hasattr(MainWindow, 'read_shared_status'):
            print("✓ MainWindow có hàm read_shared_status")
        else:
            print("✗ MainWindow thiếu hàm read_shared_status")
            
        # Kiểm tra ExecutionStatusWidget có hàm update_from_shared_status
        if hasattr(ExecutionStatusWidget, 'update_from_shared_status'):
            print("✓ ExecutionStatusWidget có hàm update_from_shared_status")
        else:
            print("✗ ExecutionStatusWidget thiếu hàm update_from_shared_status")
            
    except Exception as e:
        print(f"✗ Lỗi test GUI integration: {e}")

def cleanup_test_files():
    """Cleanup test files"""
    test_files = ["shared_status.json", "error_capture_test.png"]
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✓ Đã xóa file test: {file}")
            except:
                print(f"⚠ Không thể xóa file: {file}")

def main():
    """Main test function"""
    print("Bắt đầu test các fix đã implement...")
    print("=" * 50)
    
    # Run tests
    test_shared_status_creation()
    test_thread_barrier()
    test_ui_checks()
    test_gui_integration()
    
    print("\n=== Test Summary ===")
    print("Các test đã hoàn thành. Kiểm tra kết quả ở trên.")
    
    # Cleanup
    print("\n=== Cleanup ===")
    cleanup_test_files()
    
    print("\nTest hoàn thành!")

if __name__ == "__main__":
    main()