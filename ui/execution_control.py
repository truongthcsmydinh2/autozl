# -*- coding: utf-8 -*-
"""
Execution Control UI
Quản lý thực thi flows với real-time monitoring và logs
"""

import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QGroupBox, QLineEdit, QComboBox, QTextEdit,
    QProgressBar, QFrame, QSplitter, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QCheckBox, QSpinBox, QSlider
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QMutex
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor

class ExecutionWorker(QThread):
    """Worker thread for flow execution"""
    
    # Signals
    execution_started = pyqtSignal(str, str)  # flow_path, device_id
    execution_finished = pyqtSignal(str, str, str)  # flow_path, device_id, result
    execution_error = pyqtSignal(str, str, str)  # flow_path, device_id, error
    log_message = pyqtSignal(str, str, str, str)  # timestamp, level, device_id, message
    progress_updated = pyqtSignal(str, int)  # device_id, progress_percent
    
    def __init__(self, flow_manager, device_manager):
        super().__init__()
        self.flow_manager = flow_manager
        self.device_manager = device_manager
        self.execution_queue = []
        self.is_running = False
        self.mutex = QMutex()
        
    def add_execution(self, flow_path, device_ids, execution_mode="single"):
        """Add execution to queue"""
        self.mutex.lock()
        try:
            for device_id in device_ids:
                self.execution_queue.append({
                    'flow_path': flow_path,
                    'device_id': device_id,
                    'mode': execution_mode
                })
        finally:
            self.mutex.unlock()
            
    def run(self):
        """Execute flows in queue"""
        self.is_running = True
        
        while self.execution_queue and self.is_running:
            self.mutex.lock()
            try:
                if self.execution_queue:
                    execution = self.execution_queue.pop(0)
                else:
                    break
            finally:
                self.mutex.unlock()
                
            self.execute_flow(execution)
            
        self.is_running = False
        
    def execute_flow(self, execution):
        """Execute single flow"""
        flow_path = execution['flow_path']
        device_id = execution['device_id']
        
        try:
            # Emit start signal
            self.execution_started.emit(flow_path, device_id)
            
            # Log start
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S"),
                "INFO",
                device_id,
                f"Starting flow: {os.path.basename(flow_path)}"
            )
            
            # Simulate execution progress
            for i in range(0, 101, 10):
                if not self.is_running:
                    break
                    
                self.progress_updated.emit(device_id, i)
                self.msleep(200)  # Simulate work
                
            # Simulate execution result
            if self.is_running:
                result = "SUCCESS"
                self.execution_finished.emit(flow_path, device_id, result)
                
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S"),
                    "SUCCESS",
                    device_id,
                    f"Flow completed: {result}"
                )
            else:
                self.log_message.emit(
                    datetime.now().strftime("%H:%M:%S"),
                    "WARNING",
                    device_id,
                    "Flow execution cancelled"
                )
                
        except Exception as e:
            self.execution_error.emit(flow_path, device_id, str(e))
            self.log_message.emit(
                datetime.now().strftime("%H:%M:%S"),
                "ERROR",
                device_id,
                f"Flow error: {str(e)}"
            )
            
    def stop_execution(self):
        """Stop execution"""
        self.is_running = False
        self.execution_queue.clear()

