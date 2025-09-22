#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from dotenv import load_dotenv
from utils.conversation_manager import DevicePairManager

load_dotenv()

def test_conversation_manager():
    """Test conversation manager methods"""
    try:
        print("🔄 Testing DevicePairManager...")
        
        # Create manager
        manager = DevicePairManager()
        print("✅ Manager created successfully")
        
        # Test find_or_create_pair
        print("🔄 Testing find_or_create_pair...")
        pair = manager.find_or_create_pair('test_device_1', 'test_device_2')
        print(f"✅ Pair created/found: {pair.temp_pair_id}")
        
        # Test get_pair_by_temp_id
        print("🔄 Testing get_pair_by_temp_id...")
        found_pair = manager.get_pair_by_temp_id(pair.temp_pair_id)
        if found_pair:
            print(f"✅ Pair found by temp ID: {found_pair.temp_pair_id}")
        else:
            print("❌ Pair not found by temp ID")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_conversation_manager()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")