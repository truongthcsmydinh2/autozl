#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Device Manager Module
Tích hợp logic device management từ core1.py
"""

import subprocess
import threading
import time
import traceback
import json
import os
from typing import List, Dict, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QThread
import uiautomator2 as u2
from utils.data_manager import data_manager

class Device:
    """Device class tích hợp từ core1.py với GUI support"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.d = None
        self.connected = False
        self.screen_info = None
        self.device_info = None
        
    def connect(self) -> bool:
        """Kết nối đến device"""
        try:
            self.d = u2.connect(self.device_id)
            if self.d.info:
                self.connected = True
                self.device_info = self.d.info
                self.screen_info = {
                    'width': self.device_info.get('displayWidth', 1080),
                    'height': self.device_info.get('displayHeight', 2220)
                }
                return True
        except Exception as e:
            print(f"❌ Lỗi kết nối device {self.device_id}: {e}")
        return False
    
    def disconnect(self):
        """Ngắt kết nối device"""
        self.connected = False
        self.d = None
        self.screen_info = None
        self.device_info = None
    
    def is_connected(self) -> bool:
        """Kiểm tra trạng thái kết nối"""
        return self.connected and self.d is not None
    
    def get_info(self) -> Dict:
        """Lấy thông tin device"""
        if self.device_info:
            return self.device_info
        return {}
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Lấy kích thước màn hình"""
        if self.screen_info:
            return self.screen_info['width'], self.screen_info['height']
        return 1080, 2220
    
    def take_screenshot(self, save_path: str = None) -> str:
        """Chụp màn hình"""
        try:
            if not self.is_connected():
                return None
            
            if save_path is None:
                save_path = f"screenshot_{self.device_id.replace(':', '_')}_{int(time.time())}.png"
            
            self.d.screenshot(save_path)
            return save_path
        except Exception as e:
            print(f"❌ Lỗi chụp màn hình: {e}")
            return None
    
    # Basic touch operations
    def tap(self, x: int, y: int) -> bool:
        """Tap tại tọa độ x, y"""
        try:
            if self.is_connected():
                self.d.click(x, y)
                return True
        except Exception as e:
            print(f"❌ Lỗi tap: {e}")
        return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> bool:
        """Swipe từ điểm start đến điểm end"""
        try:
            if self.is_connected():
                self.d.swipe(start_x, start_y, end_x, end_y, duration)
                return True
        except Exception as e:
            print(f"❌ Lỗi swipe: {e}")
        return False
    
    def input_text(self, text: str) -> bool:
        """Nhập text"""
        try:
            if self.is_connected():
                self.d.send_keys(text)
                return True
        except Exception as e:
            print(f"❌ Lỗi input text: {e}")
        return False
    
    # Element operations
    def click_by_text(self, text: str, timeout: int = 5) -> bool:
        """Click element theo text"""
        try:
            if self.is_connected():
                element = self.d(text=text)
                if element.wait(timeout=timeout):
                    element.click()
                    return True
        except Exception as e:
            print(f"❌ Lỗi click by text: {e}")
        return False
    
    def click_by_resource_id(self, resource_id: str, timeout: int = 5) -> bool:
        """Click element theo resource ID"""
        try:
            if self.is_connected():
                element = self.d(resourceId=resource_id)
                if element.wait(timeout=timeout):
                    element.click()
                    return True
        except Exception as e:
            print(f"❌ Lỗi click by resource ID: {e}")
        return False
    
    def element_exists(self, **kwargs) -> bool:
        """Kiểm tra element có tồn tại không"""
        try:
            if self.is_connected():
                return self.d(**kwargs).exists
        except:
            pass
        return False

class DeviceWorker(QThread):
    """Worker thread để chạy flow trên device"""
    
    # Signals
    log_message = pyqtSignal(str, str)  # message, level
    flow_finished = pyqtSignal(str, bool)  # device_id, success
    
    def __init__(self, device_id: str, flow_function=None):
        super().__init__()
        self.device_id = device_id
        self.device = None
        self.flow_function = flow_function
        self.stop_requested = False
        
    def log(self, message: str, level: str = "INFO"):
        """Emit log message"""
        self.log_message.emit(f"[{self.device_id}] {message}", level)
    
    def run(self):
        """Main thread execution"""
        try:
            # Initialize device
            # Đảm bảo device_id có format IP:5555 cho network devices
            device_id = self.device_id
            if ':' not in device_id and '.' in device_id:  # IP address without port
                device_id = f"{device_id}:5555"
            
            self.device = Device(device_id)
            if not self.device.connect():
                self.log("❌ Không thể kết nối device", "ERROR")
                self.flow_finished.emit(self.device_id, False)
                return
            
            self.log("✅ Đã kết nối device", "SUCCESS")
            
            # Run flow if provided
            if self.flow_function and not self.stop_requested:
                try:
                    result = self.flow_function(self.device)
                    if result:
                        self.log("✅ Flow hoàn thành thành công", "SUCCESS")
                        self.flow_finished.emit(self.device_id, True)
                    else:
                        self.log("⚠️ Flow hoàn thành với lỗi", "WARNING")
                        self.flow_finished.emit(self.device_id, False)
                except Exception as e:
                    self.log(f"❌ Flow crashed: {e}", "ERROR")
                    self.flow_finished.emit(self.device_id, False)
            
        except Exception as e:
            self.log(f"❌ Worker error: {e}", "ERROR")
            self.flow_finished.emit(self.device_id, False)
        finally:
            if self.device:
                self.device.disconnect()
    
    def stop(self):
        """Request stop"""
        self.stop_requested = True
        self.quit()
        self.wait()

class DeviceManager(QObject):
    """Device Manager với GUI integration"""
    
    # Signals
    devices_updated = pyqtSignal(list)  # List of device IDs
    device_connected = pyqtSignal(str)  # device_id
    device_disconnected = pyqtSignal(str)  # device_id
    log_message = pyqtSignal(str, str)  # message, level
    
    def __init__(self):
        super().__init__()
        self.connected_devices = {}  # device_id -> Device object
        self.workers = {}  # device_id -> DeviceWorker
        self.phone_mapping = {}  # IP -> phone number (cached from DataManager)
        
        # Load phone mapping từ DataManager
        self.load_phone_mapping()
    
    def get_available_devices(self) -> List[str]:
        """Lấy danh sách devices có sẵn từ ADB"""
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
            devices_output = result.stdout
            
            # Parse danh sách devices
            lines = devices_output.strip().split('\n')[1:]  # Bỏ dòng header
            available_devices = []
            for line in lines:
                if line.strip() and '\t' in line:
                    device_id = line.split('\t')[0]
                    status = line.split('\t')[1]
                    if status == 'device':  # Chỉ lấy devices đã sẵn sàng
                        available_devices.append(device_id)
            
            self.devices_updated.emit(available_devices)
            return available_devices
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi kiểm tra ADB devices: {e}", "ERROR")
            return []
    
    def connect_device(self, device_id: str) -> bool:
        """Kết nối đến device"""
        if device_id in self.connected_devices:
            return True
        
        # Đảm bảo device_id có format IP:5555 cho network devices
        if ':' not in device_id and '.' in device_id:  # IP address without port
            device_id = f"{device_id}:5555"
        
        device = Device(device_id)
        if device.connect():
            self.connected_devices[device_id] = device
            self.device_connected.emit(device_id)
            self.log_message.emit(f"✅ Đã kết nối device: {device_id}", "SUCCESS")
            return True
        else:
            self.log_message.emit(f"❌ Không thể kết nối device: {device_id}", "ERROR")
            return False
    
    def disconnect_device(self, device_id: str):
        """Ngắt kết nối device"""
        if device_id in self.connected_devices:
            self.connected_devices[device_id].disconnect()
            del self.connected_devices[device_id]
            self.device_disconnected.emit(device_id)
            self.log_message.emit(f"🔌 Đã ngắt kết nối device: {device_id}", "INFO")
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Lấy device object"""
        return self.connected_devices.get(device_id)
    
    def get_devices(self):
        """Get list of connected devices"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = []
            for line in lines:
                if line.strip() and '\t' in line:
                    device_id, status = line.split('\t')
                    devices.append({
                        'id': device_id,
                        'status': status,
                        'name': f'Device {device_id[:8]}'
                    })
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []
    
    def get_connected_devices(self):
        """Lấy danh sách devices đã kết nối - alias for get_devices for compatibility"""
        return self.get_devices()
    
    def load_phone_mapping(self):
        """Load phone mapping từ DataManager"""
        try:
            self.phone_mapping = data_manager.get_phone_mapping()
            self.log_message.emit(f"📞 Đã load {len(self.phone_mapping)} phone mappings từ master config", "INFO")
        except Exception as e:
            self.log_message.emit(f"⚠️ Lỗi load phone mapping: {e}", "WARNING")
    
    def save_phone_mapping(self):
        """Lưu phone mapping vào DataManager"""
        try:
            # DataManager tự động lưu khi set phone mapping
            self.log_message.emit(f"💾 Phone mapping đã được lưu vào master config", "SUCCESS")
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi lưu phone mapping: {e}", "ERROR")
            return False
    
    def set_phone_mapping(self, ip: str, phone: str):
        """Set phone mapping cho IP"""
        self.phone_mapping[ip] = phone
        # Lưu vào DataManager
        data_manager.set_phone_mapping(ip, phone)
    
    def get_phone_mapping(self, ip: str) -> str:
        """Lấy phone number cho IP"""
        # Refresh từ DataManager để đảm bảo data mới nhất
        phone = data_manager.get_phone_by_ip(ip)
        return phone if phone else ""
    
    def run_flow_on_device(self, device_id: str, flow_function):
        """Chạy flow trên device trong thread riêng"""
        if device_id in self.workers:
            self.workers[device_id].stop()
        
        worker = DeviceWorker(device_id, flow_function)
        worker.log_message.connect(self.log_message)
        worker.flow_finished.connect(self._on_flow_finished)
        
        self.workers[device_id] = worker
        worker.start()
    
    def _on_flow_finished(self, device_id: str, success: bool):
        """Callback khi flow hoàn thành"""
        if device_id in self.workers:
            del self.workers[device_id]
        
        status = "thành công" if success else "thất bại"
        self.log_message.emit(f"🏁 Flow trên {device_id} hoàn thành {status}", "INFO")
    
    def stop_all_flows(self):
        """Dừng tất cả flows đang chạy"""
        for worker in self.workers.values():
            worker.stop()
        self.workers.clear()
        self.log_message.emit("🛑 Đã dừng tất cả flows", "INFO")
    
    def disconnect_all_devices(self):
        """Ngắt kết nối tất cả devices"""
        for device_id in list(self.connected_devices.keys()):
            self.disconnect_device(device_id)
        self.log_message.emit("🔌 Đã ngắt kết nối tất cả devices", "INFO")
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_all_flows()
        for device in self.connected_devices.values():
            device.disconnect()
        self.connected_devices.clear()