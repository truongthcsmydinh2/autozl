#!/usr/bin/env python3
"""
Script test API endpoint /api/pairs/create
Mục đích: Kiểm tra xem lỗi SingleAPIResponse có còn xảy ra không
"""

import requests
import json
import time

def test_create_pair_endpoint():
    print("=== TEST API ENDPOINT /api/pairs/create ===")
    
    url = "http://127.0.0.1:8000/api/pairs/create"
    payload = {
        "device_a": "test_device_a",
        "device_b": "test_device_b"
    }
    
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("\nGửi request...")
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 200:
            print("\n✅ SUCCESS: API endpoint hoạt động bình thường!")
        else:
            print(f"\n❌ ERROR: API endpoint trả về lỗi {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST ERROR: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    # Đợi một chút để server khởi động hoàn toàn
    print("Đợi 2 giây để server khởi động...")
    time.sleep(2)
    
    test_create_pair_endpoint()