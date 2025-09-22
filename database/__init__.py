"""Database access layer cho Tool Auto system

Module này cung cấp các repository classes để tương tác với Supabase database:
- SupabaseManager: Quản lý kết nối và các thao tác cơ bản
- DeviceRepository: Quản lý devices
- AutomationRepository: Quản lý automation rules
- LogRepository: Quản lý system logs
"""

from .supabase_manager import SupabaseManager, get_supabase_manager
from .device_repository import DeviceRepository
from .automation_repository import AutomationRepository
from .log_repository import LogRepository

__all__ = [
    'SupabaseManager',
    'get_supabase_manager',
    'DeviceRepository',
    'AutomationRepository',
    'LogRepository'
]

# Convenience functions để tạo repository instances
def get_device_repository() -> DeviceRepository:
    """Lấy instance của DeviceRepository"""
    return DeviceRepository()

def get_automation_repository() -> AutomationRepository:
    """Lấy instance của AutomationRepository"""
    return AutomationRepository()

def get_log_repository() -> LogRepository:
    """Lấy instance của LogRepository"""
    return LogRepository()