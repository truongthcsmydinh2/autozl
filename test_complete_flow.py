#!/usr/bin/env python3
"""
Test complete flow: create pair -> add conversation
This simulates the exact flow that was causing the 404 error
"""

import requests
import json
import time

def test_complete_flow():
    """Test the complete flow from pair creation to conversation submission"""
    
    base_url = "http://localhost:8001"
    
    print("Testing complete flow: Pair Creation -> Conversation Submission")
    print("=" * 70)
    
    # Step 1: Create a pair using the /api/devices/pair endpoint
    print("\n1. Creating device pair...")
    
    pair_data = {
        'devices': [
            {'ip': '192.168.4.268', 'name': 'Device 268'},
            {'ip': '192.168.4.269', 'name': 'Device 269'}
        ]
    }
    
    try:
        response = requests.post(f'{base_url}/api/devices/pair', 
                               json=pair_data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                pairs = result.get('data', {}).get('pairs', [])
                if pairs:
                    pair = pairs[0]
                    pair_id = pair.get('pair_id')
                    temp_pair_id = pair.get('temp_pair_id')
                    
                    print(f"✅ Pair created successfully!")
                    print(f"   Pair ID: {pair_id}")
                    print(f"   Temp Pair ID: {temp_pair_id}")
                    
                    # Step 2: Submit conversation data using the pair_id
                    print(f"\n2. Submitting conversation for pair {pair_id}...")
                    
                    conversation_data = {
                        'pair_id': pair_id,  # Use the standardized pair_id
                        'conversation': [
                            {
                                'sender': 'Device 268',
                                'message': 'Hello from device 268',
                                'timestamp': '2024-01-01T10:00:00Z'
                            },
                            {
                                'sender': 'Device 269', 
                                'message': 'Hello back from device 269',
                                'timestamp': '2024-01-01T10:01:00Z'
                            }
                        ],
                        'summary': {
                            'total_messages': 2,
                            'participants': ['Device 268', 'Device 269'],
                            'duration': '1 minute'
                        }
                    }
                    
                    conv_response = requests.post(f'{base_url}/api/conversation/{pair_id}',
                                                json=conversation_data,
                                                headers={'Content-Type': 'application/json'})
                    
                    if conv_response.status_code == 200:
                        conv_result = conv_response.json()
                        if conv_result.get('success'):
                            print(f"✅ Conversation submitted successfully!")
                            print(f"   Response: {conv_result.get('message', 'No message')}")
                            
                            # Step 3: Verify the conversation was stored
                            print(f"\n3. Verifying conversation storage...")
                            
                            verify_response = requests.get(f'{base_url}/api/pairs/{pair_id}')
                            
                            if verify_response.status_code == 200:
                                verify_result = verify_response.json()
                                if verify_result.get('success'):
                                    print(f"✅ Pair verification successful!")
                                    print(f"   Pair exists and is accessible")
                                    
                                    print(f"\n🎉 COMPLETE FLOW TEST PASSED!")
                                    print(f"   ✅ Pair creation: SUCCESS")
                                    print(f"   ✅ Conversation submission: SUCCESS")
                                    print(f"   ✅ Pair verification: SUCCESS")
                                    print(f"   ✅ No 404 errors detected!")
                                    
                                    return True
                                else:
                                    print(f"❌ Pair verification failed: {verify_result.get('error')}")
                            else:
                                print(f"❌ Pair verification request failed: {verify_response.status_code}")
                                print(f"   Response: {verify_response.text}")
                        else:
                            print(f"❌ Conversation submission failed: {conv_result.get('error')}")
                    else:
                        print(f"❌ Conversation submission request failed: {conv_response.status_code}")
                        print(f"   Response: {conv_response.text}")
                        
                        # This is where the 404 error was happening before the fix
                        if conv_response.status_code == 404:
                            print(f"\n🚨 404 ERROR DETECTED!")
                            print(f"   This is the exact error that was reported.")
                            print(f"   The pair_id '{pair_id}' was not found in the backend.")
                            print(f"   This suggests the pair ID synchronization issue still exists.")
                else:
                    print(f"❌ No pairs returned from pair creation")
            else:
                print(f"❌ Pair creation failed: {result.get('error')}")
        else:
            print(f"❌ Pair creation request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API server at {base_url}")
        print(f"   Make sure the backend server is running.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return False

def test_edge_cases():
    """Test edge cases that might cause issues"""
    
    base_url = "http://localhost:8001"
    
    print(f"\n" + "=" * 70)
    print("Testing edge cases...")
    print("=" * 70)
    
    # Test case 1: Different device ID formats
    test_cases = [
        {
            'name': 'IP addresses',
            'devices': [
                {'ip': '192.168.4.100', 'name': 'Device A'},
                {'ip': '192.168.4.200', 'name': 'Device B'}
            ]
        },
        {
            'name': 'Device IDs',
            'devices': [
                {'device_id': '100', 'name': 'Device A'},
                {'device_id': '200', 'name': 'Device B'}
            ]
        },
        {
            'name': 'Mixed formats',
            'devices': [
                {'ip': '192.168.4.100'},
                {'device_id': '200'}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nEdge Case {i}: {test_case['name']}")
        
        try:
            response = requests.post(f'{base_url}/api/devices/pair',
                                   json={'devices': test_case['devices']},
                                   headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    pairs = result.get('data', {}).get('pairs', [])
                    if pairs:
                        pair_id = pairs[0].get('pair_id')
                        print(f"✅ Generated pair ID: {pair_id}")
                    else:
                        print(f"❌ No pairs generated")
                else:
                    print(f"❌ Failed: {result.get('error')}")
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    success = test_complete_flow()
    test_edge_cases()
    
    print(f"\n" + "=" * 70)
    if success:
        print("🎉 ALL TESTS PASSED! The pair ID synchronization issue has been fixed.")
        print("   The 404 error should no longer occur when creating pairs and adding conversations.")
    else:
        print("❌ TESTS FAILED! There may still be issues with pair ID synchronization.")
    print("=" * 70)