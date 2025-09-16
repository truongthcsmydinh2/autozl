from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QPlainTextEdit, QLabel, QComboBox, QCheckBox,
    QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette
from .log_worker import LogWorker
from datetime import datetime

class TerminalLogTab(QWidget):
    """Terminal Log tab widget for displaying real-time logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_worker = None
        self.auto_scroll_enabled = True
        self.max_lines = 1000  # Maximum number of lines to keep
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Control panel
        control_group = QGroupBox("Log Controls")
        control_layout = QHBoxLayout(control_group)
        
        # Device selection
        self.device_label = QLabel("Device:")
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(150)
        self.device_combo.addItem("Select Device...")
        
        # Log type selection
        self.log_type_label = QLabel("Log Type:")
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(["ADB Logcat", "Internal Logs", "Both"])
        self.log_type_combo.setCurrentText("Both")
        
        # Auto-scroll checkbox
        self.auto_scroll_checkbox = QCheckBox("Auto Scroll")
        self.auto_scroll_checkbox.setChecked(True)
        
        # Control buttons
        self.start_button = QPushButton("Start Logging")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.stop_button = QPushButton("Stop Logging")
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.clear_button = QPushButton("Clear Logs")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        # Add controls to layout
        control_layout.addWidget(self.device_label)
        control_layout.addWidget(self.device_combo)
        control_layout.addWidget(self.log_type_label)
        control_layout.addWidget(self.log_type_combo)
        control_layout.addWidget(self.auto_scroll_checkbox)
        control_layout.addStretch()
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.clear_button)
        
        # Log display area
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 4px;
            }
        """)
        
        # Log text area
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(self.max_lines)
        
        # Set monospace font for better log readability
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.log_text.setFont(font)
        
        # Set dark theme for log area
        self.log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #264f78;
            }
        """)
        
        log_layout.addWidget(self.status_label)
        log_layout.addWidget(self.log_text)
        
        # Add groups to main layout
        layout.addWidget(control_group)
        layout.addWidget(log_group, 1)  # Give log area more space
        
        # Initialize log worker
        self.log_worker = LogWorker()
        
    def setup_connections(self):
        """Setup signal connections"""
        # Button connections
        self.start_button.clicked.connect(self.start_logging)
        self.stop_button.clicked.connect(self.stop_logging)
        self.clear_button.clicked.connect(self.clear_logs)
        
        # Auto-scroll checkbox
        self.auto_scroll_checkbox.toggled.connect(self.toggle_auto_scroll)
        
        # Log worker connections
        if self.log_worker:
            self.log_worker.log_received.connect(self.append_log)
            self.log_worker.error_occurred.connect(self.handle_error)
            
    def start_logging(self):
        """Start logging process"""
        if not self.log_worker:
            self.log_worker = LogWorker()
            self.setup_connections()
            
        # Get selected device
        device_text = self.device_combo.currentText()
        if device_text == "Select Device...":
            self.append_log("[ERROR] Please select a device first", "error")
            return
            
        # Get log type
        log_type = self.log_type_combo.currentText()
        
        try:
            # Update UI state
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.status_label.setText("Status: Logging started")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 12px;
                    padding: 4px;
                    font-weight: bold;
                }
            """)
            
            # Start appropriate logging
            if log_type in ["ADB Logcat", "Both"]:
                self.log_worker.start_adb_logcat(device_text)
                
            if log_type in ["Internal Logs", "Both"]:
                self.log_worker.start_internal_logging()
                
            # Start the worker thread
            if not self.log_worker.isRunning():
                self.log_worker.start()
                
            self.append_log(f"[SYSTEM] Logging started for {log_type} on device: {device_text}", "system")
            
        except Exception as e:
            self.handle_error(f"Failed to start logging: {str(e)}")
            
    def stop_logging(self):
        """Stop logging process"""
        if self.log_worker:
            self.log_worker.stop()
            
        # Update UI state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Logging stopped")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-size: 12px;
                padding: 4px;
                font-weight: bold;
            }
        """)
        
        self.append_log("[SYSTEM] Logging stopped", "system")
        
    def clear_logs(self):
        """Clear all logs from display"""
        self.log_text.clear()
        self.append_log("[SYSTEM] Logs cleared", "system")
        
    def toggle_auto_scroll(self, enabled):
        """Toggle auto-scroll functionality"""
        self.auto_scroll_enabled = enabled
        
    def append_log(self, message, level="info"):
        """Append log message to display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on log level
        color_map = {
            "error": "#ff6b6b",
            "warning": "#ffa726", 
            "info": "#ffffff",
            "system": "#4fc3f7",
            "adb": "#81c784",
            "internal": "#ffb74d"
        }
        
        color = color_map.get(level.lower(), "#ffffff")
        
        # Format message with timestamp and color
        formatted_message = f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        
        # Append to text area
        self.log_text.appendHtml(formatted_message)
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_enabled:
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            
    def handle_error(self, error_message):
        """Handle error messages"""
        self.append_log(f"[ERROR] {error_message}", "error")
        
        # Update status
        self.status_label.setText("Status: Error occurred")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-size: 12px;
                padding: 4px;
                font-weight: bold;
            }
        """)
        
    def update_device_list(self, devices):
        """Update the device list in combo box"""
        current_text = self.device_combo.currentText()
        self.device_combo.clear()
        self.device_combo.addItem("Select Device...")
        
        for device in devices:
            self.device_combo.addItem(device)
            
        # Restore previous selection if still available
        if current_text in devices:
            self.device_combo.setCurrentText(current_text)
            
    def closeEvent(self, event):
        """Handle widget close event"""
        if self.log_worker:
            self.log_worker.stop()
        event.accept()
        
    def __del__(self):
        """Cleanup when widget is destroyed"""
        if self.log_worker:
            self.log_worker.stop()