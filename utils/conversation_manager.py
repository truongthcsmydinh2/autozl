"""Conversation Management System

This module provides classes for managing device pairs, conversations, and summaries
with automatic cleanup and validation functionality.
"""

import json
import hashlib
import time
import random
import string
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

from database.supabase_manager import SupabaseManager, get_supabase_manager
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class SummaryData:
    """Data class for conversation summary"""
    noidung: str
    hoancanh: str
    so_cau: int
    created_at: Optional[datetime] = None
    id: Optional[str] = None


@dataclass
class ConversationContent:
    """Data class for conversation content"""
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class ConversationInput:
    """Data class for complete conversation input"""
    content: ConversationContent
    summary: SummaryData


@dataclass
class DevicePair:
    """Data class for device pair"""
    device_a: str
    device_b: str
    pair_hash: str
    temp_pair_id: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None


class ConversationValidator:
    """Validates conversation input JSON format"""
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any]) -> bool:
        """Validate JSON structure according to demo.json format"""
        try:
            # Check top-level structure
            if not isinstance(data, dict):
                raise ValueError("Input must be a JSON object")
            
            if 'content' not in data or 'summary' not in data:
                raise ValueError("Missing required fields: 'content' and 'summary'")
            
            # Validate content structure
            content = data['content']
            if not isinstance(content, dict):
                raise ValueError("'content' must be an object")
            
            if 'messages' not in content:
                raise ValueError("'content' must contain 'messages' field")
            
            messages = content['messages']
            if not isinstance(messages, list):
                raise ValueError("'messages' must be an array")
            
            # Validate message structure
            for i, message in enumerate(messages):
                if not isinstance(message, dict):
                    raise ValueError(f"Message {i} must be an object")
                
                required_fields = ['sender', 'text']
                for field in required_fields:
                    if field not in message:
                        raise ValueError(f"Message {i} missing required field: '{field}'")
            
            # Validate summary structure
            summary = data['summary']
            if not isinstance(summary, dict):
                raise ValueError("'summary' must be an object")
            
            required_summary_fields = ['noidung', 'hoancanh', 'so_cau']
            for field in required_summary_fields:
                if field not in summary:
                    raise ValueError(f"Summary missing required field: '{field}'")
            
            # Validate summary field types
            if not isinstance(summary['noidung'], str):
                raise ValueError("'noidung' must be a string")
            
            if not isinstance(summary['hoancanh'], str):
                raise ValueError("'hoancanh' must be a string")
            
            if not isinstance(summary['so_cau'], int):
                raise ValueError("'so_cau' must be an integer")
            
            return True
            
        except Exception as e:
            logger.error(f"JSON validation failed: {str(e)}")
            raise ValueError(f"Invalid JSON structure: {str(e)}")
    
    @staticmethod
    def parse_conversation_input(data: Dict[str, Any]) -> ConversationInput:
        """Parse and validate conversation input"""
        ConversationValidator.validate_json_structure(data)
        
        content = ConversationContent(
            messages=data['content']['messages'],
            metadata=data['content'].get('metadata', {})
        )
        
        summary = SummaryData(
            noidung=data['summary']['noidung'],
            hoancanh=data['summary']['hoancanh'],
            so_cau=data['summary']['so_cau']
        )
        
        return ConversationInput(content=content, summary=summary)


class DevicePairManager:
    """Manages device pairs and temporary ID mapping"""
    
    def __init__(self, supabase_manager: SupabaseManager = None):
        # Initialize supabase client directly
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = create_client(url, key)
        self._temp_mapping: Dict[str, str] = {}  # temp_pair_id -> pair_id
        self._conversation_mapping: Dict[str, str] = {}  # temp_conversation_id -> conversation_id
        
    def _get_client(self):
        """Get Supabase client"""
        return self.supabase
    
    def generate_temp_pair_id(self) -> str:
        """Generate temporary pair ID"""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"pair_temp_{timestamp}_{random_str}"
    
    def generate_temp_conversation_id(self) -> str:
        """Generate temporary conversation ID"""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"conv_temp_{timestamp}_{random_str}"
    
    def create_pair_id(self, device_a: str, device_b: str) -> str:
        """Create standardized pair ID (AB = BA) using generate_pair_id utility"""
        from utils.pair_utils import generate_pair_id
        return generate_pair_id(device_a, device_b)
    
    def create_pair_hash(self, device_a: str, device_b: str) -> str:
        """Create hash for device pair (AB = BA) - deprecated, use create_pair_id"""
        devices = sorted([device_a, device_b])
        return hashlib.md5('_'.join(devices).encode()).hexdigest()
    
    def _find_or_create_pair_sync(self, device_a: str, device_b: str) -> DevicePair:
        """Sync version of find_or_create_pair"""
        supabase = self._get_client()
        try:
            pair_id = self.create_pair_id(device_a, device_b)
            pair_hash = self.create_pair_hash(device_a, device_b)  # Keep for backward compatibility
            
            # Try to find existing pair by pair_id first, then by pair_hash
            try:
                # First try to find by standardized pair_id
                result = supabase.table('device_pairs').select('*').eq('id', pair_id).execute()
                
                if result.data:
                    pair_data = result.data[0]
                    return DevicePair(
                        id=pair_data['id'],
                        device_a=pair_data['device_a'],
                        device_b=pair_data['device_b'],
                        pair_hash=pair_data['pair_hash'],
                        temp_pair_id=pair_data['temp_pair_id'],
                        created_at=pair_data['created_at']
                    )
                
                # Fallback: try to find by pair_hash for backward compatibility
                result = supabase.table('device_pairs').select('*').eq('pair_hash', pair_hash).execute()
                
                if result.data:
                    pair_data = result.data[0]
                    return DevicePair(
                        id=pair_data['id'],
                        device_a=pair_data['device_a'],
                        device_b=pair_data['device_b'],
                        pair_hash=pair_data['pair_hash'],
                        temp_pair_id=pair_data['temp_pair_id'],
                        created_at=pair_data['created_at']
                    )
            except Exception as find_error:
                logger.warning(f"Error finding existing pair: {find_error}")
            
            # Create new pair with standardized ID
            temp_pair_id = self.generate_temp_pair_id()
            new_pair = {
                'id': pair_id,  # Use standardized pair_id as primary key
                'device_a': device_a,
                'device_b': device_b,
                'pair_hash': pair_hash,
                'temp_pair_id': temp_pair_id
            }
            
            try:
                result = supabase.table('device_pairs').upsert(new_pair).execute()
                
                if result.data:
                    pair_data = result.data[0]
                    return DevicePair(
                        id=pair_data['id'],
                        device_a=pair_data['device_a'],
                        device_b=pair_data['device_b'],
                        pair_hash=pair_data['pair_hash'],
                        temp_pair_id=pair_data['temp_pair_id'],
                        created_at=pair_data['created_at']
                    )
                
                raise Exception("Failed to create device pair - no data returned")
                
            except Exception as create_error:
                logger.error(f"Error creating new pair: {create_error}")
                raise Exception(f"Failed to create device pair: {create_error}")
            
        except Exception as e:
            logger.error(f"Error finding/creating device pair: {str(e)}")
            raise
    
    def find_or_create_pair(self, device_a: str, device_b: str) -> DevicePair:
        """Find existing pair or create new one"""
        return self._find_or_create_pair_sync(device_a, device_b)
    
    def _get_pair_by_temp_id_sync(self, temp_pair_id: str) -> Optional[DevicePair]:
        """Sync version of get_pair_by_temp_id"""
        supabase = self._get_client()
        try:
            result = supabase.table('device_pairs').select('*').eq('temp_pair_id', temp_pair_id).execute()
            
            if result.data:
                pair_data = result.data[0]
                return DevicePair(
                    id=pair_data['id'],
                    device_a=pair_data['device_a'],
                    device_b=pair_data['device_b'],
                    pair_hash=pair_data['pair_hash'],
                    temp_pair_id=pair_data['temp_pair_id'],
                    created_at=pair_data['created_at']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pair by temp ID: {str(e)}")
            return None
    
    def get_pair_by_temp_id(self, temp_pair_id: str) -> Optional[DevicePair]:
        """Get device pair by temporary ID"""
        return self._get_pair_by_temp_id_sync(temp_pair_id)
    
    def _get_pair_by_id_sync(self, pair_id: str) -> Optional[DevicePair]:
        """Sync version of get_pair_by_id"""
        supabase = self._get_client()
        try:
            result = supabase.table('device_pairs').select('*').eq('id', pair_id).execute()
            
            if result.data:
                pair_data = result.data[0]
                return DevicePair(
                    id=pair_data['id'],
                    device_a=pair_data['device_a'],
                    device_b=pair_data['device_b'],
                    pair_hash=pair_data['pair_hash'],
                    temp_pair_id=pair_data['temp_pair_id'],
                    created_at=pair_data['created_at']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting pair by ID: {str(e)}")
            return None
    
    def get_pair_by_id(self, pair_id: str) -> Optional[DevicePair]:
        """Get device pair by ID"""
        return self._get_pair_by_id_sync(pair_id)
    
    def _create_conversation_slot_sync(self, pair_id: str) -> str:
        """Sync version of create_conversation_slot"""
        supabase = self._get_client()
        try:
            temp_conversation_id = self.generate_temp_conversation_id()
            
            result = supabase.table('conversations').insert({
                'pair_id': pair_id,
                'temp_conversation_id': temp_conversation_id,
                'content': None,
                'is_active': True
            }).execute()
            
            if result.data:
                conversation_id = result.data[0]['id']
                self._conversation_mapping[temp_conversation_id] = conversation_id
                return temp_conversation_id
            
            raise Exception("Failed to create conversation slot")
            
        except Exception as e:
            logger.error(f"Error creating conversation slot: {str(e)}")
            raise
    
    def create_conversation_slot(self, pair_id: str) -> str:
        """Create conversation slot for pair and return temp conversation ID"""
        return self._create_conversation_slot_sync(pair_id)


class SummaryManager:
    """Manages conversation summaries with automatic cleanup"""
    
    MAX_SUMMARIES_PER_PAIR = 3
    
    def __init__(self, supabase_manager: SupabaseManager = None):
        # Initialize supabase client directly
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = create_client(url, key)
        
    def _get_client(self):
        """Get Supabase client"""
        return self.supabase
    
    def _save_summary_sync(self, pair_id: str, summary: SummaryData) -> str:
        """Sync version of save_summary"""
        supabase = self._get_client()
        try:
            # Insert new summary
            result = supabase.table('conversation_summaries').insert({
                'pair_id': pair_id,
                'noidung': summary.noidung,
                'hoancanh': summary.hoancanh,
                'so_cau': summary.so_cau
            }).execute()
            
            if not result.data:
                raise Exception("Failed to save summary")
            
            summary_id = result.data[0]['id']
            
            # Cleanup old summaries using database function
            supabase.rpc('cleanup_old_summaries', {'target_pair_id': pair_id}).execute()
            
            logger.info(f"Summary saved and cleanup completed for pair {pair_id}")
            return summary_id
            
        except Exception as e:
            logger.error(f"Error saving summary: {str(e)}")
            raise
    
    def save_summary(self, pair_id: str, summary: SummaryData) -> str:
        """Save summary and cleanup old ones"""
        return self._save_summary_sync(pair_id, summary)
    
    def _get_latest_summary_sync(self, pair_id: str) -> Optional[SummaryData]:
        """Sync version of get_latest_summary"""
        supabase = self._get_client()
        try:
            result = supabase.table('conversation_summaries')\
                .select('*')\
                .eq('pair_id', pair_id)\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                summary_data = result.data[0]
                return SummaryData(
                    id=summary_data['id'],
                    noidung=summary_data['noidung'],
                    hoancanh=summary_data['hoancanh'],
                    so_cau=summary_data['so_cau'],
                    created_at=summary_data['created_at']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest summary: {str(e)}")
            return None
    
    def get_latest_summary(self, pair_id: str) -> Optional[SummaryData]:
        """Get latest summary for pair"""
        return self._get_latest_summary_sync(pair_id)
    
    def _get_summaries_sync(self, pair_id: str, limit: int = 3) -> List[SummaryData]:
        """Sync version of get_summaries"""
        supabase = self._get_client()
        try:
            result = supabase.table('conversation_summaries')\
                .select('*')\
                .eq('pair_id', pair_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            summaries = []
            if result.data:
                for item in result.data:
                    summaries.append(SummaryData(
                        id=item['id'],
                        noidung=item['noidung'],
                        hoancanh=item['hoancanh'],
                        so_cau=item['so_cau'],
                        created_at=item['created_at']
                    ))
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting summaries: {str(e)}")
            return []
    
    def get_summaries(self, pair_id: str, limit: int = 3) -> List[SummaryData]:
        """Get summaries for pair (latest first)"""
        return self._get_summaries_sync(pair_id, limit)
    
    def _delete_summary_sync(self, summary_id: str) -> bool:
        """Sync version of delete_summary"""
        supabase = self._get_client()
        try:
            result = supabase.table('conversation_summaries').delete().eq('id', summary_id).execute()
            return result.data is not None
            
        except Exception as e:
            logger.error(f"Error deleting summary: {str(e)}")
            return False
    
    def delete_summary(self, summary_id: str) -> bool:
        """Delete specific summary"""
        return self._delete_summary_sync(summary_id)


class ConversationManager:
    """Main conversation management class"""
    
    def __init__(self, supabase_manager: SupabaseManager = None):
        # Initialize supabase client directly
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = create_client(url, key)
        self.pair_manager = DevicePairManager()
        self.summary_manager = SummaryManager()
        self.validator = ConversationValidator()
        self._temporary_content: Dict[str, ConversationContent] = {}  # temp_conversation_id -> content
        
    def _get_client(self):
        """Get Supabase client"""
        return self.supabase
    
    def _process_conversation_input_sync(self, device_a: str, device_b: str, 
                                       conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync version of process_conversation_input"""
        try:
            # Validate and parse input
            conversation_input = self.validator.parse_conversation_input(conversation_data)
            
            # Find or create device pair
            pair = self.pair_manager._find_or_create_pair_sync(device_a, device_b)
            
            # Create conversation slot
            temp_conversation_id = self.pair_manager._create_conversation_slot_sync(pair.id)
            
            # Store content temporarily
            self._temporary_content[temp_conversation_id] = conversation_input.content
            
            # Save summary persistently
            summary_id = self.summary_manager._save_summary_sync(pair.id, conversation_input.summary)
            
            logger.info(f"Conversation processed successfully for pair {pair.temp_pair_id}")
            
            return {
                'success': True,
                'pair_id': pair.id,
                'temp_pair_id': pair.temp_pair_id,
                'temp_conversation_id': temp_conversation_id,
                'summary_id': summary_id,
                'message': 'Conversation data processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing conversation input: {str(e)}")
            raise
    
    def process_conversation_input(self, device_a: str, device_b: str, 
                                       conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete conversation input"""
        return self._process_conversation_input_sync(device_a, device_b, conversation_data)
    
    def get_pair_summaries(self, pair_identifier: str) -> List[SummaryData]:
        """Get summaries for a device pair by standardized pair_id or temp_pair_id"""
        try:
            # Try to get pair by standardized pair_id first
            pair = self.pair_manager.get_pair_by_id(pair_identifier)
            if not pair:
                # Fallback to temp_pair_id for backward compatibility
                pair = self.pair_manager.get_pair_by_temp_id(pair_identifier)
            
            if not pair:
                return []
            
            return self.summary_manager.get_summaries(pair.id)
            
        except Exception as e:
            logger.error(f"Error getting pair summaries: {str(e)}")
            return []
    
    def _get_latest_summary_by_temp_pair_id_sync(self, temp_pair_id: str) -> Optional[SummaryData]:
        """Sync version of get_latest_summary_by_temp_pair_id"""
        supabase = self._get_client()
        try:
            # Find pair by temp_pair_id
            pair_result = supabase.table('device_pairs')\
                .select('id')\
                .eq('temp_pair_id', temp_pair_id)\
                .execute()
            
            if not pair_result.data or len(pair_result.data) == 0:
                return None
            
            pair_id = pair_result.data[0]['id']
            return self.summary_manager._get_latest_summary_sync(pair_id)
            
        except Exception as e:
            logger.error(f"Error getting latest summary by temp pair ID: {str(e)}")
            return None
    
    def get_latest_summary_by_pair_id(self, pair_identifier: str) -> Optional[SummaryData]:
        """Get latest summary by standardized pair_id or temp_pair_id"""
        try:
            # Try to get pair by standardized pair_id first
            pair = self.pair_manager.get_pair_by_id(pair_identifier)
            if not pair:
                # Fallback to temp_pair_id for backward compatibility
                pair = self.pair_manager.get_pair_by_temp_id(pair_identifier)
            
            if not pair:
                return None
            
            return self.summary_manager.get_latest_summary(pair.id)
            
        except Exception as e:
            logger.error(f"Error getting latest summary by pair ID: {str(e)}")
            return None
    
    def get_temporary_content(self, temp_conversation_id: str) -> Optional[ConversationContent]:
        """Get temporarily stored conversation content"""
        return self._temporary_content.get(temp_conversation_id)
    
    def clear_temporary_content(self, temp_conversation_id: str) -> bool:
        """Clear temporarily stored conversation content"""
        if temp_conversation_id in self._temporary_content:
            del self._temporary_content[temp_conversation_id]
            return True
        return False
    
    def _list_device_pairs_sync(self) -> List[DevicePair]:
        """Sync version of list_device_pairs"""
        supabase = self._get_client()
        try:
            result = supabase.table('device_pairs').select('*').order('created_at', desc=True).execute()
            
            pairs = []
            if result.data:
                for pair_data in result.data:
                    pairs.append(DevicePair(
                        id=pair_data['id'],
                        device_a=pair_data['device_a'],
                        device_b=pair_data['device_b'],
                        pair_hash=pair_data['pair_hash'],
                        temp_pair_id=pair_data['temp_pair_id'],
                        created_at=pair_data['created_at']
                    ))
            
            return pairs
            
        except Exception as e:
            logger.error(f"Error listing device pairs: {str(e)}")
            return []
    
    def list_device_pairs(self) -> List[DevicePair]:
        """List all device pairs"""
        return self._list_device_pairs_sync()