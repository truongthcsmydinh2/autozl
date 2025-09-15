#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để verify các sửa đổi đồng bộ hoạt động đúng
- Test barrier sync khi mở Zalo
- Test báo cáo trạng thái hoàn thành đúng
- Test cả 2 máy mở Zalo đồng thời
"""

import sys
import time
import threading
from core1 import run_zalo_automation, wait_for_group_barrier, cleanup_barrier_file

def test_progress_callback():
    """Test progress callback để đảm bảo báo cáo đúng"""
    print("\n=== TEST PROGRESS CALLBACK ===")
    
    progress_messages = []
    
    def mock_progress_callback(message):
        timestamp = time.strftime("%H:%M:%S")
        progress_msg = f"[{timestamp}] {message}"
        progress_messages.append(progress_msg)
        print(f"PROGRESS: {progress_msg}")
    
    # Test với 2 máy
    device_pairs = [[
        "192.168.5.74:5555",
        "192.168.5.82:5555"
    ]]
    
    print(f"Testing với device pairs: {device_pairs}")
    
    start_time = time.time()
    results = run_zalo_automation(
        device_pairs=device_pairs,
        progress_callback=mock_progress_callback
    )
    end_time = time.time()
    
    print(f"\n=== KẾT QUẢ TEST ===")
    print(f"Thời gian chạy: {end_time - start_time:.2f}s")
    print(f"Số progress messages: {len(progress_messages)}")
    print(f"Results: {results}")
    
    print(f"\n=== PROGRESS MESSAGES ===")
    for msg in progress_messages:
        print(msg)
    
    # Kiểm tra message cuối cùng có phải là hoàn thành không
    if progress_messages:
        last_message = progress_messages[-1]
        if "🏁" in last_message:
            print("✅ Progress callback báo hoàn thành đúng")
        else:
            print("❌ Progress callback không báo hoàn thành")
    
    return results

def test_barrier_sync():
    """Test barrier sync mechanism"""
    print("\n=== TEST BARRIER SYNC ===")
    
    devices = ["192.168.5.74:5555", "192.168.5.82:5555"]
    barrier_name = "test_barrier"
    
    # Cleanup barrier file trước test
    cleanup_barrier_file(barrier_name)
    
    def device_worker(device_ip, delay):
        print(f"Device {device_ip} starting with {delay}s delay")
        time.sleep(delay)  # Simulate different start times
        
        print(f"Device {device_ip} reaching barrier...")
        # Signal ready first
        from core1 import signal_ready_at_barrier
        signal_ready_at_barrier(barrier_name, device_ip)
        
        # Then wait for barrier
        result = wait_for_group_barrier(
            group_id=barrier_name,
            device_count=len(devices),
            timeout=30
        )
        print(f"Device {device_ip} barrier result: {result}")
        return result
    
    # Tạo threads cho 2 devices với delay khác nhau
    threads = []
    results = {}
    
    def worker_wrapper(device_ip, delay):
        results[device_ip] = device_worker(device_ip, delay)
    
    # Device 1 delay 2s, Device 2 delay 5s
    thread1 = threading.Thread(target=worker_wrapper, args=(devices[0], 2))
    thread2 = threading.Thread(target=worker_wrapper, args=(devices[1], 5))
    
    start_time = time.time()
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    end_time = time.time()
    
    print(f"\n=== KẾT QUẢ BARRIER SYNC ===")
    print(f"Thời gian total: {end_time - start_time:.2f}s")
    print(f"Results: {results}")
    
    # Cleanup
    cleanup_barrier_file(barrier_name)
    
    # Verify cả 2 devices đều True
    if all(result == True for result in results.values()):
        print("✅ Barrier sync hoạt động đúng")
        return True
    else:
        print("❌ Barrier sync có vấn đề")
        return False
    
    return results

def test_app_open_barrier():
    """Test barrier sync cho việc mở app"""
    print("\n=== TEST APP OPEN BARRIER ===")
    
    devices = ["192.168.5.74:5555", "192.168.5.82:5555"]
    
    # Test PRE-OPEN barrier sync (mới thêm)
    pre_barrier_name = "pre_app_open"
    post_barrier_name = "app_opened"
    
    # Cleanup barrier files
    cleanup_barrier_file(pre_barrier_name)
    cleanup_barrier_file(post_barrier_name)
    
    def simulate_app_open(device_ip, open_delay):
        print(f"Device {device_ip} testing pre-open barrier...")
        # Signal ready for pre-open first
        from core1 import signal_ready_at_barrier
        signal_ready_at_barrier(pre_barrier_name, device_ip)
        
        # Wait for pre-open barrier với timeout dài hơn
        print(f"Device {device_ip} waiting for pre-open barrier with {len(devices)} devices...")
        pre_result = wait_for_group_barrier(
            group_id=pre_barrier_name,
            device_count=len(devices),
            timeout=60  # Tăng timeout lên 60s
        )
        print(f"Device {device_ip} pre-open barrier result: {pre_result}")
        
        if not pre_result:
            print(f"❌ Device {device_ip} pre-open barrier FAILED - continuing anyway")
        else:
            print(f"✅ Device {device_ip} pre-open barrier SUCCESS")
        
        print(f"Device {device_ip} simulating app open with {open_delay}s delay")
        time.sleep(open_delay)  # Simulate app opening time
        
        print(f"Device {device_ip} app opened, waiting for post-open barrier...")
        # Signal ready for post-open
        signal_ready_at_barrier(post_barrier_name, device_ip)
        
        # Then wait for post-open barrier
        post_result = wait_for_group_barrier(
            group_id=post_barrier_name,
            device_count=len(devices),
            timeout=60
        )
        print(f"Device {device_ip} post-open barrier result: {post_result}")
        
        final_result = pre_result and post_result
        print(f"Device {device_ip} FINAL RESULT: pre={pre_result}, post={post_result}, final={final_result}")
        return final_result
    
    threads = []
    results = {}
    
    def worker_wrapper(device_ip, delay):
        results[device_ip] = simulate_app_open(device_ip, delay)
    
    # Simulate khác nhau thời gian mở app
    thread1 = threading.Thread(target=worker_wrapper, args=(devices[0], 3))
    thread2 = threading.Thread(target=worker_wrapper, args=(devices[1], 7))
    
    start_time = time.time()
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    end_time = time.time()
    
    print(f"\n=== KẾT QUẢ APP OPEN BARRIER ===")
    print(f"Thời gian total: {end_time - start_time:.2f}s")
    print(f"Results: {results}")
    
    # Cleanup
    cleanup_barrier_file(pre_barrier_name)
    cleanup_barrier_file(post_barrier_name)
    
    if all(result == True for result in results.values()):
        print("✅ App open barrier sync (pre + post) hoạt động đúng")
        return True
    else:
        print("❌ App open barrier sync có vấn đề")
        return False
    
    return results

def main():
    """Chạy tất cả tests"""
    print("🧪 BẮT ĐẦU TEST CÁC SỬA ĐỔI ĐỒNG BỘ")
    print("=" * 50)
    
    try:
        # Test 1: Barrier sync cơ bản
        barrier_results = test_barrier_sync()
        
        # Test 2: App open barrier sync
        app_barrier_results = test_app_open_barrier()
        
        # Test 3: Progress callback (chỉ test nếu có devices thực)
        print("\n⚠️ Để test progress callback với devices thực, uncomment dòng dưới:")
        print("# progress_results = test_progress_callback()")
        
        print("\n" + "=" * 50)
        print("🏁 HOÀN THÀNH TẤT CẢ TESTS")
        
        # Tổng kết - sử dụng kết quả đã có
        all_success = barrier_results and app_barrier_results
        
        if not barrier_results:
            print("❌ Barrier sync test failed")
        else:
            print("✅ Barrier sync test passed")
        
        if not app_barrier_results:
            print("❌ App open barrier test failed")
        else:
            print("✅ App open barrier test passed")
        
        if all_success:
            print("✅ TẤT CẢ TESTS THÀNH CÔNG")
        else:
            print("❌ MỘT SỐ TESTS THẤT BẠI")
            
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()