from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QScrollArea, QTextEdit, QLineEdit, QProgressBar,
    QMessageBox, QGroupBox, QSplitter, QSpacerItem, QSizePolicy,
    QFrame, QTabWidget, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from utils.data_manager import data_manager
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AutomationWorker(QThread):
    """Worker thread for automation to prevent UI freezing"""
    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    # New signals for status table
    message_status_updated = pyqtSignal(str, str, str, int)  # device_id, message, status, countdown
    device_status_updated = pyqtSignal(str, str)  # device_id, status
    
    def __init__(self, automation_data):
        super().__init__()
        self.automation_data = automation_data
        self.should_stop = False
        self._stop_event = None
    
    def run(self):
        try:
            # Import and run automation
            from core1 import run_zalo_automation
            import threading
            
            # Create stop event for core1.py
            self._stop_event = threading.Event()
            
            # Add stop_event to automation_data
            self.automation_data['stop_event'] = self._stop_event
            
            # Create status callback for real-time updates
            def status_callback(signal_type, *args):
                if not self.should_stop:
                    if signal_type == 'message_status_updated':
                        # Format từ core1.py: status_callback('message_status_updated', {data})
                        if len(args) > 0 and isinstance(args[0], dict):
                            data = args[0]
                            device_ip = data.get('device_ip', '')
                            content = data.get('content', '')
                            status = data.get('status', '')
                            delay_time = data.get('delay_time', 0)
                            self.message_status_updated.emit(device_ip, content, status, int(delay_time))
                    elif signal_type == 'device_status':
                        # Format từ core1.py: status_callback('device_status', device_ip, status, extra)
                        if len(args) >= 2:
                            device_ip = args[0]
                            status = args[1]
                            self.device_status_updated.emit(device_ip, status)
            
            results = run_zalo_automation(
                self.automation_data['device_pairs'],
                self.automation_data['conversations'],
                self.automation_data['phone_mapping'],
                progress_callback=self.progress_updated.emit,
                status_callback=status_callback,
                stop_event=self._stop_event
            )
            
            if not self.should_stop:
                self.finished.emit(results)
            else:
                self.finished.emit({})
                
        except Exception as e:
            if not self.should_stop:
                self.error_occurred.emit(str(e))
    
    def stop(self):
        """Stop automation gracefully"""
        self.should_stop = True
        
        # Signal core1.py to stop
        if self._stop_event:
            self._stop_event.set()
        
        # Give it a moment to stop gracefully
        if self.isRunning():
            self.wait(2000)  # Wait up to 2 seconds
            
        # Force terminate if still running
        if self.isRunning():
            self.terminate()
            self.wait(1000)  # Wait for termination

class DeviceCheckBox(QCheckBox):
    """Custom checkbox for device selection with enhanced styling"""
    def __init__(self, device_id, phone_number):
        super().__init__()
        self.device_id = device_id
        self.phone_number = phone_number
        
        # Create display text
        display_text = f"📱 {device_id}"
        if phone_number and phone_number != "Chưa có số":
            display_text += f" ({phone_number})"
        
        self.setText(display_text)
        self.setStyleSheet("""
            QCheckBox {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                spacing: 10px;
                background-color: #34495e;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                margin: 3px;
            }
            QCheckBox:hover {
                background-color: #3498db;
                border-color: #2980b9;
            }
            QCheckBox:checked {
                background-color: #27ae60;
                border-color: #229954;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #bdc3c7;
                background-color: #ecf0f1;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border-color: #27ae60;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #229954;
            }
        """)

class ZaloAutomationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.device_checkboxes = []
        self.conversation_texts = []
        self.device_pairs = []
        self.all_devices = []
        self.automation_worker = None
        
        # Status table data
        self.status_table_data = {}
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        # Initialize UI and load devices
        self.init_ui()
        self.load_devices()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🤖 Zalo Automation Tool")
        self.setMinimumSize(1200, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("🤖 Zalo Automation Tool")
        title_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                font-size: 24px;
                padding: 15px;
                background-color: #34495e;
                border-radius: 12px;
                border: 3px solid #2c3e50;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
            QTabBar::tab {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #5dade2;
            }
        """)
        
        # Create main automation tab
        self.create_main_tab()
        
        # Create status tab
        self.create_status_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status label
        self.status_label = QLabel("⚡ Sẵn sàng")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                color: #ecf0f1;
                background-color: #2c3e50;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
    
    def create_main_tab(self):
        """Create main automation tab"""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Create splitter for device selection and conversation input
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Device selection section
        device_widget = self.create_device_section()
        splitter.addWidget(device_widget)
        
        # Conversation input section
        conversation_widget = self.create_conversation_section()
        splitter.addWidget(conversation_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        # Pair devices button
        self.pair_btn = QPushButton("🔗 Ghép Cặp Devices")
        self.pair_btn.clicked.connect(self.pair_devices)
        self.pair_btn.setFixedHeight(45)
        self.pair_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        control_layout.addWidget(self.pair_btn)
        
        # Apply conversation button
        self.apply_btn = QPushButton("📝 Apply Conversation")
        self.apply_btn.clicked.connect(self.apply_conversation)
        self.apply_btn.setFixedHeight(45)
        self.apply_btn.setStyleSheet(self.get_button_style("#9b59b6", "#8e44ad"))
        control_layout.addWidget(self.apply_btn)
        
        # Start automation button
        self.start_btn = QPushButton("🚀 Bắt Đầu Automation")
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setFixedHeight(45)
        self.start_btn.setStyleSheet(self.get_button_style("#27ae60", "#229954"))
        control_layout.addWidget(self.start_btn)
        
        # Stop automation button
        self.stop_btn = QPushButton("⏹️ Dừng Automation")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedHeight(45)
        self.stop_btn.setStyleSheet(self.get_button_style("#e74c3c", "#c0392b"))
        control_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(control_layout)
        
        self.tab_widget.addTab(main_widget, "🤖 Automation")
    
    def create_device_section(self):
        """Create device selection section"""
        device_widget = QWidget()
        device_layout = QVBoxLayout(device_widget)
        device_layout.setContentsMargins(10, 10, 10, 10)
        device_layout.setSpacing(10)
        
        # Device selection title
        device_title = QLabel("📱 Chọn Devices")
        device_title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        device_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        device_layout.addWidget(device_title)
        
        # Device selection buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("✅ Chọn Tất Cả")
        select_all_btn.clicked.connect(self.select_all_devices)
        select_all_btn.setStyleSheet(self.get_compact_button_style("#27ae60", "#229954"))
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("❌ Bỏ Chọn Tất Cả")
        deselect_all_btn.clicked.connect(self.deselect_all_devices)
        deselect_all_btn.setStyleSheet(self.get_compact_button_style("#e74c3c", "#c0392b"))
        button_layout.addWidget(deselect_all_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_devices)
        refresh_btn.setStyleSheet(self.get_compact_button_style("#f39c12", "#e67e22"))
        button_layout.addWidget(refresh_btn)
        
        device_layout.addLayout(button_layout)
        
        # Device list scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
        """)
        
        # Device list widget
        self.device_list_widget = QWidget()
        self.device_list_layout = QVBoxLayout(self.device_list_widget)
        self.device_list_layout.setContentsMargins(10, 10, 10, 10)
        self.device_list_layout.setSpacing(5)
        
        scroll_area.setWidget(self.device_list_widget)
        device_layout.addWidget(scroll_area)
        
        return device_widget
    
    def create_conversation_section(self):
        """Create conversation input section"""
        conversation_widget = QWidget()
        conversation_layout = QVBoxLayout(conversation_widget)
        conversation_layout.setContentsMargins(10, 10, 10, 10)
        conversation_layout.setSpacing(10)
        
        # Conversation title
        conversation_title = QLabel("💬 Nhập Hội Thoại")
        conversation_title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        conversation_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        conversation_layout.addWidget(conversation_title)
        
        # Conversation input area
        conversation_scroll = QScrollArea()
        conversation_scroll.setWidgetResizable(True)
        conversation_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
        """)
        
        # Conversation input widget
        self.conversation_input_widget = QWidget()
        self.conversation_input_layout = QVBoxLayout(self.conversation_input_widget)
        self.conversation_input_layout.setContentsMargins(10, 10, 10, 10)
        self.conversation_input_layout.setSpacing(10)
        
        # Add initial conversation inputs
        for i in range(3):
            self.add_conversation_input(i + 1)
        
        # Add conversation button
        add_conversation_btn = QPushButton("➕ Thêm Hội Thoại")
        add_conversation_btn.clicked.connect(self.add_conversation_input)
        add_conversation_btn.setStyleSheet(self.get_compact_button_style("#3498db", "#2980b9"))
        self.conversation_input_layout.addWidget(add_conversation_btn)
        
        conversation_scroll.setWidget(self.conversation_input_widget)
        conversation_layout.addWidget(conversation_scroll)
        
        return conversation_widget
    
    def add_conversation_input(self, group_id=None):
        """Add a new conversation input"""
        if group_id is None:
            group_id = len(self.conversation_texts) + 1
        
        # Create group box for conversation
        group_box = QGroupBox(f"Hội thoại {group_id}")
        group_box.setStyleSheet("""
            QGroupBox {
                color: #ecf0f1;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
        """)
        
        group_layout = QVBoxLayout(group_box)
        
        # Text input
        text_edit = QTextEdit()
        text_edit.setPlaceholderText(f"Nhập nội dung hội thoại {group_id}...")
        text_edit.setMaximumHeight(120)
        text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        group_layout.addWidget(text_edit)
        
        # Remove button
        if len(self.conversation_texts) > 0:  # Don't add remove button for first conversation
            remove_btn = QPushButton("🗑️ Xóa")
            remove_btn.clicked.connect(lambda: self.remove_conversation_input(group_box, text_edit))
            remove_btn.setStyleSheet(self.get_compact_button_style("#e74c3c", "#c0392b"))
            group_layout.addWidget(remove_btn)
        
        # Insert before the "Add" button
        insert_index = self.conversation_input_layout.count() - 1
        self.conversation_input_layout.insertWidget(insert_index, group_box)
        
        self.conversation_texts.append(text_edit)
    
    def remove_conversation_input(self, group_box, text_edit):
        """Remove a conversation input"""
        if len(self.conversation_texts) > 1:  # Keep at least one conversation
            self.conversation_texts.remove(text_edit)
            group_box.setParent(None)
            group_box.deleteLater()
    
    def get_button_style(self, bg_color, hover_color):
        """Get button style with specified colors"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                transform: translateY(2px);
            }}
            QPushButton:disabled {{
                background-color: #7f8c8d;
                color: #bdc3c7;
            }}
        """
    
    def get_compact_button_style(self, bg_color, hover_color):
        """Get compact button style with specified colors"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                padding: 8px 15px;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
        """
    
    def load_devices(self):
        """Load available devices"""
        try:
            # Clear existing checkboxes
            for checkbox in self.device_checkboxes:
                checkbox.setParent(None)
                checkbox.deleteLater()
            self.device_checkboxes.clear()
            
            # Get devices from data manager
            devices = data_manager.get_devices_with_phone_numbers()
            phone_mapping = data_manager.get_phone_mapping()
            
            self.all_devices = devices
            
            if not devices:
                no_device_label = QLabel("❌ Không tìm thấy device nào")
                no_device_label.setStyleSheet("""
                    QLabel {
                        color: #e74c3c;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 20px;
                        text-align: center;
                    }
                """)
                no_device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.device_list_layout.addWidget(no_device_label)
                return
            
            # Create checkboxes for each device
            for device in devices:
                device_id = device.get('device_id', 'Unknown')
                phone_number = phone_mapping.get(device_id, "Chưa có số")
                
                checkbox = DeviceCheckBox(device_id, phone_number)
                self.device_checkboxes.append(checkbox)
                self.device_list_layout.addWidget(checkbox)
            
            # Add spacer
            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.device_list_layout.addItem(spacer)
            
            self.status_label.setText(f"📱 Đã tải {len(devices)} devices")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải devices: {str(e)}")
    
    def select_all_devices(self):
        """Select all devices"""
        for checkbox in self.device_checkboxes:
            checkbox.setChecked(True)
    
    def deselect_all_devices(self):
        """Deselect all devices"""
        for checkbox in self.device_checkboxes:
            checkbox.setChecked(False)
    
    def apply_conversation(self):
        """Apply conversation data"""
        try:
            # Get conversation data from text inputs
            conversations = []
            for i, text_edit in enumerate(self.conversation_texts):
                conversation = text_edit.toPlainText().strip()
                if conversation:
                    conversations.append({
                        'group_id': i + 1,
                        'content': conversation
                    })
            
            if not conversations:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ít nhất 1 đoạn hội thoại!")
                return
            
            # Parse conversations
            parsed_conversations = self.parse_conversations(conversations)
            
            # Save conversation data
            self.save_conversation_data(parsed_conversations)
            
            QMessageBox.information(self, "Thành công", 
                f"Đã apply {len(parsed_conversations)} hội thoại thành công!")
            
            self.status_label.setText(f"✅ Đã apply {len(parsed_conversations)} hội thoại")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể apply conversation: {str(e)}")
    
    def parse_conversations(self, conversations):
        """Parse conversation data"""
        parsed = []
        
        for conv in conversations:
            content = conv['content']
            group_id = conv['group_id']
            
            # Split by lines and process each line
            lines = content.split('\n')
            messages = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Simple parsing - each line is a message
                    messages.append({
                        'content': line,
                        'delay': 2  # Default 2 second delay
                    })
            
            if messages:
                parsed.append({
                    'group_id': group_id,
                    'messages': messages
                })
        
        return parsed
    
    def save_conversation_data(self, conversations):
        """Save conversation data to file"""
        try:
            import json
            
            # Save to conversations.json
            with open('conversations.json', 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
            
            print(f"Đã lưu {len(conversations)} hội thoại vào conversations.json")
            
        except Exception as e:
            raise Exception(f"Không thể lưu conversation data: {str(e)}")
    
    def create_status_tab(self):
        """Create real-time status monitoring tab"""
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(15, 15, 15, 15)
        status_layout.setSpacing(15)
        
        # Status title
        status_title = QLabel("📊 Trạng Thái Real-time")
        status_title.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                font-size: 18px;
                padding: 15px;
                background-color: #34495e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        
        # Control buttons for status tab
        status_control_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Xóa Bảng")
        clear_btn.clicked.connect(self.clear_status_table)
        clear_btn.setStyleSheet(self.get_compact_button_style("#e74c3c", "#c0392b"))
        status_control_layout.addWidget(clear_btn)
        
        status_control_layout.addStretch()
        status_layout.addLayout(status_control_layout)
        
        # Status table
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(5)
        self.status_table.setHorizontalHeaderLabels(["Device", "Message", "Status", "Countdown", "Time"])
        
        # Set table style
        self.status_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                gridline-color: #34495e;
                color: #ecf0f1;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #34495e;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 10px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
        """)
        
        # Set column widths
        header = self.status_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 150)  # Device
        header.resizeSection(1, 300)  # Message
        header.resizeSection(2, 100)  # Status
        header.resizeSection(3, 100)  # Countdown
        
        status_layout.addWidget(self.status_table)
        
        self.tab_widget.addTab(status_widget, "📊 Status")
    
    def clear_status_table(self):
        """Clear status table"""
        self.status_table.setRowCount(0)
        self.status_table_data.clear()
    
    def update_message_status(self, device_id, message, status, countdown):
        """Update message status in real-time table"""
        try:
            from datetime import datetime
            
            # Create unique key for this message
            message_key = f"{device_id}_{message[:50]}"
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Check if this message already exists in table
            if message_key in self.status_table_data:
                row = self.status_table_data[message_key]['row']
                # Update existing row
                self.status_table.setItem(row, 2, QTableWidgetItem(status))
                self.status_table.setItem(row, 3, QTableWidgetItem(str(countdown)))
                self.status_table.setItem(row, 4, QTableWidgetItem(current_time))
            else:
                # Add new row
                row_count = self.status_table.rowCount()
                self.status_table.insertRow(row_count)
                
                self.status_table.setItem(row_count, 0, QTableWidgetItem(device_id))
                self.status_table.setItem(row_count, 1, QTableWidgetItem(message[:100]))  # Truncate long messages
                self.status_table.setItem(row_count, 2, QTableWidgetItem(status))
                self.status_table.setItem(row_count, 3, QTableWidgetItem(str(countdown)))
                self.status_table.setItem(row_count, 4, QTableWidgetItem(current_time))
                
                # Store row reference
                self.status_table_data[message_key] = {
                    'row': row_count,
                    'countdown': countdown
                }
            
            # Color code status
            status_item = self.status_table.item(self.status_table_data[message_key]['row'], 2)
            if status == "Sending":
                status_item.setBackground(Qt.GlobalColor.yellow)
            elif status == "Sent":
                status_item.setBackground(Qt.GlobalColor.green)
            elif status == "Error":
                status_item.setBackground(Qt.GlobalColor.red)
            
            # Auto scroll to bottom
            self.status_table.scrollToBottom()
            
        except Exception as e:
            print(f"Error updating message status: {e}")
    
    def update_countdown(self):
        """Update countdown timers in status table"""
        try:
            for message_key, data in self.status_table_data.items():
                if data['countdown'] > 0:
                    data['countdown'] -= 1
                    row = data['row']
                    if row < self.status_table.rowCount():
                        self.status_table.setItem(row, 3, QTableWidgetItem(str(data['countdown'])))
        except Exception as e:
            print(f"Error updating countdown: {e}")
    
    def pair_devices(self):
        """Pair selected devices"""
        try:
            # Get selected devices
            selected_devices = []
            for checkbox in self.device_checkboxes:
                if checkbox.isChecked():
                    # Create device dict with both 'ip' and 'device_id' for compatibility
                    device_id = checkbox.device_id
                    ip = device_id.split(':')[0] if ':' in device_id else device_id
                    selected_devices.append({
                        'device_id': device_id,
                        'ip': ip,  # Add ip field for core1.py compatibility
                        'phone_number': checkbox.phone_number
                    })
            
            if len(selected_devices) < 2:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 2 devices để ghép cặp!")
                return
            
            # Create device pairs as tuples instead of dicts
            self.device_pairs = []
            for i in range(0, len(selected_devices), 2):
                if i + 1 < len(selected_devices):
                    # Create tuple (device1, device2) instead of dict
                    pair = (selected_devices[i], selected_devices[i + 1])
                    self.device_pairs.append(pair)
            
            # Handle odd number of devices
            if len(selected_devices) % 2 == 1:
                # Add the last device as a single device pair with None as device2
                single_pair = (selected_devices[-1], None)
                self.device_pairs.append(single_pair)
            
            QMessageBox.information(self, "Thành công", 
                f"Đã ghép {len(self.device_pairs)} cặp devices thành công!")
            
            self.status_label.setText(f"🔗 Đã ghép {len(self.device_pairs)} cặp devices")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể ghép cặp devices: {str(e)}")
    
    def start_automation(self):
        """Start automation process"""
        try:
            # Validate inputs
            if not self.device_pairs:
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng ghép cặp devices trước!")
                return
            
            # Check if conversations.json exists
            if not os.path.exists('conversations.json'):
                QMessageBox.warning(self, "Cảnh báo", "Vui lòng apply conversation trước!")
                return
            
            # Load conversations
            import json
            with open('conversations.json', 'r', encoding='utf-8') as f:
                conversations = json.load(f)
            
            if not conversations:
                QMessageBox.warning(self, "Cảnh báo", "Không có conversation nào để thực hiện!")
                return
            
            # Get phone mapping
            phone_mapping = data_manager.get_phone_mapping()
            
            # Prepare automation data
            automation_data = {
                'device_pairs': self.device_pairs,
                'conversations': conversations,
                'phone_mapping': phone_mapping
            }
            
            # Start automation worker
            self.automation_worker = AutomationWorker(automation_data)
            self.automation_worker.progress_updated.connect(self.update_progress)
            self.automation_worker.finished.connect(self.automation_finished)
            self.automation_worker.error_occurred.connect(self.on_automation_error)
            
            # Connect status signals
            self.automation_worker.message_status_updated.connect(self.update_message_status)
            self.automation_worker.device_status_updated.connect(self.update_device_status)
            
            self.automation_worker.start()
            
            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.status_label.setText("🚀 Đang chạy automation...")
            
            # Start countdown timer
            self.countdown_timer.start(1000)  # Update every second
            
            QMessageBox.information(self, "Thành công", "Đã bắt đầu automation!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể bắt đầu automation: {str(e)}")
    
    def stop_automation(self):
        """Stop automation process"""
        try:
            if self.automation_worker and self.automation_worker.isRunning():
                self.automation_worker.stop()
                
                # Update UI
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.progress_bar.setVisible(False)
                self.status_label.setText("⏹️ Đã dừng automation")
                
                # Stop countdown timer
                self.countdown_timer.stop()
                
                QMessageBox.information(self, "Thông báo", "Đã dừng automation!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể dừng automation: {str(e)}")
    
    def update_progress(self, message):
        """Update progress message"""
        self.status_label.setText(f"🔄 {message}")
    
    def update_device_status(self, device_id, status):
        """Update device status"""
        print(f"Device {device_id}: {status}")
    
    def automation_finished(self, results):
        """Handle automation completion"""
        try:
            # Update UI
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            
            # Stop countdown timer
            self.countdown_timer.stop()
            
            if results:
                self.status_label.setText("✅ Automation hoàn thành thành công!")
                QMessageBox.information(self, "Thành công", "Automation đã hoàn thành thành công!")
            else:
                self.status_label.setText("⚠️ Automation đã dừng")
            
            # Clean up worker
            if self.automation_worker:
                self.automation_worker.deleteLater()
                self.automation_worker = None
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi hoàn thành automation: {str(e)}")
    
    def on_automation_error(self, error_message):
        """Handle automation error"""
        try:
            # Update UI
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"❌ Lỗi: {error_message}")
            
            # Stop countdown timer
            self.countdown_timer.stop()
            
            QMessageBox.critical(self, "Lỗi Automation", f"Automation gặp lỗi:\n{error_message}")
            
            # Clean up worker
            if self.automation_worker:
                self.automation_worker.deleteLater()
                self.automation_worker = None
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xử lý automation error: {str(e)}")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyleSheet("""
        QApplication {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
    """)
    
    widget = ZaloAutomationWidget()
    widget.show()
    
    sys.exit(app.exec())