#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supabase Repository Classes
Thay thế các operations với JSON files bằng Supabase database operations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseConnection:
    """Singleton class for Supabase connection"""
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_client(self) -> Client:
        if self._client is None:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables")
            
            self._client = create_client(supabase_url, supabase_key)
        
        return self._client

class DeviceMappingRepository:
    """Repository for device mapping operations (replaces phone_mapping.json)"""
    
    def __init__(self):
        self.supabase = SupabaseConnection().get_client()
        self.table_name = 'devices'
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all device mappings as dict {device_id: phone_number}"""
        try:
            result = self.supabase.table(self.table_name).select('device_id, phone_number').execute()
            
            mappings = {}
            for row in result.data:
                if row['phone_number']:  # Only include devices with phone numbers
                    mappings[row['device_id']] = row['phone_number']
            
            return mappings
        except Exception as e:
            print(f"Error getting device mappings: {e}")
            return {}
    
    def get_phone_number(self, device_id: str) -> Optional[str]:
        """Get phone number for specific device"""
        try:
            result = self.supabase.table(self.table_name).select('phone_number').eq('device_id', device_id).execute()
            
            if result.data:
                return result.data[0]['phone_number']
            return None
        except Exception as e:
            print(f"Error getting phone number for device {device_id}: {e}")
            return None
    
    def set_phone_mapping(self, device_id: str, phone_number: str, created_by: str = "system") -> bool:
        """Set or update phone mapping for device"""
        try:
            # Use upsert to update phone_number in devices table
            upsert_data = {
                'device_id': device_id,
                'phone_number': phone_number,
                'last_update': datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name).upsert(upsert_data, on_conflict='device_id').execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error setting phone mapping for device {device_id}: {e}")
            return False
    
    def remove_mapping(self, device_id: str) -> bool:
        """Remove device mapping (set phone_number to null)"""
        try:
            result = self.supabase.table(self.table_name).update({
                'phone_number': None,
                'last_update': datetime.now().isoformat()
            }).eq('device_id', device_id).execute()
            return True
        except Exception as e:
            print(f"Error removing mapping for device {device_id}: {e}")
            return False

class DeviceStatusRepository:
    """Repository for device status operations (replaces status.json)"""
    
    def __init__(self):
        self.supabase = SupabaseConnection().get_client()
        self.table_name = 'devices'
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get all device status as dict {device_id: status_info}"""
        try:
            result = self.supabase.table(self.table_name).select('device_id, status, message, progress, current_message_id, last_update').execute()
            
            status_dict = {}
            for row in result.data:
                status_dict[row['device_id']] = {
                    'status': row['status'],
                    'message': row['message'] or '',
                    'progress': row['progress'] or 0,
                    'current_message_id': row['current_message_id'],
                    'last_update': row['last_update'],
                    'timestamp': row['last_update']  # Use last_update as timestamp
                }
            
            return status_dict
        except Exception as e:
            print(f"Error getting device status: {e}")
            return {}
    
    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """Get status for specific device"""
        try:
            result = self.supabase.table(self.table_name).select('device_id, status, message, progress, current_message_id, last_update').eq('device_id', device_id).execute()
            
            if result.data:
                row = result.data[0]
                return {
                    'status': row['status'],
                    'message': row['message'] or '',
                    'progress': row['progress'] or 0,
                    'current_message_id': row['current_message_id'],
                    'last_update': row['last_update'],
                    'timestamp': row['last_update']  # Use last_update as timestamp
                }
            return None
        except Exception as e:
            print(f"Error getting status for device {device_id}: {e}")
            return None
    
    def update_device_status(self, device_id: str, status: str, message: str = '', 
                           progress: int = 0, current_message_id: str = '') -> bool:
        """Update device status using upsert"""
        try:
            from datetime import datetime
            
            upsert_data = {
                'device_id': device_id,
                'status': status,
                'message': message,
                'progress': progress,
                'current_message_id': current_message_id,
                'last_update': datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name).upsert(upsert_data, on_conflict='device_id').execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating device status: {e}")
            return False
    
    def clear_all_status(self) -> bool:
        """Clear all device status"""
        try:
            result = self.supabase.table(self.table_name).delete().neq('id', 0).execute()
            return True
        except Exception as e:
            print(f"Error clearing device status: {e}")
            return False

class ConversationRepository:
    """Repository for conversation templates (replaces conversations.json)"""
    
    def __init__(self):
        self.supabase = SupabaseConnection().get_client()
        self.table_name = 'conversation_templates'
    
    def get_conversation_by_group(self, group_id: int) -> Optional[List[Dict]]:
        """Get conversation messages by group ID"""
        try:
            result = self.supabase.table(self.table_name).select('messages').eq('group_id', group_id).execute()
            
            if result.data:
                messages_json = result.data[0]['messages']
                return json.loads(messages_json)
            return None
        except Exception as e:
            print(f"Error getting conversation for group {group_id}: {e}")
            return None
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversation templates"""
        try:
            result = self.supabase.table(self.table_name).select('*').execute()
            
            conversations = []
            for row in result.data:
                conversations.append({
                    'group_id': row['group_id'],
                    'messages': json.loads(row['messages'])
                })
            
            return conversations
        except Exception as e:
            print(f"Error getting all conversations: {e}")
            return []
    
    def save_conversation(self, group_id: int, messages: List[Dict]) -> bool:
        """Save or update conversation template"""
        try:
            # Check if conversation exists
            existing = self.supabase.table(self.table_name).select('id').eq('group_id', group_id).execute()
            
            messages_json = json.dumps(messages, ensure_ascii=False)
            
            if existing.data:
                # Update existing
                result = self.supabase.table(self.table_name).update({
                    'messages': messages_json,
                    'updated_at': datetime.now().isoformat()
                }).eq('group_id', group_id).execute()
            else:
                # Insert new
                result = self.supabase.table(self.table_name).insert({
                    'group_id': group_id,
                    'messages': messages_json
                }).execute()
            
            return True
        except Exception as e:
            print(f"Error saving conversation for group {group_id}: {e}")
            return False

class AppConfigRepository:
    """Repository for app configuration (replaces config/app_config.json)"""
    
    def __init__(self):
        self.supabase = SupabaseConnection().get_client()
        self.table_name = 'app_configs'
    
    def get_config(self, config_name: str = 'app_config') -> Optional[Dict]:
        """Get app configuration"""
        try:
            result = self.supabase.table(self.table_name).select('config_data').eq('config_name', config_name).execute()
            
            if result.data:
                config_json = result.data[0]['config_data']
                return json.loads(config_json)
            return None
        except Exception as e:
            print(f"Error getting config {config_name}: {e}")
            return None
    
    def save_config(self, config_data: Dict, config_name: str = 'app_config') -> bool:
        """Save or update app configuration"""
        try:
            # Check if config exists
            existing = self.supabase.table(self.table_name).select('id').eq('config_name', config_name).execute()
            
            config_json = json.dumps(config_data, ensure_ascii=False)
            
            if existing.data:
                # Update existing
                result = self.supabase.table(self.table_name).update({
                    'config_data': config_json,
                    'updated_at': datetime.now().isoformat()
                }).eq('config_name', config_name).execute()
            else:
                # Insert new
                result = self.supabase.table(self.table_name).insert({
                    'config_name': config_name,
                    'config_data': config_json
                }).execute()
            
            return True
        except Exception as e:
            print(f"Error saving config {config_name}: {e}")
            return False