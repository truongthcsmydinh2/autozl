#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_supabase_connection():
    """Test supabase connection and operations"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        print(f"URL: {url[:20]}...")
        print(f"Key: {key[:20]}...")
        
        # Create client
        supabase = create_client(url, key)
        print("✅ Client created successfully")
        
        # Test simple query
        result = supabase.table('device_pairs').select('*').limit(1).execute()
        print(f"✅ Query executed successfully")
        print(f"Result type: {type(result)}")
        print(f"Data: {result.data}")
        
        # Test insert
        test_data = {
            'device_a': 'test_a',
            'device_b': 'test_b', 
            'pair_hash': 'test_hash_123',
            'temp_pair_id': 'test_temp_123'
        }
        
        insert_result = supabase.table('device_pairs').insert(test_data).execute()
        print(f"✅ Insert executed successfully")
        print(f"Insert result: {insert_result.data}")
        
        # Clean up
        if insert_result.data:
            cleanup_result = supabase.table('device_pairs').delete().eq('id', insert_result.data[0]['id']).execute()
            print(f"✅ Cleanup successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_supabase_connection()