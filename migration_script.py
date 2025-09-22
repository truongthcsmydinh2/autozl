#!/usr/bin/env python3
"""
Supabase Migration Script
Migrates data from JSON files to existing Supabase tables
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase package not found. Please install it with: pip install supabase")
    sys.exit(1)

class SupabaseMigrator:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Missing Supabase credentials in .env file")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            raise Exception(f"❌ Failed to initialize Supabase client: {e}")
    
    def test_connection(self):
        """Test Supabase connection"""
        try:
            # Test with existing devices table
            result = self.supabase.table('devices').select('id').limit(1).execute()
            print("✅ Supabase connection test successful")
            return True
        except Exception as e:
            print(f"❌ Supabase connection test failed: {e}")
            return False
    
    def migrate_phone_mapping(self):
        """Migrate phone_mapping.json to devices table"""
        try:
            if not os.path.exists('phone_mapping.json'):
                print("⚠️  phone_mapping.json not found, skipping...")
                return True
            
            with open('phone_mapping.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            phone_mapping = data.get('phone_mapping', {})
            
            print(f"📱 Migrating {len(phone_mapping)} phone mappings...")
            
            for device_address, phone_number in phone_mapping.items():
                # Check if device already exists
                existing = self.supabase.table('devices').select('id').eq('device_id', device_address).execute()
                
                if existing.data:
                    # Update existing device
                    self.supabase.table('devices').update({
                        'phone_number': phone_number,
                        'updated_at': datetime.now().isoformat()
                    }).eq('device_id', device_address).execute()
                    print(f"  ✅ Updated device {device_address} -> {phone_number}")
                else:
                    # Insert new device
                    self.supabase.table('devices').insert({
                        'device_id': device_address,
                        'phone_number': phone_number,
                        'status': 'idle'
                    }).execute()
                    print(f"  ✅ Added device {device_address} -> {phone_number}")
            
            print("✅ Phone mapping migration completed")
            return True
            
        except Exception as e:
            print(f"❌ Phone mapping migration failed: {e}")
            return False
    
    def migrate_device_status(self):
        """Migrate status.json to devices table"""
        try:
            if not os.path.exists('status.json'):
                print("⚠️  status.json not found, skipping...")
                return True
            
            with open('status.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            device_statuses = data.get('device_statuses', {})
            
            print(f"📊 Migrating {len(device_statuses)} device statuses...")
            
            for device_id, status_info in device_statuses.items():
                # Update device status
                update_data = {
                    'status': status_info.get('status', 'idle'),
                    'message': status_info.get('message', ''),
                    'progress': status_info.get('progress', 0),
                    'current_message_id': status_info.get('current_message_id'),
                    'last_update': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                result = self.supabase.table('devices').update(update_data).eq('device_id', device_id).execute()
                
                if result.data:
                    print(f"  ✅ Updated status for device {device_id}")
                else:
                    print(f"  ⚠️  Device {device_id} not found, skipping status update")
            
            print("✅ Device status migration completed")
            return True
            
        except Exception as e:
            print(f"❌ Device status migration failed: {e}")
            return False
    
    def migrate_conversations(self):
        """Migrate conversations.json to conversation_templates and conversation_messages tables"""
        try:
            if not os.path.exists('conversations.json'):
                print("⚠️  conversations.json not found, skipping...")
                return True
            
            with open('conversations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conversations = data.get('conversations', [])
            
            print(f"💬 Migrating {len(conversations)} conversations...")
            
            for conv in conversations:
                group_id = conv.get('group_id')
                messages = conv.get('messages', [])
                
                # Check if template already exists
                existing_template = self.supabase.table('conversation_templates').select('id').eq('group_id', group_id).execute()
                
                if existing_template.data:
                    template_id = existing_template.data[0]['id']
                    print(f"  ✅ Using existing template for group {group_id}")
                else:
                    # Create new conversation template
                    template_result = self.supabase.table('conversation_templates').insert({
                        'group_id': group_id,
                        'name': f"Conversation Group {group_id}",
                        'description': f"Migrated conversation with {len(messages)} messages",
                        'is_active': True
                    }).execute()
                    
                    template_id = template_result.data[0]['id']
                    print(f"  ✅ Created template for group {group_id}")
                
                # Delete existing messages for this template
                self.supabase.table('conversation_messages').delete().eq('template_id', template_id).execute()
                
                # Insert messages
                for idx, message in enumerate(messages):
                    self.supabase.table('conversation_messages').insert({
                        'template_id': template_id,
                        'sequence_order': idx + 1,
                        'content': message.get('content', ''),
                        'delay_seconds': message.get('delay', 2),
                        'device_role': message.get('device_role', 'device_a')
                    }).execute()
                
                print(f"  ✅ Migrated {len(messages)} messages for group {group_id}")
            
            print("✅ Conversations migration completed")
            return True
            
        except Exception as e:
            print(f"❌ Conversations migration failed: {e}")
            return False
    
    def migrate_app_config(self):
        """Migrate config/app_config.json to app_configurations table"""
        try:
            config_path = 'config/app_config.json'
            if not os.path.exists(config_path):
                print("⚠️  config/app_config.json not found, skipping...")
                return True
            
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"⚙️  Migrating app configuration...")
            
            # Migrate each config section
            for key, value in data.items():
                # Check if config already exists
                existing = self.supabase.table('app_configurations').select('id').eq('config_key', key).execute()
                
                if existing.data:
                    # Update existing config
                    self.supabase.table('app_configurations').update({
                        'config_value': value,
                        'updated_at': datetime.now().isoformat()
                    }).eq('config_key', key).execute()
                    print(f"  ✅ Updated config: {key}")
                else:
                    # Insert new config
                    self.supabase.table('app_configurations').insert({
                        'config_key': key,
                        'config_value': value,
                        'description': f"Migrated from app_config.json - {key}",
                        'is_active': True
                    }).execute()
                    print(f"  ✅ Added config: {key}")
            
            print("✅ App configuration migration completed")
            return True
            
        except Exception as e:
            print(f"❌ App configuration migration failed: {e}")
            return False
    
    def run_migration(self):
        """Run complete migration process"""
        print("🚀 Starting Supabase migration...")
        print("=" * 50)
        
        # Test connection first
        print("Testing Supabase connection...")
        if not self.test_connection():
            return False
        
        success = True
        
        # Run migrations
        success &= self.migrate_phone_mapping()
        success &= self.migrate_device_status()
        success &= self.migrate_conversations()
        success &= self.migrate_app_config()
        
        if success:
            print("\n🎉 Migration completed successfully!")
            print("📊 All JSON data has been migrated to Supabase")
            print("💡 You can now use the Supabase repositories in your application")
        else:
            print("\n❌ Migration completed with errors")
            print("🔍 Please check the error messages above")
        
        return success

if __name__ == "__main__":
    try:
        migrator = SupabaseMigrator()
        migrator.run_migration()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)