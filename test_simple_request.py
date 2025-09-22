#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to debug the isoformat error
"""

import requests
import json

def test_simple_request():
    url = "http://127.0.0.1:8000/api/pairs/create"
    payload = {
        "device_a": "test1",
        "device_b": "test2"
    }
    
    try:
        print(f"Sending request to {url}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nSuccess Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\nError Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw error: {response.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_request()