class ExecutionStatusWidget(QWidget):
    """Widget hiển thị trạng thái execution"""
    
    def __init__(self):
        super().__init__()
        self.device_progress = {}  # device_id -> progress_bar
        self.device_status = {}   # device_id -> status_label
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📊 Execution Status")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Status table
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(4)
        self.status_table.setHorizontalHeaderLabels(["Device", "Flow", "Progress", "Status"])
        
        # Set column widths
        header = self.status_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        
        self.status_table.setColumnWidth(0, 120)
        self.status_table.setColumnWidth(2, 150)
        self.status_table.setColumnWidth(3, 100)
        
        layout.addWidget(self.status_table)
        
        # Overall progress
        overall_group = QGroupBox("Overall Progress")
        overall_layout = QVBoxLayout()
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background-color: #4a90e2;
                border-radius: 6px;
            }
        """)
        
        self.overall_label = QLabel("Ready")
        self.overall_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        overall_layout.addWidget(self.overall_progress)
        overall_layout.addWidget(self.overall_label)
        overall_group.setLayout(overall_layout)
        
        layout.addWidget(overall_group)
        self.setLayout(layout)
        
    def add_execution(self, device_id, flow_name):
        """Add execution to status table"""
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        
        # Device ID
        self.status_table.setItem(row, 0, QTableWidgetItem(device_id))
        
        # Flow name
        self.status_table.setItem(row, 1, QTableWidgetItem(flow_name))
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196f3;
                border-radius: 3px;
            }
        """)
        self.status_table.setCellWidget(row, 2, progress_bar)
        self.device_progress[device_id] = progress_bar
        
        # Status
        status_item = QTableWidgetItem("Queued")
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_table.setItem(row, 3, status_item)
        self.device_status[device_id] = status_item
        
    def update_progress(self, device_id, progress):
        """Update device progress"""
        if device_id in self.device_progress:
            self.device_progress[device_id].setValue(progress)
            
        # Update overall progress
        self.update_overall_progress()
        
    def update_status(self, device_id, status, color=None):
        """Update device status"""
        if device_id in self.device_status:
            self.device_status[device_id].setText(status)
            
            if color:
                self.device_status[device_id].setForeground(QColor(color))
                
    def update_overall_progress(self):
        """Update overall progress"""
        if not self.device_progress:
            self.overall_progress.setValue(0)
            self.overall_label.setText("Ready")
            return
            
        total_progress = sum(pb.value() for pb in self.device_progress.values())
        avg_progress = total_progress // len(self.device_progress)
        
        self.overall_progress.setValue(avg_progress)
        
        if avg_progress == 100:
            self.overall_label.setText("All executions completed")
        elif avg_progress > 0:
            self.overall_label.setText(f"Executing... {avg_progress}%")
        else:
            self.overall_label.setText("Starting...")
            
    def clear_status(self):
        """Clear all status"""
        self.status_table.setRowCount(0)
        self.device_progress.clear()
        self.device_status.clear()
        self.overall_progress.setValue(0)
        self.overall_label.setText("Ready")

