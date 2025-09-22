from typing import List, Optional, Dict, Any
from datetime import datetime
from .supabase_manager import get_supabase_manager

class DeviceRepository:
    """Repository để quản lý devices trong Supabase"""
    
    def __init__(self):
        self.db = get_supabase_manager()
        self.table = 'devices'
    
    def create_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo device mới"""
        # Thêm timestamp
        device_data['created_at'] = datetime.utcnow().isoformat()
        device_data['updated_at'] = datetime.utcnow().isoformat()
        
        return self.db.insert_record(self.table, device_data)
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Lấy device theo ID"""
        return self.db.get_record_by_id(self.table, device_id)
    
    def get_device_by_mac(self, mac_address: str) -> Optional[Dict[str, Any]]:
        """Lấy device theo MAC address"""
        try:
            result = self.db.supabase.table(self.table).select('*').eq('mac_address', mac_address).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Lỗi get device by MAC {mac_address}: {e}")
            raise
    
    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Lấy tất cả devices"""
        return self.db.get_all_records(self.table)
    
    def get_devices_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Lấy devices theo status"""
        return self.db.query_records(self.table, {'status': status})
    
    def get_devices_by_type(self, device_type: str) -> List[Dict[str, Any]]:
        """Lấy devices theo type"""
        return self.db.query_records(self.table, {'device_type': device_type})
    
    def update_device(self, device_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update device"""
        # Thêm timestamp
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        return self.db.update_record(self.table, device_id, update_data)
    
    def update_device_status(self, device_id: str, status: str) -> Dict[str, Any]:
        """Update status của device"""
        return self.update_device(device_id, {'status': status})
    
    def update_device_last_seen(self, device_id: str) -> Dict[str, Any]:
        """Update last_seen của device"""
        return self.update_device(device_id, {'last_seen': datetime.utcnow().isoformat()})
    
    def delete_device(self, device_id: str) -> bool:
        """Xóa device"""
        return self.db.delete_record(self.table, device_id)
    
    def search_devices(self, search_term: str) -> List[Dict[str, Any]]:
        """Tìm kiếm devices theo tên hoặc MAC address"""
        try:
            # Search by name
            name_results = self.db.supabase.table(self.table).select('*').ilike('name', f'%{search_term}%').execute()
            
            # Search by MAC address
            mac_results = self.db.supabase.table(self.table).select('*').ilike('mac_address', f'%{search_term}%').execute()
            
            # Combine results and remove duplicates
            all_results = name_results.data + mac_results.data
            unique_results = {device['id']: device for device in all_results}
            
            return list(unique_results.values())
        except Exception as e:
            print(f"Lỗi search devices với term '{search_term}': {e}")
            raise
    
    def get_device_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê devices"""
        try:
            all_devices = self.get_all_devices()
            
            stats = {
                'total_devices': len(all_devices),
                'online_devices': len([d for d in all_devices if d['status'] == 'online']),
                'offline_devices': len([d for d in all_devices if d['status'] == 'offline']),
                'by_type': {}
            }
            
            # Count by device type
            for device in all_devices:
                device_type = device.get('device_type', 'unknown')
                stats['by_type'][device_type] = stats['by_type'].get(device_type, 0) + 1
            
            return stats
        except Exception as e:
            print(f"Lỗi get device statistics: {e}")
            raise