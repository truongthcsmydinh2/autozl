#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

import requests
import json
from supabase import create_client, Client

def check_database_pairs():
    """Check what pairs are actually stored in database"""
    print("Checking database for stored pairs...")
    print("=" * 50)
    
    # Initialize Supabase client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not url or not key:
        print("❌ Supabase credentials not found!")
        return
    
    supabase: Client = create_client(url, key)
    
    try:
        # Get all pairs from database
        result = supabase.table('device_pairs').select('*').execute()
        
        if result.data:
            print(f"Found {len(result.data)} pairs in database:")
            for pair in result.data:
                print(f"  - ID: {pair['id']}")
                print(f"    Device A: {pair['device_a']}")
                print(f"    Device B: {pair['device_b']}")
                print(f"    Pair Hash: {pair['pair_hash']}")
                print(f"    Temp Pair ID: {pair['temp_pair_id']}")
                print(f"    Created: {pair['created_at']}")
                print()
        else:
            print("❌ No pairs found in database!")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def test_pair_creation_and_storage():
    """Test complete flow: create pair -> check database -> submit conversation"""
    print("Testing complete pair creation and storage flow...")
    print("=" * 60)
    
    # Step 1: Create pair via API
    print("1. Creating pair via API...")
    try:
        response = requests.post('http://localhost:8001/api/devices/pair', 
                               json={
                                   'devices': [
                                       {'ip': '192.168.1.268', 'device_id': 'device_268'},
                                       {'ip': '192.168.1.269', 'device_id': 'device_269'}
                                   ]
                               })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pair created successfully!")
            print(f"   Full response: {json.dumps(result, indent=2)}")
            
            # Extract pair_id from the response structure
            if 'data' in result and 'pairs' in result['data'] and len(result['data']['pairs']) > 0:
                first_pair = result['data']['pairs'][0]
                pair_id = first_pair.get('pair_id')
                temp_pair_id = first_pair.get('temp_pair_id')
                backend_id = first_pair.get('backend_id')
                print(f"   Extracted Pair ID: {pair_id}")
                print(f"   Extracted Temp Pair ID: {temp_pair_id}")
                print(f"   Extracted Backend ID: {backend_id}")
            else:
                pair_id = None
                print(f"   ❌ No pairs found in response!")
        else:
            print(f"❌ Failed to create pair: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error creating pair: {e}")
        return
    
    # Step 2: Check database immediately after creation
    print("\n2. Checking database after pair creation...")
    check_database_pairs()
    
    # Step 3: Try to get the pair by ID via API
    print(f"\n3. Testing GET /api/pairs/{pair_id}...")
    try:
        response = requests.get(f'http://localhost:8001/api/pairs/{pair_id}')
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Pair found via API!")
            print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Pair not found via API: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting pair: {e}")
    
    # Step 4: Try to submit conversation
    print(f"\n4. Testing conversation submission for pair {pair_id}...")
    try:
        conversation_data = {
            'conversation': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ],
            'summary': {
                'noidung': 'Test conversation',
                'hoancanh': 'Testing',
                'so_cau': 2
            }
        }
        
        response = requests.post(f'http://localhost:8001/api/conversation/{pair_id}',
                               json=conversation_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation submitted successfully!")
            print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Conversation submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error submitting conversation: {e}")

if __name__ == '__main__':
    print("Debug: Pair Storage and Retrieval")
    print("=" * 60)
    
    # First check what's currently in database
    check_database_pairs()
    
    print("\n" + "=" * 60)
    
    # Then test complete flow
    test_pair_creation_and_storage()