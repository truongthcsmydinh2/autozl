# -*- coding: utf-8 -*-
"""
Unified Data Manager with Supabase Integration
Quản lý tập trung dữ liệu devices và phone mapping với Supabase và fallback JSON
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import Supabase repositories
try:
    from database.device_repository import DeviceRepository
    from database.log_repository import LogRepository
    from database.supabase_manager import SupabaseManager
    SUPABASE_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Supabase repositories not available: {e}")
    SUPABASE_AVAILABLE = False

class DataManager:
    """Singleton class quản lý tập trung dữ liệu với Supabase và JSON fallback"""
    
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
            
            # Data storage (for fallback)
            self.master_config = {}
            self.phone_mapping = {}
            self.device_data = {}
            
            # Supabase repositories
            self.use_supabase = False
            self.device_repo = None
            self.log_repo = None
            
            # Initialize data sources
            self._initialize_data_sources()
            DataManager._initialized = True
    
    def _initialize_data_sources(self):
        """Initialize Supabase repositories or fallback to JSON"""
        try:
            if SUPABASE_AVAILABLE:
                # Try to initialize Supabase
                supabase_manager = SupabaseManager()
                if supabase_manager.test_connection():
                    self.device_repo = DeviceRepository()
                    self.log_repo = LogRepository()
                    self.use_supabase = True
                    print("[OK] DataManager: Using Supabase for data storage")
                    # Still load phone_mapping from JSON for sync operations
                    self._load_phone_mapping_from_json()
                else:
                    print("[WARNING] DataManager: Supabase connection failed, using JSON fallback")
                    self._load_json_data()
            else:
                print("[WARNING] DataManager: Supabase not available, using JSON fallback")
                self._load_json_data()
        except Exception as e:
            print(f"[ERROR] DataManager: Error initializing Supabase: {e}")
            print("[WARNING] DataManager: Falling back to JSON storage")
            self._load_json_data()
    
    def _load_phone_mapping_from_json(self):
        """Load phone mapping from JSON file (for Supabase mode)"""
        try:
            # Load phone mapping from original file
            if os.path.exists(self.phone_mapping_file):
                with open(self.phone_mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'phone_mapping' in data:
                        self.phone_mapping.update(data['phone_mapping'])
                        print(f"[OK] Loaded phone mapping from JSON: {len(self.phone_mapping)} entries")
                    elif isinstance(data, dict):
                        self.phone_mapping.update(data)
                        print(f"[OK] Loaded phone mapping from JSON: {len(self.phone_mapping)} entries")
        except Exception as e:
            print(f"[ERROR] Error loading phone mapping from JSON: {e}")
    
    def _load_json_data(self):
        """Load data from JSON files (fallback method)"""
        self.use_supabase = False
        try:
            # Load from master config or migrate from legacy files
            if os.path.exists(self.master_config_file):
                with open(self.master_config_file, 'r', encoding='utf-8') as f:
                    self.master_config = json.load(f)
                
                # Extract data from master config
                if 'devices' in self.master_config:
                    devices = self.master_config['devices']
                    for device_id, device_data in devices.items():
                        phone = device_data.get('phone', '')
                        self.phone_mapping[device_id] = phone
                        
                        self.device_data[device_id] = {
                            'phone': phone,
                            'note': device_data.get('note', ''),
                            'zalo_number': device_data.get('zalo_number', ''),
                            'device_info': device_data.get('device_info', {}),
                            'last_updated': device_data.get('last_updated', '')
                        }
                
                print(f"[OK] Loaded from JSON: {len(self.phone_mapping)} phone mappings, {len(self.device_data)} devices")
            else:
                print("[INFO] Master config not found, migrating from legacy files...")
                self._migrate_from_legacy_files()
                
        except Exception as e:
            print(f"[ERROR] Error loading JSON data: {e}")
            self._migrate_from_legacy_files()
    
    def _migrate_from_legacy_files(self):
        """Migrate data from legacy files to master_config.json"""
        try:
            # Load phone mapping from original file
            if os.path.exists(self.phone_mapping_file):
                with open(self.phone_mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'phone_mapping' in data:
                        self.phone_mapping.update(data['phone_mapping'])
                    elif isinstance(data, dict):
                        self.phone_mapping.update(data)
            
            # Load device data from original file
            if os.path.exists(self.device_data_file):
                with open(self.device_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.device_data.update(data)
            
            # Load phone mapping from config folder (higher priority)
            if os.path.exists(self.config_phone_mapping_file):
                with open(self.config_phone_mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'phone_mapping' in data:
                        self.phone_mapping.update(data['phone_mapping'])
                    elif isinstance(data, dict):
                        self.phone_mapping.update(data)
            
            print(f"[INFO] Migrated {len(self.phone_mapping)} phone mappings and {len(self.device_data)} devices")
            
            # Create master config from migrated data
            self._create_master_config_from_legacy()
            
        except Exception as e:
            print(f"[ERROR] Error migrating legacy files: {e}")
    
    def _create_master_config_from_legacy(self):
        """Create master_config.json from legacy data"""
        try:
            # Create master config structure
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
            
            # Merge device data and phone mapping
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
            
            # Save master config
            self._save_master_config()
            print(f"[OK] Created master_config.json with {len(self.master_config['devices'])} devices")
            
        except Exception as e:
            print(f"[ERROR] Error creating master config: {e}")
    
    def get_phone_mapping(self, device_id: str = None) -> Dict[str, str]:
        """Get phone mapping from Supabase or JSON"""
        try:
            if self.use_supabase and self.device_repo:
                # Get from Supabase
                if device_id:
                    result = self.device_repo.db.supabase.table('devices').select('device_id, phone_number').eq('device_id', device_id).execute()
                    if result.data:
                        return result.data[0].get('phone_number', '')
                    return ''
                else:
                    result = self.device_repo.db.supabase.table('devices').select('device_id, phone_number').execute()
                    mapping = {}
                    for device in result.data:
                        mapping[device['device_id']] = device.get('phone_number', '')
                    return mapping
            else:
                # Fallback to JSON
                if device_id:
                    return self.phone_mapping.get(device_id, "")
                return self.phone_mapping.copy()
        except Exception as e:
            print(f"[ERROR] Error getting phone mapping: {e}")
            # Fallback to JSON
            if device_id:
                return self.phone_mapping.get(device_id, "")
            return self.phone_mapping.copy()
    
    def get_phone_by_ip(self, ip: str) -> Optional[str]:
        """Get phone number by IP"""
        device_key = ip if ':' in ip else f"{ip}:5555"
        return self.get_phone_mapping(device_key)
    
    def set_phone_mapping(self, device_id: str, phone: str) -> bool:
        """Set phone mapping for device"""
        try:
            if self.use_supabase and self.device_repo:
                # Update in Supabase
                result = self.device_repo.db.supabase.table('devices').select('*').eq('device_id', device_id).execute()
                if result.data:
                    # Update existing device
                    device = result.data[0]
                    self.device_repo.update_device(device['id'], {'phone_number': phone})
                else:
                    # Create new device
                    device_info = {
                        'device_id': device_id,
                        'phone_number': phone,
                        'status': 'idle',
                        'message': '',
                        'progress': 0
                    }
                    self.device_repo.create_device(device_info)
                
                # Also update JSON for fallback
                self.phone_mapping[device_id] = phone
                self._update_master_config_device(device_id, {'phone': phone})
                return True
            else:
                # Update JSON only
                self.phone_mapping[device_id] = phone
                return self._update_master_config_device(device_id, {'phone': phone})
                
        except Exception as e:
            print(f"[ERROR] Error setting phone mapping: {e}")
            # Fallback to JSON
            self.phone_mapping[device_id] = phone
            return self._update_master_config_device(device_id, {'phone': phone})
    
    def remove_phone_mapping(self, device_id: str) -> bool:
        """Remove phone mapping"""
        try:
            if self.use_supabase and self.device_repo:
                # Update in Supabase
                result = self.device_repo.db.supabase.table('devices').select('*').eq('device_id', device_id).execute()
                if result.data:
                    device = result.data[0]
                    self.device_repo.update_device(device['id'], {'phone_number': ''})
                
                # Also update JSON for fallback
                if device_id in self.phone_mapping:
                    del self.phone_mapping[device_id]
                self._update_master_config_device(device_id, {'phone': ''})
                return True
            else:
                # Update JSON only
                if device_id in self.phone_mapping:
                    del self.phone_mapping[device_id]
                return self._update_master_config_device(device_id, {'phone': ''})
                
        except Exception as e:
            print(f"[ERROR] Error removing phone mapping: {e}")
            # Fallback to JSON
            if device_id in self.phone_mapping:
                del self.phone_mapping[device_id]
            return self._update_master_config_device(device_id, {'phone': ''})
    
    def get_device_note(self, ip: str) -> Optional[str]:
        """Get device note by IP"""
        try:
            device_key = ip if ':' in ip else f"{ip}:5555"
            
            if self.use_supabase and self.device_repo:
                # Get from Supabase
                result = self.device_repo.db.supabase.table('devices').select('message').eq('device_id', device_key).execute()
                if result.data:
                    return result.data[0].get('message', '')
                return None
            else:
                # Fallback to JSON
                if device_key in self.device_data:
                    return self.device_data[device_key].get('note', '')
                
                if 'devices' in self.master_config and device_key in self.master_config['devices']:
                    return self.master_config['devices'][device_key].get('note', '')
                
                return None
        except Exception as e:
            print(f"[ERROR] Error getting device note: {e}")
            # Fallback to JSON
            device_key = ip if ':' in ip else f"{ip}:5555"
            if device_key in self.device_data:
                return self.device_data[device_key].get('note', '')
            return None
    
    def set_device_note(self, device_id: str, note: str) -> bool:
        """Update device note"""
        try:
            if self.use_supabase and self.device_repo:
                # Update in Supabase
                result = self.device_repo.db.supabase.table('devices').select('*').eq('device_id', device_id).execute()
                if result.data:
                    device = result.data[0]
                    self.device_repo.update_device(device['id'], {'message': note})
                else:
                    # Create new device
                    device_info = {
                        'device_id': device_id,
                        'phone_number': self.phone_mapping.get(device_id, ''),
                        'status': 'idle',
                        'message': note,
                        'progress': 0
                    }
                    self.device_repo.create_device(device_info)
                
                # Also update JSON for fallback
                if device_id not in self.device_data:
                    self.device_data[device_id] = {}
                self.device_data[device_id]['note'] = note
                return self._update_master_config_device(device_id, {'note': note})
            else:
                # Update JSON only
                if device_id not in self.device_data:
                    self.device_data[device_id] = {}
                self.device_data[device_id]['note'] = note
                return self._update_master_config_device(device_id, {'note': note})
                
        except Exception as e:
            print(f"[ERROR] Error setting device note: {e}")
            # Fallback to JSON
            if device_id not in self.device_data:
                self.device_data[device_id] = {}
            self.device_data[device_id]['note'] = note
            return self._update_master_config_device(device_id, {'note': note})
    
    def get_device_phone(self, device_id: str) -> Optional[str]:
        """Get device phone number"""
        return self.get_phone_mapping(device_id)
    
    def set_device_phone(self, device_id: str, phone: str) -> bool:
        """Set device phone number"""
        return self.set_phone_mapping(device_id, phone)
    
    def update_device_phone(self, device_id: str, phone: str) -> bool:
        """Update device phone number - alias for set_phone_mapping"""
        return self.set_phone_mapping(device_id, phone)
    
    def get_device_name(self, device_id: str) -> str:
        """Get custom device name by device ID"""
        try:
            if self.use_supabase and self.device_repo:
                # Get from Supabase
                result = self.device_repo.db.supabase.table('devices').select('custom_name').eq('device_id', device_id).execute()
                if result.data and result.data[0].get('custom_name'):
                    return result.data[0]['custom_name']
                # Fallback to device_id if no custom name
                return device_id
            else:
                # Fallback to JSON
                if device_id in self.device_data and 'custom_name' in self.device_data[device_id]:
                    return self.device_data[device_id]['custom_name']
                
                if 'devices' in self.master_config and device_id in self.master_config['devices']:
                    return self.master_config['devices'][device_id].get('custom_name', device_id)
                
                return device_id
        except Exception as e:
            print(f"[ERROR] Error getting device name: {e}")
            return device_id
    
    def set_device_name(self, device_id: str, name: str) -> bool:
        """Set custom device name"""
        try:
            if self.use_supabase and self.device_repo:
                # Update in Supabase
                result = self.device_repo.db.supabase.table('devices').select('*').eq('device_id', device_id).execute()
                if result.data:
                    device = result.data[0]
                    self.device_repo.update_device(device['id'], {'custom_name': name})
                else:
                    # Create new device
                    device_info = {
                        'device_id': device_id,
                        'phone_number': self.phone_mapping.get(device_id, ''),
                        'status': 'idle',
                        'message': '',
                        'custom_name': name,
                        'progress': 0
                    }
                    self.device_repo.create_device(device_info)
                
                # Also update JSON for fallback
                if device_id not in self.device_data:
                    self.device_data[device_id] = {}
                self.device_data[device_id]['custom_name'] = name
                return self._update_master_config_device(device_id, {'custom_name': name})
            else:
                # Update JSON only
                if device_id not in self.device_data:
                    self.device_data[device_id] = {}
                self.device_data[device_id]['custom_name'] = name
                return self._update_master_config_device(device_id, {'custom_name': name})
                
        except Exception as e:
            print(f"[ERROR] Error setting device name: {e}")
            # Fallback to JSON
            if device_id not in self.device_data:
                self.device_data[device_id] = {}
            self.device_data[device_id]['custom_name'] = name
            return self._update_master_config_device(device_id, {'custom_name': name})
    
    def get_devices_with_phone_numbers(self) -> List[Dict]:
        """Get list of devices with phone numbers for UI - scan only, no auto-save to database"""
        devices = []
        current_adb_devices = set()
        
        try:
            # Get current ADB devices for display only
            import subprocess
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip() and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            device_id = parts[0].strip()
                            status = parts[1].strip()
                            if status == 'device':  # Only ready devices
                                # Detect device type: USB (no port) vs LAN (with port)
                                if ':' in device_id:
                                    # LAN connection - keep as is
                                    current_adb_devices.add(device_id)
                                else:
                                    # USB connection - don't add port
                                    current_adb_devices.add(device_id)
        except Exception as e:
            print(f"[WARNING] Warning: Could not get ADB devices: {e}")
            # Continue with empty current_adb_devices set
        
        try:
            # Process ALL current ADB devices - scan only, no database operations
            for device_key in current_adb_devices:
                try:
                    ip = device_key.split(':')[0] if ':' in device_key else device_key
                    
                    # Determine device type
                    device_type = 'LAN' if ':' in device_key else 'USB'
                    
                    # Get phone mapping - check multiple formats for compatibility
                    phone = ''
                    # For USB devices, check both with and without :5555
                    if device_type == 'USB':
                        phone = self.phone_mapping.get(device_key, '') or self.phone_mapping.get(f"{device_key}:5555", '')
                    else:
                        # For LAN devices, check exact match and IP only
                        phone = self.phone_mapping.get(device_key, '') or self.phone_mapping.get(ip, '')
                    
                    # Get device name from existing data (if any) - no database query
                    device_name = device_key
                    if self.use_supabase:
                        # Only check existing data, don't create new entries
                        try:
                            result = self.device_repo.db.supabase.table('devices').select('custom_name').eq('device_id', device_key).execute()
                            if result.data and result.data[0].get('custom_name'):
                                device_name = result.data[0]['custom_name']
                        except:
                            pass  # Use default name if query fails
                    else:
                        # Check JSON data
                        device_name = self.device_data.get(device_key, {}).get('custom_name', device_key)
                    
                    device_info = {
                        'ip': ip,
                        'device_id': device_key,
                        'phone': phone,
                        'note': '',  # Don't load notes for scan-only mode
                        'status': 'connected',  # Show as connected since it's from ADB
                        'name': device_name,
                        'type': device_type  # Add device type info
                    }
                    devices.append(device_info)
                    
                except Exception as e:
                    print(f"[WARNING] Warning: Error processing device {device_key}: {e}")
                    continue
                        
        except Exception as e:
            print(f"[ERROR] Error getting devices with phone numbers: {e}")
            # Fallback to existing data without ADB check
            try:
                if self.use_supabase and self.device_repo:
                    result = self.device_repo.db.supabase.table('devices').select('*').execute()
                    if result and result.data:
                        for device in result.data:
                            device_id = device.get('device_id', '')
                            if ':5555' in device_id:
                                ip = device_id.split(':')[0]
                                phone = self.phone_mapping.get(device_id, '') or device.get('phone_number', '')
                                device_info = {
                                    'ip': ip,
                                    'device_id': device_id,
                                    'phone': phone,
                                    'note': device.get('message', ''),
                                    'status': 'offline',  # Mark as offline since ADB check failed
                                    'name': device.get('custom_name', device_id)
                                }
                                devices.append(device_info)
                else:
                    # Fallback to JSON data
                    for device_key, device_data in self.device_data.items():
                        if ':5555' in device_key:
                            ip = device_key.split(':')[0]
                            device_info = {
                                'ip': ip,
                                'device_id': device_key,
                                'phone': self.phone_mapping.get(device_key, ''),
                                'note': device_data.get('note', ''),
                                'status': 'offline',  # Mark as offline since ADB check failed
                                'name': device_data.get('custom_name', device_key)
                            }
                            devices.append(device_info)
            except Exception as fallback_error:
                print(f"[ERROR] Fallback also failed: {fallback_error}")
                # Return empty list if all else fails
                devices = []
        
        return devices
    
    def _update_master_config_device(self, device_id: str, updates: Dict) -> bool:
        """Update device in master config"""
        try:
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
                    'note': '',
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # Apply updates
            self.master_config['devices'][device_id].update(updates)
            self.master_config['devices'][device_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return self._save_master_config()
        except Exception as e:
            print(f"[ERROR] Error updating master config device: {e}")
            return False
    
    def _save_master_config(self):
        """Save master config to file"""
        try:
            # Update metadata
            if 'metadata' not in self.master_config:
                self.master_config['metadata'] = {}
            
            self.master_config['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Ensure config directory exists
            os.makedirs('config', exist_ok=True)
            
            # Save master config
            with open(self.master_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.master_config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error saving master config: {e}")
            return False
    
    def get_device_data(self) -> Dict:
        """Get current device data"""
        return self.device_data.copy()
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Get all devices for API compatibility"""
        try:
            if self.use_supabase and self.device_repo:
                # Get from Supabase
                devices = self.device_repo.get_all_devices()
                result = []
                for device in devices:
                    device_info = {
                        'id': device.get('id'),
                        'device_id': device.get('device_id', ''),
                        'name': device.get('custom_name') or device.get('device_id', ''),
                        'phone_number': device.get('phone_number', ''),
                        'ip_address': device.get('device_id', '').split(':')[0] if ':' in device.get('device_id', '') else device.get('device_id', ''),
                        'status': device.get('status', 'offline'),
                        'message': device.get('message', ''),
                        'progress': device.get('progress', 0),
                        'created_at': device.get('created_at'),
                        'updated_at': device.get('updated_at')
                    }
                    result.append(device_info)
                return result
            else:
                # Fallback to get_devices_with_phone_numbers for JSON mode
                return self.get_devices_with_phone_numbers()
        except Exception as e:
            print(f"[ERROR] Error getting all devices: {e}")
            # Fallback to get_devices_with_phone_numbers
            return self.get_devices_with_phone_numbers()
    
    def reload_data(self):
        """Reload data from all sources"""
        if self.use_supabase:
            # Reinitialize Supabase connection
            self._initialize_data_sources()
        else:
            # Reload JSON data
            self.phone_mapping.clear()
            self.device_data.clear()
            self._load_json_data()
        print("[DataManager] Data reloaded from all sources")
    
    def sync_with_adb_devices(self):
        """Sync data with actual ADB devices"""
        import subprocess
        try:
            # Get device list from ADB
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            current_devices = set()
            for line in lines:
                if line.strip() and '\t' in line:
                    device_id = line.split('\t')[0]
                    status = line.split('\t')[1]
                    if status == 'device':  # Only ready devices
                        current_devices.add(device_id)
            
            # Format current devices with port
            current_formatted_devices = set()
            for device_id in current_devices:
                formatted_device_id = device_id if ':' in device_id else f"{device_id}:5555"
                current_formatted_devices.add(formatted_device_id)
            
            if self.use_supabase and self.device_repo:
                # Get all existing devices from Supabase
                existing_result = self.device_repo.db.supabase.table('devices').select('*').execute()
                existing_devices = {device['device_id']: device for device in existing_result.data}
                
                # Remove or mark offline devices that are no longer connected
                for existing_device_id, existing_device in existing_devices.items():
                    if existing_device_id not in current_formatted_devices:
                        # Device is no longer connected - remove from Supabase
                        self.device_repo.db.supabase.table('devices').delete().eq('id', existing_device['id']).execute()
                        print(f"[INFO] Removed disconnected device {existing_device_id}")
                
                # Update or create connected devices
                for device_id in current_devices:
                    formatted_device_id = device_id if ':' in device_id else f"{device_id}:5555"
                    
                    if formatted_device_id not in existing_devices:
                        # Create new device in Supabase with phone mapping
                        phone_number = self.phone_mapping.get(formatted_device_id, '')
                        
                        device_info = {
                            'device_id': formatted_device_id,
                            'phone_number': phone_number,
                            'status': 'idle',
                            'message': '',
                            'progress': 0
                        }
                        self.device_repo.create_device(device_info)
                        print(f"[OK] Created device {formatted_device_id} with phone {phone_number}")
                    else:
                        # Update existing device with phone mapping if needed
                        existing_device = existing_devices[formatted_device_id]
                        phone_number = self.phone_mapping.get(formatted_device_id, '')
                        
                        updates = {}
                        if phone_number and existing_device.get('phone_number') != phone_number:
                            updates['phone_number'] = phone_number
                        
                        # Ensure device is marked as connected/idle
                        if existing_device.get('status') != 'idle':
                            updates['status'] = 'idle'
                        
                        if updates:
                            self.device_repo.update_device(existing_device['id'], updates)
                            print(f"[OK] Updated device {formatted_device_id}")
            
            # Update JSON data - remove disconnected devices
            devices_to_remove = []
            for device_key in self.device_data.keys():
                if ':5555' in device_key and device_key not in current_formatted_devices:
                    devices_to_remove.append(device_key)
            
            for device_key in devices_to_remove:
                del self.device_data[device_key]
                if device_key in self.phone_mapping:
                    # Keep phone mapping for future reconnections
                    pass
                print(f"[INFO] Removed disconnected device from JSON: {device_key}")
            
            # Add or update connected devices in JSON
            for device_id in current_devices:
                formatted_device_id = device_id if ':' in device_id else f"{device_id}:5555"
                
                if formatted_device_id not in self.device_data:
                    self.device_data[formatted_device_id] = {
                        "phone": "",
                        "note": "",
                        "last_updated": self._get_current_timestamp()
                    }
                else:
                    self.device_data[formatted_device_id]["last_updated"] = self._get_current_timestamp()
                
                if formatted_device_id not in self.phone_mapping:
                    self.phone_mapping[formatted_device_id] = ""
            
            # Save JSON data
            self._save_master_config()
            
            return len(current_devices)
            
        except Exception as e:
            print(f"[DataManager] Error syncing with ADB devices: {e}")
            return 0
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cleanup_duplicate_entries(self):
        """Remove all entries with only IP (no port) from phone_mapping"""
        entries_to_remove = []
        
        for key in self.phone_mapping.keys():
            if ':' not in key:  # Entry with only IP, no port
                entries_to_remove.append(key)
        
        for key in entries_to_remove:
            del self.phone_mapping[key]
            print(f"[DataManager] Removed duplicate entry: {key}")
        
        if entries_to_remove:
            self._save_master_config()
            print(f"[DataManager] Cleaned up {len(entries_to_remove)} duplicate entries")
        
        return len(entries_to_remove)
    
    def log_action(self, device_id: str, action: str, status: str, message: str = ""):
        """Log action to Supabase or fallback to file"""
        try:
            if self.use_supabase and self.log_repo:
                # Get device UUID from device_id
                result = self.device_repo.db.supabase.table('devices').select('id').eq('device_id', device_id).execute()
                if result.data:
                    device_uuid = result.data[0]['id']
                    
                    log_entry = {
                        'device_id': device_uuid,
                        'session_id': f"action_{device_id}_{int(time.time())}",
                        'log_level': 'info' if status == 'success' else 'error',
                        'component': 'automation',
                        'message': f"Action: {action}, Status: {status}. {message}",
                        'metadata': {
                            'action': action,
                            'status': status,
                            'original_device_id': device_id
                        }
                    }
                    
                    self.log_repo.create_log(log_entry)
                    return True
            
            # Fallback to file logging
            log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Device: {device_id}, Action: {action}, Status: {status}. {message}\n"
            os.makedirs('logs', exist_ok=True)
            with open('logs/automation.log', 'a', encoding='utf-8') as f:
                f.write(log_message)
            return True
            
        except Exception as e:
            print(f"[ERROR] Error logging action: {e}")
            return False

# Singleton instance
data_manager = DataManager()