#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test migration results
"""

from utils.data_manager import DataManager
from utils.supabase_data_manager import SupabaseDataManager

def test_data_manager():
    print("🔍 Testing DataManager...")
    
    try:
        dm = DataManager()
        
        # Test device data
        device_data = dm.get_device_data()
        print(f"📊 Device data: {len(device_data)} devices")
        
        # Test phone mapping
        phone_mapping = dm.get_phone_mapping()
        print(f"📞 Phone mapping: {len(phone_mapping)} mappings")
        
        # Sample devices
        print("\n📋 Sample devices:")
        for i, (k, v) in enumerate(list(device_data.items())[:5]):
            note = v.get('note', 'N/A') if isinstance(v, dict) else str(v)
            print(f"  {k}: {note}")
        
        # Sample phone mapping
        print("\n📞 Sample phone mapping:")
        for i, (k, v) in enumerate(list(phone_mapping.items())[:5]):
            print(f"  {k}: {v}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing DataManager: {e}")
        return False

def test_supabase_data_manager():
    print("\n🔍 Testing SupabaseDataManager...")
    
    try:
        sdm = SupabaseDataManager()
        
        # Test phone mapping
        phone_mapping = sdm.load_phone_mapping()
        print(f"📞 Supabase phone mapping: {len(phone_mapping)} mappings")
        
        # Sample mappings
        print("\n📞 Sample Supabase phone mapping:")
        for i, (k, v) in enumerate(list(phone_mapping.items())[:5]):
            print(f"  {k}: {v}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing SupabaseDataManager: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing migration results...\n")
    
    success1 = test_data_manager()
    success2 = test_supabase_data_manager()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")