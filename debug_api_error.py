#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test conversation manager methods directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.conversation_manager import ConversationManager
import traceback

def test_pair_creation():
    """Test device pair creation directly"""
    try:
        print("Initializing ConversationManager...")
        conversation_manager = ConversationManager()
        
        print("Testing find_or_create_pair method...")
        device_a = "test_device_a"
        device_b = "test_device_b"
        
        print(f"Creating pair for devices: {device_a}, {device_b}")
        pair = conversation_manager.pair_manager.find_or_create_pair(device_a, device_b)
        
        print(f"Success! Pair created: {pair}")
        print(f"Pair ID: {pair.id}")
        print(f"Temp Pair ID: {pair.temp_pair_id}")
        
        return True
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debug API Error ===")
    success = test_pair_creation()
    
    if success:
        print("\n✅ Test passed successfully!")
    else:
        print("\n❌ Test failed!")