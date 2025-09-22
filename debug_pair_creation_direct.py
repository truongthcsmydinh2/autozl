#!/usr/bin/env python3
"""
Script debug để test trực tiếp hàm find_or_create_pair
Mục đích: Tìm hiểu nguyên nhân lỗi 'SingleAPIResponse can't be used in await expression'
"""

import sys
import traceback
from utils.conversation_manager import ConversationManager

def debug_pair_creation():
    print("=== DEBUG PAIR CREATION ===")
    print("Khởi tạo ConversationManager...")
    
    try:
        # Tạo instance ConversationManager
        conv_manager = ConversationManager()
        print(f"ConversationManager created: {type(conv_manager)}")
        print(f"pair_manager type: {type(conv_manager.pair_manager)}")
        
        # Test gọi find_or_create_pair
        print("\nGọi pair_manager.find_or_create_pair('test_a', 'test_b')...")
        result = conv_manager.pair_manager.find_or_create_pair('test_a', 'test_b')
        
        print(f"\nKết quả:")
        print(f"Type: {type(result)}")
        print(f"Value: {result}")
        
        # Kiểm tra các thuộc tính của result
        print(f"\nThuộc tính của result:")
        print(f"Dir: {dir(result)}")
        
        # Kiểm tra xem có phải là Supabase response không
        if hasattr(result, '__class__'):
            print(f"Class name: {result.__class__.__name__}")
            print(f"Module: {result.__class__.__module__}")
        
        # Kiểm tra xem có method __await__ không
        if hasattr(result, '__await__'):
            print("WARNING: Object có __await__ method - đây có thể là async object!")
        
        # Thử truy cập các thuộc tính thông thường của DevicePair
        try:
            if hasattr(result, 'device_a'):
                print(f"device_a: {result.device_a}")
            if hasattr(result, 'device_b'):
                print(f"device_b: {result.device_b}")
            if hasattr(result, 'temp_pair_id'):
                print(f"temp_pair_id: {result.temp_pair_id}")
        except Exception as attr_error:
            print(f"Lỗi khi truy cập thuộc tính: {attr_error}")
            
    except Exception as e:
        print(f"\nLỖI XẢY RA:")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        
        # Kiểm tra xem có phải lỗi liên quan đến Supabase không
        if 'SingleAPIResponse' in str(e):
            print("\n*** ĐÂY LÀ LỖI SUPABASE SingleAPIResponse ***")
            print("Có thể do:")
            print("1. Version conflict của supabase-py")
            print("2. Sử dụng sync method với async response")
            print("3. Cấu hình Supabase client không đúng")
            
        # Kiểm tra Supabase version
        try:
            import supabase
            print(f"\nSupabase version: {supabase.__version__}")
        except:
            print("\nKhông thể kiểm tra Supabase version")

if __name__ == "__main__":
    debug_pair_creation()