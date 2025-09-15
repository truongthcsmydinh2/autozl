# -*- coding: utf-8 -*-
"""
Phone Manage Widget
Quản lý thông tin thiết bị Android bao gồm IP, số điện thoại và ghi chú
"""

import json
import os
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.data_manager import data_manager

class PhoneMappingWidget(QWidget):
    """Widget quản lý thông tin thiết bị"""
    
    device_info_changed = pyqtSignal(dict)  # Emit when device info changes
    
    def __init__(self, device_manager=None, config_manager=None):
        super().__init__()
        self.device_manager = device_manager
        self.config_manager = config_manager
        self.device_data = {}
        self.setup_ui()
        self.load_device_data()
        
        # Connect to device manager signals if available
        if self.device_manager:
            if hasattr(self.device_manager, 'devices_changed'):
                self.device_manager.devices_changed.connect(self.on_devices_changed)
            # Initial refresh of devices
            self.refresh_devices()
        
    def setup_ui(self):
        """Thiết lập giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Phone Manage")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Save To button
        self.save_to_btn = QPushButton("Save To")
        self.save_to_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.save_to_btn.clicked.connect(self.save_to_file)
        header_layout.addWidget(self.save_to_btn)
        
        layout.addLayout(header_layout)
        
        # Table with 5 columns
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["STT", "IP máy", "Phone Number", "Note", "Action"])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        
        # Set fixed widths for STT and Action columns
        self.table.setColumnWidth(0, 60)  # STT column
        self.table.setColumnWidth(4, 100)  # Action column
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                gridline-color: #555555;
                selection-background-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
                height: 30px;
            }
            QTableWidget::item:selected {
                background-color: #404040;
            }
            QLineEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                height: 20px;
                max-height: 20px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #66BB6A;
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #555555;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.table)
        
        # Connect item delegate for custom editing
        self.table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        self.setLayout(layout)
        
    def refresh_devices(self):
        """Refresh danh sách thiết bị using DataManager"""
        try:
            self.table.setRowCount(0)  # Clear existing rows
            
            devices = data_manager.get_devices_with_phone_numbers()
            for i, device in enumerate(devices):
                self.add_device_row(i + 1, device)
                    
        except Exception as e:
            print(f"Error refreshing devices: {e}")
            
    def add_device_row(self, stt, device_info):
        """Thêm một hàng thiết bị vào bảng"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        device_id = device_info['device_id']
        
        # STT
        self.table.setItem(row, 0, QTableWidgetItem(str(stt)))
        
        # IP máy
        self.table.setItem(row, 1, QTableWidgetItem(device_id))
        
        # Phone Number - lấy từ device_info
        phone_item = QTableWidgetItem(device_info.get('phone', ''))
        phone_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 2, phone_item)
        
        # Note - lấy từ device_info
        note_item = QTableWidgetItem(device_info.get('note', ''))
        note_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 3, note_item)
        
        # STT và IP không thể chỉnh sửa
        stt_item = self.table.item(row, 0)
        if stt_item:
            stt_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        
        ip_item = self.table.item(row, 1)
        if ip_item:
            ip_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        
        # Action - nút Save
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(lambda checked, did=device_id: self.save_device_info(did, row))
        self.table.setCellWidget(row, 4, save_btn)
        
        # Set row height để đảm bảo nhất quán
        self.table.setRowHeight(row, 35)
                
    def on_devices_changed(self, devices):
        """Xử lý khi danh sách thiết bị thay đổi"""
        self.refresh_devices()
        
    def on_item_double_clicked(self, item):
        """Xử lý khi double-click vào item để chỉnh sửa"""
        if item.column() in [2, 3]:  # Chỉ cho phép chỉnh sửa cột Phone Number và Note
            # Đảm bảo cell có thể chỉnh sửa
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
            
            # Set row height để đảm bảo input field không bị quá to
            self.table.setRowHeight(item.row(), 35)
            
            # Start editing
            self.table.editItem(item)
        
    def save_device_info(self, device_id, row):
        """Lưu thông tin thiết bị từ bảng"""
        try:
            # Lấy thông tin từ bảng
            phone_item = self.table.item(row, 2)
            note_item = self.table.item(row, 3)
            
            phone = phone_item.text().strip() if phone_item else ""
            note = note_item.text().strip() if note_item else ""
            
            # Validate phone number nếu có
            if phone and not self.validate_phone_number(phone):
                QMessageBox.warning(self, "Warning", "Invalid phone number format. Please enter 9 digits (without 0) or 10 digits (with 0).")
                return
            
            # Extract IP from device_id
            ip = device_id.split(':')[0] if ':' in device_id else device_id
            
            # Save using DataManager
            data_manager.set_phone_mapping(ip, phone)
            data_manager.set_device_note(ip, note)
            
            # Update local device_data to persist changes
            if device_id not in self.device_data:
                self.device_data[device_id] = {}
            self.device_data[device_id]['phone'] = phone
            self.device_data[device_id]['note'] = note
            
            # Emit signal
            self.device_info_changed.emit(self.device_data)
            
            QMessageBox.information(self, "Success", f"Device {device_id} information saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save device info: {str(e)}")
        
    def save_to_file(self):
        """Xuất dữ liệu ra file"""
        if not self.device_data:
            QMessageBox.information(self, "Info", "No data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Device Data", 
            "device_data.json", 
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.device_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
                

        
    def load_device_data(self):
        """Load device data using DataManager"""
        try:
            # Reload data from all sources
            data_manager.reload_data()
            
            # Load device data into local storage
            self.device_data = data_manager.get_device_data()
            
            # Also get phone mapping data
            phone_mapping = data_manager.get_phone_mapping()
            
            # Merge phone mapping into device_data if not already present
            for ip, phone in phone_mapping.items():
                device_key = f"{ip}:5555"
                if device_key not in self.device_data:
                    self.device_data[device_key] = {}
                if 'phone' not in self.device_data[device_key] or not self.device_data[device_key]['phone']:
                    self.device_data[device_key]['phone'] = phone
            
            self.refresh_devices()
        except Exception as e:
            print(f"Error loading device data: {e}")
            
    def save_device_data(self):
        """Save device data using DataManager"""
        # DataManager handles saving automatically
        pass
            
    def validate_phone_number(self, phone):
        """Validate phone number format - supports 9 digits (without 0) or 10 digits (with 0)"""
        import re
        # Remove any spaces or special characters
        clean_phone = re.sub(r'[^0-9]', '', phone)
        
        # Check for 9 digits (without leading 0) or 10 digits (with leading 0)
        if len(clean_phone) == 9:
            # 9 digits without leading 0
            return clean_phone[0] != '0'
        elif len(clean_phone) == 10:
            # 10 digits with leading 0
            return clean_phone[0] == '0'
        else:
            return False
            
    def showEvent(self, event):
        """Được gọi khi widget được hiển thị"""
        super().showEvent(event)
        self.refresh_devices()
            
    def get_device_data(self):
        """Get current device data"""
        return self.device_data.copy()
        
    def set_device_data(self, data):
        """Set device data"""
        self.device_data = data.copy() if data else {}
        self.refresh_devices()