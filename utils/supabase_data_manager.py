#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Data Manager
Thay thế DataManager cũ sử dụng JSON files bằng Supabase repositories
"""

import os
import sys
from typing import Dict, List, Optional, Any

# Add repositories to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'repositories'))

from supabase_repository import (
    DeviceMappingRepository,
    DeviceStatusRepository, 
    ConversationRepository,
    AppConfigRepository
)

class SupabaseDataManager:
    """Data manager using Supabase instead of JSON files"""
    
    def __init__(self):
        self.device_mapping_repo = DeviceMappingRepository()
        self.device_status_repo = DeviceStatusRepository()
        self.conversation_repo = ConversationRepository()
        self.app_config_repo = AppConfigRepository()
    
    # Device Mapping Methods (replaces phone_mapping.json operations)
    def load_phone_mapping(self) -> Dict[str, str]:
        """Load phone mapping from Supabase"""
        return self.device_mapping_repo.get_all_mappings()
    
    def save_phone_mapping(self, mapping: Dict[str, str], created_by: str = "system") -> bool:
        """Save phone mapping to Supabase"""
        try:
            for device_id, phone_number in mapping.items():
                if phone_number:  # Only save non-empty phone numbers
                    self.device_mapping_repo.set_phone_mapping(device_id, phone_number, created_by)
            return True
        except Exception as e:
            print(f"Error saving phone mapping: {e}")
            return False
    
    def get_phone_number(self, device_id: str) -> Optional[str]:
        """Get phone number for device"""
        return self.device_mapping_repo.get_phone_number(device_id)
    
    def set_phone_mapping(self, device_id: str, phone_number: str) -> bool:
        """Set phone mapping for single device"""
        return self.device_mapping_repo.set_phone_mapping(device_id, phone_number)
    
    def remove_phone_mapping(self, device_id: str) -> bool:
        """Remove phone mapping for device"""
        return self.device_mapping_repo.remove_mapping(device_id)
    
    # Device Status Methods (replaces status.json operations)
    def load_status(self) -> Dict[str, Any]:
        """Load device status from Supabase"""
        devices_status = self.device_status_repo.get_all_status()
        
        # Calculate overall status
        overall_status = "idle"
        last_update = 0
        
        if devices_status:
            statuses = [status['status'] for status in devices_status.values()]
            
            if any(status == 'running' for status in statuses):
                overall_status = "running"
            elif any(status == 'error' for status in statuses):
                overall_status = "error"
            elif all(status == 'completed' for status in statuses):
                overall_status = "completed"
            
            # Get latest update time
            for status in devices_status.values():
                if status.get('last_update'):
                    try:
                        from datetime import datetime
                        timestamp = datetime.fromisoformat(status['last_update']).timestamp()
                        last_update = max(last_update, timestamp)
                    except:
                        pass
        
        return {
            "devices": devices_status,
            "overall_status": overall_status,
            "last_update": last_update
        }
    
    def save_status(self, status_data: Dict[str, Any]) -> bool:
        """Save device status to Supabase"""
        try:
            devices = status_data.get('devices', {})
            
            for device_id, status_info in devices.items():
                self.device_status_repo.update_device_status(
                    device_id=device_id,
                    status=status_info.get('status', 'unknown'),
                    message=status_info.get('message', ''),
                    progress=status_info.get('progress', 0),
                    current_message_id=status_info.get('current_message_id')
                )
            
            return True
        except Exception as e:
            print(f"Error saving status: {e}")
            return False
    
    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """Get status for specific device"""
        return self.device_status_repo.get_device_status(device_id)
    
    def update_device_status(self, device_id: str, status: str, message: str = "", 
                           progress: int = 0, current_message_id: Optional[str] = None) -> bool:
        """Update status for specific device"""
        return self.device_status_repo.update_device_status(
            device_id, status, message, progress, current_message_id
        )
    
    def clear_all_status(self) -> bool:
        """Clear all device status"""
        return self.device_status_repo.clear_all_status()
    
    # Conversation Methods (replaces conversations.json operations)
    def load_conversations(self) -> List[Dict]:
        """Load all conversation templates from Supabase"""
        return self.conversation_repo.get_all_conversations()
    
    def load_conversation_by_group(self, group_id: int) -> Optional[List[Dict]]:
        """Load conversation by group ID"""
        return self.conversation_repo.get_conversation_by_group(group_id)
    
    def save_conversations(self, conversations: List[Dict]) -> bool:
        """Save conversation templates to Supabase"""
        try:
            for conversation in conversations:
                group_id = conversation.get('group_id')
                messages = conversation.get('messages', [])
                
                if group_id is not None:
                    self.conversation_repo.save_conversation(group_id, messages)
            
            return True
        except Exception as e:
            print(f"Error saving conversations: {e}")
            return False
    
    def save_conversation(self, group_id: int, messages: List[Dict]) -> bool:
        """Save single conversation template"""
        return self.conversation_repo.save_conversation(group_id, messages)
    
    # App Config Methods (replaces config/app_config.json operations)
    def load_app_config(self) -> Optional[Dict]:
        """Load app configuration from Supabase"""
        return self.app_config_repo.get_config('app_config')
    
    def save_app_config(self, config_data: Dict) -> bool:
        """Save app configuration to Supabase"""
        return self.app_config_repo.save_config(config_data, 'app_config')
    
    def get_config_value(self, key_path: str, default=None):
        """Get specific config value using dot notation (e.g., 'ui.language')"""
        config = self.load_app_config()
        if not config:
            return default
        
        keys = key_path.split('.')
        value = config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config_value(self, key_path: str, value) -> bool:
        """Set specific config value using dot notation"""
        config = self.load_app_config() or {}
        
        keys = key_path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        return self.save_app_config(config)
    
    # Utility Methods
    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Try to access each repository
            self.device_mapping_repo.get_all_mappings()
            self.device_status_repo.get_all_status()
            self.conversation_repo.get_all_conversations()
            self.app_config_repo.get_config('app_config')
            return True
        except Exception as e:
            print(f"Supabase connection test failed: {e}")
            return False
    
    def migrate_from_json_files(self) -> bool:
        """Migrate data from existing JSON files to Supabase"""
        try:
            # This would typically be done by the migration script
            # But we can provide a method to trigger it from the data manager
            import subprocess
            import sys
            
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'migration_script.py')
            result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Migration completed successfully")
                return True
            else:
                print(f"Migration failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error running migration: {e}")
            return False
    
    # Sync Data Methods (replaces sync_group_X.json operations)
    def get_sync_data(self, group_id: int) -> Optional[Dict]:
        """Get sync data for a group from Supabase"""
        try:
            # Use automation_logs table to store sync data
            response = self.supabase.table('automation_logs').select('*').eq('group_id', group_id).eq('log_type', 'sync_data').order('created_at', desc=True).limit(1).execute()
            
            if response.data:
                log_entry = response.data[0]
                return {
                    'current_message_id': log_entry.get('current_message_id', 1),
                    'timestamp': log_entry.get('created_at'),
                    'broadcast_signal': log_entry.get('message', '')
                }
            return None
        except Exception as e:
            print(f"Error getting sync data: {e}")
            return None
    
    def update_sync_data(self, group_id: int, sync_data: Dict) -> bool:
        """Update sync data for a group in Supabase"""
        try:
            # Store sync data in automation_logs table
            log_data = {
                'group_id': group_id,
                'log_type': 'sync_data',
                'current_message_id': sync_data.get('current_message_id', 1),
                'message': sync_data.get('broadcast_signal', ''),
                'metadata': {
                    'timestamp': sync_data.get('timestamp'),
                    'sync_type': 'message_sync'
                }
            }
            
            response = self.supabase.table('automation_logs').insert(log_data).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error updating sync data: {e}")
            return False

# Backward compatibility - create instance that can be imported
supabase_data_manager = SupabaseDataManager()

# Legacy function wrappers for backward compatibility
def load_phone_mapping():
    return supabase_data_manager.load_phone_mapping()

def save_phone_mapping(mapping, created_by="system"):
    return supabase_data_manager.save_phone_mapping(mapping, created_by)

def load_status():
    return supabase_data_manager.load_status()

def save_status(status_data):
    return supabase_data_manager.save_status(status_data)

def load_conversations():
    return supabase_data_manager.load_conversations()

def save_conversations(conversations):
    return supabase_data_manager.save_conversations(conversations)