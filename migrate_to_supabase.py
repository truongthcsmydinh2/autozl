#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration Script: JSON to Supabase
Chuyển dữ liệu từ các file JSON sang Supabase database
"""

import os
import json
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def backup_json_files():
    """Tạo backup cho các file JSON trước khi migrate"""
    print("📦 Tạo backup cho các file JSON...")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    json_files = [
        'master_config.json',
        'phone_mapping.json', 
        'device_data.json',
        'shared_status.json'
    ]
    
    for file in json_files:
        if os.path.exists(file):
            import shutil
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"✅ Backup: {file} -> {backup_dir}/{file}")
    
    print(f"📦 Backup hoàn thành trong thư mục: {backup_dir}")
    return backup_dir

def migrate_device_data():
    """Migrate device data từ JSON sang Supabase"""
    print("\n🔄 Migrate device data...")
    
    try:
        from database.device_repository import DeviceRepository
        from utils.data_manager import DataManager
        
        device_repo = DeviceRepository()
        data_manager = DataManager()
        
        # Load dữ liệu từ JSON
        device_data = data_manager.get_device_data()
        phone_mapping = data_manager.get_phone_mapping()
        
        migrated_count = 0
        
        # Migrate device data
        for device_id, data in device_data.items():
            try:
                # Tìm phone number từ phone mapping
                phone_number = None
                for phone, ip_port in phone_mapping.items():
                    if ip_port == device_id:
                        phone_number = phone
                        break
                
                device_info = {
                    'device_id': device_id,
                    'phone_number': phone_number,
                    'status': 'idle',
                    'message': data.get('note', ''),
                    'progress': 0
                }
                
                # Kiểm tra xem device đã tồn tại chưa (theo device_id)
                try:
                    result = device_repo.db.supabase.table('devices').select('*').eq('device_id', device_id).execute()
                    if result.data:
                        existing = result.data[0]
                        device_repo.update_device(existing['id'], device_info)
                        print(f"✅ Updated device: {device_id}")
                    else:
                        device_repo.create_device(device_info)
                        print(f"✅ Created device: {device_id}")
                    migrated_count += 1
                except Exception as e:
                    print(f"❌ Lỗi migrate device {device_id}: {e}")
                
            except Exception as e:
                print(f"❌ Lỗi migrate device {device_id}: {e}")
        
        # Migrate phone mapping riêng biệt
        for phone, ip_port in phone_mapping.items():
            try:
                if ip_port not in device_data:  # Device chưa có trong device_data
                    device_info = {
                        'device_id': ip_port,
                        'phone_number': phone,
                        'status': 'idle',
                        'message': f'From phone mapping: {phone}',
                        'progress': 0
                    }
                    
                    try:
                        result = device_repo.db.supabase.table('devices').select('*').eq('device_id', ip_port).execute()
                        if not result.data:
                            device_repo.create_device(device_info)
                            print(f"✅ Created device from phone mapping: {ip_port} -> {phone}")
                            migrated_count += 1
                    except Exception as e:
                        print(f"❌ Lỗi migrate phone mapping {phone}: {e}")
                        
            except Exception as e:
                print(f"❌ Lỗi migrate phone mapping {phone}: {e}")
        
        print(f"✅ Migrate device data hoàn thành: {migrated_count} devices")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi migrate device data: {e}")
        return False

def migrate_automation_logs():
    """Migrate automation logs từ các file log sang Supabase"""
    print("\n🔄 Migrate automation logs...")
    
    try:
        from database.log_repository import LogRepository
        
        log_repo = LogRepository()
        
        # Tìm các file log
        log_files = []
        for file in os.listdir('.'):
            if file.endswith('.log') or 'log' in file.lower():
                log_files.append(file)
        
        if not log_files:
            print("ℹ️ Không tìm thấy file log để migrate")
            return True
        
        migrated_count = 0
        
        for log_file in log_files[:5]:  # Giới hạn 5 file để tránh quá tải
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]  # Chỉ lấy 100 dòng cuối
                
                for line in lines:
                    if line.strip():
                        log_entry = {
                            'log_level': 'INFO',
                            'message': line.strip(),
                            'metadata': {
                                'source_file': log_file,
                                'migrated_at': datetime.now().isoformat(),
                                'component': 'migration'
                            }
                        }
                        
                        try:
                            log_repo.create_log(log_entry)
                            migrated_count += 1
                        except Exception as e:
                            print(f"❌ Lỗi tạo log entry: {e}")
                
                print(f"✅ Migrated log file: {log_file}")
                
            except Exception as e:
                print(f"❌ Lỗi migrate log file {log_file}: {e}")
        
        print(f"✅ Migrate automation logs hoàn thành: {migrated_count} entries")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi migrate automation logs: {e}")
        return False

def verify_migration():
    """Verify dữ liệu đã migrate thành công"""
    print("\n🔍 Verify migration...")
    
    try:
        from database.device_repository import DeviceRepository
        from database.log_repository import LogRepository
        
        device_repo = DeviceRepository()
        log_repo = LogRepository()
        
        # Kiểm tra devices
        devices = device_repo.get_all_devices()
        print(f"✅ Devices trong Supabase: {len(devices)}")
        
        # Kiểm tra logs
        try:
            result = log_repo.db.supabase.table('automation_logs').select('*').limit(10).execute()
            logs = result.data
            print(f"✅ Logs trong Supabase: {len(logs)}")
        except Exception as e:
            print(f"❌ Lỗi get logs: {e}")
        
        # Hiển thị một số sample data
        if devices:
            print("\n📋 Sample devices:")
            for device in devices[:3]:
                print(f"  - {device.get('device_id')}: {device.get('phone_number', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi verify migration: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Bắt đầu migration từ JSON sang Supabase...\n")
    
    # Test kết nối Supabase trước
    try:
        from database.supabase_manager import get_supabase_manager
        db = get_supabase_manager()
        if not db.test_connection():
            print("❌ Không thể kết nối đến Supabase. Vui lòng kiểm tra cấu hình.")
            return False
    except Exception as e:
        print(f"❌ Lỗi kết nối Supabase: {e}")
        return False
    
    # Tạo backup
    backup_dir = backup_json_files()
    
    # Migrate dữ liệu
    success = True
    
    if not migrate_device_data():
        success = False
    
    if not migrate_automation_logs():
        success = False
    
    # Verify migration
    if not verify_migration():
        success = False
    
    if success:
        print(f"\n🎉 Migration hoàn thành thành công!")
        print(f"📦 Backup được lưu tại: {backup_dir}")
        print("\n⚠️ Lưu ý: Các file JSON gốc vẫn được giữ nguyên để fallback.")
    else:
        print(f"\n❌ Migration có lỗi. Vui lòng kiểm tra và thử lại.")
        print(f"📦 Backup được lưu tại: {backup_dir}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)