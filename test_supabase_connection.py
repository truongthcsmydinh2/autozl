#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Supabase Connection Script
Kiểm tra kết nối và environment variables cho Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test environment variables"""
    print("🔍 Kiểm tra Environment Variables...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL không được tìm thấy trong environment variables")
        return False
    
    if not supabase_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY không được tìm thấy trong environment variables")
        return False
    
    print(f"✅ SUPABASE_URL: {supabase_url[:50]}...")
    print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {supabase_key[:20]}...")
    return True

def test_supabase_connection():
    """Test kết nối đến Supabase"""
    print("\n🔗 Kiểm tra kết nối Supabase...")
    
    try:
        from database.supabase_manager import get_supabase_manager
        
        # Get Supabase manager
        db = get_supabase_manager()
        
        # Test connection
        if db.test_connection():
            print("✅ Kết nối Supabase thành công!")
            return True
        else:
            print("❌ Không thể kết nối đến Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi kết nối Supabase: {e}")
        return False

def test_database_tables():
    """Test các bảng trong database"""
    print("\n📋 Kiểm tra các bảng trong database...")
    
    try:
        from database.supabase_manager import get_supabase_manager
        
        db = get_supabase_manager()
        
        # Test các bảng chính
        tables_to_test = ['devices', 'automation_logs', 'system_logs', 'conversation_templates']
        
        for table in tables_to_test:
            try:
                result = db.supabase.table(table).select('id').limit(1).execute()
                print(f"✅ Bảng '{table}': OK")
            except Exception as e:
                print(f"❌ Bảng '{table}': {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra bảng: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Bắt đầu test kết nối Supabase...\n")
    
    # Test environment variables
    if not test_environment_variables():
        print("\n❌ Environment variables không đầy đủ. Vui lòng cấu hình SUPABASE_URL và SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Không thể kết nối đến Supabase")
        return False
    
    # Test database tables
    if not test_database_tables():
        print("\n⚠️ Một số bảng có vấn đề")
    
    print("\n🎉 Test hoàn thành!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)