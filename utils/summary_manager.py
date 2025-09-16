import json
import os
from typing import Dict, Optional, Tuple
from datetime import datetime

class SummaryManager:
    """Quản lý lưu trữ và truy xuất summary theo cặp thiết bị"""
    
    def __init__(self, storage_file: str = "pair_summaries.json"):
        self.storage_file = storage_file
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Đảm bảo file lưu trữ tồn tại"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _get_pair_key(self, device1_ip: str, device2_ip: str) -> str:
        """Tạo key cho cặp thiết bị (sorted để đảm bảo consistency)"""
        devices = sorted([device1_ip, device2_ip])
        return f"{devices[0]}-{devices[1]}"
    
    def save_summary(self, device1_ip: str, device2_ip: str, summary: Dict) -> bool:
        """Lưu summary cho cặp thiết bị"""
        try:
            pair_key = self._get_pair_key(device1_ip, device2_ip)
            
            # Load existing data
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add timestamp to summary
            summary_with_timestamp = {
                **summary,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save new summary
            data[pair_key] = summary_with_timestamp
            
            # Write back to file
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi lưu summary: {str(e)}")
            return False
    
    def get_summary(self, device1_ip: str, device2_ip: str) -> Optional[Dict]:
        """Lấy summary cho cặp thiết bị"""
        try:
            pair_key = self._get_pair_key(device1_ip, device2_ip)
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get(pair_key)
            
        except Exception as e:
            print(f"Lỗi khi đọc summary: {str(e)}")
            return None
    
    def has_summary(self, device1_ip: str, device2_ip: str) -> bool:
        """Kiểm tra xem cặp thiết bị có summary hay không"""
        return self.get_summary(device1_ip, device2_ip) is not None
    
    def delete_summary(self, device1_ip: str, device2_ip: str) -> bool:
        """Xóa summary của cặp thiết bị"""
        try:
            pair_key = self._get_pair_key(device1_ip, device2_ip)
            
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if pair_key in data:
                del data[pair_key]
                
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Lỗi khi xóa summary: {str(e)}")
            return False
    
    def get_all_summaries(self) -> Dict[str, Dict]:
        """Lấy tất cả summaries"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi khi đọc tất cả summaries: {str(e)}")
            return {}
    
    def get_summary_count(self) -> int:
        """Đếm số lượng summaries đã lưu"""
        return len(self.get_all_summaries())

# Singleton instance
summary_manager = SummaryManager()