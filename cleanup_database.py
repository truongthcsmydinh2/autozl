#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xóa tất cả device pairs và conversation summaries trong database
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def get_supabase_client() -> Client:
    """Tạo Supabase client"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase credentials in .env")
    
    return create_client(url, key)

def cleanup_database():
    """Xóa tất cả device pairs và conversation summaries"""
    try:
        supabase = get_supabase_client()
        
        print("🧹 Bắt đầu cleanup database...")
        
        # Đếm records trước khi xóa
        pairs_count = supabase.table('device_pairs').select('id', count='exact').execute()
        summaries_count = supabase.table('conversation_summaries').select('id', count='exact').execute()
        
        print(f"📊 Tìm thấy {pairs_count.count} device pairs và {summaries_count.count} conversation summaries")
        
        # Xóa conversation summaries trước (có thể có foreign key)
        if summaries_count.count > 0:
            print("🗑️ Đang xóa conversation summaries...")
            result = supabase.table('conversation_summaries').delete().gte('created_at', '1900-01-01').execute()
            print(f"✅ Đã xóa {len(result.data)} conversation summaries")
        
        # Xóa device pairs
        if pairs_count.count > 0:
            print("🗑️ Đang xóa device pairs...")
            result = supabase.table('device_pairs').delete().gte('created_at', '1900-01-01').execute()
            print(f"✅ Đã xóa {len(result.data)} device pairs")
        
        # Verify database đã sạch
        print("🔍 Kiểm tra database sau khi cleanup...")
        remaining_pairs = supabase.table('device_pairs').select('id', count='exact').execute()
        remaining_summaries = supabase.table('conversation_summaries').select('id', count='exact').execute()
        
        print(f"📊 Còn lại: {remaining_pairs.count} device pairs, {remaining_summaries.count} conversation summaries")
        
        if remaining_pairs.count == 0 and remaining_summaries.count == 0:
            print("🎉 Database đã được cleanup thành công!")
            return True
        else:
            print("⚠️ Vẫn còn records trong database")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi cleanup database: {str(e)}")
        return False

def test_auto_create():
    """Test tính năng auto-create pair"""
    try:
        import requests
        
        print("\n🧪 Testing auto-create functionality...")
        
        # Test với pair_id không tồn tại
        test_pair_id = "pair_999_888"
        test_url = f"http://localhost:8001/api/conversation/{test_pair_id}"
        
        print(f"📡 Gửi request đến: {test_url}")
        
        # Gửi POST request với conversation data
        test_data = {
            "conversation": [
                {
                    "role": "user",
                    "content": "Test message for auto-create"
                }
            ],
            "summary": {
                "noidung": "Test summary for auto-create pair",
                "hoancanh": "Testing auto-create functionality",
                "so_cau": 1
            }
        }
        
        response = requests.post(test_url, json=test_data)
        
        if response.status_code == 200:
            print("✅ Auto-create thành công!")
            print(f"📄 Response: {response.json()}")
            
            # Verify pair đã được tạo
            supabase = get_supabase_client()
            pairs = supabase.table('device_pairs').select('*').execute()
            print(f"📊 Hiện có {len(pairs.data)} device pairs trong database")
            
            return True
        else:
            print(f"❌ Auto-create failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi khi test auto-create: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Database Cleanup & Test Script")
    print("=" * 40)
    
    # Cleanup database
    cleanup_success = cleanup_database()
    
    if cleanup_success:
        # Test auto-create
        test_success = test_auto_create()
        
        if test_success:
            print("\n🎉 Tất cả tests đã pass!")
            sys.exit(0)
        else:
            print("\n❌ Auto-create test failed")
            sys.exit(1)
    else:
        print("\n❌ Database cleanup failed")
        sys.exit(1)