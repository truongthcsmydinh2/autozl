#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test Flask endpoint directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import traceback
from flask import Flask, jsonify, request
from utils.conversation_manager import ConversationManager

def test_flask_endpoint():
    """Test Flask endpoint directly"""
    try:
        print("Initializing ConversationManager...")
        conversation_manager = ConversationManager()
        
        print("Testing create_device_pair endpoint logic...")
        
        # Simulate request data
        data = {
            'device_a': 'test_device_a',
            'device_b': 'test_device_b'
        }
        
        device_a = data['device_a']
        device_b = data['device_b']
        
        print(f"Calling find_or_create_pair with: {device_a}, {device_b}")
        pair = conversation_manager.pair_manager.find_or_create_pair(device_a, device_b)
        
        print(f"Pair object type: {type(pair)}")
        print(f"Pair object: {pair}")
        
        # Test JSON serialization
        response_data = {
            'success': True,
            'pair': {
                'id': pair.id,
                'device_a': pair.device_a,
                'device_b': pair.device_b,
                'temp_pair_id': pair.temp_pair_id,
                'created_at': str(pair.created_at) if pair.created_at else None
            }
        }
        
        print("Testing JSON serialization...")
        json_response = json.dumps(response_data)
        print(f"JSON response: {json_response}")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debug Flask Endpoint ===")
    success = test_flask_endpoint()
    
    if success:
        print("\n✅ Test passed successfully!")
    else:
        print("\n❌ Test failed!")