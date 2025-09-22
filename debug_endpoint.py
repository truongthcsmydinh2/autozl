#!/usr/bin/env python3

import requests
import json
import traceback

def test_endpoint():
    try:
        print("🔄 Testing /api/pairs/create endpoint...")
        
        url = 'http://localhost:8000/api/pairs/create'
        payload = {
            'device_a': 'EndpointTestDevice1',
            'device_b': 'EndpointTestDevice2'
        }
        
        print(f"📤 Sending request to {url}")
        print(f"📤 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        print(f"📥 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"✅ JSON Response: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint()