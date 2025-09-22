from typing import List, Optional, Dict, Any
from datetime import datetime
from .supabase_manager import get_supabase_manager

class AutomationRepository:
    """Repository để quản lý automation rules trong Supabase"""
    
    def __init__(self):
        self.db = get_supabase_manager()
        self.table = 'automation_rules'
    
    def create_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo automation rule mới"""
        # Thêm timestamp
        rule_data['created_at'] = datetime.utcnow().isoformat()
        rule_data['updated_at'] = datetime.utcnow().isoformat()
        
        return self.db.insert_record(self.table, rule_data)
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Lấy rule theo ID"""
        return self.db.get_record_by_id(self.table, rule_id)
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Lấy tất cả automation rules"""
        return self.db.get_all_records(self.table)
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """Lấy các rules đang active"""
        return self.db.query_records(self.table, {'is_active': True})
    
    def get_rules_by_trigger_type(self, trigger_type: str) -> List[Dict[str, Any]]:
        """Lấy rules theo trigger type"""
        try:
            result = self.db.supabase.table(self.table).select('*').contains('trigger_conditions', {'type': trigger_type}).execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get rules by trigger type {trigger_type}: {e}")
            raise
    
    def get_rules_by_device(self, device_id: str) -> List[Dict[str, Any]]:
        """Lấy rules liên quan đến device"""
        try:
            # Tìm rules có device_id trong trigger_conditions hoặc actions
            trigger_rules = self.db.supabase.table(self.table).select('*').contains('trigger_conditions', {'device_id': device_id}).execute()
            action_rules = self.db.supabase.table(self.table).select('*').contains('actions', {'device_id': device_id}).execute()
            
            # Combine và remove duplicates
            all_rules = trigger_rules.data + action_rules.data
            unique_rules = {rule['id']: rule for rule in all_rules}
            
            return list(unique_rules.values())
        except Exception as e:
            print(f"Lỗi get rules by device {device_id}: {e}")
            raise
    
    def update_rule(self, rule_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update automation rule"""
        # Thêm timestamp
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        return self.db.update_record(self.table, rule_id, update_data)
    
    def toggle_rule_status(self, rule_id: str) -> Dict[str, Any]:
        """Toggle trạng thái active/inactive của rule"""
        rule = self.get_rule_by_id(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} không tồn tại")
        
        new_status = not rule.get('is_active', False)
        return self.update_rule(rule_id, {'is_active': new_status})
    
    def update_rule_last_executed(self, rule_id: str) -> Dict[str, Any]:
        """Update thời gian last_executed của rule"""
        return self.update_rule(rule_id, {'last_executed': datetime.utcnow().isoformat()})
    
    def delete_rule(self, rule_id: str) -> bool:
        """Xóa automation rule"""
        return self.db.delete_record(self.table, rule_id)
    
    def search_rules(self, search_term: str) -> List[Dict[str, Any]]:
        """Tìm kiếm rules theo tên hoặc description"""
        try:
            # Search by name
            name_results = self.db.supabase.table(self.table).select('*').ilike('name', f'%{search_term}%').execute()
            
            # Search by description
            desc_results = self.db.supabase.table(self.table).select('*').ilike('description', f'%{search_term}%').execute()
            
            # Combine results and remove duplicates
            all_results = name_results.data + desc_results.data
            unique_results = {rule['id']: rule for rule in all_results}
            
            return list(unique_results.values())
        except Exception as e:
            print(f"Lỗi search rules với term '{search_term}': {e}")
            raise
    
    def get_rules_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê automation rules"""
        try:
            all_rules = self.get_all_rules()
            
            stats = {
                'total_rules': len(all_rules),
                'active_rules': len([r for r in all_rules if r.get('is_active', False)]),
                'inactive_rules': len([r for r in all_rules if not r.get('is_active', False)]),
                'by_trigger_type': {},
                'recently_executed': 0
            }
            
            # Count by trigger type
            for rule in all_rules:
                trigger_conditions = rule.get('trigger_conditions', {})
                trigger_type = trigger_conditions.get('type', 'unknown')
                stats['by_trigger_type'][trigger_type] = stats['by_trigger_type'].get(trigger_type, 0) + 1
                
                # Count recently executed (last 24 hours)
                if rule.get('last_executed'):
                    last_executed = datetime.fromisoformat(rule['last_executed'].replace('Z', '+00:00'))
                    if (datetime.utcnow() - last_executed.replace(tzinfo=None)).days < 1:
                        stats['recently_executed'] += 1
            
            return stats
        except Exception as e:
            print(f"Lỗi get rules statistics: {e}")
            raise
    
    def get_rules_for_execution(self) -> List[Dict[str, Any]]:
        """Lấy các rules sẵn sàng để execute (active và có trigger conditions phù hợp)"""
        try:
            # Lấy tất cả active rules
            active_rules = self.get_active_rules()
            
            # Filter rules có thể execute (có trigger conditions hợp lệ)
            executable_rules = []
            for rule in active_rules:
                trigger_conditions = rule.get('trigger_conditions', {})
                if trigger_conditions and trigger_conditions.get('type'):
                    executable_rules.append(rule)
            
            return executable_rules
        except Exception as e:
            print(f"Lỗi get rules for execution: {e}")
            raise