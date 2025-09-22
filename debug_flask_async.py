#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Flask async behavior
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import traceback
import asyncio
import inspect

# Load environment variables
load_dotenv()

def debug_flask_async():
    """Debug Flask async behavior"""
    try:
        print("Checking if we're in async context...")
        
        # Check if we're in an event loop
        try:
            loop = asyncio.get_running_loop()
            print(f"❌ Running in async event loop: {loop}")
            print("This could be causing the await expression error!")
            return False
        except RuntimeError:
            print("✅ Not running in async event loop")
        
        # Import and test ConversationManager directly
        print("\nTesting ConversationManager import...")
        from utils.conversation_manager import ConversationManager
        
        print("Initializing ConversationManager...")
        conversation_manager = ConversationManager()
        
        print("Testing find_or_create_pair method...")
        pair_manager = conversation_manager.pair_manager
        
        # Check if any methods are async
        find_method = getattr(pair_manager, 'find_or_create_pair')
        if inspect.iscoroutinefunction(find_method):
            print("❌ find_or_create_pair is ASYNC function!")
            return False
        else:
            print("✅ find_or_create_pair is SYNC function")
        
        # Test the actual call
        print("\nTesting actual method call...")
        result = pair_manager.find_or_create_pair('debug_a', 'debug_b')
        print(f"Result type: {type(result)}")
        print(f"Result: {result}")
        
        # Check if result is awaitable
        if hasattr(result, '__await__'):
            print("❌ Result is awaitable - this is the problem!")
            return False
        else:
            print("✅ Result is not awaitable")
        
        print("\n✅ All async checks passed!")
        return True
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_flask_context():
    """Test Flask context behavior"""
    try:
        print("\n=== Testing Flask Context ===")
        
        from flask import Flask
        app = Flask(__name__)
        
        with app.app_context():
            print("Inside Flask app context")
            
            # Test ConversationManager in Flask context
            from utils.conversation_manager import ConversationManager
            conversation_manager = ConversationManager()
            
            print("Testing pair creation in Flask context...")
            pair = conversation_manager.pair_manager.find_or_create_pair('flask_a', 'flask_b')
            print(f"Pair created: {pair}")
            
            print("✅ Flask context test passed!")
            return True
            
    except Exception as e:
        print(f"Flask context error: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debug Flask Async ===")
    
    success1 = debug_flask_async()
    success2 = test_flask_context()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")