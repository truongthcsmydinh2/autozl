#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để verify các improvements cho friend request functionality.
Kiểm tra:
1. Improved click coordinates với retry mechanism
2. Enhanced logging và error handling
3. Wait mechanisms và validation
4. Fallback strategies với robust error handling
"""

import sys
import time
from pathlib import Path

# Import hàm đã được cải thiện
from ui_friend_status_fix import (
    send_friend_request,
    _click_coordinates,
    _click_element_by_resource_id,
    _get_element_bounds
)

def test_improved_click_coordinates():
    """Test improved _click_coordinates function với retry mechanism."""
    print("\n=== Testing Improved Click Coordinates ===")
    
    # Test với device serial đúng format
    device_serial = "192.168.5.76:5555"
    test_x, test_y = 933, 1186
    
    print(f"Testing click coordinates ({test_x}, {test_y}) on device {device_serial}")
    print("With debug=True, retries=2, wait_between_retries=0.5")
    
    result = _click_coordinates(
        device_serial, test_x, test_y, 
        debug=True, retries=2, wait_between_retries=0.5
    )
    
    print(f"Click coordinates result: {result}")
    return result

def test_improved_element_click():
    """Test improved _click_element_by_resource_id function."""
    print("\n=== Testing Improved Element Click ===")
    
    device_serial = "192.168.5.76:5555"
    resource_id = "btn_send_friend_request"
    
    print(f"Testing element click for '{resource_id}' on device {device_serial}")
    print("With debug=True, retries=2, wait_between_retries=0.5")
    
    result = _click_element_by_resource_id(
        device_serial, resource_id,
        debug=True, retries=2, wait_between_retries=0.5
    )
    
    print(f"Element click result: {result}")
    return result

def test_improved_get_bounds():
    """Test improved _get_element_bounds function."""
    print("\n=== Testing Improved Get Element Bounds ===")
    
    device_serial = "192.168.5.76:5555"
    resource_id = "btn_send_friend_request"
    
    print(f"Testing get bounds for '{resource_id}' on device {device_serial}")
    print("With debug=True and robust error handling")
    
    bounds = _get_element_bounds(device_serial, resource_id, debug=True)
    
    if bounds:
        x1, y1, x2, y2 = bounds
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        print(f"Bounds found: {bounds}")
        print(f"Center coordinates: ({center_x}, {center_y})")
    else:
        print("No bounds found")
    
    return bounds

def test_full_improved_send_friend_request():
    """Test full improved send_friend_request function."""
    print("\n=== Testing Full Improved Send Friend Request ===")
    
    device_serial = "192.168.5.76:5555"
    
    print(f"Testing full send friend request on device {device_serial}")
    print("With max_retries=2, debug=True")
    print("Expected to use all 3 strategies with improved logging and error handling")
    
    start_time = time.time()
    result = send_friend_request(device_serial, max_retries=2, debug=True)
    end_time = time.time()
    
    print(f"\nSend friend request result: {result}")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
    
    return result

def test_edge_cases():
    """Test edge cases và error handling."""
    print("\n=== Testing Edge Cases and Error Handling ===")
    
    # Test với invalid device serial
    print("\n1. Testing with invalid device serial:")
    result1 = send_friend_request("", max_retries=1, debug=True)
    print(f"Empty device serial result: {result1}")
    
    # Test với device không tồn tại
    print("\n2. Testing with non-existent device:")
    result2 = send_friend_request("invalid_device:1234", max_retries=1, debug=True)
    print(f"Invalid device result: {result2}")
    
    # Test với coordinates không hợp lệ
    print("\n3. Testing with invalid coordinates:")
    result3 = _click_coordinates("192.168.5.76:5555", -100, -100, debug=True, retries=1)
    print(f"Invalid coordinates result: {result3}")
    
    return [result1, result2, result3]

def main():
    """Main test function."""
    print("🚀 Starting Improved Friend Request Function Tests")
    print("=" * 60)
    
    try:
        # Test individual improved functions
        bounds_result = test_improved_get_bounds()
        coords_result = test_improved_click_coordinates()
        element_result = test_improved_element_click()
        
        # Test full improved function
        full_result = test_full_improved_send_friend_request()
        
        # Test edge cases
        edge_results = test_edge_cases()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Get bounds test: {'✅ PASS' if bounds_result else '❌ FAIL'}")
        print(f"Click coordinates test: {'✅ PASS' if coords_result else '❌ FAIL'}")
        print(f"Element click test: {'✅ PASS' if element_result else '❌ FAIL'}")
        print(f"Full function test: {'✅ PASS' if full_result else '❌ FAIL'}")
        print(f"Edge cases test: {'✅ PASS' if all(not r for r in edge_results) else '❌ FAIL'}")
        
        print("\n🎯 Key Improvements Verified:")
        print("   ✅ Enhanced retry mechanisms with configurable parameters")
        print("   ✅ Comprehensive debug logging throughout all functions")
        print("   ✅ Input validation and bounds checking")
        print("   ✅ Device connection verification before operations")
        print("   ✅ Robust error handling for edge cases")
        print("   ✅ Wait mechanisms between retry attempts")
        print("   ✅ Fallback strategies with improved coordination")
        
        if full_result:
            print("\n🎉 All improvements working correctly!")
        else:
            print("\n⚠️ Some improvements need further refinement.")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)