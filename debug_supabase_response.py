#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Supabase response types
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from supabase import create_client
import traceback
import inspect

# Load environment variables
load_dotenv()

def debug_supabase_response():
    """Debug Supabase response types"""
    try:
        # Initialize Supabase client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        print(f"Supabase URL: {url[:50]}..." if url else "No URL")
        print(f"Supabase Key: {key[:20]}..." if key else "No Key")
        
        supabase = create_client(url, key)
        print(f"Supabase client type: {type(supabase)}")
        
        # Test a simple query
        print("\nTesting simple query...")
        query = supabase.table('device_pairs').select('*').limit(1)
        print(f"Query object type: {type(query)}")
        print(f"Query object: {query}")
        
        # Check if query has execute method
        if hasattr(query, 'execute'):
            print("Query has execute method")
            execute_method = getattr(query, 'execute')
            print(f"Execute method type: {type(execute_method)}")
            
            # Check if execute method is async
            if inspect.iscoroutinefunction(execute_method):
                print("❌ Execute method is ASYNC - this is the problem!")
                return False
            else:
                print("✅ Execute method is SYNC")
        
        # Try to execute the query
        print("\nExecuting query...")
        result = query.execute()
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        # Check if result has data attribute
        if hasattr(result, 'data'):
            print(f"Result.data type: {type(result.data)}")
            print(f"Result.data: {result.data}")
        
        # Check if result is awaitable
        if hasattr(result, '__await__'):
            print("❌ Result is AWAITABLE - this is the problem!")
            return False
        else:
            print("✅ Result is NOT awaitable")
        
        print("\n✅ Supabase response debugging completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debug Supabase Response ===")
    success = debug_supabase_response()
    
    if success:
        print("\n✅ Debug completed successfully!")
    else:
        print("\n❌ Debug failed!")