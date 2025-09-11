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
        
        # 1. Load từ phone_mapping.json (core1.py)
        core_mapping = self._load_json_file(self.phone_mapping_file)
        if core_mapping and 'phone_mapping' in core_mapping:
            self._phone_mapping.update(core_mapping['phone_mapping'])
            print(f"[DataManager] Loaded {len(core_mapping['phone_mapping'])} entries from core phone_mapping.json")
        
        # 2. Load từ device_data.json (GUI)
        device_data = self._load_json_file(self.device_data_file)
        if device_data:
            # Convert device_data format to phone_mapping format
            for device_id, data in device_data.items():
                if 'phone' in data and data['phone']:
                    # Extract IP from device_id
                    ip = device_id.split(':')[0] if ':' in device_id else device_id
                    self._phone_mapping[ip] = data['phone']
            self._device_data = device_data
            print(f"[DataManager] Loaded {len(device_data)} entries from device_data.json")
        
        # 3. Load từ config/phone_mapping.json (GUI config)
        config_mapping = self._load_json_file(self.config_phone_mapping_file)
        if config_mapping and 'phone_mapping' in config_mapping:
            self._phone_mapping.update(config_mapping['phone_mapping'])
            print(f"[DataManager] Loaded {len(config_mapping['phone_mapping'])} entries from config phone_mapping.json")
        
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
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
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
        # Normalize IP (remove port if exists)
        clean_ip = ip.split(':')[0] if ':' in ip else ip
        return self._phone_mapping.get(clean_ip)
    
    def set_phone_mapping(self, ip: str, phone: str) -> bool:
        """Cập nhật phone mapping"""
        # Normalize IP
        clean_ip = ip.split(':')[0] if ':' in ip else ip
        
        # Update in-memory data
        self._phone_mapping[clean_ip] = phone
        
        # Update device_data format
        device_key = f"{clean_ip}:5555"
        if device_key not in self._device_data:
            self._device_data[device_key] = {}
        self._device_data[device_key]['phone'] = phone
        
        # Save to all files
        return self._save_all_data()
    
    def remove_phone_mapping(self, ip: str) -> bool:
        """Xóa phone mapping"""
        clean_ip = ip.split(':')[0] if ':' in ip else ip
        
        # Remove from in-memory data
        if clean_ip in self._phone_mapping:
            del self._phone_mapping[clean_ip]
        
        # Remove from device_data
        device_key = f"{clean_ip}:5555"
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
        
        # Get all unique IPs from both sources
        all_ips = set()
        
        # From phone mapping
        all_ips.update(self._phone_mapping.keys())
        
        # From device data
        for device_key in self._device_data.keys():
            ip = device_key.split(':')[0] if ':' in device_key else device_key
            all_ips.add(ip)
        
        for ip in sorted(all_ips):
            device_info = {
                'ip': ip,
                'device_id': f"{ip}:5555",
                'phone': self.get_phone_by_ip(ip) or '',
                'note': self._device_data.get(f"{ip}:5555", {}).get('note', '')
            }
            devices.append(device_info)
        
        return devices
    
    def reload_data(self):
        """Reload data từ tất cả các file"""
        self._phone_mapping.clear()
        self._device_data.clear()
        self._load_all_data()
        print("[DataManager] Data reloaded from all sources")

# Singleton instance
data_manager = DataManager()