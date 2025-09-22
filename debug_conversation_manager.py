#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug ConversationManager in Flask context
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import traceback
import json

# Load environment variables
load_dotenv()

def debug_conversation_manager():
    """Debug ConversationManager initialization and usage"""
    try:
        print("=== Debug ConversationManager ===")
        
        # Test import
        print("1. Testing import...")
        from utils.conversation_manager import ConversationManager
        print("✅ Import successful")
        
        # Test initialization
        print("\n2. Testing initialization...")
        conversation_manager = ConversationManager()
        print("✅ Initialization successful")
        print(f"ConversationManager type: {type(conversation_manager)}")
        
        # Test pair_manager access
        print("\n3. Testing pair_manager access...")
        pair_manager = conversation_manager.pair_manager
        print(f"PairManager type: {type(pair_manager)}")
        print("✅ PairManager access successful")
        
        # Test find_or_create_pair method
        print("\n4. Testing find_or_create_pair method...")
        print("Calling find_or_create_pair('debug_device_a', 'debug_device_b')...")
        
        # Add detailed debugging
        import inspect
        method = getattr(pair_manager, 'find_or_create_pair')
        print(f"Method type: {type(method)}")
        print(f"Is coroutine function: {inspect.iscoroutinefunction(method)}")
        
        # Call the method
        result = pair_manager.find_or_create_pair('debug_device_a', 'debug_device_b')
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        # Check if result has __await__ method
        if hasattr(result, '__await__'):
            print("❌ Result has __await__ method - this is the problem!")
            print(f"__await__ method: {getattr(result, '__await__')}")
            return False
        else:
            print("✅ Result does not have __await__ method")
        
        # Test JSON serialization
        print("\n5. Testing JSON serialization...")
        response_data = {
            'success': True,
            'pair': {
                'id': result.id,
                'device_a': result.device_a,
                'device_b': result.device_b,
                'temp_pair_id': result.temp_pair_id,
                'created_at': str(result.created_at) if result.created_at else None
            }
        }
        
        json_str = json.dumps(response_data)
        print(f"JSON serialization successful: {len(json_str)} characters")
        print("✅ JSON serialization successful")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

def debug_supabase_client():
    """Debug Supabase client behavior"""
    try:
        print("\n=== Debug Supabase Client ===")
        
        # Import and check Supabase client
        from utils.data_manager import data_manager
        print(f"DataManager type: {type(data_manager)}")
        
        if hasattr(data_manager, 'supabase'):
            supabase_client = data_manager.supabase
            print(f"Supabase client type: {type(supabase_client)}")
            
            # Check if client has async methods
            import inspect
            methods = [method for method in dir(supabase_client) if not method.startswith('_')]
            async_methods = [method for method in methods if inspect.iscoroutinefunction(getattr(supabase_client, method, None))]
            
            print(f"Total methods: {len(methods)}")
            print(f"Async methods: {len(async_methods)}")
            if async_methods:
                print(f"Async methods found: {async_methods[:5]}...")  # Show first 5
            else:
                print("No async methods found")
        
        print("✅ Supabase client debug complete")
        return True
        
    except Exception as e:
        print(f"❌ Supabase debug error: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = debug_conversation_manager()
    success2 = debug_supabase_client()
    
    if success1 and success2:
        print("\n🎉 All debugging tests passed!")
    else:
        print("\n💥 Some debugging tests failed!")