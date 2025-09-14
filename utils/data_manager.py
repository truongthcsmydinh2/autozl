# -*- coding: utf-8 -*-
"""
Unified Data Manager
Quản lý tập trung dữ liệu devices và phone mapping cho toàn bộ ứng dụng
"""

import json
import os
import time
from typing import Dict, List, Optional

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
            self.phone_mapping_file = "phone_mapping.json"
            self.device_data_file = "data/device_data.json"
            self.config_phone_mapping_file = "config/phone_mapping.json"
            
            # Unified data storage
            self._phone_mapping = {}
            self._device_data = {}
            
            # Load data from all sources
            self._load_all_data()
            DataManager._initialized = True
    
    def _load_all_data(self):
        """Load data từ tất cả các nguồn và merge lại"""
        print("[DataManager] Loading data from all sources...")
        
        # 1. Load từ phone_mapping.json (core1.py) - only entries with port
        core_mapping = self._load_json_file(self.phone_mapping_file)
        if core_mapping and 'phone_mapping' in core_mapping:
            # Only load entries with port format
            for key, value in core_mapping['phone_mapping'].items():
                if ':5555' in key:
                    self._phone_mapping[key] = value
            print(f"[DataManager] Loaded {len([k for k in core_mapping['phone_mapping'].keys() if ':5555' in k])} entries with port from core phone_mapping.json")
        
        # 2. Load từ device_data.json (GUI)
        device_data = self._load_json_file(self.device_data_file)
        if device_data:
            # Convert device_data format to phone_mapping format
            for device_id, data in device_data.items():
                if 'phone' in data and data['phone']:
                    # Keep device_id with port for consistency
                    self._phone_mapping[device_id] = data['phone']
            self._device_data = device_data
            print(f"[DataManager] Loaded {len(device_data)} entries from device_data.json")
        
        # 3. Load từ config/phone_mapping.json (GUI config) - only entries with port
        config_mapping = self._load_json_file(self.config_phone_mapping_file)
        if config_mapping and 'phone_mapping' in config_mapping:
            # Only load entries with port format
            for key, value in config_mapping['phone_mapping'].items():
                if ':5555' in key:
                    self._phone_mapping[key] = value
            print(f"[DataManager] Loaded {len([k for k in config_mapping['phone_mapping'].keys() if ':5555' in k])} entries with port from config phone_mapping.json")
        
        print(f"[DataManager] Total unified phone mapping: {len(self._phone_mapping)} entries")
        print(f"[DataManager] Unified mapping: {self._phone_mapping}")
    
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
    
    def get_phone_mapping(self) -> Dict[str, str]:
        """Lấy phone mapping hiện tại"""
        return self._phone_mapping.copy()
    
    def get_phone_by_ip(self, ip: str) -> Optional[str]:
        """Lấy số điện thoại theo IP"""
        # Only use format with port 5555
        device_key = ip if ':' in ip else f"{ip}:5555"
        return self._phone_mapping.get(device_key)
    
    def set_phone_mapping(self, ip: str, phone: str) -> bool:
        """Cập nhật phone mapping"""
        # Keep original format with port for consistency
        device_key = ip if ':' in ip else f"{ip}:5555"
        clean_ip = ip.split(':')[0] if ':' in ip else ip
        
        # Update in-memory data with device_key (includes port)
        self._phone_mapping[device_key] = phone
        
        # Update device_data format
        if device_key not in self._device_data:
            self._device_data[device_key] = {}
        self._device_data[device_key]['phone'] = phone
        
        # Save to all files
        return self._save_all_data()
    
    def remove_phone_mapping(self, ip: str) -> bool:
        """Xóa phone mapping"""
        device_key = ip if ':' in ip else f"{ip}:5555"
        clean_ip = ip.split(':')[0] if ':' in ip else ip
        
        # Remove from in-memory data (try both formats)
        if device_key in self._phone_mapping:
            del self._phone_mapping[device_key]
        if clean_ip in self._phone_mapping:
            del self._phone_mapping[clean_ip]
        
        # Remove from device_data
        if device_key in self._device_data and 'phone' in self._device_data[device_key]:
            del self._device_data[device_key]['phone']
            if not self._device_data[device_key]:  # Remove empty entry
                del self._device_data[device_key]
        
        return self._save_all_data()
    
    def _save_all_data(self) -> bool:
        """Lưu data vào tất cả các file"""
        success = True
        
        # 1. Save to phone_mapping.json (core1.py format)
        core_data = {
            'phone_mapping': self._phone_mapping,
            'timestamp': time.time(),
            'created_by': 'GUI DataManager'
        }
        if not self._save_json_file(self.phone_mapping_file, core_data):
            success = False
        
        # 2. Save to device_data.json (GUI format)
        if not self._save_json_file(self.device_data_file, self._device_data):
            success = False
        
        # 3. Save to config/phone_mapping.json (GUI config format)
        config_data = {
            'phone_mapping': self._phone_mapping,
            'timestamp': time.time(),
            'created_by': 'GUI DataManager'
        }
        if not self._save_json_file(self.config_phone_mapping_file, config_data):
            success = False
        
        if success:
            print(f"[DataManager] Successfully saved data to all files")
        else:
            print(f"[DataManager] Some files failed to save")
        
        return success
    
    def get_device_data(self) -> Dict:
        """Lấy device data hiện tại"""
        return self._device_data.copy()
    
    def set_device_note(self, ip: str, note: str) -> bool:
        """Cập nhật note cho device"""
        clean_ip = ip.split(':')[0] if ':' in ip else ip
        device_key = f"{clean_ip}:5555"
        
        if device_key not in self._device_data:
            self._device_data[device_key] = {}
        
        self._device_data[device_key]['note'] = note
        
        # Save device_data.json
        return self._save_json_file(self.device_data_file, self._device_data)
    
    def get_devices_with_phone_numbers(self) -> List[Dict]:
        """Lấy danh sách devices kèm số điện thoại cho UI"""
        devices = []
        
        # Only get devices with port 5555 format
        device_keys = set()
        
        # From phone mapping - only entries with port
        for key in self._phone_mapping.keys():
            if ':5555' in key:
                device_keys.add(key)
        
        # From device data - only entries with port
        for device_key in self._device_data.keys():
            if ':5555' in device_key:
                device_keys.add(device_key)
        
        for device_key in sorted(device_keys):
            ip = device_key.split(':')[0]
            device_info = {
                'ip': ip,
                'device_id': device_key,
                'phone': self._phone_mapping.get(device_key, ''),
                'note': self._device_data.get(device_key, {}).get('note', '')
            }
            devices.append(device_info)
        
        return devices
    
    def reload_data(self):
        """Reload data từ tất cả các file"""
        self._phone_mapping.clear()
        self._device_data.clear()
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
            existing_device_data = self._device_data.copy()
            existing_phone_mapping = self._phone_mapping.copy()
            
            # Cập nhật device_data.json - chỉ thêm devices mới với format IP:5555
            for device_id in current_devices:
                # Ensure device_id has port format for device_data
                formatted_device_id = device_id if ':' in device_id else f"{device_id}:5555"
                
                if formatted_device_id not in self._device_data:
                    # Tạo entry mới cho device chưa có
                    self._device_data[formatted_device_id] = {
                        "phone": "",
                        "note": "",
                        "last_updated": self._get_current_timestamp()
                    }
                else:
                    # Giữ nguyên data cũ, chỉ update timestamp
                    self._device_data[formatted_device_id]["last_updated"] = self._get_current_timestamp()
            
            # Cập nhật phone_mapping - chỉ thêm device_id với port 5555
            for device_id in current_devices:
                # Ensure device_id has port format
                if ':' not in device_id:
                    device_id = f"{device_id}:5555"
                
                if device_id not in self._phone_mapping:
                    # Chỉ thêm device_id với format IP:5555
                    self._phone_mapping[device_id] = ""
                # Giữ nguyên phone numbers đã có
            
            # Xóa devices không còn kết nối (optional - có thể comment để giữ lại)
            devices_to_remove = []
            for device_id in list(self._device_data.keys()):
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
        
        for key in self._phone_mapping.keys():
            if ':' not in key:  # Entry chỉ có IP, không có port
                entries_to_remove.append(key)
        
        for key in entries_to_remove:
            del self._phone_mapping[key]
            print(f"[DataManager] Removed duplicate entry: {key}")
        
        if entries_to_remove:
            self._save_all_data()
            print(f"[DataManager] Cleaned up {len(entries_to_remove)} duplicate entries")
        
        return len(entries_to_remove)

# Singleton instance
data_manager = DataManager()