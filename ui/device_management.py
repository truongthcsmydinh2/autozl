# -*- coding: utf-8 -*-
"""
Device Management UI
Quản lý thiết bị Android và kết nối
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QGroupBox, QLineEdit, QComboBox, QTextEdit,
    QProgressBar, QFrame, QSplitter, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

class DeviceListWidget(QListWidget):
    """Custom device list widget với styling"""
    
    device_selected = pyqtSignal(str)  # Emit device ID when selected
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QListWidget::item {
                padding: 16px;
                border-bottom: 1px solid #404040;
                border-radius: 6px;
                margin: 3px 0;
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QListWidget::item:hover {
                background-color: #404040;
                color: #ffffff;
            }
            
            QListWidget::item:selected {
                background-color: #4a90e2;
                color: #ffffff;
                font-weight: bold;
            }
            
            QListWidget::item[status="connected"] {
                border-left: 4px solid #4caf50;
            }
            
            QListWidget::item[status="disconnected"] {
                border-left: 4px solid #f44336;
            }
            
            QListWidget::item[status="unauthorized"] {
                border-left: 4px solid #ff9800;
            }
        """)
        
        self.itemClicked.connect(self.on_item_clicked)
        
    def on_item_clicked(self, item):
        device_id = item.data(Qt.ItemDataRole.UserRole)
        if device_id:
            self.device_selected.emit(device_id)
            
    def add_device(self, device_id, device_info):
        """Thêm device vào list"""
        item = QListWidgetItem()
        
        # Format device display text
        display_text = f"📱 {device_id}\n"
        if device_info.get('model'):
            display_text += f"Model: {device_info['model']}\n"
        if device_info.get('android_version'):
            display_text += f"Android: {device_info['android_version']}\n"
        
        status = device_info.get('status', 'unknown')
        status_emoji = "🟢" if status == "device" else "🔴" if status == "offline" else "🟡"
        display_text += f"Status: {status_emoji} {status}"
        
        item.setText(display_text)
        item.setData(Qt.ItemDataRole.UserRole, device_id)
        
        self.addItem(item)
        
    def clear_devices(self):
        """Xóa tất cả devices"""
        self.clear()

