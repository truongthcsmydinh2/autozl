import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseManager:
    """Quản lý kết nối và các thao tác cơ bản với Supabase database"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY trong environment variables")
        
        self.supabase: Client = create_client(self.url, self.key)
    
    def test_connection(self) -> bool:
        """Test kết nối đến Supabase"""
        try:
            # Test bằng cách query một bảng đơn giản
            result = self.supabase.table('devices').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"Lỗi kết nối Supabase: {e}")
            return False
    
    def get_client(self) -> Client:
        """Trả về Supabase client để sử dụng trực tiếp"""
        return self.supabase
    
    # Utility methods cho các thao tác chung
    def insert_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert một record vào bảng"""
        try:
            result = self.supabase.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Lỗi insert vào {table}: {e}")
            raise
    
    def update_record(self, table: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update một record theo ID"""
        try:
            result = self.supabase.table(table).update(data).eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Lỗi update {table} ID {record_id}: {e}")
            raise
    
    def delete_record(self, table: str, record_id: str) -> bool:
        """Delete một record theo ID"""
        try:
            result = self.supabase.table(table).delete().eq('id', record_id).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Lỗi delete {table} ID {record_id}: {e}")
            raise
    
    def get_record_by_id(self, table: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Lấy một record theo ID"""
        try:
            result = self.supabase.table(table).select('*').eq('id', record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Lỗi get {table} ID {record_id}: {e}")
            raise
    
    def get_all_records(self, table: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Lấy tất cả records từ một bảng"""
        try:
            query = self.supabase.table(table).select('*')
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get all {table}: {e}")
            raise
    
    def query_records(self, table: str, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Query records với filters"""
        try:
            query = self.supabase.table(table).select('*')
            
            for field, value in filters.items():
                query = query.eq(field, value)
            
            if limit:
                query = query.limit(limit)
                
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi query {table} với filters {filters}: {e}")
            raise
    
    def rpc(self, function_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call a Supabase RPC function"""
        try:
            if params:
                result = self.supabase.rpc(function_name, params).execute()
            else:
                result = self.supabase.rpc(function_name).execute()
            return result
        except Exception as e:
            print(f"Lỗi gọi RPC {function_name}: {e}")
            raise
    
    def table(self, table_name: str):
        """Get table reference for chaining operations"""
        return self.supabase.table(table_name)

# Singleton instance
_supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Lấy singleton instance của SupabaseManager"""
    global _supabase_manager
    if _supabase_manager is None:
        _supabase_manager = SupabaseManager()
    return _supabase_manager