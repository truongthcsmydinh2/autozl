#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core1 Supabase Update Script
Cập nhật core1.py để sử dụng Supabase repositories thay vì JSON operations
"""

import os
import sys
import shutil
from datetime import datetime

def backup_original_file():
    """Backup file core1.py gốc"""
    original_file = "core1.py"
    backup_file = f"core1_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ Đã backup {original_file} -> {backup_file}")
        return backup_file
    else:
        print(f"❌ Không tìm thấy file {original_file}")
        return None

def update_imports():
    """Cập nhật imports để sử dụng Supabase"""
    return '''
# === SUPABASE IMPORTS ===
from utils.supabase_data_manager import SupabaseDataManager
from repositories.supabase_repository import (
    SupabaseConnection,
    DeviceMappingRepository, 
    DeviceStatusRepository,
    ConversationRepository,
    AppConfigRepository
)

# Initialize Supabase data manager
supabase_data_manager = SupabaseDataManager()
'''

def create_supabase_phone_map_functions():
    """Tạo các hàm thay thế cho phone mapping operations"""
    return '''
def load_phone_map_from_file():
    """Load phone mapping từ Supabase - thay thế JSON operations"""
    try:
        print("📡 Loading phone mapping từ Supabase...")
        phone_mapping = supabase_data_manager.load_phone_mapping()
        print(f"✅ Loaded {len(phone_mapping)} phone mappings từ Supabase")
        return phone_mapping
    except Exception as e:
        print(f"⚠️ Lỗi load phone mapping từ Supabase: {e}")
        print("🔄 Fallback về JSON file...")
        
        # Fallback về JSON nếu Supabase fail
        try:
            import json
            if os.path.exists(PHONE_CONFIG_FILE):
                with open(PHONE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    phone_mapping = data.get('phone_mapping', {})
                    print(f"⚠️ Loaded phone mapping từ JSON fallback: {len(phone_mapping)} devices")
                    return phone_mapping
        except Exception as json_error:
            print(f"❌ Lỗi JSON fallback: {json_error}")
        
        return {}

def save_phone_map_to_file(phone_map):
    """Lưu phone mapping vào Supabase - thay thế JSON operations"""
    try:
        print("📡 Saving phone mapping vào Supabase...")
        success = supabase_data_manager.save_phone_mapping(phone_map, created_by="core1.py CLI")
        
        if success:
            print(f"✅ Đã lưu {len(phone_map)} phone mappings vào Supabase")
            return True
        else:
            print("❌ Lỗi lưu phone mapping vào Supabase")
            return False
            
    except Exception as e:
        print(f"⚠️ Lỗi save phone mapping vào Supabase: {e}")
        print("🔄 Fallback về JSON file...")
        
        # Fallback về JSON nếu Supabase fail
        try:
            import json
            import time
            
            # Tạo data structure cho JSON
            data = {
                "phone_mapping": phone_map,
                "timestamp": time.time(),
                "created_by": "core1.py CLI (Supabase fallback)"
            }
            
            with open(PHONE_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"⚠️ Đã lưu phone mapping vào JSON fallback")
            return True
            
        except Exception as json_error:
            print(f"❌ Lỗi JSON fallback: {json_error}")
            return False
'''

def create_supabase_status_functions():
    """Tạo các hàm thay thế cho status operations"""
    return '''
def update_shared_status(device_ip, status, message="", progress=0, current_message_id=None):
    """Cập nhật trạng thái shared cho device - sử dụng Supabase"""
    try:
        print(f"📡 Updating device status vào Supabase: {device_ip} -> {status}")
        
        # Cập nhật status vào Supabase
        success = supabase_data_manager.update_device_status(
            device_ip=device_ip,
            status=status,
            message=message,
            progress=progress,
            current_message_id=current_message_id
        )
        
        if success:
            print(f"✅ Đã cập nhật status cho {device_ip}")
            return True
        else:
            print(f"❌ Lỗi cập nhật status cho {device_ip}")
            return False
            
    except Exception as e:
        print(f"⚠️ Lỗi update status vào Supabase: {e}")
        print("🔄 Fallback về JSON file...")
        
        # Fallback về JSON operations
        import json
        import time as time_module
        
        status_file = get_status_file_path()
        
        # Retry logic để handle concurrent access
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Đọc dữ liệu hiện tại
                data = {}
                if os.path.exists(status_file):
                    with open(status_file, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                        except:
                            data = {}
                
                # Cập nhật trạng thái device
                if 'devices' not in data:
                    data['devices'] = {}
                
                data['devices'][device_ip] = {
                    'status': status,
                    'message': message,
                    'progress': progress,
                    'current_message_id': current_message_id,
                    'last_update': time.time(),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Cập nhật overall status
                device_statuses = [d['status'] for d in data['devices'].values()]
                if all(s == 'completed' for s in device_statuses):
                    data['overall_status'] = 'completed'
                elif any(s == 'error' for s in device_statuses):
                    data['overall_status'] = 'error'
                elif any(s == 'running' for s in device_statuses):
                    data['overall_status'] = 'running'
                else:
                    data['overall_status'] = 'idle'
                
                data['last_update'] = time.time()
                
                # Ghi lại file
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"⚠️ Đã cập nhật status vào JSON fallback")
                return True
                
            except Exception as retry_error:
                if attempt < max_retries - 1:
                    time_module.sleep(0.1 * (attempt + 1))
                else:
                    print(f"❌ Lỗi JSON fallback: {retry_error}")
                    return False
        
        return False

def read_shared_status():
    """Đọc trạng thái shared hiện tại từ Supabase"""
    try:
        print("📡 Reading shared status từ Supabase...")
        status_data = supabase_data_manager.get_all_device_status()
        
        # Convert Supabase format về format cũ
        devices = {}
        overall_status = 'idle'
        
        for device_status in status_data:
            device_ip = device_status.get('device_ip')
            devices[device_ip] = {
                'status': device_status.get('status'),
                'message': device_status.get('message', ''),
                'progress': device_status.get('progress', 0),
                'current_message_id': device_status.get('current_message_id'),
                'last_update': device_status.get('last_update', 0),
                'timestamp': device_status.get('timestamp', '')
            }
        
        # Tính overall status
        if devices:
            device_statuses = [d['status'] for d in devices.values()]
            if all(s == 'completed' for s in device_statuses):
                overall_status = 'completed'
            elif any(s == 'error' for s in device_statuses):
                overall_status = 'error'
            elif any(s == 'running' for s in device_statuses):
                overall_status = 'running'
        
        result = {
            'devices': devices,
            'overall_status': overall_status,
            'last_update': max([d.get('last_update', 0) for d in devices.values()], default=0)
        }
        
        print(f"✅ Loaded status cho {len(devices)} devices từ Supabase")
        return result
        
    except Exception as e:
        print(f"⚠️ Lỗi read status từ Supabase: {e}")
        print("🔄 Fallback về JSON file...")
        
        # Fallback về JSON
        import json
        status_file = get_status_file_path()
        
        try:
            if os.path.exists(status_file):
                with open(status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"⚠️ Loaded status từ JSON fallback")
                return data
            else:
                return {'devices': {}, 'overall_status': 'idle', 'last_update': 0}
        except Exception as json_error:
            print(f"❌ Lỗi JSON fallback: {json_error}")
            return {'devices': {}, 'overall_status': 'error', 'last_update': 0}
'''

def create_supabase_conversation_functions():
    """Tạo các hàm thay thế cho conversation operations"""
    return '''
def load_conversation_from_file(group_id):
    """Load cuộc hội thoại từ Supabase - thay thế JSON operations"""
    try:
        print(f"📡 Loading conversation cho group {group_id} từ Supabase...")
        conversation = supabase_data_manager.load_conversation_by_group(group_id)
        
        if conversation:
            print(f"✅ Loaded {len(conversation)} messages cho group {group_id} từ Supabase")
            return conversation
        else:
            print(f"⚠️ Không tìm thấy conversation cho group {group_id} trong Supabase")
            
    except Exception as e:
        print(f"⚠️ Lỗi load conversation từ Supabase: {e}")
        print("🔄 Fallback về JSON file...")
    
    # Fallback về JSON operations
    try:
        import json
        
        # Thử load từ conversations.json trước
        if os.path.exists('conversations.json'):
            with open('conversations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                conversations = data.get('conversations', [])
                
                # Tìm conversation cho group này
                for conv in conversations:
                    if conv.get('group_id') == group_id:
                        messages = conv.get('messages', [])
                        # Convert format từ conversations.json sang format cũ
                        converted_messages = []
                        for i, msg in enumerate(messages, 1):
                            converted_messages.append({
                                "message_id": i,
                                "device_number": 1 if msg.get('device_role') == 'device_a' else 2,
                                "content": msg.get('content', '')
                            })
                        print(f"⚠️ Loaded {len(converted_messages)} messages từ conversations.json")
                        return converted_messages
        
        # Fallback về conversation_data.json
        if os.path.exists('conversation_data.json'):
            with open('conversation_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Tìm conversation cho group này
            conversations = data.get('conversations', {})
            pair_key = f"pair_{group_id}"
            
            if pair_key in conversations:
                messages = conversations[pair_key].get('conversation', [])
                print(f"⚠️ Loaded {len(messages)} messages từ conversation_data.json")
                return messages
                
    except Exception as e:
        print(f"❌ Lỗi load từ JSON fallback: {e}")
    
    # Fallback conversation đơn giản nếu không load được
    print("⚠️ Sử dụng fallback conversation mặc định")
    return [
        {"message_id": 1, "device_number": 1, "content": "Cậu đang làm gì đấy"},
        {"message_id": 2, "device_number": 2, "content": "Đang xem phim nè"},
        {"message_id": 3, "device_number": 1, "content": "Phim gì thế"},
        {"message_id": 4, "device_number": 2, "content": "Phim hài vui lắm"},
        {"message_id": 5, "device_number": 1, "content": "Cho tớ link đi"},
        {"message_id": 6, "device_number": 2, "content": "Xíu gửi nha"},
        {"message_id": 7, "device_number": 1, "content": "Ok luôn"},
        {"message_id": 8, "device_number": 2, "content": "Cậu ăn cơm chưa"},
        {"message_id": 9, "device_number": 1, "content": "Chưa đói nên chưa ăn"},
        {"message_id": 10, "device_number": 2, "content": "Ăn sớm đi kẻo đói"}
    ]
'''

def create_updated_core1():
    """Tạo file core1.py đã cập nhật với Supabase"""
    print("🔄 Đang tạo core1.py với Supabase integration...")
    
    # Đọc file core1.py gốc
    with open('core1.py', 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Tìm và thay thế các import statements
    import_section = """import os
