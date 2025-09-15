#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho Enhanced Barrier Synchronization
Kiểm tra cơ chế đồng bộ giữa nhiều máy để đảm bảo tất cả mở Zalo cùng lúc
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime

# Add current directory to path để import core1
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core1 import (
        wait_for_group_barrier, 
        signal_ready_at_barrier, 
        cleanup_barrier_file,
        get_barrier_file_path,
        determine_group_and_role
    )
except ImportError as e:
    print(f"❌ Không thể import từ core1: {e}")
    print("💡 Đảm bảo file core1.py tồn tại trong cùng thư mục")
    sys.exit(1)

class SyncTester:
    """Class để test cơ chế đồng bộ Enhanced Barrier"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, details="", duration=0):
        """Ghi log kết quả test"""
        result = {
            'test_name': test_name,
            'status': status,
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} [{result['timestamp']}] {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        if duration > 0:
            print(f"   ⏱️ Duration: {duration:.2f}s")
        print()
    
    def simulate_device(self, device_ip, group_id, device_count, barrier_timeout=60):
        """Mô phỏng một device tham gia barrier synchronization"""
        start_time = time.time()
        
        try:
            print(f"🚀 Device {device_ip} - Bắt đầu simulation cho nhóm {group_id}")
            
            # Signal ready
            signal_success = signal_ready_at_barrier(group_id, device_ip)
            if not signal_success:
                return False, f"Signal failed for {device_ip}"
            
            # Wait for barrier
            barrier_success = wait_for_group_barrier(group_id, device_count, timeout=barrier_timeout)
            
            duration = time.time() - start_time
            
            if barrier_success:
                return True, f"Device {device_ip} synchronized successfully in {duration:.2f}s"
            else:
                return False, f"Device {device_ip} timeout after {duration:.2f}s"
                
        except Exception as e:
            duration = time.time() - start_time
            return False, f"Device {device_ip} error after {duration:.2f}s: {e}"
    
    def test_basic_barrier_sync(self):
        """Test cơ bản: 2 devices đồng bộ"""
        test_start = time.time()
        group_id = "test_basic"
        device_count = 2
        devices = ["192.168.1.100", "192.168.1.101"]
        
        print(f"🧪 Test Basic Barrier Sync - Nhóm {group_id}")
        print(f"📋 Devices: {devices}")
        
        # Cleanup trước khi test
        cleanup_barrier_file(group_id)
        
        # Tạo threads cho mỗi device
        threads = []
        results = {}
        
        def device_thread(device_ip, delay=0):
            if delay > 0:
                time.sleep(delay)
            success, details = self.simulate_device(device_ip, group_id, device_count, 30)
            results[device_ip] = (success, details)
        
        # Start tất cả threads với delay nhỏ
        for i, device_ip in enumerate(devices):
            delay = i * 0.1  # Delay 0.1s giữa các devices
            thread = threading.Thread(target=device_thread, args=(device_ip, delay))
            threads.append(thread)
            thread.start()
        
        # Wait cho tất cả threads
        for thread in threads:
            thread.join()
        
        # Kiểm tra kết quả
        duration = time.time() - test_start
        all_success = all(result[0] for result in results.values())
        
        if all_success:
            self.log_test("Basic Barrier Sync", "PASS", 
                         f"Tất cả {device_count} devices đồng bộ thành công", duration)
        else:
            failed_devices = [ip for ip, (success, _) in results.items() if not success]
            self.log_test("Basic Barrier Sync", "FAIL", 
                         f"Devices failed: {failed_devices}", duration)
        
        # Cleanup
        cleanup_barrier_file(group_id)
        return all_success
    
    def test_timeout_scenario(self):
        """Test scenario timeout: chỉ 1 device signal ready"""
        test_start = time.time()
        group_id = "test_timeout"
        device_count = 2
        single_device = "192.168.1.200"
        
        print(f"🧪 Test Timeout Scenario - Nhóm {group_id}")
        print(f"📋 Chỉ 1/{device_count} devices sẽ signal ready")
        
        # Cleanup trước khi test
        cleanup_barrier_file(group_id)
        
        # Chỉ 1 device signal ready, timeout ngắn để test nhanh
        success, details = self.simulate_device(single_device, group_id, device_count, 10)
        
        duration = time.time() - test_start
        
        # Trong trường hợp này, expect timeout (success = False)
        if not success and "timeout" in details.lower():
            self.log_test("Timeout Scenario", "PASS", 
                         f"Timeout đúng như mong đợi: {details}", duration)
            result = True
        else:
            self.log_test("Timeout Scenario", "FAIL", 
                         f"Không timeout như mong đợi: {details}", duration)
            result = False
        
        # Cleanup
        cleanup_barrier_file(group_id)
        return result
    
    def test_multiple_groups(self):
        """Test nhiều nhóm đồng thời"""
        test_start = time.time()
        
        print(f"🧪 Test Multiple Groups Simultaneously")
        
        groups = {
            "group_A": ["192.168.1.10", "192.168.1.11"],
            "group_B": ["192.168.1.20", "192.168.1.21"]
        }
        
        # Cleanup tất cả groups
        for group_id in groups.keys():
            cleanup_barrier_file(group_id)
        
        threads = []
        results = {}
        
        def group_thread(group_id, devices):
            group_results = {}
            group_threads = []
            
            def device_thread(device_ip, delay=0):
                if delay > 0:
                    time.sleep(delay)
                success, details = self.simulate_device(device_ip, group_id, len(devices), 30)
                group_results[device_ip] = (success, details)
            
            # Start devices trong group với delay ngẫu nhiên nhỏ
            for i, device_ip in enumerate(devices):
                delay = i * 0.1  # Delay 0.1s giữa các devices
                thread = threading.Thread(target=device_thread, args=(device_ip, delay))
                group_threads.append(thread)
                thread.start()
            
            # Wait cho tất cả devices trong group
            for thread in group_threads:
                thread.join()
            
            results[group_id] = group_results
        
        # Start tất cả groups
        for group_id, devices in groups.items():
            thread = threading.Thread(target=group_thread, args=(group_id, devices))
            threads.append(thread)
            thread.start()
        
        # Wait cho tất cả groups
        for thread in threads:
            thread.join()
        
        # Kiểm tra kết quả
        duration = time.time() - test_start
        all_groups_success = True
        
        for group_id, group_results in results.items():
            group_success = all(result[0] for result in group_results.values())
            if not group_success:
                all_groups_success = False
                failed_devices = [ip for ip, (success, _) in group_results.items() if not success]
                print(f"❌ Group {group_id} failed: {failed_devices}")
            else:
                print(f"✅ Group {group_id} success: {list(group_results.keys())}")
        
        if all_groups_success:
            self.log_test("Multiple Groups", "PASS", 
                         f"Tất cả {len(groups)} groups đồng bộ thành công", duration)
        else:
            self.log_test("Multiple Groups", "FAIL", 
                         "Một số groups failed", duration)
        
        # Cleanup
        for group_id in groups.keys():
            cleanup_barrier_file(group_id)
        
        return all_groups_success
    
    def test_determine_group_and_role(self):
        """Test hàm determine_group_and_role"""
        test_start = time.time()
        
        print(f"🧪 Test Group and Role Determination")
        
        test_cases = [
            {
                'devices': ['192.168.1.100', '192.168.1.101'],
                'expected_groups': 1
            },
            {
                'devices': ['192.168.1.100', '192.168.1.101', '192.168.1.102', '192.168.1.103'],
                'expected_groups': 2
            },
            {
                'devices': ['10.0.0.1', '10.0.0.2', '10.0.0.3'],
                'expected_groups': 2  # 3 devices = 2 groups (2+1)
            }
        ]
        
        all_passed = True
        
        for i, case in enumerate(test_cases):
            devices = case['devices']
            expected_groups = case['expected_groups']
            
            # Test với device đầu tiên
            test_ip = devices[0]
            group_id, role = determine_group_and_role(test_ip, devices)
            
            # Kiểm tra tất cả devices để đếm số groups
            groups_found = set()
            for device in devices:
                gid, _ = determine_group_and_role(device, devices)
                groups_found.add(gid)
            
            actual_groups = len(groups_found)
            
            if actual_groups == expected_groups:
                print(f"✅ Test case {i+1}: {actual_groups} groups (expected {expected_groups})")
            else:
                print(f"❌ Test case {i+1}: {actual_groups} groups (expected {expected_groups})")
                all_passed = False
        
        duration = time.time() - test_start
        
        if all_passed:
            self.log_test("Group and Role Determination", "PASS", 
                         "Tất cả test cases passed", duration)
        else:
            self.log_test("Group and Role Determination", "FAIL", 
                         "Một số test cases failed", duration)
        
        return all_passed
    
    def run_all_tests(self):
        """Chạy tất cả tests"""
        print("🚀 Bắt đầu Enhanced Sync Testing")
        print("=" * 50)
        
        tests = [
            self.test_determine_group_and_role,
            self.test_basic_barrier_sync,
            self.test_timeout_scenario,
            self.test_multiple_groups
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_func.__name__, "ERROR", f"Exception: {e}")
        
        print("=" * 50)
        print(f"📊 Test Summary: {passed}/{total} tests passed")
        
        total_duration = time.time() - self.start_time
        print(f"⏱️ Total duration: {total_duration:.2f}s")
        
        if passed == total:
            print("🎉 Tất cả tests PASSED! Enhanced Sync hoạt động tốt.")
            return True
        else:
            print(f"⚠️ {total - passed} tests FAILED. Cần kiểm tra lại.")
            return False
    
    def print_detailed_results(self):
        """In chi tiết kết quả tests"""
        print("\n📋 Detailed Test Results:")
        print("-" * 60)
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_icon} [{result['timestamp']}] {result['test_name']}")
            print(f"   Status: {result['status']}")
            if result['details']:
                print(f"   Details: {result['details']}")
            if result['duration'] > 0:
                print(f"   Duration: {result['duration']:.2f}s")
            print()

def main():
    """Main function"""
    print("🔧 Enhanced Barrier Synchronization Test Suite")
    print(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = SyncTester()
    
    try:
        success = tester.run_all_tests()
        tester.print_detailed_results()
        
        if success:
            print("\n🎯 Kết luận: Enhanced Sync mechanism hoạt động tốt!")
            print("💡 Tất cả máy trong cùng nhóm sẽ mở Zalo đồng thời.")
            return 0
        else:
            print("\n⚠️ Kết luận: Cần cải tiến thêm Enhanced Sync mechanism.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Test bị dừng bởi user")
        return 1
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())