from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .supabase_manager import get_supabase_manager

class LogRepository:
    """Repository để quản lý system logs trong Supabase"""
    
    def __init__(self):
        self.db = get_supabase_manager()
        self.table = 'automation_logs'
    
    def create_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo log entry mới"""
        # Supabase tự động tạo created_at, không cần thêm timestamp
        return self.db.insert_record(self.table, log_data)
    
    def log_info(self, message: str, component: str = 'system', metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Tạo info log"""
        log_data = {
            'log_level': 'INFO',
            'message': message,
            'metadata': metadata or {'component': component}
        }
        return self.create_log(log_data)
    
    def log_warning(self, message: str, component: str = 'system', metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Tạo warning log"""
        log_data = {
            'log_level': 'WARNING',
            'message': message,
            'metadata': metadata or {'component': component}
        }
        return self.create_log(log_data)
    
    def log_error(self, message: str, component: str = 'system', metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Tạo error log"""
        log_data = {
            'log_level': 'ERROR',
            'message': message,
            'metadata': metadata or {'component': component}
        }
        return self.create_log(log_data)
    
    def log_debug(self, message: str, component: str = 'system', metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Tạo debug log"""
        log_data = {
            'log_level': 'DEBUG',
            'message': message,
            'metadata': metadata or {'component': component}
        }
        return self.create_log(log_data)
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Lấy log theo ID"""
        return self.db.get_record_by_id(self.table, log_id)
    
    def get_logs_by_level(self, level: str, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Lấy logs theo level"""
        try:
            query = self.db.supabase.table(self.table).select('*').eq('level', level).order('timestamp', desc=True)
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get logs by level {level}: {e}")
            raise
    
    def get_logs_by_component(self, component: str, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Lấy logs theo component"""
        try:
            query = self.db.supabase.table(self.table).select('*').eq('component', component).order('timestamp', desc=True)
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get logs by component {component}: {e}")
            raise
    
    def get_logs_by_time_range(self, start_time: datetime, end_time: datetime, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Lấy logs trong khoảng thời gian"""
        try:
            query = (self.db.supabase.table(self.table)
                    .select('*')
                    .gte('timestamp', start_time.isoformat())
                    .lte('timestamp', end_time.isoformat())
                    .order('timestamp', desc=True))
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get logs by time range: {e}")
            raise
    
    def get_recent_logs(self, hours: int = 24, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Lấy logs gần đây"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        end_time = datetime.utcnow()
        return self.get_logs_by_time_range(start_time, end_time, limit)
    
    def search_logs(self, search_term: str, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Tìm kiếm logs theo message"""
        try:
            query = (self.db.supabase.table(self.table)
                    .select('*')
                    .ilike('message', f'%{search_term}%')
                    .order('timestamp', desc=True))
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi search logs với term '{search_term}': {e}")
            raise
    
    def get_error_logs(self, hours: int = 24, limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Lấy error logs gần đây"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        try:
            query = (self.db.supabase.table(self.table)
                    .select('*')
                    .eq('level', 'error')
                    .gte('timestamp', start_time.isoformat())
                    .order('timestamp', desc=True))
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get error logs: {e}")
            raise
    
    def get_logs_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Lấy thống kê logs"""
        try:
            recent_logs = self.get_recent_logs(hours)
            
            stats = {
                'total_logs': len(recent_logs),
                'by_level': {},
                'by_component': {},
                'error_count': 0,
                'warning_count': 0
            }
            
            for log in recent_logs:
                level = log.get('level', 'unknown')
                component = log.get('component', 'unknown')
                
                # Count by level
                stats['by_level'][level] = stats['by_level'].get(level, 0) + 1
                
                # Count by component
                stats['by_component'][component] = stats['by_component'].get(component, 0) + 1
                
                # Count errors and warnings
                if level == 'error':
                    stats['error_count'] += 1
                elif level == 'warning':
                    stats['warning_count'] += 1
            
            return stats
        except Exception as e:
            print(f"Lỗi get logs statistics: {e}")
            raise
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """Xóa logs cũ hơn số ngày chỉ định"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = (self.db.supabase.table(self.table)
                     .delete()
                     .lt('timestamp', cutoff_date.isoformat())
                     .execute())
            return len(result.data)
        except Exception as e:
            print(f"Lỗi cleanup old logs: {e}")
            raise
    
    def get_logs_with_filters(self, 
                             level: Optional[str] = None,
                             component: Optional[str] = None,
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None,
                             limit: Optional[int] = 100) -> List[Dict[str, Any]]:
        """Lấy logs với nhiều filters"""
        try:
            query = self.db.supabase.table(self.table).select('*')
            
            if level:
                query = query.eq('level', level)
            if component:
                query = query.eq('component', component)
            if start_time:
                query = query.gte('timestamp', start_time.isoformat())
            if end_time:
                query = query.lte('timestamp', end_time.isoformat())
            
            query = query.order('timestamp', desc=True)
            if limit:
                query = query.limit(limit)
                
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"Lỗi get logs with filters: {e}")
            raise