import sys
import time
import json
import threading
import subprocess
import random
from datetime import datetime
import uiautomator2 as u2
from typing import Dict, List, Optional, Any"""
    
    # Thêm Supabase imports
    updated_imports = import_section + update_imports()
    
    # Thay thế imports trong content
    lines = original_content.split('\n')
    updated_lines = []
    import_section_found = False
    
    for line in lines:
        if line.startswith('import ') or line.startswith('from '):
            if not import_section_found:
                updated_lines.append(updated_imports)
                import_section_found = True
            # Skip original import lines
            continue
        else:
            updated_lines.append(line)
    
    updated_content = '\n'.join(updated_lines)
    
    # Thay thế các function definitions
    function_replacements = {
        'def load_phone_map_from_file():': create_supabase_phone_map_functions(),
        'def save_phone_map_to_file(phone_map):': '',  # Đã include trong phone_map_functions
        'def update_shared_status(device_ip, status, message="", progress=0, current_message_id=None):': create_supabase_status_functions(),
        'def read_shared_status():': '',  # Đã include trong status_functions
        'def load_conversation_from_file(group_id):': create_supabase_conversation_functions()
    }
    
    # Apply replacements
    for old_func, new_func in function_replacements.items():
        if old_func in updated_content and new_func:
            # Find function and replace it
            start_idx = updated_content.find(old_func)
            if start_idx != -1:
                # Find end of function (next def or end of file)
                lines_after_func = updated_content[start_idx:].split('\n')
                func_lines = [lines_after_func[0]]  # Include function definition
                
                for i, line in enumerate(lines_after_func[1:], 1):
                    if line.startswith('def ') and not line.startswith('    '):
                        break
                    func_lines.append(line)
                
                old_function = '\n'.join(func_lines)
                updated_content = updated_content.replace(old_function, new_func)
    
    return updated_content

def main():
    """Main function để thực hiện update"""
    print("🚀 Bắt đầu cập nhật core1.py để sử dụng Supabase...")
    
    # Backup file gốc
    backup_file = backup_original_file()
    if not backup_file:
        print("❌ Không thể backup file gốc")
        return False
    
    try:
        # Tạo nội dung mới
        updated_content = create_updated_core1()
        
        # Ghi file mới
        with open('core1.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Đã cập nhật core1.py với Supabase integration")
        print(f"📁 File backup: {backup_file}")
        print("\n📋 Các thay đổi chính:")
        print("  - load_phone_map_from_file() -> sử dụng Supabase")
        print("  - save_phone_map_to_file() -> sử dụng Supabase")
        print("  - update_shared_status() -> sử dụng Supabase")
        print("  - read_shared_status() -> sử dụng Supabase")
        print("  - load_conversation_from_file() -> sử dụng Supabase")
        print("  - Thêm fallback về JSON nếu Supabase fail")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi cập nhật file: {e}")
        
        # Restore backup nếu có lỗi
        if backup_file and os.path.exists(backup_file):
            shutil.copy2(backup_file, 'core1.py')
            print(f"🔄 Đã restore từ backup: {backup_file}")
        
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Cập nhật thành công! Core1.py đã sẵn sàng sử dụng Supabase.")
        print("💡 Hãy test kết nối Supabase trước khi chạy automation.")
    else:
        print("\n❌ Cập nhật thất bại. Vui lòng kiểm tra lại.")
    
    sys.exit(0 if success else 1)