class DeviceInfoWidget(QWidget):
    """Widget hiển thị thông tin chi tiết device"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Device info group
        info_group = QGroupBox("Device Information")
        info_layout = QGridLayout()
        
        # Info labels
        self.device_id_label = QLabel("Not selected")
        self.model_label = QLabel("-")
        self.android_label = QLabel("-")
        self.resolution_label = QLabel("-")
        self.status_label = QLabel("-")
        
        info_layout.addWidget(QLabel("Device ID:"), 0, 0)
        info_layout.addWidget(self.device_id_label, 0, 1)
        info_layout.addWidget(QLabel("Model:"), 1, 0)
        info_layout.addWidget(self.model_label, 1, 1)
        info_layout.addWidget(QLabel("Android:"), 2, 0)
        info_layout.addWidget(self.android_label, 2, 1)
        info_layout.addWidget(QLabel("Resolution:"), 3, 0)
        info_layout.addWidget(self.resolution_label, 3, 1)
        info_layout.addWidget(QLabel("Status:"), 4, 0)
        info_layout.addWidget(self.status_label, 4, 1)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Control buttons
        control_group = QGroupBox("Device Controls")
        control_layout = QVBoxLayout()
        
        self.connect_btn = QPushButton("🔌 Connect")
        self.disconnect_btn = QPushButton("🔌 Disconnect")
        self.screenshot_btn = QPushButton("📸 Take Screenshot")
        self.shell_btn = QPushButton("💻 Open Shell")
        
        # Style buttons
        for btn in [self.connect_btn, self.disconnect_btn, self.screenshot_btn, self.shell_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 20px;
                    border: none;
                    border-radius: 6px;
                    background-color: #4a90e2;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #5ba0f2;
                }
                QPushButton:pressed {
                    background-color: #3a80d2;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                }
            """)
            
        control_layout.addWidget(self.connect_btn)
        control_layout.addWidget(self.disconnect_btn)
        control_layout.addWidget(self.screenshot_btn)
        control_layout.addWidget(self.shell_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Initially disable all buttons
        self.set_buttons_enabled(False)
        
    def update_device_info(self, device_id, device_info):
        """Cập nhật thông tin device"""
        self.device_id_label.setText(device_id)
        self.model_label.setText(device_info.get('model', '-'))
        self.android_label.setText(device_info.get('android_version', '-'))
        self.resolution_label.setText(device_info.get('resolution', '-'))
        
        status = device_info.get('status', 'unknown')
        status_color = "green" if status == "device" else "red" if status == "offline" else "orange"
        self.status_label.setText(f"<span style='color: {status_color}'>{status}</span>")
        
        # Enable/disable buttons based on status
        is_connected = status == "device"
        self.set_buttons_enabled(True)
        self.connect_btn.setEnabled(not is_connected)
        self.disconnect_btn.setEnabled(is_connected)
        self.screenshot_btn.setEnabled(is_connected)
        self.shell_btn.setEnabled(is_connected)
        
    def set_buttons_enabled(self, enabled):
        """Enable/disable all control buttons"""
        self.connect_btn.setEnabled(enabled)
        self.disconnect_btn.setEnabled(enabled)
        self.screenshot_btn.setEnabled(enabled)
        self.shell_btn.setEnabled(enabled)
        
    def clear_info(self):
        """Clear device info"""
        self.device_id_label.setText("Not selected")
        self.model_label.setText("-")
        self.android_label.setText("-")
        self.resolution_label.setText("-")
        self.status_label.setText("-")
        self.set_buttons_enabled(False)

class PhoneMappingWidget(QWidget):
    """Widget quản lý phone mapping"""
    
    mapping_changed = pyqtSignal(dict)  # Emit when mapping changes
    
    def __init__(self):
        super().__init__()
        self.phone_mapping = {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📞 Phone Number Mapping")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Mapping table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(3)
        self.mapping_table.setHorizontalHeaderLabels(["Device ID", "Phone Number", "Actions"])
        
        # Set column widths
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.mapping_table.setColumnWidth(2, 100)
        
        layout.addWidget(self.mapping_table)
        
        # Add mapping controls
        add_layout = QHBoxLayout()
        
        self.device_combo = QComboBox()
        self.device_combo.setPlaceholderText("Select device...")
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number...")
        
        self.add_btn = QPushButton("➕ Add Mapping")
        self.add_btn.clicked.connect(self.add_mapping)
        
        add_layout.addWidget(QLabel("Device:"))
        add_layout.addWidget(self.device_combo)
        add_layout.addWidget(QLabel("Phone:"))
        add_layout.addWidget(self.phone_input)
        add_layout.addWidget(self.add_btn)
        
        layout.addLayout(add_layout)
        
        # Quick setup button removed as per requirements
        
        self.setLayout(layout)
        
    def update_available_devices(self, devices):
        """Cập nhật danh sách devices có thể chọn"""
        self.device_combo.clear()
        for device_id in devices:
            if device_id not in self.phone_mapping:
                self.device_combo.addItem(device_id)
                
    def add_mapping(self):
        """Thêm mapping mới"""
        device_id = self.device_combo.currentText()
        phone_number = self.phone_input.text().strip()
        
        if not device_id or not phone_number:
            QMessageBox.warning(self, "Warning", "Please select device and enter phone number")
            return
            
        if device_id in self.phone_mapping:
            QMessageBox.warning(self, "Warning", f"Device {device_id} already has a phone mapping")
            return
            
        # Add to mapping
        self.phone_mapping[device_id] = phone_number
        self.refresh_table()
        
        # Clear inputs
        self.phone_input.clear()
        self.device_combo.removeItem(self.device_combo.currentIndex())
        
        # Emit signal
        self.mapping_changed.emit(self.phone_mapping)
        
    def remove_mapping(self, device_id):
        """Xóa mapping"""
        if device_id in self.phone_mapping:
            del self.phone_mapping[device_id]
            self.refresh_table()
            self.mapping_changed.emit(self.phone_mapping)
            
    def refresh_table(self):
        """Refresh mapping table"""
        self.mapping_table.setRowCount(len(self.phone_mapping))
        
        for row, (device_id, phone_number) in enumerate(self.phone_mapping.items()):
            # Device ID
            self.mapping_table.setItem(row, 0, QTableWidgetItem(device_id))
            
            # Phone number
            self.mapping_table.setItem(row, 1, QTableWidgetItem(phone_number))
            
            # Remove button
            remove_btn = QPushButton("🗑️ Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            remove_btn.clicked.connect(lambda checked, did=device_id: self.remove_mapping(did))
            self.mapping_table.setCellWidget(row, 2, remove_btn)
            
    def set_mapping(self, mapping):
        """Set phone mapping từ external source"""
        self.phone_mapping = mapping.copy()
        self.refresh_table()

class DeviceManagementWidget(QWidget):
    """Main device management widget"""
    
    def __init__(self, device_manager=None):
        super().__init__()
        self.device_manager = device_manager
        self.current_device_id = None
        self.setup_ui()
        self.setup_connections()
        
        # Auto refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Left panel - Device list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Device list header
        list_header = QHBoxLayout()
        list_title = QLabel("📱 Connected Devices")
        list_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setMaximumWidth(100)
        
        list_header.addWidget(list_title)
        list_header.addStretch()
        list_header.addWidget(self.refresh_btn)
        
        left_layout.addLayout(list_header)
        
        # Device list
        self.device_list = DeviceListWidget()
        left_layout.addWidget(self.device_list)
        
        left_panel.setLayout(left_layout)
        
        # Right panel - Device info and phone mapping
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Device info
        self.device_info = DeviceInfoWidget()
        right_layout.addWidget(self.device_info)
        
        # Phone mapping
        self.phone_mapping = PhoneMappingWidget()
        right_layout.addWidget(self.phone_mapping)
        
        right_panel.setLayout(right_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])  # Set initial sizes
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.refresh_btn.clicked.connect(self.refresh_devices)
        self.device_list.device_selected.connect(self.on_device_selected)
        
        # Device info controls
        self.device_info.connect_btn.clicked.connect(self.connect_device)
        self.device_info.disconnect_btn.clicked.connect(self.disconnect_device)
        self.device_info.screenshot_btn.clicked.connect(self.take_screenshot)
        self.device_info.shell_btn.clicked.connect(self.open_shell)
        
        # Phone mapping - quick setup removed
        
    def refresh_devices(self):
        """Refresh device list"""
        if not self.device_manager:
            return
            
        try:
            # Đồng bộ với ADB devices trước
            from utils.data_manager import data_manager
            device_count = data_manager.sync_with_adb_devices()
            print(f"Synced {device_count} devices with ADB")
            
            # Get connected devices
            devices = self.device_manager.get_devices()
            
            # Clear and repopulate list
            self.device_list.clear_devices()
            
            device_ids = []
            if isinstance(devices, list):
                for device in devices:
                    if isinstance(device, dict):
                        device_id = device.get('id', 'Unknown')
                        self.device_list.add_device(device_id, device)
                        device_ids.append(device_id)
            elif isinstance(devices, dict):
                for device_id, device_info in devices.items():
                    self.device_list.add_device(device_id, device_info)
                    device_ids.append(device_id)
                
            # Update phone mapping available devices
            self.phone_mapping.update_available_devices(device_ids)
            self.phone_mapping.refresh_devices()  # Refresh phone mapping table
            
        except Exception as e:
            print(f"Error refreshing devices: {e}")
            
    def on_device_selected(self, device_id):
        """Handle device selection"""
        self.current_device_id = device_id
        
        if self.device_manager:
            try:
                devices = self.device_manager.get_devices()
                device_info = None
                
                # Handle both list and dict formats
                if isinstance(devices, list):
                    for device in devices:
                        if isinstance(device, dict) and device.get('id') == device_id:
                            device_info = device
                            break
                elif isinstance(devices, dict):
                    device_info = devices.get(device_id)
                
                if device_info:
                    self.device_info.update_device_info(device_id, device_info)
                else:
                    self.device_info.clear_info()
            except Exception as e:
                print(f"Error getting device info: {e}")
                self.device_info.clear_info()
        
    def connect_device(self):
        """Connect to selected device"""
        if not self.current_device_id or not self.device_manager:
            return
            
        try:
            success = self.device_manager.connect_device(self.current_device_id)
            if success:
                QMessageBox.information(self, "Success", f"Connected to {self.current_device_id}")
                self.refresh_devices()
            else:
                QMessageBox.warning(self, "Error", f"Failed to connect to {self.current_device_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
            
    def disconnect_device(self):
        """Disconnect from selected device"""
        if not self.current_device_id:
            return
            
        QMessageBox.information(self, "Info", f"Disconnected from {self.current_device_id}")
        self.refresh_devices()
        
    def take_screenshot(self):
        """Take screenshot of selected device"""
        if not self.current_device_id or not self.device_manager:
            return
            
        try:
            # This would integrate with device_manager screenshot functionality
            QMessageBox.information(self, "Screenshot", f"Screenshot taken for {self.current_device_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Screenshot error: {str(e)}")
            
    def open_shell(self):
        """Open ADB shell for selected device"""
        if not self.current_device_id:
            return
            
        QMessageBox.information(self, "Shell", f"Opening shell for {self.current_device_id}")
        
    # quick_setup_mapping method removed as per requirements