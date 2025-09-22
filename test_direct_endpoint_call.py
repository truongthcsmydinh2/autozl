#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test endpoint directly by importing and calling the function
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import traceback
import json

# Load environment variables
load_dotenv()

def test_direct_endpoint_call():
    """Test by directly calling the endpoint function"""
    try:
        print("=== Test Direct Endpoint Call ===")
        
        # Import Flask and create app context
        from flask import Flask, request
        from utils.conversation_manager import ConversationManager
        
        app = Flask(__name__)
        
        # Test data
        test_data = {
            'device_a': 'direct_call_test_a',
            'device_b': 'direct_call_test_b'
        }
        
        # Create the endpoint function with debug
        def create_device_pair_debug():
            """Debug version of create_device_pair"""
            import traceback
            try:
                print("[DEBUG] create_device_pair called")
                data = request.get_json()
                print(f"[DEBUG] Request data: {data}")
                
                if not data or 'device_a' not in data or 'device_b' not in data:
                    print("[DEBUG] Missing device data")
                    return {'success': False, 'error': 'Missing device_a or device_b'}, 400
                
                device_a = data['device_a']
                device_b = data['device_b']
                print(f"[DEBUG] Devices: {device_a}, {device_b}")
                
                print("[DEBUG] Creating ConversationManager...")
                conversation_manager = ConversationManager()
                print(f"[DEBUG] ConversationManager created: {type(conversation_manager)}")
                
                print("[DEBUG] Getting pair_manager...")
                pair_manager = conversation_manager.pair_manager
                print(f"[DEBUG] PairManager: {type(pair_manager)}")
                
                print("[DEBUG] Calling find_or_create_pair...")
                pair = pair_manager.find_or_create_pair(device_a, device_b)
                print(f"[DEBUG] Pair result: {pair}")
                print(f"[DEBUG] Pair type: {type(pair)}")
                
                # Check if pair has __await__
                if hasattr(pair, '__await__'):
                    print("[DEBUG] ERROR: Pair has __await__ method!")
                    return {'success': False, 'error': 'Pair is awaitable - this should not happen'}, 500
                
                print("[DEBUG] Creating response...")
                response_data = {
                    'success': True,
                    'pair': {
                        'id': pair.id,
                        'device_a': pair.device_a,
                        'device_b': pair.device_b,
                        'temp_pair_id': pair.temp_pair_id,
                        'created_at': pair.created_at
                    }
                }
                print(f"[DEBUG] Response data: {response_data}")
                
                return response_data, 200
            except Exception as e:
                print(f"[DEBUG] Exception in create_device_pair: {str(e)}")
                print(f"[DEBUG] Exception type: {type(e).__name__}")
                print("[DEBUG] Full traceback:")
                traceback.print_exc()
                return {'success': False, 'error': str(e)}, 500
        
        # Test with request context
        with app.test_request_context(
            '/api/pairs/create',
            method='POST',
            data=json.dumps(test_data),
            content_type='application/json'
        ):
            print("\nCalling endpoint function directly...")
            result, status_code = create_device_pair_debug()
            print(f"\nResult: {result}")
            print(f"Status code: {status_code}")
            
            if status_code == 200:
                print("✅ Direct endpoint call successful")
                return True
            else:
                print("❌ Direct endpoint call failed")
                return False
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_import_chain():
    """Test the import chain to see where the issue might be"""
    try:
        print("\n=== Test Import Chain ===")
        
        print("1. Testing ConversationManager import...")
        from utils.conversation_manager import ConversationManager
        print("✅ ConversationManager imported")
        
        print("2. Testing ConversationManager creation...")
        cm = ConversationManager()
        print(f"✅ ConversationManager created: {type(cm)}")
        
        print("3. Testing pair_manager access...")
        pm = cm.pair_manager
        print(f"✅ PairManager accessed: {type(pm)}")
        
        print("4. Testing find_or_create_pair method...")
        method = pm.find_or_create_pair
        print(f"✅ Method accessed: {type(method)}")
        
        print("5. Testing method call...")
        pair = method('import_test_a', 'import_test_b')
        print(f"✅ Method called: {type(pair)}")
        
        print("6. Testing pair attributes...")
        print(f"  - id: {pair.id}")
        print(f"  - device_a: {pair.device_a}")
        print(f"  - device_b: {pair.device_b}")
        print(f"  - temp_pair_id: {pair.temp_pair_id}")
        print(f"  - created_at: {pair.created_at}")
        
        print("7. Testing __await__ check...")
        has_await = hasattr(pair, '__await__')
        print(f"  - Has __await__: {has_await}")
        
        if has_await:
            print("❌ ERROR: Pair has __await__ method!")
            return False
        
        print("✅ All import chain tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Import chain error: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_import_chain()
    success2 = test_direct_endpoint_call()
    
    if success1 and success2:
        print("\n🎉 All direct tests passed!")
    else:
        print("\n💥 Some direct tests failed!")