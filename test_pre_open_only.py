#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test đơn giản chỉ cho pre-open barrier
"""

import sys
import os
import time
import threading

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core1 import wait_for_group_barrier, signal_ready_at_barrier

def cleanup_barrier_file(barrier_name):
    """Cleanup barrier file"""
    try:
        barrier_file = f"barrier_group_{barrier_name}.json"
        if os.path.exists(barrier_file):
            os.remove(barrier_file)
            print(f"🧹 Đã cleanup barrier file: {barrier_file}")
    except Exception as e:
        print(f"⚠️ Lỗi cleanup barrier file: {e}")

def test_pre_open_barrier_only():
    """Test chỉ pre-open barrier"""
    print("\n=== TEST PRE-OPEN BARRIER ONLY ===")
    
    devices = ["192.168.5.74:5555", "192.168.5.82:5555"]
    barrier_name = "pre_app_open"
    
    # Cleanup trước
    cleanup_barrier_file(barrier_name)
    time.sleep(1)  # Đợi cleanup hoàn tất
    
    def device_worker(device_ip, delay):
        print(f"\n[{device_ip}] Starting with {delay}s delay")
        time.sleep(delay)
        
        print(f"[{device_ip}] Signaling ready for pre-open barrier...")
        signal_ready_at_barrier(barrier_name, device_ip)
        print(f"[{device_ip}] Signal sent, now waiting for barrier...")
        
        result = wait_for_group_barrier(
            group_id=barrier_name,
            device_count=len(devices),
            timeout=30
        )
        
        print(f"[{device_ip}] Pre-open barrier result: {result}")
        return result
    
    results = {}
    
    def worker_wrapper(device_ip, delay):
        results[device_ip] = device_worker(device_ip, delay)
    
    # Tạo threads
    thread1 = threading.Thread(target=worker_wrapper, args=(devices[0], 1))
    thread2 = threading.Thread(target=worker_wrapper, args=(devices[1], 2))
    
    print("\nStarting threads...")
    start_time = time.time()
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    end_time = time.time()
    
    print(f"\n=== RESULTS ===")
    print(f"Total time: {end_time - start_time:.2f}s")
    print(f"Results: {results}")
    
    # Cleanup
    cleanup_barrier_file(barrier_name)
    
    if all(result == True for result in results.values()):
        print("✅ Pre-open barrier test PASSED")
        return True
    else:
        print("❌ Pre-open barrier test FAILED")
        return False

if __name__ == "__main__":
    test_pre_open_barrier_only()