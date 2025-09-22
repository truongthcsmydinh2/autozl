#!/usr/bin/env python3
"""
Test specific pair lookup cases from original error logs
"""

import requests
import json
from utils.pair_utils import generate_pair_id

def test_specific_pairs():
    """Test specific pair lookups that were failing"""
    
    base_url = "http://localhost:8000"
    
    print("Testing specific pair lookup cases:")
    print("=" * 50)
    
    # Test cases from original error logs
    test_cases = [
        "pair_81_85",
        "pair_158_81", 
        "pair_1_2",
        "pair_3_5",
        "pair_76_93"
    ]
    
    for pair_id in test_cases:
        print(f"\n🔍 Testing lookup: {pair_id}")
        
        try:
            # Test lookup via new endpoint
            response = requests.get(f"{base_url}/api/pairs/{pair_id}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'pair' in data:
                    pair = data['pair']
                    print(f"   ✅ Found: {pair['id']}")
                    print(f"   Devices: {pair['device_a']} + {pair['device_b']}")
                    
                    # Verify ID consistency
                    regenerated = generate_pair_id(pair['device_a'], pair['device_b'])
                    if regenerated == pair['id']:
                        print(f"   ✅ ID consistency: PASS")
                    else:
                        print(f"   ❌ ID consistency: FAIL")
                        print(f"      Expected: {regenerated}")
                        print(f"      Actual: {pair['id']}")
                else:
                    print(f"   ❌ Invalid response format")
            elif response.status_code == 404:
                print(f"   ❌ Not found: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Raw response: {response.text}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Specific pair lookup test completed!")

if __name__ == "__main__":
    test_specific_pairs()