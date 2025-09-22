#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Flask test to isolate the issue
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from flask import Flask, jsonify, request
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/test/pairs/create', methods=['POST'])
def test_create_device_pair():
    """Test create device pair endpoint"""
    try:
        print("=== Test Endpoint Called ===")
        
        data = request.get_json()
        print(f"Request data: {data}")
        
        if not data or 'device_a' not in data or 'device_b' not in data:
            return jsonify({'success': False, 'error': 'Missing device_a or device_b'}), 400
        
        device_a = data['device_a']
        device_b = data['device_b']
        print(f"Devices: {device_a}, {device_b}")
        
        # Import ConversationManager inside the endpoint
        print("Importing ConversationManager...")
        from utils.conversation_manager import ConversationManager
        
        print("Initializing ConversationManager...")
        conversation_manager = ConversationManager()
        
        print("Calling find_or_create_pair...")
        pair = conversation_manager.pair_manager.find_or_create_pair(device_a, device_b)
        print(f"Pair result: {pair}")
        print(f"Pair type: {type(pair)}")
        
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
        
        print(f"Response data: {response_data}")
        print("=== Test Endpoint Success ===")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"=== Test Endpoint Error ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        print("=== End Error ===")
        
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test/health', methods=['GET'])
def test_health():
    """Test health endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Test server is running'
    })

if __name__ == '__main__':
    print("Starting minimal test server...")
    app.run(host='0.0.0.0', port=8001, debug=True, use_reloader=False)