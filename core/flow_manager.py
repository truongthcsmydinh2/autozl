#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Manager Module
Quản lý và thực thi automation flows
"""

import os
import re
import time
import json
import threading
from typing import Dict, List, Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QFileSystemWatcher
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FlowExecutionHandler(FileSystemEventHandler):
    """Handler cho hot-reload flows"""
    
    def __init__(self, flow_manager):
        self.flow_manager = flow_manager
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith('.py'):
            # Debounce: chỉ reload nếu file không được modify trong 1 giây
            current_time = time.time()
            if event.src_path in self.last_modified:
                if current_time - self.last_modified[event.src_path] < 1.0:
                    return
            
            self.last_modified[event.src_path] = current_time
            self.flow_manager.reload_flow_file(event.src_path)

class FlowManager(QObject):
    """Flow Manager với hot-reload support"""
    
    # Signals
    flow_loaded = pyqtSignal(str, str)  # flow_name, flow_content
    flow_reloaded = pyqtSignal(str)  # flow_name
    flow_error = pyqtSignal(str, str)  # flow_name, error_message
    log_message = pyqtSignal(str, str)  # message, level
    
    def __init__(self):
        super().__init__()
        self.flows = {}  # flow_name -> flow_function
        self.flow_files = {}  # flow_name -> file_path
        self.flow_contents = {}  # flow_name -> source_code
        self.flows_directory = "flows"
        self.observer = None
        self.flow_pattern = re.compile(r"#\s*===\s*FLOW START\s*===\s*(.*?)#\s*===\s*FLOW END\s*===", re.S)
        
        # Ensure flows directory exists
        os.makedirs(self.flows_directory, exist_ok=True)
        
        # Setup file watcher for hot-reload
        self.setup_file_watcher()
    
    def setup_file_watcher(self):
        """Setup file watcher cho hot-reload"""
        try:
            self.observer = Observer()
            event_handler = FlowExecutionHandler(self)
            self.observer.schedule(event_handler, self.flows_directory, recursive=True)
            self.observer.start()
            self.log_message.emit("🔄 Hot-reload đã được kích hoạt", "INFO")
        except Exception as e:
            self.log_message.emit(f"⚠️ Không thể setup hot-reload: {e}", "WARNING")
    
    def load_flows_from_directory(self):
        """Load tất cả flows từ thư mục flows"""
        try:
            for filename in os.listdir(self.flows_directory):
                if filename.endswith('.py'):
                    file_path = os.path.join(self.flows_directory, filename)
                    self.load_flow_from_file(file_path)
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi load flows: {e}", "ERROR")
    
    def load_flow_from_file(self, file_path: str) -> bool:
        """Load flow từ file Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            flow_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Tìm flow function trong file
            flow_function = self.extract_flow_function(content)
            if flow_function:
                self.flows[flow_name] = flow_function
                self.flow_files[flow_name] = file_path
                self.flow_contents[flow_name] = content
                
                self.flow_loaded.emit(flow_name, content)
                self.log_message.emit(f"✅ Đã load flow: {flow_name}", "SUCCESS")
                return True
            else:
                self.log_message.emit(f"⚠️ Không tìm thấy flow function trong {flow_name}", "WARNING")
                return False
                
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi load flow từ {file_path}: {e}", "ERROR")
            self.flow_error.emit(flow_name if 'flow_name' in locals() else file_path, str(e))
            return False
    
    def extract_flow_function(self, content: str) -> Optional[Callable]:
        """Extract flow function từ source code"""
        try:
            # Tìm vùng FLOW START/END
            match = self.flow_pattern.search(content)
            if match:
                flow_code = match.group(1)
            else:
                # Nếu không có markers, sử dụng toàn bộ file
                flow_code = content
            
            # Tạo namespace để exec code
            namespace = {
                '__builtins__': __builtins__,
                'time': time,
                'os': os,
                'json': json,
                're': re
            }
            
            # Import các modules cần thiết
            try:
                import uiautomator2 as u2
                namespace['u2'] = u2
            except ImportError:
                pass
            
            # Exec flow code
            exec(flow_code, namespace, namespace)
            
            # Tìm flow function
            if 'flow' in namespace and callable(namespace['flow']):
                return namespace['flow']
            
            # Tìm function có tên chứa 'flow'
            for name, obj in namespace.items():
                if callable(obj) and 'flow' in name.lower() and not name.startswith('_'):
                    return obj
            
            return None
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi extract flow function: {e}", "ERROR")
            return None
    
    def reload_flow_file(self, file_path: str):
        """Reload flow từ file (hot-reload)"""
        flow_name = os.path.splitext(os.path.basename(file_path))[0]
        
        if self.load_flow_from_file(file_path):
            self.flow_reloaded.emit(flow_name)
            self.log_message.emit(f"🔄 Đã reload flow: {flow_name}", "INFO")
    
    def create_new_flow(self, flow_name: str, template: str = "basic") -> str:
        """Tạo flow mới từ template"""
        file_path = os.path.join(self.flows_directory, f"{flow_name}.py")
        
        if os.path.exists(file_path):
            raise FileExistsError(f"Flow {flow_name} đã tồn tại")
        
        template_content = self.get_flow_template(template)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            self.log_message.emit(f"✅ Đã tạo flow mới: {flow_name}", "SUCCESS")
            return file_path
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi tạo flow: {e}", "ERROR")
            raise
    
    def get_flow_template(self, template: str) -> str:
        """Lấy template cho flow mới"""
        templates = {
            "basic": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Flow Template
"""

import time

# === FLOW START ===
def flow(device):
    """
    Basic flow function
    Args:
        device: Device object với các methods để control Android device
    Returns:
        "SUCCESS" nếu thành công, "LOGIN_REQUIRED" nếu cần login, hoặc False nếu lỗi
    """
    try:
        # Kiểm tra device đã kết nối
        if not device.is_connected():
            print("❌ Device chưa kết nối")
            return False
        
        # Chụp screenshot để debug
        screenshot_path = device.take_screenshot()
        if screenshot_path:
            print(f"📸 Screenshot saved: {screenshot_path}")
        
        # TODO: Thêm logic automation ở đây
        print("🚀 Flow đang chạy...")
        
        # Example: Click vào một element
        # if device.click_by_text("Button Text"):
        #     print("✅ Clicked button successfully")
        # else:
        #     print("❌ Button not found")
        
        time.sleep(1)
        
        print("✅ Flow hoàn thành")
        return "SUCCESS"
        
    except Exception as e:
        print(f"❌ Flow error: {e}")
        return False
# === FLOW END ===
''',
            
            "zalo": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zalo Automation Flow Template
"""

import time

# === FLOW START ===
def flow(device, all_devices=None):
    """
    Zalo automation flow
    Args:
        device: Device object
        all_devices: List of all device IPs (for group conversations)
    Returns:
        "SUCCESS", "LOGIN_REQUIRED", or False
    """
    try:
        # Kiểm tra device
        if not device.is_connected():
            return False
        
        # Mở Zalo app
        if not device.click_by_text("Zalo"):
            print("❌ Không tìm thấy Zalo app")
            return False
        
        time.sleep(3)
        
        # Kiểm tra đã login chưa
        if device.element_exists(text="Đăng nhập"):
            print("🔐 Cần đăng nhập Zalo")
            return "LOGIN_REQUIRED"
        
        # TODO: Thêm logic Zalo automation
        print("📱 Zalo automation đang chạy...")
        
        return "SUCCESS"
        
    except Exception as e:
        print(f"❌ Zalo flow error: {e}")
        return False
# === FLOW END ===
'''
        }
        
        return templates.get(template, templates["basic"])
    
    def save_flow(self, flow_name: str, content: str) -> bool:
        """Lưu flow content vào file"""
        try:
            file_path = os.path.join(self.flows_directory, f"{flow_name}.py")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Reload flow
            self.load_flow_from_file(file_path)
            self.log_message.emit(f"💾 Đã lưu flow: {flow_name}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi lưu flow: {e}", "ERROR")
            return False
    
    def delete_flow(self, flow_name: str) -> bool:
        """Xóa flow"""
        try:
            if flow_name in self.flow_files:
                file_path = self.flow_files[flow_name]
                os.remove(file_path)
                
                # Remove from memory
                del self.flows[flow_name]
                del self.flow_files[flow_name]
                del self.flow_contents[flow_name]
                
                self.log_message.emit(f"🗑️ Đã xóa flow: {flow_name}", "INFO")
                return True
            else:
                self.log_message.emit(f"⚠️ Flow không tồn tại: {flow_name}", "WARNING")
                return False
                
        except Exception as e:
            self.log_message.emit(f"❌ Lỗi xóa flow: {e}", "ERROR")
            return False
    
    def get_flow_function(self, flow_name: str) -> Optional[Callable]:
        """Lấy flow function"""
        return self.flows.get(flow_name)
    
    def get_flow_content(self, flow_name: str) -> str:
        """Lấy flow source code"""
        return self.flow_contents.get(flow_name, "")
    
    def get_available_flows(self) -> List[str]:
        """Lấy danh sách flows có sẵn"""
        return list(self.flows.keys())
    
    def validate_flow_syntax(self, content: str) -> tuple[bool, str]:
        """Validate flow syntax"""
        try:
            compile(content, '<string>', 'exec')
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def cleanup(self):
        """Cleanup resources"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.flows.clear()
        self.flow_files.clear()
        self.flow_contents.clear()