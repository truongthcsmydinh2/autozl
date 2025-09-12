# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, 
    QPushButton, QTextEdit, QScrollArea, QFrame, QProgressBar,
    QMessageBox, QGroupBox, QGridLayout, QSpacerItem, QSizePolicy,
    QLineEdit, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
import json
import os
import sys
import subprocess
import threading
from typing import List, Dict
from utils.data_manager import data_manager

# Import core1 functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core1 import get_available_devices_for_gui, run_automation_from_gui, load_phone_map_from_file
except ImportError:
    def get_available_devices_for_gui():
        return []
    def run_automation_from_gui(devices, conversation):
        return {}
    def load_phone_map_from_file():
        return {}

class AutomationWorker(QThread):
    """Worker thread để chạy automation không block UI"""
    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, automation_data):
        super().__init__()
        self.automation_data = automation_data
        self.is_running = True
    
    def run(self):
        """Run automation in background thread"""
        try:
            device_pairs = self.automation_data['device_pairs']
            conversations = self.automation_data['conversations']
            phone_mapping = self.automation_data['phone_mapping']
            
            self.progress_updated.emit(f"🔌 Kết nối {len(device_pairs)} cặp devices...")
            
            # Prepare device list for core1.py
            device_list = []
            for device1, device2 in device_pairs:
                device_list.extend([device1['ip'], device2['ip']])
            
            # Prepare parameters for core1.py
            automation_params = {
                'devices': device_list,
                'conversations': conversations,
                'phone_mapping': phone_mapping,
                'pairs': device_pairs
            }
            
            # Run automation from core1
            results = run_automation_from_gui(automation_params)
            
            self.progress_updated.emit("✅ Hoàn thành automation!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        self.is_running = False
        self.terminate()

class DeviceCheckBox(QCheckBox):
    """Custom checkbox cho device với thông tin bổ sung"""
    def __init__(self, device_id, phone_number=None):
        super().__init__()
        self.device_id = device_id
        self.phone_number = phone_number
        
        # Format display text
        display_text = device_id
        if phone_number and phone_number != "Chưa có số":
            display_text += f" ({phone_number})"
        
        self.setText(display_text)
        self.setFixedHeight(22)  # Further reduced height for more devices
        self.setMinimumWidth(200)  # Minimum width for proper display
        self.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
                padding: 4px 8px;
                margin: 1px 0px;
                spacing: 8px;
                border: 1px solid transparent;
                border-radius: 4px;
                min-height: 24px;
                max-height: 28px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                margin-right: 8px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2d2d2d;
                border: 2px solid #555555;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #106ebe;
                border: 2px solid #106ebe;
            }
            QCheckBox:hover {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QCheckBox:focus {
                border: 1px solid #0078d4;
                outline: none;
            }
        """)

class ZaloAutomationWidget(QWidget):
    """Widget chính cho chức năng Nuôi Zalo"""
    
    def __init__(self):
        super().__init__()
        self.devices = []
        self.device_checkboxes = []
        self.phone_map = {}
        self.automation_worker = None
        
        self.init_ui()
        self.load_devices()
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🤖 Nuôi Zalo Automation")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Device Selection Section
        self.create_device_section(layout)
        
        # Pairing Section
        self.create_pairing_section(layout)
        
        # Conversation Section
        self.create_conversation_section(layout)
        
        # Control Section
        self.create_control_section(layout)
        
        # Progress Section
        self.create_progress_section(layout)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def create_device_section(self, layout):
        """Tạo section chọn devices với QSplitter và fixed sizes"""
        device_group = QGroupBox("📱 Chọn Devices")
        device_group.setFixedHeight(400)  # Fixed height for entire section
        device_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                padding-bottom: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Main splitter for vertical layout
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        
        # Top frame for refresh button
        refresh_frame = QFrame()
        refresh_frame.setFixedHeight(40)
        refresh_frame.setFrameStyle(QFrame.Shape.Box)
        refresh_frame.setStyleSheet("QFrame { border: 1px solid #333; background-color: #2a2a2a; }")
        refresh_layout = QHBoxLayout(refresh_frame)
        refresh_layout.setContentsMargins(5, 5, 5, 5)
        
        refresh_btn = QPushButton("🔄 Refresh Devices")
        refresh_btn.clicked.connect(self.load_devices)
        refresh_btn.setFixedSize(150, 30)
        QTimer.singleShot(100, self.load_devices)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        main_splitter.addWidget(refresh_frame)
        
        # Search frame
        search_frame = QFrame()
        search_frame.setFixedHeight(35)
        search_frame.setFrameStyle(QFrame.Shape.Box)
        search_frame.setStyleSheet("QFrame { border: 1px solid #333; background-color: #2a2a2a; }")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        search_label = QLabel("Tìm kiếm:")
        search_label.setFixedSize(60, 25)
        search_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập IP hoặc số điện thoại...")
        self.search_input.setFixedHeight(25)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 3px 6px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        self.search_input.textChanged.connect(self.filter_devices)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_splitter.addWidget(search_frame)
        
        # Counter frame
        counter_frame = QFrame()
        counter_frame.setFixedHeight(25)
        counter_frame.setFrameStyle(QFrame.Shape.Box)
        counter_frame.setStyleSheet("QFrame { border: 1px solid #333; background-color: #2a2a2a; }")
        counter_layout = QHBoxLayout(counter_frame)
        counter_layout.setContentsMargins(5, 2, 5, 2)
        
        self.device_counter_label = QLabel("Đã chọn: 0 devices")
        self.device_counter_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        counter_layout.addWidget(self.device_counter_label)
        main_splitter.addWidget(counter_frame)
        
        # Scroll area frame
        scroll_frame = QFrame()
        scroll_frame.setFixedHeight(350)
        scroll_frame.setFrameStyle(QFrame.Shape.Box)
        scroll_frame.setStyleSheet("QFrame { border: 1px solid #333; background-color: #2a2a2a; }")
        scroll_layout = QVBoxLayout(scroll_frame)
        scroll_layout.setContentsMargins(2, 2, 2, 2)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(345)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2d2d2d;
            }
            QScrollBar:vertical {
                background-color: #3d3d3d;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 15px;
            }
        """)
        
        self.device_container = QWidget()
        self.device_layout = QVBoxLayout(self.device_container)
        self.device_layout.setSpacing(0)
        self.device_layout.setContentsMargins(2, 2, 2, 2)
        scroll_area.setWidget(self.device_container)
        
        scroll_layout.addWidget(scroll_area)
        main_splitter.addWidget(scroll_frame)
        
        # Button frame
        button_frame = QFrame()
        button_frame.setFixedHeight(45)
        button_frame.setFrameStyle(QFrame.Shape.Box)
        button_frame.setStyleSheet("QFrame { border: 1px solid #333; background-color: #2a2a2a; }")
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(10)
        
        select_all_btn = QPushButton("✅ Chọn tất cả")
        select_all_btn.clicked.connect(self.select_all_devices)
        select_all_btn.setFixedSize(120, 35)
        select_all_btn.setStyleSheet(self.get_button_style("#28a745"))
        
        select_none_btn = QPushButton("❌ Bỏ chọn tất cả")
        select_none_btn.clicked.connect(self.select_none_devices)
        select_none_btn.setFixedSize(120, 35)
        select_none_btn.setStyleSheet(self.get_button_style("#dc3545"))
        
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(select_none_btn)
        button_layout.addStretch()
        main_splitter.addWidget(button_frame)
        
        # Set splitter sizes to prevent resizing
        main_splitter.setSizes([40, 35, 25, 350, 45])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setStretchFactor(2, 0)
        main_splitter.setStretchFactor(3, 1)
        main_splitter.setStretchFactor(4, 0)
        
        # Add splitter to group
        group_layout = QVBoxLayout(device_group)
        group_layout.setContentsMargins(10, 20, 10, 10)
        group_layout.addWidget(main_splitter)
        
        layout.addWidget(device_group)
    
    def create_pairing_section(self, layout):
        """Tạo section ghép cặp"""
        pairing_group = QGroupBox("💑 Ghép Cặp Devices")
        pairing_group.setStyleSheet(self.get_group_style())
        
        pairing_layout = QVBoxLayout(pairing_group)
        
        self.pairing_info = QLabel("Chọn devices và nhấn 'Ghép cặp' để tự động pair devices")
        self.pairing_info.setStyleSheet("color: #cccccc; font-size: 14px; padding: 10px;")
        pairing_layout.addWidget(self.pairing_info)
        
        self.pair_btn = QPushButton("💕 Ghép Cặp")
        self.pair_btn.clicked.connect(self.pair_devices)
        self.pair_btn.setStyleSheet(self.get_button_style("#ff6b6b"))
        pairing_layout.addWidget(self.pair_btn)
        
        layout.addWidget(pairing_group)
    
    def create_conversation_section(self, layout):
        """Tạo section nhập hội thoại"""
        conv_group = QGroupBox("💬 Đoạn Hội Thoại")
        conv_group.setStyleSheet(self.get_group_style())
        
        conv_layout = QVBoxLayout(conv_group)
        
        conv_label = QLabel("Nhập đoạn hội thoại để automation:")
        conv_label.setStyleSheet("color: #ffffff; font-size: 14px; margin-bottom: 5px;")
        conv_layout.addWidget(conv_label)
        
        self.conversation_text = QTextEdit()
        self.conversation_text.setPlaceholderText("Nhập đoạn hội thoại ở đây...\nVí dụ: Xin chào! Bạn có khỏe không?")
        self.conversation_text.setMaximumHeight(80)
        self.conversation_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
        conv_layout.addWidget(self.conversation_text)
        
        layout.addWidget(conv_group)
    
    def create_control_section(self, layout):
        """Tạo section điều khiển"""
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Bắt Đầu Auto")
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setStyleSheet(self.get_button_style("#28a745", large=True))
        
        self.stop_btn = QPushButton("⏹️ Dừng Auto")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setStyleSheet(self.get_button_style("#dc3545", large=True))
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
    
    def create_progress_section(self, layout):
        """Tạo section hiển thị progress"""
        progress_group = QGroupBox("📊 Trạng Thái")
        progress_group.setStyleSheet(self.get_group_style())
        
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Sẵn sàng để bắt đầu automation")
        self.status_label.setStyleSheet("color: #cccccc; font-size: 14px; padding: 10px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
    
    def get_group_style(self):
        """Style cho QGroupBox"""
        return """
            QGroupBox {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
    
    def get_button_style(self, color, large=False):
        """Style cho buttons"""
        size = "padding: 12px 24px; font-size: 16px;" if large else "padding: 8px 16px; font-size: 14px;"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                {size}
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.3)};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #999999;
            }}
        """
    
    def darken_color(self, color, factor=0.2):
        """Làm tối màu"""
        if color == "#28a745":
            return "#1e7e34" if factor < 0.3 else "#155724"
        elif color == "#dc3545":
            return "#c82333" if factor < 0.3 else "#bd2130"
        elif color == "#0078d4":
            return "#106ebe" if factor < 0.3 else "#005a9e"
        elif color == "#ff6b6b":
            return "#ff5252" if factor < 0.3 else "#f44336"
        return color
    
    def load_devices(self):
        """Load available devices using DataManager with proper error handling"""
        try:
            # Update status
            self.status_label.setText("🔄 Đang tải devices...")
            
            # Đồng bộ với ADB devices trước
            device_count = data_manager.sync_with_adb_devices()
            print(f"Synced {device_count} devices with ADB")
            
            # Reload data from DataManager
            data_manager.reload_data()
            
            # Get devices with phone numbers
            devices = data_manager.get_devices_with_phone_numbers()
            
            # Store all devices for filtering
            self.all_devices = devices if devices else []
            
            # Display devices (this will handle empty list properly)
            self.display_devices(self.all_devices)
            
            # Update status
            if devices:
                self.status_label.setText(f"✅ Tìm thấy {len(devices)} devices")
                self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            else:
                self.status_label.setText("⚠️ Không tìm thấy device nào. Vui lòng kết nối devices và nhấn Refresh.")
                self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
                
        except Exception as e:
            # Clear devices on error
            self.all_devices = []
            self.display_devices([])
            
            # Show error in status
            error_msg = f"❌ Lỗi load devices: {str(e)}"
            self.status_label.setText(error_msg)
            self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            
            # Also show error message box for critical errors
            QMessageBox.warning(self, "Lỗi", error_msg)
    
    def display_devices(self, devices):
        """Display devices in the UI with proper layout management"""
        # Clear existing checkboxes and layout items
        for checkbox in self.device_checkboxes:
            checkbox.setParent(None)
            checkbox.deleteLater()
        self.device_checkboxes.clear()
        
        # Clear all items from layout
        while self.device_layout.count():
            child = self.device_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.spacerItem():
                del child
        
        if not devices:
            no_device_label = QLabel("❌ Không tìm thấy device nào")
            no_device_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 14px;
                    padding: 20px;
                    text-align: center;
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    margin: 10px;
                }
            """)
            no_device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.device_layout.addWidget(no_device_label)
        else:
            for device in devices:
                phone_number = device['phone'] if device['phone'] else "Chưa có số"
                
                checkbox = DeviceCheckBox(device['ip'], phone_number)
                # Store device info in checkbox
                checkbox.device_info = device
                checkbox.stateChanged.connect(self.update_device_counter)
                
                self.device_checkboxes.append(checkbox)
                self.device_layout.addWidget(checkbox)
        
        # Add spacer at the end to push content to top
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.device_layout.addItem(spacer)
        
        # Update container size
        self.device_container.adjustSize()
        
        self.update_device_counter()
    
    def filter_devices(self):
        """Filter devices based on search text with improved performance"""
        search_text = self.search_input.text().lower().strip()
        
        if not hasattr(self, 'all_devices') or not self.all_devices:
            # No devices to filter
            self.display_devices([])
            return
        
        if not search_text:
            # Show all devices
            self.display_devices(self.all_devices)
        else:
            # Filter devices with multiple criteria
            filtered_devices = []
            for device in self.all_devices:
                # Search in IP and phone number
                ip_text = device.get('ip', '').lower()
                phone_text = device.get('phone', '').lower()
                
                # Check if search text matches IP or phone
                if (search_text in ip_text or 
                    search_text in phone_text or
                    search_text in f"{ip_text} {phone_text}"):
                    filtered_devices.append(device)
            
            self.display_devices(filtered_devices)
            
            # Update search status
            if filtered_devices:
                self.status_label.setText(f"🔍 Tìm thấy {len(filtered_devices)}/{len(self.all_devices)} devices")
            else:
                self.status_label.setText(f"🔍 Không tìm thấy device nào với từ khóa '{search_text}'")
                self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
    
    def update_device_counter(self):
        """Update device counter and validate even number"""
        selected_count = len(self.get_selected_devices())
        
        if selected_count % 2 == 0:
            self.device_counter_label.setText(f"Đã chọn: {selected_count} devices ✓")
            self.device_counter_label.setStyleSheet("""
                QLabel {
                    color: #00ff00;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 5px;
                }
            """)
        else:
            self.device_counter_label.setText(f"Đã chọn: {selected_count} devices (cần số chẵn!)")
            self.device_counter_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 5px;
                }
            """)
    
    def select_all_devices(self):
        """Chọn tất cả devices"""
        for checkbox in self.device_checkboxes:
            checkbox.setChecked(True)
        self.update_device_counter()
    
    def select_none_devices(self):
        """Bỏ chọn tất cả devices"""
        for checkbox in self.device_checkboxes:
            checkbox.setChecked(False)
        self.update_device_counter()
    
    def get_selected_devices(self):
        """Get list of selected devices with their info"""
        selected = []
        for checkbox in self.device_checkboxes:
            if checkbox.isChecked():
                if hasattr(checkbox, 'device_info'):
                    selected.append(checkbox.device_info)
                else:
                    # Fallback for old format
                    selected.append({'ip': checkbox.device_id, 'phone': '', 'note': ''})
        return selected
    
    def pair_devices(self):
        """Ghép cặp devices đã chọn với random algorithm"""
        selected = self.get_selected_devices()
        
        if len(selected) < 2:
            QMessageBox.warning(self, "Cảnh báo", "Cần chọn ít nhất 2 devices để ghép cặp!")
            return
        
        if len(selected) % 2 != 0:
            QMessageBox.warning(self, "Cảnh báo", "Số lượng devices phải là số chẵn để ghép cặp!")
            return
        
        # Random shuffle for pairing - mỗi lần ấn sẽ shuffle lại
        import random
        devices_to_pair = selected.copy()
        random.shuffle(devices_to_pair)
        
        # Create pairs
        self.device_pairs = []
        for i in range(0, len(devices_to_pair), 2):
            device1_info = devices_to_pair[i]
            device2_info = devices_to_pair[i+1]
            pair = (device1_info, device2_info)
            self.device_pairs.append(pair)
        
        # Display pairs with phone numbers
        pairs_text = "🔗 Kết quả ghép cặp:\n\n"
        for i, (device1, device2) in enumerate(self.device_pairs, 1):
            phone1 = device1.get('phone', 'Chưa có số')
            phone2 = device2.get('phone', 'Chưa có số')
            pairs_text += f"Cặp {i}: {device1['ip']} ({phone1}) ↔ {device2['ip']} ({phone2})\n"
        
        self.pairing_info.setText(pairs_text)
        
        QMessageBox.information(self, "Thành công", f"Đã ghép {len(self.device_pairs)} cặp devices!\nMỗi lần ấn 'Ghép cặp' sẽ random lại.")
        
        self.status_label.setText(f"✅ Đã ghép {len(self.device_pairs)} cặp devices")
    
    def start_automation(self):
        """Bắt đầu automation với validation và tích hợp core1.py"""
        selected_devices = self.get_selected_devices()
        conversation = self.conversation_text.toPlainText().strip()
        
        # Validation
        if not selected_devices:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 1 device!")
            return
        
        if len(selected_devices) % 2 != 0:
            QMessageBox.warning(self, "Cảnh báo", "Số lượng devices phải là số chẵn!")
            return
        
        if not hasattr(self, 'device_pairs') or not self.device_pairs:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng ghép cặp devices trước!")
            return
        
        if not conversation:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đoạn hội thoại!")
            return
        
        # Prepare data for core1.py
        automation_data = {
            'device_pairs': self.device_pairs,
            'conversations': [conversation] * len(self.device_pairs),
            'phone_mapping': data_manager.get_phone_mapping()
        }
        
        # Confirm
        pairs_summary = "\n".join([f"Cặp {i+1}: {pair[0]['ip']} ↔ {pair[1]['ip']}" 
                                  for i, pair in enumerate(self.device_pairs)])
        
        reply = QMessageBox.question(
            self, "Xác nhận", 
            f"Bắt đầu automation với {len(self.device_pairs)} cặp devices?\n\n{pairs_summary}\n\nTiếp tục?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Start automation
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start worker thread with new automation function
        self.automation_worker = AutomationWorker(automation_data)
        self.automation_worker.progress_updated.connect(self.update_progress)
        self.automation_worker.finished.connect(self.automation_finished)
        self.automation_worker.error_occurred.connect(self.on_automation_error)
        self.automation_worker.start()
        
        self.status_label.setText("🚀 Đang chạy automation...")
        self.status_label.setVisible(True)
    
    def stop_automation(self):
        """Dừng automation"""
        if hasattr(self, 'automation_worker') and self.automation_worker:
            self.automation_worker.stop()
            self.automation_worker = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("⏹️ Đã dừng automation")
        self.status_label.setStyleSheet("color: #ff9800; font-weight: bold;")
    
    def update_progress(self, message):
        """Cập nhật progress"""
        self.status_label.setText(message)
    
    def automation_finished(self, results):
        """Automation hoàn thành"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if results:
            success_count = sum(1 for result in results.values() if result.get('status') == 'completed')
            total_count = len(results)
            message = f"✅ Hoàn thành: {success_count}/{total_count} thành công"
            self.status_label.setText(message)
            QMessageBox.information(self, "Thành công", message)
        else:
            message = "❌ Automation thất bại"
            self.status_label.setText(message)
            QMessageBox.critical(self, "Lỗi", message)
        
        self.automation_worker = None
    
    def on_automation_error(self, error_message):
        """Xử lý khi có lỗi trong automation"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        message = f"❌ Lỗi: {error_message}"
        self.status_label.setText(message)
        QMessageBox.critical(self, "Lỗi", message)
        
        self.automation_worker = None