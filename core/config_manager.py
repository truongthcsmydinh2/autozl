#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager Module
Quản lý cấu hình ứng dụng và settings
"""

import os
import json
import time
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from utils.data_manager import data_manager

class ConfigManager(QObject):
    """Configuration Manager với GUI integration"""
    
    # Signals
    config_changed = pyqtSignal(str, object)  # key, value
    config_loaded = pyqtSignal()
    config_saved = pyqtSignal()
    log_message = pyqtSignal(str, str)  # message, level
    
    def __init__(self):
        super().__init__()
        self.config_dir = "config"
        # Legacy config file for app settings only
        self.config_file = os.path.join(self.config_dir, "app_config.json")
        
        # Default configuration
        self.default_config = {
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
                "max_log_size": 10485760,  # 10MB
                "backup_count": 5,
                "log_format": "%(asctime)s - %(levelname)s - %(message)s"
            }
        }
        
        self.config = self.default_config.copy()
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration từ file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge với default config để đảm bảo có đầy đủ keys
                self.config = self._merge_config(self.default_config, loaded_config)
                
                self.config_loaded.emit()
                self.log_message.emit("✅ Đã load configuration", "SUCCESS")
                return True
            else:
                # Tạo file config mới với default values
                self.save_config()
                self.log_message.emit("📝 Đã tạo configuration file mới", "INFO")
                return True
                
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi load configuration: {e}", "ERROR")
            # Fallback to default config
            self.config = self.default_config.copy()
            return False
    
    def save_config(self) -> bool:
        """Lưu configuration vào file"""
        try:
            config_data = {
                "config": self.config,
                "timestamp": time.time(),
                "version": "1.0.0",
                "created_by": "Android Automation GUI"
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.config_saved.emit()
            self.log_message.emit("💾 Đã lưu configuration", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi lưu configuration: {e}", "ERROR")
            return False
    
    def load_phone_mapping(self) -> bool:
        """Load phone mapping từ DataManager (deprecated - use DataManager directly)"""
        try:
            devices = data_manager.get_devices_with_phone_numbers()
            self.log_message.emit(f"📞 Đã load {len(devices)} devices từ master config", "INFO")
            return True
                
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi load phone mapping: {e}", "ERROR")
            return False
    
    def save_phone_mapping(self) -> bool:
        """Lưu phone mapping vào DataManager (deprecated - use DataManager directly)"""
        try:
            # Phone mapping now managed by DataManager
            self.log_message.emit("💾 Phone mapping được lưu vào master config", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi lưu phone mapping: {e}", "ERROR")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Lấy giá trị config theo key (support nested keys với dot notation)"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def get_config(self) -> Dict[str, Any]:
        """Lấy toàn bộ configuration dictionary"""
        return self.config.copy()
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """Set giá trị config (support nested keys với dot notation)"""
        try:
            keys = key.split('.')
            config_ref = self.config
            
            # Navigate to parent of target key
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Set value
            config_ref[keys[-1]] = value
            
            # Emit signal
            self.config_changed.emit(key, value)
            
            # Auto save if requested
            if save:
                self.save_config()
            
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi set config {key}: {e}", "ERROR")
            return False
    
    def get_phone_mapping(self, ip: str) -> str:
        """Lấy phone number cho IP từ DataManager"""
        try:
            devices = data_manager.get_devices_with_phone_numbers()
            for device in devices:
                if device.get('ip') == ip:
                    return device.get('phone', '')
            return ''
        except Exception:
            return ''
    
    def set_phone_mapping(self, ip: str, phone: str, save: bool = True) -> bool:
        """Set phone mapping cho IP qua DataManager"""
        try:
            data_manager.update_device_phone(ip, phone)
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi set phone mapping: {e}", "ERROR")
            return False
    
    def remove_phone_mapping(self, ip: str, save: bool = True) -> bool:
        """Xóa phone mapping cho IP qua DataManager"""
        try:
            data_manager.update_device_phone(ip, '')
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi xóa phone mapping: {e}", "ERROR")
            return False
    
    def get_all_phone_mappings(self) -> Dict[str, str]:
        """Lấy tất cả phone mappings từ DataManager"""
        try:
            devices = data_manager.get_devices_with_phone_numbers()
            return {device.get('ip', ''): device.get('phone', '') for device in devices if device.get('ip')}
        except Exception:
            return {}
    
    def reset_to_default(self, section: str = None) -> bool:
        """Reset config về default values"""
        try:
            if section:
                if section in self.default_config:
                    self.config[section] = self.default_config[section].copy()
                    self.log_message.emit(f"🔄 Đã reset {section} về default", "INFO")
                else:
                    self.log_message.emit(f"⚠️ Section không tồn tại: {section}", "WARNING")
                    return False
            else:
                self.config = self.default_config.copy()
                self.log_message.emit("🔄 Đã reset toàn bộ config về default", "INFO")
            
            self.save_config()
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi reset config: {e}", "ERROR")
            return False
    
    def export_config(self, file_path: str) -> bool:
        """Export config ra file"""
        try:
            # Get devices from DataManager
            devices = data_manager.get_devices_with_phone_numbers()
            phone_mapping = {device.get('ip', ''): device.get('phone', '') for device in devices if device.get('ip')}
            
            export_data = {
                "config": self.config,
                "phone_mapping": phone_mapping,
                "devices": devices,
                "export_timestamp": time.time(),
                "version": "1.0.0"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log_message.emit(f"📤 Đã export config: {file_path}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi export config: {e}", "ERROR")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """Import config từ file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Import config
            if "config" in import_data:
                self.config = self._merge_config(self.default_config, import_data["config"])
            
            # Import devices to DataManager
            if "devices" in import_data:
                for device in import_data["devices"]:
                    ip = device.get('ip')
                    phone = device.get('phone', '')
                    if ip:
                        data_manager.update_device_phone(ip, phone)
            elif "phone_mapping" in import_data:
                # Fallback for old format
                for ip, phone in import_data["phone_mapping"].items():
                    data_manager.update_device_phone(ip, phone)
            
            # Save imported data
            self.save_config()
            
            self.config_loaded.emit()
            self.log_message.emit(f"📥 Đã import config: {file_path}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi import config: {e}", "ERROR")
            return False
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config với default config"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Vietnamese phone number pattern
        pattern = r'^(\+84|84|0)?[3-9][0-9]{8}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '')))
    
    def get_app_info(self) -> Dict[str, Any]:
        """Lấy thông tin ứng dụng"""
        try:
            devices = data_manager.get_devices_with_phone_numbers()
            devices_count = len(devices)
        except Exception:
            devices_count = 0
            
        return {
            "name": "Android Automation GUI",
            "version": "1.0.0",
            "config_file": self.config_file,
            "master_config_file": data_manager.master_config_file,
            "config_sections": list(self.config.keys()),
            "devices_count": devices_count
        }