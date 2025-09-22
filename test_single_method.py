#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_single_method():
    """Test supabase .single() method"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # Create client
        supabase = create_client(url, key)
        print("✅ Client created successfully")
        
        # Test .single() method
        print("🔄 Testing .single() method...")
        result = supabase.table('device_pairs').select('*').limit(1).single().execute()
        print(f"✅ Single query executed successfully")
        print(f"Result type: {type(result)}")
        print(f"Data: {result.data}")
        
        # Test without .single()
        print("🔄 Testing without .single()...")
        result2 = supabase.table('device_pairs').select('*').limit(1).execute()
        print(f"✅ Normal query executed successfully")
        print(f"Result type: {type(result2)}")
        print(f"Data: {result2.data}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_single_method()