class LogsViewerWidget(QWidget):
    """Widget hiển thị logs với filtering"""
    
    def __init__(self):
        super().__init__()
        self.logs = []  # Store all logs
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header with filters
        header_layout = QHBoxLayout()
        
        header_label = QLabel("📋 Execution Logs")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        # Log level filter
        self.level_filter = QComboBox()
        self.level_filter.addItems(["All Levels", "INFO", "SUCCESS", "WARNING", "ERROR"])
        self.level_filter.currentTextChanged.connect(self.filter_logs)
        
        # Device filter
        self.device_filter = QComboBox()
        self.device_filter.addItem("All Devices")
        self.device_filter.currentTextChanged.connect(self.filter_logs)
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search logs...")
        self.search_input.textChanged.connect(self.filter_logs)
        
        # Clear button
        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_logs)
        
        # Auto-scroll checkbox
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Level:"))
        header_layout.addWidget(self.level_filter)
        header_layout.addWidget(QLabel("Device:"))
        header_layout.addWidget(self.device_filter)
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.auto_scroll_cb)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setFont(QFont("Consolas", 10))
        self.logs_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """)
        
        layout.addWidget(self.logs_display)
        self.setLayout(layout)
        
    def add_log(self, timestamp, level, device_id, message):
        """Add log entry"""
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'device_id': device_id,
            'message': message
        }
        
        self.logs.append(log_entry)
        
        # Add device to filter if not exists
        if device_id and device_id != "All Devices":
            for i in range(self.device_filter.count()):
                if self.device_filter.itemText(i) == device_id:
                    break
            else:
                self.device_filter.addItem(device_id)
                
        # Update display
        self.filter_logs()
        
    def filter_logs(self):
        """Filter and display logs"""
        level_filter = self.level_filter.currentText()
        device_filter = self.device_filter.currentText()
        search_text = self.search_input.text().lower()
        
        filtered_logs = []
        
        for log in self.logs:
            # Level filter
            if level_filter != "All Levels" and log['level'] != level_filter:
                continue
                
            # Device filter
            if device_filter != "All Devices" and log['device_id'] != device_filter:
                continue
                
            # Search filter
            if search_text and search_text not in log['message'].lower():
                continue
                
            filtered_logs.append(log)
            
        # Display filtered logs
        self.display_logs(filtered_logs)
        
    def display_logs(self, logs):
        """Display logs in text widget"""
        self.logs_display.clear()
        
        for log in logs:
            # Color based on level
            level_colors = {
                'INFO': '#ffffff',
                'SUCCESS': '#4caf50',
                'WARNING': '#ff9800',
                'ERROR': '#f44336'
            }
            
            color = level_colors.get(log['level'], '#ffffff')
            
            # Format log line
            log_line = f"<span style='color: #888'>[{log['timestamp']}]</span> "
            log_line += f"<span style='color: {color}; font-weight: bold'>[{log['level']}]</span> "
            log_line += f"<span style='color: #64b5f6'>[{log['device_id']}]</span> "
            log_line += f"<span style='color: #ffffff'>{log['message']}</span><br>"
            
            self.logs_display.insertHtml(log_line)
            
        # Auto-scroll to bottom
        if self.auto_scroll_cb.isChecked():
            cursor = self.logs_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.logs_display.setTextCursor(cursor)
            
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
        self.logs_display.clear()
        
        # Reset device filter
        self.device_filter.clear()
        self.device_filter.addItem("All Devices")

class ExecutionControlWidget(QWidget):
    """Main execution control widget"""
    
    def __init__(self, flow_manager=None, device_manager=None):
        super().__init__()
        self.flow_manager = flow_manager
        self.device_manager = device_manager
        self.execution_worker = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Control panel
        control_group = QGroupBox("🎮 Execution Control")
        control_layout = QGridLayout()
        
        # Flow selection
        control_layout.addWidget(QLabel("Flow:"), 0, 0)
        self.flow_combo = QComboBox()
        self.flow_combo.setPlaceholderText("Select flow to execute...")
        control_layout.addWidget(self.flow_combo, 0, 1, 1, 2)
        
        self.browse_flow_btn = QPushButton("📁 Browse")
        control_layout.addWidget(self.browse_flow_btn, 0, 3)
        
        # Device selection
        control_layout.addWidget(QLabel("Devices:"), 1, 0)
        self.device_list = QListWidget()
        self.device_list.setMaximumHeight(100)
        self.device_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        control_layout.addWidget(self.device_list, 1, 1, 2, 2)
        
        self.refresh_devices_btn = QPushButton("🔄 Refresh")
        control_layout.addWidget(self.refresh_devices_btn, 1, 3)
        
        self.select_all_btn = QPushButton("✅ Select All")
        control_layout.addWidget(self.select_all_btn, 2, 3)
        
        # Execution mode
        control_layout.addWidget(QLabel("Mode:"), 3, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Sequential", "Parallel", "Single Device"])
        control_layout.addWidget(self.mode_combo, 3, 1)
        
        # Delay between executions
        control_layout.addWidget(QLabel("Delay (s):"), 3, 2)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 60)
        self.delay_spin.setValue(1)
        control_layout.addWidget(self.delay_spin, 3, 3)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️ Start Execution")
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Stop Execution")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.stop_btn.setEnabled(False)
        
        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.pause_btn.setEnabled(False)
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        # Status and logs tabs
        tabs = QTabWidget()
        
        # Execution status tab
        self.execution_status = ExecutionStatusWidget()
        tabs.addTab(self.execution_status, "📊 Status")
        
        # Logs tab
        self.logs_viewer = LogsViewerWidget()
        tabs.addTab(self.logs_viewer, "📋 Logs")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Buttons
        self.browse_flow_btn.clicked.connect(self.browse_flow)
        self.refresh_devices_btn.clicked.connect(self.refresh_devices)
        self.select_all_btn.clicked.connect(self.select_all_devices)
        self.start_btn.clicked.connect(self.start_execution)
        self.stop_btn.clicked.connect(self.stop_execution)
        self.pause_btn.clicked.connect(self.pause_execution)
        
        # Load initial data
        self.refresh_flows()
        self.refresh_devices()
        
    def refresh_flows(self):
        """Refresh available flows"""
        self.flow_combo.clear()
        
        flows_dir = "flows"
        if os.path.exists(flows_dir):
            for file in os.listdir(flows_dir):
                if file.endswith(('.py', '.json', '.flow')):
                    self.flow_combo.addItem(file, os.path.join(flows_dir, file))
                    
    def browse_flow(self):
        """Browse for flow file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Flow File", "flows",
            "Flow Files (*.py *.json *.flow);;All Files (*)"
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            # Add to combo if not exists
            for i in range(self.flow_combo.count()):
                if self.flow_combo.itemData(i) == file_path:
                    self.flow_combo.setCurrentIndex(i)
                    return
                    
            self.flow_combo.addItem(filename, file_path)
            self.flow_combo.setCurrentIndex(self.flow_combo.count() - 1)
            
    def refresh_devices(self):
        """Refresh available devices"""
        self.device_list.clear()
        
        if self.device_manager:
            try:
                devices = self.device_manager.get_devices()
                if isinstance(devices, list):
                    for device in devices:
                        if isinstance(device, dict):
                            device_id = device.get('id', 'Unknown')
                            status = device.get('status', 'unknown')
                            item_text = f"📱 {device_id} ({status})"
                            
                            item = QListWidgetItem(item_text)
                            item.setData(Qt.ItemDataRole.UserRole, device_id)
                            
                            # Enable only connected devices
                            if status == "device":
                                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                            else:
                                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                                
                            self.device_list.addItem(item)
                elif isinstance(devices, dict):
                    for device_id, device_info in devices.items():
                        status = device_info.get('status', 'unknown')
                        item_text = f"📱 {device_id} ({status})"
                        
                        item = QListWidgetItem(item_text)
                        item.setData(Qt.ItemDataRole.UserRole, device_id)
                        
                        # Enable only connected devices
                        if status == "device":
                            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
                        else:
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                            
                        self.device_list.addItem(item)
                    
            except Exception as e:
                print(f"Error refreshing devices: {e}")
                
    def select_all_devices(self):
        """Select all available devices"""
        for i in range(self.device_list.count()):
            item = self.device_list.item(i)
            if item.flags() & Qt.ItemFlag.ItemIsEnabled:
                item.setSelected(True)
                
    def start_execution(self):
        """Start flow execution"""
        # Validate inputs
        flow_path = self.flow_combo.currentData()
        if not flow_path:
            QMessageBox.warning(self, "Warning", "Please select a flow to execute")
            return
            
        selected_devices = []
        for item in self.device_list.selectedItems():
            device_id = item.data(Qt.ItemDataRole.UserRole)
            selected_devices.append(device_id)
            
        if not selected_devices:
            QMessageBox.warning(self, "Warning", "Please select at least one device")
            return
            
        # Clear previous status
        self.execution_status.clear_status()
        
        # Add executions to status
        flow_name = os.path.basename(flow_path)
        for device_id in selected_devices:
            self.execution_status.add_execution(device_id, flow_name)
            
        # Create and start worker
        self.execution_worker = ExecutionWorker(self.flow_manager, self.device_manager)
        
        # Connect worker signals
        self.execution_worker.execution_started.connect(self.on_execution_started)
        self.execution_worker.execution_finished.connect(self.on_execution_finished)
        self.execution_worker.execution_error.connect(self.on_execution_error)
        self.execution_worker.log_message.connect(self.logs_viewer.add_log)
        self.execution_worker.progress_updated.connect(self.execution_status.update_progress)
        
        # Add executions to worker
        execution_mode = self.mode_combo.currentText().lower()
        self.execution_worker.add_execution(flow_path, selected_devices, execution_mode)
        
        # Start worker
        self.execution_worker.start()
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.pause_btn.setEnabled(True)
        
        # Log start
        self.logs_viewer.add_log(
            datetime.now().strftime("%H:%M:%S"),
            "INFO",
            "SYSTEM",
            f"Started execution of {flow_name} on {len(selected_devices)} device(s)"
        )
        
    def stop_execution(self):
        """Stop flow execution"""
        if self.execution_worker:
            self.execution_worker.stop_execution()
            self.execution_worker.wait(3000)  # Wait up to 3 seconds
            
        # Update UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        
        # Log stop
        self.logs_viewer.add_log(
            datetime.now().strftime("%H:%M:%S"),
            "WARNING",
            "SYSTEM",
            "Execution stopped by user"
        )
        
    def pause_execution(self):
        """Pause/resume execution"""
        # This would implement pause/resume functionality
        QMessageBox.information(self, "Info", "Pause/Resume functionality will be implemented")
        
    def on_execution_started(self, flow_path, device_id):
        """Handle execution started"""
        self.execution_status.update_status(device_id, "Running", "blue")
        
    def on_execution_finished(self, flow_path, device_id, result):
        """Handle execution finished"""
        self.execution_status.update_progress(device_id, 100)
        
        if result == "SUCCESS":
            self.execution_status.update_status(device_id, "Success", "green")
        else:
            self.execution_status.update_status(device_id, "Failed", "red")
            
        # Check if all executions are done
        self.check_all_executions_done()
        
    def on_execution_error(self, flow_path, device_id, error):
        """Handle execution error"""
        self.execution_status.update_status(device_id, "Error", "red")
        self.check_all_executions_done()
        
    def check_all_executions_done(self):
        """Check if all executions are completed"""
        if self.execution_worker and not self.execution_worker.isRunning():
            # All done, update UI
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            
            self.logs_viewer.add_log(
                datetime.now().strftime("%H:%M:%S"),
                "INFO",
                "SYSTEM",
                "All executions completed"
            )