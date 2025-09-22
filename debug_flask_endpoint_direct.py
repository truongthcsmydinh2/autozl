#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Flask endpoint directly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import traceback
import json

# Load environment variables
load_dotenv()

def test_flask_endpoint_direct():
    """Test Flask endpoint directly without HTTP request"""
    try:
        print("=== Test Flask Endpoint Direct ===")
        
        # Import Flask app
        print("1. Importing Flask app...")
        from flask import Flask
        from utils.conversation_manager import ConversationManager
        
        # Create test app
        app = Flask(__name__)
        
        # Define the endpoint function directly
        def create_device_pair_direct():
            """Direct call to create_device_pair logic"""
            try:
                print("Inside create_device_pair_direct...")
                
                # Simulate request data
                data = {
                    'device_a': 'direct_test_a',
                    'device_b': 'direct_test_b'
                }
                
                print(f"Data: {data}")
                
                if not data or 'device_a' not in data or 'device_b' not in data:
                    return {'success': False, 'error': 'Missing device_a or device_b'}, 400
                
                device_a = data['device_a']
                device_b = data['device_b']
                
                print(f"Devices: {device_a}, {device_b}")
                
                print("Creating ConversationManager...")
                conversation_manager = ConversationManager()
                print(f"ConversationManager created: {type(conversation_manager)}")
                
                print("Getting pair_manager...")
                pair_manager = conversation_manager.pair_manager
                print(f"PairManager: {type(pair_manager)}")
                
                print("Calling find_or_create_pair...")
                pair = pair_manager.find_or_create_pair(device_a, device_b)
                print(f"Pair result: {pair}")
                print(f"Pair type: {type(pair)}")
                
                # Check if pair has __await__
                if hasattr(pair, '__await__'):
                    print("❌ Pair has __await__ method!")
                    return {'success': False, 'error': 'Pair is awaitable'}, 500
                
                print("Creating response...")
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
                
                print(f"Response data: {response_data}")
                return response_data, 200
                
            except Exception as e:
                print(f"Error in create_device_pair_direct: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                traceback.print_exc()
                return {'success': False, 'error': str(e)}, 500
        
        # Test with Flask app context
        print("\n2. Testing with Flask app context...")
        with app.app_context():
            print("Inside Flask app context")
            result, status_code = create_device_pair_direct()
            print(f"Result: {result}")
            print(f"Status code: {status_code}")
            
            if status_code == 200:
                print("✅ Direct endpoint test successful")
                return True
            else:
                print("❌ Direct endpoint test failed")
                return False
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_with_request_context():
    """Test with Flask request context"""
    try:
        print("\n=== Test with Request Context ===")
        
        from flask import Flask, request
        import json
        
        app = Flask(__name__)
        
        # Test data
        test_data = {
            'device_a': 'request_test_a',
            'device_b': 'request_test_b'
        }
        
        with app.test_request_context(
            '/api/pairs/create',
            method='POST',
            data=json.dumps(test_data),
            content_type='application/json'
        ):
            print("Inside request context")
            
            # Get JSON data like in real endpoint
            data = request.get_json()
            print(f"Request data: {data}")
            
            if not data or 'device_a' not in data or 'device_b' not in data:
                print("❌ Missing data")
                return False
            
            device_a = data['device_a']
            device_b = data['device_b']
            
            print("Creating ConversationManager in request context...")
            from utils.conversation_manager import ConversationManager
            conversation_manager = ConversationManager()
            
            print("Calling find_or_create_pair in request context...")
            pair = conversation_manager.pair_manager.find_or_create_pair(device_a, device_b)
            
            print(f"Pair: {pair}")
            print("✅ Request context test successful")
            return True
        
    except Exception as e:
        print(f"❌ Request context error: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success1 = test_flask_endpoint_direct()
    success2 = test_with_request_context()
    
    if success1 and success2:
        print("\n🎉 All Flask context tests passed!")
    else:
        print("\n💥 Some Flask context tests failed!")