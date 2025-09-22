#!/usr/bin/env python3
"""
Script debug chi tiết để kiểm tra vấn đề created_at
"""

import sys
import traceback
from utils.conversation_manager import ConversationManager

def debug_created_at_issue():
    print("=== DEBUG CREATED_AT ISSUE ===")
    
    try:
        # Tạo instance ConversationManager
        conv_manager = ConversationManager()
        
        # Test gọi find_or_create_pair
        print("Gọi pair_manager.find_or_create_pair('debug_a', 'debug_b')...")
        pair = conv_manager.pair_manager.find_or_create_pair('debug_a', 'debug_b')
        
        print(f"\nPair object: {pair}")
        print(f"Pair type: {type(pair)}")
        
        # Kiểm tra chi tiết created_at
        print(f"\n=== CREATED_AT ANALYSIS ===")
        print(f"pair.created_at: {pair.created_at}")
        print(f"type(pair.created_at): {type(pair.created_at)}")
        print(f"repr(pair.created_at): {repr(pair.created_at)}")
        
        # Kiểm tra xem có method isoformat không
        has_isoformat = hasattr(pair.created_at, 'isoformat')
        print(f"hasattr(pair.created_at, 'isoformat'): {has_isoformat}")
        
        if has_isoformat:
            print("Trying to call isoformat()...")
            try:
                iso_result = pair.created_at.isoformat()
                print(f"isoformat() result: {iso_result}")
            except Exception as iso_error:
                print(f"Error calling isoformat(): {iso_error}")
        else:
            print("No isoformat method, converting to string...")
            str_result = str(pair.created_at)
            print(f"str() result: {str_result}")
            
        # Test logic tương tự như trong Flask endpoint
        print(f"\n=== FLASK ENDPOINT LOGIC TEST ===")
        try:
            flask_logic_result = pair.created_at.isoformat() if hasattr(pair.created_at, 'isoformat') else str(pair.created_at)
            print(f"Flask logic result: {flask_logic_result}")
        except Exception as flask_error:
            print(f"Flask logic error: {flask_error}")
            print(f"Error type: {type(flask_error)}")
            traceback.print_exc()
            
        # Kiểm tra tất cả attributes của created_at
        print(f"\n=== ALL ATTRIBUTES OF created_at ===")
        print(f"dir(pair.created_at): {dir(pair.created_at)}")
        
    except Exception as e:
        print(f"\nLỖI CHÍNH:")
        print(f"Exception: {e}")
        print(f"Exception type: {type(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_created_at_issue()