# -*- coding: utf-8 -*-
"""
Unified Data Manager
Quản lý tập trung dữ liệu devices và phone mapping cho toàn bộ ứng dụng
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class DataManager:
    """Singleton class quản lý tập trung dữ liệu"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.master_config_file = "config/master_config.json"
            
            # Legacy file paths for migration
            self.phone_mapping_file = "phone_mapping.json"
            self.device_data_file = "data/device_data.json"
            self.config_phone_mapping_file = "config/phone_mapping.json"
            
            # Data storage
            self.master_config = {}
            self.phone_mapping = {}
            self.device_data = {}
            
            # Load data from all sources
            self._load_all_data()
            DataManager._initialized = True
    
    def _load_all_data(self):
        """Load dữ liệu từ master_config.json hoặc migrate từ các file cũ"""
        try:
            # Kiểm tra xem master_config.json có tồn tại không
            if os.path.exists(self.master_config_file):
                # Load từ master config
                with open(self.master_config_file, 'r', encoding='utf-8') as f:
                    self.master_config = json.load(f)
                
                # Extract data từ master config
                if 'devices' in self.master_config:
                    devices = self.master_config['devices']
                    for device_id, device_data in devices.items():
                        # Extract phone mapping - add tất cả devices kể cả phone rỗng
                        phone = device_data.get('phone', '')
                        self.phone_mapping[device_id] = phone
                        
                        # Extract device data - include phone và note
                        self.device_data[device_id] = {
                            'phone': phone,
                            'note': device_data.get('note', ''),
                            'zalo_number': device_data.get('zalo_number', ''),
                            'device_info': device_data.get('device_info', {}),
                            'last_updated': device_data.get('last_updated', '')
                        }
                
                print(f"✅ Loaded from master config: {len(self.phone_mapping)} phone mappings, {len(self.device_data)} devices")
            else:
                # Migration: Load từ các file cũ và tạo master config
                print("🔄 Master config not found, migrating from legacy files...")
                self._migrate_from_legacy_files()
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            # Fallback to legacy loading
            self._migrate_from_legacy_files()
    
    def _migrate_from_legacy_files(self):
        """Migrate dữ liệu từ các file cũ sang master_config.json"""
        try:
            # Load phone mapping từ file gốc
            if os.path.exists(self.phone_mapping_file):
                with open(self.phone_mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'phone_mapping' in data:
                        self.phone_mapping.update(data['phone_mapping'])
                    elif isinstance(data, dict):
                        self.phone_mapping.update(data)
            
            # Load device data từ file gốc
            if os.path.exists(self.device_data_file):
                with open(self.device_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.device_data.update(data)
            
            # Load phone mapping từ config folder (ưu tiên cao hơn)
            if os.path.exists(self.config_phone_mapping_file):
                with open(self.config_phone_mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'phone_mapping' in data:
                        self.phone_mapping.update(data['phone_mapping'])
                    elif isinstance(data, dict):
                        self.phone_mapping.update(data)
            
            print(f"🔄 Migrated {len(self.phone_mapping)} phone mappings and {len(self.device_data)} devices")
            
            # Tạo master config từ dữ liệu đã migrate
            self._create_master_config_from_legacy()
            
        except Exception as e:
            print(f"❌ Error migrating legacy files: {e}")
    
    def _create_master_config_from_legacy(self):
        """Tạo master_config.json từ dữ liệu legacy"""
        try:
            # Tạo cấu trúc master config
            self.master_config = {
                "app": {
                    "theme": "dark",
                    "language": "vi",
                    "auto_save": True,
                    "auto_reload": True,
                    "log_level": "INFO",
                    "max_log_lines": 1000,
                    "screenshot_dir": "screenshots",
                    "backup_flows": True
                },
                "device": {
                    "connection_timeout": 10,
                    "default_wait_timeout": 5,
                    "screenshot_quality": 80,
                    "auto_connect": False,
                    "retry_attempts": 3,
                    "retry_delay": 2
                },
                "flow": {
                    "auto_reload": True,
                    "syntax_check": True,
                    "backup_before_save": True,
                    "default_template": "basic",
                    "execution_timeout": 300,
                    "parallel_execution": True
                },
                "ui": {
                    "window_width": 1200,
                    "window_height": 800,
                    "sidebar_width": 250,
                    "font_size": 10,
                    "show_toolbar": True,
                    "show_statusbar": True,
                    "remember_window_state": True
                },
                "logging": {
                    "enable_file_logging": True,
                    "log_file": "logs/app.log",
                    "max_log_size": 10485760,
                    "backup_count": 5,
                    "log_format": "%(asctime)s - %(levelname)s - %(message)s"
                },
                "devices": {},
                "metadata": {
                    "version": "1.0.0",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "created_by": "Data Migration Tool"
                }
            }
            
            # Merge device data và phone mapping
            for device_id in set(list(self.phone_mapping.keys()) + list(self.device_data.keys())):
                device_info = self.device_data.get(device_id, {})
                phone = self.phone_mapping.get(device_id, "")
                
                self.master_config["devices"][device_id] = {
                    "phone": phone,
                    "zalo_number": device_info.get('zalo_number', ''),
                    "device_info": device_info.get('device_info', {
                        "model": "Unknown",
                        "android_version": "Unknown",
                        "resolution": "Unknown",
                        "status": "device"
                    }),
                    "last_updated": device_info.get('last_updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                }
            
            # Lưu master config
            self._save_master_config()
            print(f"✅ Created master_config.json with {len(self.master_config['devices'])} devices")
            
        except Exception as e:
            print(f"❌ Error creating master config: {e}")
    
    def _load_json_file(self, file_path: str) -> Dict:
        """Load JSON file safely"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[DataManager] Error loading {file_path}: {e}")
        return {}
    
    def _save_json_file(self, file_path: str, data: Dict) -> bool:
        """Save JSON file safely"""
        try:
            # Create directory if not exists
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Only create directory if path is not empty
                os.makedirs(dir_path, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[DataManager] Error saving {file_path}: {e}")
            return False
    
    def get_phone_mapping(self, device_id: str = None) -> Dict[str, str]:
        """Lấy phone mapping"""
        if device_id:
            return self.phone_mapping.get(device_id, "")
        return self.phone_mapping.copy()
    
    def get_phone_by_ip(self, ip: str) -> Optional[str]:
        """Lấy số điện thoại theo IP"""
        # Only use format with port 5555
        device_key = ip if ':' in ip else f"{ip}:5555"
        return self.phone_mapping.get(device_key)
    
    def set_phone_mapping(self, device_id: str, phone: str) -> bool:
        """Set phone mapping cho device"""
        try:
            self.phone_mapping[device_id] = phone
            
            # Cập nhật master config
            if 'devices' not in self.master_config:
                self.master_config['devices'] = {}
            
            if device_id not in self.master_config['devices']:
                self.master_config['devices'][device_id] = {
                    'phone': phone,
                    'zalo_number': '',
                    'device_info': {
                        'model': 'Unknown',
                        'android_version': 'Unknown',
                        'resolution': 'Unknown',
                        'status': 'device'
                    },
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                self.master_config['devices'][device_id]['phone'] = phone
                self.master_config['devices'][device_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return self._save_master_config()
        except Exception as e:
            print(f"❌ Error setting phone mapping: {e}")
            return False
    
    def remove_phone_mapping(self, device_id: str) -> bool:
        """Xóa phone mapping"""
        try:
            if device_id in self.phone_mapping:
                del self.phone_mapping[device_id]
            
            # Cập nhật master config
            if 'devices' in self.master_config and device_id in self.master_config['devices']:
                self.master_config['devices'][device_id]['phone'] = ''
                self.master_config['devices'][device_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return self._save_master_config()
        except Exception as e:
            print(f"❌ Error removing phone mapping: {e}")
            return False
    
    def _save_all_data(self):
        """Lưu dữ liệu vào master_config.json"""
        return self._save_master_config()
    
    def _save_master_config(self):
        """Lưu master config vào file"""
        try:
            # Cập nhật metadata
            if 'metadata' not in self.master_config:
                self.master_config['metadata'] = {}
            
            self.master_config['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Đảm bảo thư mục config tồn tại
            os.makedirs('config', exist_ok=True)
            
            # Lưu master config
            with open(self.master_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.master_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved master config with {len(self.master_config.get('devices', {}))} devices")
            return True
            
        except Exception as e:
            print(f"❌ Error saving master config: {e}")
            return False
    
    def get_device_data(self) -> Dict:
        """Lấy device data hiện tại"""
        return self.device_data.copy()
    
    def set_device_note(self, device_id: str, note: str) -> bool:
        """Cập nhật note cho device"""
        try:
            if device_id not in self.device_data:
                self.device_data[device_id] = {}
            
            self.device_data[device_id]['note'] = note
            
            # Cập nhật master config
            if 'devices' not in self.master_config:
                self.master_config['devices'] = {}
            
            if device_id not in self.master_config['devices']:
                self.master_config['devices'][device_id] = {
                    'phone': self.phone_mapping.get(device_id, ''),
                    'zalo_number': '',
                    'device_info': {
                        'model': 'Unknown',
                        'android_version': 'Unknown',
                        'resolution': 'Unknown',
                        'status': 'device'
                    },
                    'note': note,
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                self.master_config['devices'][device_id]['note'] = note
                self.master_config['devices'][device_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return self._save_master_config()
        except Exception as e:
            print(f"❌ Error setting device note: {e}")
            return False
    
    def get_devices_with_phone_numbers(self) -> List[Dict]:
        """Lấy danh sách devices kèm số điện thoại cho UI"""
        devices = []
        
        # Only get devices with port 5555 format
        device_keys = set()
        
        # From phone mapping - only entries with port
        for key in self.phone_mapping.keys():
            if ':5555' in key:
                device_keys.add(key)
        
        # From device data - only entries with port
        for device_key in self.device_data.keys():
            if ':5555' in device_key:
                device_keys.add(device_key)
        
        for device_key in sorted(device_keys):
            ip = device_key.split(':')[0]
            device_info = {
                'ip': ip,
                'device_id': device_key,
                'phone': self.phone_mapping.get(device_key, ''),
                'note': self.device_data.get(device_key, {}).get('note', '')
            }
            devices.append(device_info)
        
        return devices
    
    def reload_data(self):
        """Reload data từ tất cả các file"""
        self.phone_mapping.clear()
        self.device_data.clear()
        self._load_all_data()
        print("[DataManager] Data reloaded from all sources")
    
    def sync_with_adb_devices(self):
        """Đồng bộ dữ liệu với ADB devices thực tế"""
        import subprocess
        try:
            # Lấy danh sách devices từ ADB
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            current_devices = set()
            for line in lines:
                if line.strip() and '\t' in line:
                    device_id = line.split('\t')[0]
                    status = line.split('\t')[1]
                    if status == 'device':  # Chỉ lấy devices sẵn sàng
                        current_devices.add(device_id)
            
            # Backup existing data để preserve phone numbers
            existing_device_data = self.device_data.copy()
            existing_phone_mapping = self.phone_mapping.copy()
            
            # Cập nhật device_data.json - chỉ thêm devices mới với format IP:5555
            for device_id in current_devices:
                # Ensure device_id has port format for device_data
                formatted_device_id = device_id if ':' in device_id else f"{device_id}:5555"
                
                if formatted_device_id not in self.device_data:
                    # Tạo entry mới cho device chưa có
                    self.device_data[formatted_device_id] = {
                        "phone": "",
                        "note": "",
                        "last_updated": self._get_current_timestamp()
                    }
                else:
                    # Giữ nguyên data cũ, chỉ update timestamp
                    self.device_data[formatted_device_id]["last_updated"] = self._get_current_timestamp()
            
            # Cập nhật phone_mapping - chỉ thêm device_id với port 5555
            for device_id in current_devices:
                # Ensure device_id has port format
                if ':' not in device_id:
                    device_id = f"{device_id}:5555"
                
                if device_id not in self.phone_mapping:
                    # Chỉ thêm device_id với format IP:5555
                    self.phone_mapping[device_id] = ""
                # Giữ nguyên phone numbers đã có
            
            # Xóa devices không còn kết nối (optional - có thể comment để giữ lại)
            devices_to_remove = []
            for device_id in list(self.device_data.keys()):
                # Check both formats: with and without port
                clean_device_id = device_id.split(':')[0] if ':' in device_id else device_id
                if clean_device_id not in current_devices and device_id not in current_devices:
                    devices_to_remove.append(device_id)
            
            # Comment dòng này nếu muốn giữ lại devices cũ
            # for device_id in devices_to_remove:
            #     del self._device_data[device_id]
            #     ip = device_id.split(':')[0] if ':' in device_id else device_id
            #     if ip in self._phone_mapping:
            #         del self._phone_mapping[ip]
            
            # Lưu vào file
            self._save_all_data()
            
            print(f"[DataManager] Synced {len(current_devices)} devices with ADB")
            return len(current_devices)
            
        except Exception as e:
            print(f"[DataManager] Error syncing with ADB devices: {e}")
            return 0
    
    def _get_current_timestamp(self):
        """Lấy timestamp hiện tại"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cleanup_duplicate_entries(self):
        """Xóa tất cả entries chỉ có IP không có port từ phone_mapping"""
        entries_to_remove = []
        
        for key in self.phone_mapping.keys():
            if ':' not in key:  # Entry chỉ có IP, không có port
                entries_to_remove.append(key)
        
        for key in entries_to_remove:
            del self.phone_mapping[key]
            print(f"[DataManager] Removed duplicate entry: {key}")
        
        if entries_to_remove:
            self._save_all_data()
            print(f"[DataManager] Cleaned up {len(entries_to_remove)} duplicate entries")
        
        return len(entries_to_remove)

# Singleton instance
data_manager = DataManager()