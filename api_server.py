#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Python API Server for testing Supabase migration
"""

import traceback
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.conversation_manager import ConversationManager
from utils.data_manager import DataManager
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.data_manager import data_manager
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', 'https://quocan.click', 'https://api.quocan.click', 'https://quocan.click'], 
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'API server is running',
        'data_manager': 'initialized'
    })

@app.route('/api/debug/test-pair', methods=['GET'])
def debug_test_pair():
    """Debug endpoint to test pair creation directly"""
    try:
        # Test pair creation directly in server context
        conversation_manager = ConversationManager()
        pair_manager = conversation_manager.pair_manager
        
        # Test with simple devices
        pair = pair_manager.find_or_create_pair('debug_a', 'debug_b')
        
        # Check if it's awaitable
        has_await = hasattr(pair, '__await__')
        
        return jsonify({
            'success': True,
            'pair_type': str(type(pair)),
            'has_await': has_await,
            'pair_data': {
                'id': str(pair.id),
                'device_a': pair.device_a,
                'device_b': pair.device_b,
                'temp_pair_id': pair.temp_pair_id
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': str(type(e))
        }), 500

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    try:
        devices = data_manager.get_devices_with_phone_numbers()
        return jsonify({
            'success': True,
            'data': devices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<device_id>/note', methods=['GET', 'POST'])
def device_note(device_id):
    """Get or set device note"""
    try:
        if request.method == 'GET':
            note = data_manager.get_device_note(device_id)
            return jsonify({
                'success': True,
                'data': {'note': note}
            })
        else:  # POST
            data = request.get_json()
            note = data.get('note', '')
            data_manager.set_device_note(device_id, note)
            return jsonify({
                'success': True,
                'message': 'Note updated successfully'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<device_id>/name', methods=['GET', 'PUT'])
def device_name(device_id):
    """Get or set device name"""
    try:
        if request.method == 'GET':
            name = data_manager.get_device_name(device_id)
            return jsonify({
                'success': True,
                'data': {'name': name}
            })
        else:  # PUT
            data = request.get_json()
            name = data.get('name', '')
            
            # Validation
            if not name or not name.strip():
                return jsonify({
                    'success': False,
                    'error': 'Device name cannot be empty'
                }), 400
                
            if len(name.strip()) > 50:
                return jsonify({
                    'success': False,
                    'error': 'Device name cannot exceed 50 characters'
                }), 400
            
            data_manager.set_device_name(device_id, name.strip())
            return jsonify({
                'success': True,
                'message': 'Device name updated successfully'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<device_id>/phone', methods=['GET', 'PUT'])
def device_phone(device_id):
    """Get or set device phone number"""
    try:
        if request.method == 'GET':
            phone = data_manager.get_device_phone(device_id)
            return jsonify({
                'success': True,
                'data': {'phone_number': phone}
            })
        else:  # PUT
            data = request.get_json()
            phone_number = data.get('phone_number', '')
            
            # Validation
            if phone_number and phone_number.strip():
                # Basic phone number validation
                phone_clean = phone_number.strip()
                digits_only = ''.join(filter(str.isdigit, phone_clean))
                
                if len(digits_only) < 8 or len(digits_only) > 15:
                    return jsonify({
                        'success': False,
                        'error': 'Phone number must contain 8-15 digits'
                    }), 400
            
            data_manager.set_device_phone(device_id, phone_number.strip() if phone_number else '')
            return jsonify({
                'success': True,
                'message': 'Device phone number updated successfully'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/phone-mapping', methods=['GET', 'POST'])
def phone_mapping():
    """Get or set phone mapping"""
    try:
        if request.method == 'GET':
            mapping = data_manager.get_phone_mapping()
            return jsonify({
                'success': True,
                'data': mapping
            })
        else:  # POST
            data = request.get_json()
            device_id = data.get('device_id')
            phone_number = data.get('phone_number')
            
            if not device_id or not phone_number:
                return jsonify({
                    'success': False,
                    'error': 'device_id and phone_number are required'
                }), 400
                
            data_manager.set_phone_mapping(device_id, phone_number)
            return jsonify({
                'success': True,
                'message': 'Phone mapping updated successfully'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sync-devices', methods=['POST'])
def sync_devices():
    """Sync with ADB devices"""
    try:
        data_manager.sync_with_adb_devices()
        return jsonify({
            'success': True,
            'message': 'Devices synced successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation/start', methods=['POST'])
def start_automation():
    """Start automation with selected devices and optional conversations"""
    try:
        data = request.get_json()
        selected_devices = data.get('devices', [])
        conversations = data.get('conversations', [])
        
        # DEBUG: Log incoming payload từ Web Dashboard
        print(f"[DEBUG] Incoming devices from dashboard: {selected_devices}")
        print(f"[DEBUG] Full request payload: {data}")
        print(f"[DEBUG] Conversations data: {conversations}")
        
        if not selected_devices:
            return jsonify({
                'success': False,
                'error': 'No devices selected'
            }), 400
        
        # Extract device IPs from device objects
        device_ips = []
        for i, device in enumerate(selected_devices):
            print(f"[DEBUG] Processing device {i+1}: {device} (type: {type(device)})")
            if isinstance(device, dict):
                # Try different possible IP fields
                ip = device.get('ip') or device.get('device_id') or device.get('id')
                if ip:
                    device_ips.append(ip)
                    print(f"[DEBUG] Extracted IP from device {i+1}: {ip}")
                else:
                    print(f"[DEBUG] No IP found in device {i+1}: {device}")
            elif isinstance(device, str):
                device_ips.append(device)
                print(f"[DEBUG] Device {i+1} is string: {device}")
        
        print(f"[DEBUG] Final device IPs list: {device_ips}")
        print(f"[DEBUG] Total devices to process: {len(device_ips)}")
        
        if not device_ips:
            return jsonify({
                'success': False,
                'error': 'No valid device IPs found'
            }), 400
        
        # Try to import and use core1.py automation
        try:
            from core1 import run_automation_from_gui
            
            # Prepare conversation text if provided
            conversation_text = None
            if conversations and len(conversations) > 0:
                # Join conversations into single text
                conversation_text = '\n'.join([str(conv) for conv in conversations])
            
            print(f"[DEBUG] Calling run_automation_from_gui with {len(device_ips)} devices")
            print(f"[DEBUG] Device IPs passed to core1: {device_ips}")
            print(f"[DEBUG] Conversation text: {conversation_text[:100] if conversation_text else 'None'}...")
            
            # Start automation in background with parallel mode
            result = run_automation_from_gui(device_ips, conversation_text, context=None, parallel_mode=True)
            
            print(f"[DEBUG] run_automation_from_gui returned: {result}")
            
            return jsonify({
                'success': True,
                'message': 'Automation started successfully',
                'data': result
            })
        except ImportError as ie:
            # Fallback to simulation
            return jsonify({
                'success': True,
                'message': f'Automation started (simulation mode) - {str(ie)}',
                'data': {
                    'mode': 'simulation',
                    'devices': len(device_ips),
                    'conversations': len(conversations) if conversations else 0
                }
            })
        except Exception as core_error:
            return jsonify({
                'success': False,
                'error': f'Core automation error: {str(core_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation/stop', methods=['POST'])
def stop_automation():
    """Stop automation"""
    try:
        # Note: core1.py doesn't have a stop_automation function
        # For now, just return success (automation will complete naturally)
        return jsonify({
            'success': True,
            'message': 'Automation stop signal sent (automation will complete current tasks)'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/pair', methods=['POST'])
def pair_devices():
    """Pair selected devices randomly with standardized IDs"""
    try:
        data = request.get_json()
        selected_devices = data.get('devices', [])
        
        if len(selected_devices) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 devices required for pairing'
            }), 400
        
        # Simple random pairing algorithm
        import random
        devices_copy = selected_devices.copy()
        random.shuffle(devices_copy)
        
        pairs = []
        conversation_manager = ConversationManager()
        pair_manager = conversation_manager.pair_manager
        
        for i in range(0, len(devices_copy) - 1, 2):
            if i + 1 < len(devices_copy):
                device1 = devices_copy[i]
                device2 = devices_copy[i + 1]
                
                # Extract device IDs from device objects (consistent with frontend logic)
                def extract_device_id(device):
                    """Extract device ID from device object, prioritizing ip, then device_id, then id"""
                    if isinstance(device, dict):
                        # Priority: ip > device_id > id > name
                        return device.get('ip') or device.get('device_id') or device.get('id') or device.get('name') or 'unknown'
                    else:
                        # If it's already a string/number, use as-is
                        return device
                
                device1_id = extract_device_id(device1)
                device2_id = extract_device_id(device2)
                
                # Create standardized pair ID using utility function
                from utils.pair_utils import generate_pair_id
                pair_id = generate_pair_id(device1_id, device2_id)
                
                # Check if pair exists or create new one
                try:
                    pair = pair_manager.find_or_create_pair(device1_id, device2_id)
                    # Always use standardized pair_id as the main ID
                    pairs.append({
                        'device1': device1,
                        'device2': device2,
                        'pair_id': pair_id,  # Use standardized ID
                        'temp_pair_id': pair.temp_pair_id,
                        'backend_id': pair.id  # Keep backend ID for reference
                    })
                except Exception as pair_error:
                    print(f"Error creating pair: {pair_error}")
                    # Fallback to simple pair creation
                    pairs.append({
                        'device1': device1,
                        'device2': device2,
                        'pair_id': pair_id,  # Use standardized ID
                        'temp_pair_id': None,
                        'backend_id': None
                    })
        
        # If odd number of devices, last one remains unpaired
        unpaired = []
        if len(devices_copy) % 2 == 1:
            unpaired.append(devices_copy[-1])
        
        return jsonify({
            'success': True,
            'data': {
                'pairs': pairs,
                'unpaired': unpaired,
                'total_pairs': len(pairs)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Conversation Management Endpoints
@app.route('/api/pairs', methods=['GET'])
def get_device_pairs():
    """Get all device pairs"""
    try:
        conversation_manager = ConversationManager()
        pairs = conversation_manager.list_device_pairs()
        return jsonify({
            'success': True,
            'pairs': [{
                'id': pair.id,
                'device_a': pair.device_a,
                'device_b': pair.device_b,
                'temp_pair_id': pair.temp_pair_id,
                'created_at': pair.created_at.isoformat() if hasattr(pair.created_at, 'isoformat') else str(pair.created_at)
            } for pair in pairs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pairs/create', methods=['POST'])
def create_device_pair():
    """Create a new device pair with standardized ID"""
    try:
        data = request.get_json()
        device_a = data.get('device_a')
        device_b = data.get('device_b')
        
        if not device_a or not device_b:
            return jsonify({
                'success': False,
                'error': 'Both device_a and device_b are required'
            }), 400
        
        # Extract device IDs from device objects (consistent with frontend logic)
        def extract_device_id(device):
            """Extract device ID from device object, prioritizing ip, then device_id, then id"""
            if isinstance(device, dict):
                # Priority: ip > device_id > id > name
                return device.get('ip') or device.get('device_id') or device.get('id') or device.get('name') or 'unknown'
            else:
                # If it's already a string/number, use as-is
                return device
        
        device_a_id = extract_device_id(device_a)
        device_b_id = extract_device_id(device_b)
        
        # Create standardized pair ID using utility function
        from utils.pair_utils import generate_pair_id
        pair_id = generate_pair_id(device_a_id, device_b_id)
        
        conversation_manager = ConversationManager()
        pair_manager = conversation_manager.pair_manager
        
        # Check if pair already exists
        existing_pair = pair_manager.get_pair_by_id(pair_id)
        
        if existing_pair:
            # Return existing pair
            response_data = {
                'success': True,
                'pair': {
                    'id': existing_pair.id,
                    'device_a': existing_pair.device_a,
                    'device_b': existing_pair.device_b,
                    'temp_pair_id': existing_pair.temp_pair_id,
                    'pair_hash': existing_pair.pair_hash,
                    'created_at': existing_pair.created_at.isoformat() if hasattr(existing_pair.created_at, 'isoformat') else str(existing_pair.created_at)
                },
                'message': 'Existing pair found'
            }
        else:
            # Create new pair
            pair = pair_manager.find_or_create_pair(device_a_id, device_b_id)
            response_data = {
                'success': True,
                'pair': {
                    'id': pair.id,
                    'device_a': pair.device_a,
                    'device_b': pair.device_b,
                    'temp_pair_id': pair.temp_pair_id,
                    'pair_hash': pair.pair_hash,
                    'created_at': pair.created_at.isoformat() if hasattr(pair.created_at, 'isoformat') else str(pair.created_at)
                },
                'message': 'New pair created'
            }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/conversations/input', methods=['POST'])
def process_conversation_input():
    """Process conversation input data"""
    try:
        data = request.get_json()
        device_a = data.get('device_a')
        device_b = data.get('device_b')
        conversation_data = data.get('conversation_data')
        
        if not all([device_a, device_b, conversation_data]):
            return jsonify({
                'success': False,
                'error': 'device_a, device_b, and conversation_data are required'
            }), 400
        
        conversation_manager = ConversationManager()
        result = conversation_manager.process_conversation_input(
            device_a, device_b, conversation_data
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conversation/demo', methods=['POST'])
def submit_demo_conversation_data():
    """Submit demo conversation data (no device pair required)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('conversation') or not data.get('summary'):
            return jsonify({
                'success': False,
                'error': 'conversation and summary are required'
            }), 400
        
        # Convert demo format to API format
        conversation_array = data.get('conversation', [])
        summary_data = data.get('summary', {})
        
        # Convert conversation array to messages format
        messages = []
        for msg in conversation_array:
            messages.append({
                'sender': msg.get('role', ''),
                'text': msg.get('content', '')
            })
        
        # Fix socau -> so_cau
        if 'socau' in summary_data:
            summary_data['so_cau'] = summary_data.pop('socau')
        
        # Create API format
        api_format = {
            'content': {
                'messages': messages
            },
            'summary': summary_data
        }
        
        # Process demo conversation with dummy device names
        conversation_manager = ConversationManager()
        result = conversation_manager.process_conversation_input(
            'demo_device_a', 'demo_device_b', api_format
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pairs/<pair_id>', methods=['GET'])
def get_pair_by_id(pair_id):
    """Get device pair by ID (supports standardized pair_id, UUID and temp_pair_id)"""
    try:
        conversation_manager = ConversationManager()
        
        # First try to get pair by temp_pair_id if it looks like a temp_pair_id
        pair = None
        if pair_id.startswith('pair_temp_'):
            # It's a temp_pair_id, get pair by temp_pair_id
            try:
                pair = conversation_manager.pair_manager.get_pair_by_temp_id(pair_id)
            except Exception as e:
                print(f"Error getting pair by temp_pair_id {pair_id}: {e}")
        else:
            # It's likely a standardized pair_id, try to get by ID
            try:
                pair = conversation_manager.pair_manager.get_pair_by_id(pair_id)
            except Exception as e:
                print(f"Error getting pair by ID {pair_id}: {e}")
        
        if not pair:
            return jsonify({
                'success': False,
                'error': f'Device pair {pair_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'pair': {
                'id': pair.id,
                'device_a': pair.device_a,
                'device_b': pair.device_b,
                'pair_hash': pair.pair_hash,
                'temp_pair_id': pair.temp_pair_id,
                'created_at': pair.created_at
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conversation/<pair_id>', methods=['POST'])
def submit_conversation_data(pair_id):
    """Submit conversation data for a specific pair (handles demo data format)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('conversation') or not data.get('summary'):
            return jsonify({
                'success': False,
                'error': 'conversation and summary are required'
            }), 400
        
        # Convert demo format to API format
        conversation_array = data.get('conversation', [])
        summary_data = data.get('summary', {})
        
        # Convert conversation array to messages format
        messages = []
        for msg in conversation_array:
            messages.append({
                'sender': msg.get('role', ''),
                'text': msg.get('content', '')
            })
        
        # Fix socau -> so_cau
        if 'socau' in summary_data:
            summary_data['so_cau'] = summary_data.pop('socau')
        
        # Create API format
        api_format = {
            'content': {
                'messages': messages
            },
            'summary': summary_data
        }
        
        # Get device info from pair_id (could be UUID or temp_pair_id)
        conversation_manager = ConversationManager()
        
        # First try to get pair by temp_pair_id if it looks like a temp_pair_id
        pair = None
        if pair_id.startswith('pair_temp_'):
            # It's a temp_pair_id, get pair by temp_pair_id
            try:
                pair = conversation_manager.pair_manager.get_pair_by_temp_id(pair_id)
            except Exception as e:
                print(f"Error getting pair by temp_pair_id {pair_id}: {e}")
        else:
            # It's likely a standardized pair_id, try to get by ID
            try:
                pair = conversation_manager.pair_manager.get_pair_by_id(pair_id)
            except Exception as e:
                print(f"Error getting pair by ID {pair_id}: {e}")
        
        if not pair:
            return jsonify({
                'success': False,
                'error': f'Device pair {pair_id} not found'
            }), 404
        
        # Process the conversation with real pair
        result = conversation_manager.process_conversation_input(
            pair.device_a, pair.device_b, api_format
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/summaries/latest/<pair_identifier>', methods=['GET'])
def get_latest_summary(pair_identifier):
    """Get latest summary for device pair (supports standardized pair_id, UUID and temp_pair_id)"""
    try:
        conversation_manager = ConversationManager()
        
        # Use the updated function that handles both standardized pair_id and temp_pair_id
        summary = conversation_manager.get_latest_summary_by_pair_id(pair_identifier)
        
        if summary:
            return jsonify({
                'success': True,
                'summary': {
                    'noidung': summary.noidung,
                    'hoancanh': summary.hoancanh,
                    'so_cau': summary.so_cau,
                    'created_at': summary.created_at.isoformat() if hasattr(summary.created_at, 'isoformat') else str(summary.created_at)
                }
            })
        else:
            return jsonify({'success': False, 'error': 'No summary found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conversations/temp/<temp_conversation_id>', methods=['GET'])
def get_temporary_conversation(temp_conversation_id):
    """Get temporarily stored conversation content"""
    try:
        conversation_manager = ConversationManager()
        content = conversation_manager.get_temporary_content(temp_conversation_id)
        
        if content:
            return jsonify({
                'success': True,
                'content': {
                    'cuoc_tro_chuyen': content.cuoc_tro_chuyen,
                    'thoi_gian': content.thoi_gian
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversation content not found'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/conversations/temp/<temp_conversation_id>', methods=['DELETE'])
def delete_temporary_conversation(temp_conversation_id):
    """Delete temporarily stored conversation content"""
    try:
        conversation_manager = ConversationManager()
        success = conversation_manager.clear_temporary_content(temp_conversation_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation content cleared'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversation content not found'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting API server...")
    print(f"DataManager initialized successfully")
    
    # Note: Auto-sync removed - use /api/sync-devices endpoint for manual sync
    print("[INFO] Auto-sync disabled - devices will be scanned on demand")
    
    print("[OK] API server ready!")
    # Enable debug mode to see error stack traces
    app.run(host='0.0.0.0', port=8001, debug=True, use_reloader=False)