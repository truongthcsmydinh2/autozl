from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QScrollArea, QTextEdit, QLineEdit, QProgressBar,
    QMessageBox, QGroupBox, QSplitter, QSpacerItem, QSizePolicy,
    QFrame, QTabWidget, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView
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
    def __init__(self, device_id, phone_number, note="Không có"):
        super().__init__()
        self.device_id = device_id
        self.phone_number = phone_number
        self.note = note
        
        # Create display text
        display_text = f"📱 {device_id}"
        if phone_number and phone_number != "Chưa có số":
            display_text += f" ({phone_number} - Máy: {note})"
        else:
            display_text += f" (Máy: {note})"
        
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
        
        # Status table data
        self.status_table_data = {}
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        
        # Initialize UI and load devices
        self.init_ui()
        self.load_devices()
    
    def apply_conversation(self):
        """Xử lý dữ liệu hội thoại khi click Apply"""
        try:
            # Lấy dữ liệu hội thoại từ text inputs
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
            
            # Phân tích hội thoại thành messages theo role
            parsed_conversations = self.parse_conversations(conversations)
            
            # Lưu dữ liệu vào conversation_data.json
            self.save_conversation_data(parsed_conversations)
            
            # Tìm và cập nhật ExecutionStatusWidget
            main_window = self.window()
            if hasattr(main_window, 'tab_widget'):
                for i in range(main_window.tab_widget.count()):
                    widget = main_window.tab_widget.widget(i)
                    if hasattr(widget, 'execution_status_widget'):
                        widget.execution_status_widget.load_conversation_data()
                        widget.execution_status_widget.start_status_monitoring()  # Bắt đầu monitor status.json
                        break
            
            QMessageBox.information(self, "Thành công", f"Đã áp dụng {len(conversations)} đoạn hội thoại!\nDữ liệu đã được lưu và hiển thị trong bảng status.")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi áp dụng hội thoại: {str(e)}")
    
    def parse_conversations(self, conversations):
        """Phân tích hội thoại thành messages theo role"""
        parsed_data = []
        
        for conv in conversations:
            lines = conv['content'].split('\n')
            messages_role1 = []
            messages_role2 = []
            message_id = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Xác định role dựa trên pattern hoặc thứ tự
                if message_id % 2 == 1:  # Role 1 (device 1)
                    messages_role1.append({
                        'message_id': message_id,
                        'content': line,
                        'status': 'pending',
                        'device_number': 1
                    })
                else:  # Role 2 (device 2)
                    messages_role2.append({
                        'message_id': message_id,
                        'content': line,
                        'status': 'pending',
                        'device_number': 2
                    })
                
                message_id += 1
            
            parsed_data.append({
                'group_id': conv['group_id'],
                'role1_messages': messages_role1,
                'role2_messages': messages_role2
            })
        
        return parsed_data
    
    def save_conversation_data(self, parsed_conversations):
        """Lưu dữ liệu hội thoại vào conversation_data.json"""
        import json
        import os
        from datetime import datetime
        
        try:
            # Tạo cấu trúc dữ liệu để lưu
            conversation_data = {
                'timestamp': datetime.now().isoformat(),
                'total_pairs': len(parsed_conversations),
                'conversations': {}
            }
            
            for i, conv in enumerate(parsed_conversations, 1):
                pair_key = f'pair_{i}'
                conversation_data['conversations'][pair_key] = {
                    'devices': {
                        'device_1': {'device_number': 1},
                        'device_2': {'device_number': 2}
                    },
                    'messages': []
                }
                
                # Thêm messages từ role 1
                for msg in conv['role1_messages']:
                    conversation_data['conversations'][pair_key]['messages'].append({
                        'message_id': msg['message_id'],
                        'device_number': 1,
                        'content': msg['content'],
                        'status': 'pending'
                    })
                
                # Thêm messages từ role 2
                for msg in conv['role2_messages']:
                    conversation_data['conversations'][pair_key]['messages'].append({
                        'message_id': msg['message_id'],
                        'device_number': 2,
                        'content': msg['content'],
                        'status': 'pending'
                    })
                
                # Sắp xếp messages theo message_id
                conversation_data['conversations'][pair_key]['messages'].sort(
                    key=lambda x: x['message_id']
                )
            
            # Lưu vào file
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conversation_data.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            raise Exception(f"Lỗi khi lưu dữ liệu: {str(e)}")
    
    def create_status_tab(self):
        """Tạo tab hiển thị status real-time"""
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(15, 15, 15, 15)
        status_layout.setSpacing(10)
        
        # Title
        title_label = QLabel("📊 Trạng Thái Automation Real-time")
        title_label.setStyleSheet("""
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
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(title_label)
        
        # Status table
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(4)
        self.status_table.setHorizontalHeaderLabels(["Nick/Device", "Nội dung tin nhắn", "Trạng thái", "Countdown"])
        
        # Table styling
        self.status_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 8px;
                gridline-color: #34495e;
                font-size: 12px;
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
                font-size: 12px;
            }
        """)
        
        # Set column widths
        header = self.status_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Nick/Device
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nội dung tin nhắn
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Countdown
        
        status_layout.addWidget(self.status_table)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Xóa Bảng")
        clear_btn.clicked.connect(self.clear_status_table)
        clear_btn.setFixedHeight(35)
        clear_btn.setStyleSheet(self.get_compact_button_style("#e74c3c", "#c0392b"))
        status_layout.addWidget(clear_btn)
        
        self.tab_widget.addTab(status_widget, "📊 Status")
    
    def clear_status_table(self):
        """Xóa nội dung bảng status"""
        if hasattr(self, 'status_table'):
            self.status_table.setRowCount(0)
        if hasattr(self, 'status_table_data'):
            self.status_table_data.clear()
    
    def add_device_to_status_table(self, device_ip, initial_status="Đang khởi tạo"):
        """Thêm device vào bảng status"""
        if not hasattr(self, 'status_table') or not hasattr(self, 'status_table_data'):
            return
            
        row_count = self.status_table.rowCount()
        self.status_table.insertRow(row_count)
        
        # Nick/Device
        device_item = QTableWidgetItem(device_ip)
        device_item.setFlags(device_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.status_table.setItem(row_count, 0, device_item)
        
        # Nội dung tin nhắn
        message_item = QTableWidgetItem("")
        message_item.setFlags(message_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.status_table.setItem(row_count, 1, message_item)
        
        # Trạng thái
        status_item = QTableWidgetItem(initial_status)
        status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.status_table.setItem(row_count, 2, status_item)
        
        # Countdown
        countdown_item = QTableWidgetItem("")
        countdown_item.setFlags(countdown_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.status_table.setItem(row_count, 3, countdown_item)
        
        # Store row index for this device
        self.status_table_data[device_ip] = {
            'row': row_count,
            'countdown': 0,
            'message': '',
            'status': initial_status
        }
    
    def update_device_status(self, device_ip, status):
        """Cập nhật trạng thái device"""
        if not hasattr(self, 'status_table') or not hasattr(self, 'status_table_data'):
            return
            
        if device_ip in self.status_table_data:
            row = self.status_table_data[device_ip]['row']
            self.status_table_data[device_ip]['status'] = status
            
            status_item = QTableWidgetItem(status)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            
            # Color coding for status
            if "Hoàn thành" in status:
                status_item.setBackground(Qt.GlobalColor.darkGreen)
            elif "Đang gửi" in status:
                status_item.setBackground(Qt.GlobalColor.darkBlue)
            elif "Delay" in status or "Chờ" in status:
                status_item.setBackground(Qt.GlobalColor.darkYellow)
            elif "Lỗi" in status:
                status_item.setBackground(Qt.GlobalColor.darkRed)
            
            self.status_table.setItem(row, 2, status_item)
    
    def update_message_status(self, device_ip, content, status, delay_time):
        """Cập nhật tin nhắn và countdown"""
        if not hasattr(self, 'status_table') or not hasattr(self, 'status_table_data'):
            return
            
        if device_ip in self.status_table_data:
            row = self.status_table_data[device_ip]['row']
            self.status_table_data[device_ip]['message'] = content
            self.status_table_data[device_ip]['countdown'] = delay_time
            
            # Update message
            message_item = QTableWidgetItem(content[:50] + "..." if len(content) > 50 else content)
            message_item.setFlags(message_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.status_table.setItem(row, 1, message_item)
            
            # Update status
            self.update_device_status(device_ip, status)
            
            # Update countdown
            countdown_text = f"{delay_time}s" if delay_time > 0 else ""
            countdown_item = QTableWidgetItem(countdown_text)
            countdown_item.setFlags(countdown_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.status_table.setItem(row, 3, countdown_item)
    
    def update_countdown(self):
        """Cập nhật countdown timer mỗi giây"""
        if not hasattr(self, 'status_table') or not hasattr(self, 'status_table_data'):
            return
            
        for device_ip, data in self.status_table_data.items():
            if data['countdown'] > 0:
                data['countdown'] -= 1
                row = data['row']
                
                countdown_text = f"{data['countdown']}s" if data['countdown'] > 0 else ""
                countdown_item = QTableWidgetItem(countdown_text)
                countdown_item.setFlags(countdown_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.status_table.setItem(row, 3, countdown_item)
    
    def start_status_tracking(self):
        """Bắt đầu tracking status khi automation chạy"""
        # Clear existing data
        self.clear_status_table()
        
        # Add devices to table
        selected_devices = self.get_selected_devices()
        for device in selected_devices:
            device_ip = device['ip'] if isinstance(device, dict) else device
            self.add_device_to_status_table(device_ip)
        
        # Start countdown timer
        if hasattr(self, 'countdown_timer'):
            self.countdown_timer.start(1000)  # Update every second
        
        # Switch to status tab
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setCurrentIndex(4)  # Status tab is index 4
    
    def stop_status_tracking(self):
        """Dừng tracking status"""
        if hasattr(self, 'countdown_timer'):
            self.countdown_timer.stop()
        
        # Clear status table data
        if hasattr(self, 'status_table_data'):
            self.status_table_data.clear()
        
        # Clear status table if it exists
        if hasattr(self, 'status_table'):
            self.status_table.setRowCount(0)
    
    def init_ui(self):
        """Khởi tạo giao diện compact với QTabWidget"""
        # Set compact window properties
        self.setWindowTitle("🔥 Zalo Automation - Compact")
        self.setMinimumSize(1000, 600)
        self.resize(1200, 700)
        
        # Main layout with compact spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Set compact dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
        """)
        
        # Compact title section
        title_section = self.create_compact_title_section()
        main_layout.addWidget(title_section)
        
        # Tab widget for organized layout
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
                padding: 8px 16px;
                margin: 2px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #5dade2;
            }
        """)
        
        # Create tabs
        self.create_device_tab()
        self.create_pairing_tab()
        self.create_conversation_tab()
        self.create_control_tab()
        self.create_status_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Compact status bar
        self.status_label = QLabel("🚀 Sẵn sàng")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #2c3e50;
            }
        """)
        main_layout.addWidget(self.status_label)
    
    def create_compact_title_section(self):
        """Tạo compact title section"""
        title_frame = QFrame()
        title_frame.setFixedHeight(50)
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
                border: 1px solid #2980b9;
            }
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 5, 15, 5)
        
        title_label = QLabel("🔥 ZALO AUTOMATION - COMPACT")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(title_label)
        
        return title_frame
    
    def create_device_tab(self):
        """Tạo tab chọn devices"""
        device_widget = QWidget()
        device_layout = QVBoxLayout(device_widget)
        device_layout.setContentsMargins(10, 10, 10, 10)
        device_layout.setSpacing(8)
        
        # Control buttons
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(5)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_devices)
        self.refresh_btn.setFixedHeight(30)
        self.refresh_btn.setStyleSheet(self.get_compact_button_style("#3498db", "#2980b9"))
        
        self.select_all_btn = QPushButton("✅ Chọn Tất Cả")
        self.select_all_btn.clicked.connect(self.select_all_devices)
        self.select_all_btn.setFixedHeight(30)
        self.select_all_btn.setStyleSheet(self.get_compact_button_style("#27ae60", "#229954"))
        
        self.select_none_btn = QPushButton("❌ Bỏ Chọn")
        self.select_none_btn.clicked.connect(self.select_none_devices)
        self.select_none_btn.setFixedHeight(30)
        self.select_none_btn.setStyleSheet(self.get_compact_button_style("#95a5a6", "#7f8c8d"))
        
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.select_all_btn)
        control_layout.addWidget(self.select_none_btn)
        
        device_layout.addWidget(control_frame)
        
        # Search section
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_label = QLabel("🔍 Tìm:")
        search_label.setStyleSheet("color: #bdc3c7; font-weight: bold; font-size: 12px;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("IP hoặc số điện thoại...")
        self.search_input.textChanged.connect(self.filter_devices)
        self.search_input.setFixedHeight(25)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        device_layout.addWidget(search_frame)
        
        # Counter
        self.device_counter_label = QLabel("Đã chọn: 0 devices")
        self.device_counter_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                background-color: #34495e;
                border-radius: 4px;
                border: 1px solid #2c3e50;
            }
        """)
        device_layout.addWidget(self.device_counter_label)
        
        # Scroll area for devices
        self.device_scroll = QScrollArea()
        self.device_scroll.setWidgetResizable(True)
        self.device_scroll.setMinimumHeight(300)
        self.device_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #34495e;
                border-radius: 6px;
                background-color: #2c3e50;
            }
            QScrollBar:vertical {
                background-color: #34495e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 5px;
                min-height: 15px;
            }
        """)
        
        self.device_container = QWidget()
        self.device_layout = QVBoxLayout(self.device_container)
        self.device_layout.setContentsMargins(5, 5, 5, 5)
        self.device_layout.setSpacing(3)
        
        self.device_scroll.setWidget(self.device_container)
        device_layout.addWidget(self.device_scroll)
        
        self.tab_widget.addTab(device_widget, "📱 Devices")
    
    def create_pairing_tab(self):
        """Tạo tab ghép cặp"""
        pairing_widget = QWidget()
        pairing_layout = QVBoxLayout(pairing_widget)
        pairing_layout.setContentsMargins(15, 15, 15, 15)
        pairing_layout.setSpacing(10)
        
        self.pairing_info = QLabel("Chọn devices và nhấn 'Ghép cặp' để tự động pair")
        self.pairing_info.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 14px;
                padding: 15px;
                border: none;
                background-color: #34495e;
                border-radius: 6px;
                line-height: 1.4;
            }
        """)
        pairing_layout.addWidget(self.pairing_info)
        
        self.pair_btn = QPushButton("💕 Ghép Cặp")
        self.pair_btn.clicked.connect(self.pair_devices)
        self.pair_btn.setFixedHeight(45)
        self.pair_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        pairing_layout.addWidget(self.pair_btn)
        
        pairing_layout.addStretch()
        
        self.tab_widget.addTab(pairing_widget, "💑 Ghép Cặp")
    
    def create_conversation_tab(self):
        """Tạo tab hội thoại"""
        conv_widget = QWidget()
        conv_layout = QVBoxLayout(conv_widget)
        conv_layout.setContentsMargins(10, 10, 10, 10)
        conv_layout.setSpacing(8)
        
        # Info label
        info_label = QLabel("Số đoạn hội thoại tự động cập nhật theo số nhóm")
        info_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 12px;
                font-style: italic;
                padding: 10px;
                border: none;
                background-color: #34495e;
                border-radius: 6px;
            }
        """)
        conv_layout.addWidget(info_label)
        
        # Scroll area for conversation inputs
        self.conversation_scroll = QScrollArea()
        self.conversation_scroll.setWidgetResizable(True)
        self.conversation_scroll.setMinimumHeight(400)
        self.conversation_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #34495e;
                border-radius: 6px;
                background-color: #2c3e50;
            }
            QScrollBar:vertical {
                background-color: #34495e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 5px;
                min-height: 15px;
            }
        """)
        
        # Container for conversation inputs
        self.conversation_container = QWidget()
        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.conversation_layout.setSpacing(10)
        self.conversation_layout.setContentsMargins(10, 10, 10, 10)
        
        self.conversation_scroll.setWidget(self.conversation_container)
        conv_layout.addWidget(self.conversation_scroll)
        
        # List to store conversation text widgets
        self.conversation_texts = []
        
        # Apply button
        self.apply_btn = QPushButton("✅ Apply")
        self.apply_btn.clicked.connect(self.apply_conversation)
        self.apply_btn.setFixedHeight(35)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        conv_layout.addWidget(self.apply_btn)
        
        self.tab_widget.addTab(conv_widget, "💬 Hội Thoại")
    
    def create_control_tab(self):
        """Tạo tab điều khiển"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)
        
        # Start/Stop buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        
        self.start_btn = QPushButton("🚀 Bắt Đầu Auto")
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setFixedHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Dừng Auto")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        control_layout.addWidget(button_frame)
        
        # Progress section
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_label = QLabel("Tiến trình:")
        progress_label.setStyleSheet("color: #bdc3c7; font-weight: bold; font-size: 12px;")
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 4px;
                background-color: #2c3e50;
                text-align: center;
                font-size: 10px;
                color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_text = QTextEdit()
        self.progress_text.setMaximumHeight(200)
        self.progress_text.setStyleSheet("""
            QTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #2c3e50;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                font-family: 'Consolas', monospace;
            }
        """)
        progress_layout.addWidget(self.progress_text)
        
        control_layout.addWidget(progress_frame)
        control_layout.addStretch()
        
        self.tab_widget.addTab(control_widget, "⚙️ Điều Khiển")
    
    def get_compact_button_style(self, bg_color, hover_color):
        """Trả về compact button style"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-height: 25px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
            }}
        """
    
    def pair_devices(self):
        """Ghép cặp devices đã chọn"""
        selected_devices = self.get_selected_devices()
        if len(selected_devices) < 2:
            QMessageBox.warning(self, "Cảnh báo", "Cần chọn ít nhất 2 devices để ghép cặp!")
            return
        
        if len(selected_devices) % 2 != 0:
            QMessageBox.warning(self, "Cảnh báo", "Số devices phải là số chẵn để ghép cặp!")
            return
        
        # Logic ghép cặp devices
        pairs = []
        for i in range(0, len(selected_devices), 2):
            pairs.append((selected_devices[i], selected_devices[i+1]))
        
        pair_text = "\n".join([f"Cặp {i+1}: {pair[0]} ↔ {pair[1]}" for i, pair in enumerate(pairs)])
        self.pairing_info.setText(f"Đã ghép {len(pairs)} cặp:\n{pair_text}")
        
        QMessageBox.information(self, "Thành công", f"Đã ghép {len(pairs)} cặp devices!")
    
    def get_selected_devices(self):
        """Lấy danh sách devices đã chọn"""
        selected = []
        for i in range(self.device_layout.count()):
            widget = self.device_layout.itemAt(i).widget()
            if isinstance(widget, DeviceCheckBox) and widget.isChecked():
                selected.append(widget.device_id)
        return selected
    
    def start_automation(self):
        """Bắt đầu automation"""
        selected_devices = self.get_selected_devices()
        if not selected_devices:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn ít nhất 1 device!")
            return
        
        conversations = []
        for text_edit in self.conversation_texts:
            text = text_edit.toPlainText().strip()
            if text:
                conversations.append(text)
        
        if not conversations:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập ít nhất 1 đoạn hội thoại!")
            return
        
        # Disable start button, enable stop button
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Start automation worker
        self.automation_worker = AutomationWorker(selected_devices, conversations)
        self.automation_worker.progress_updated.connect(self.update_progress)
        self.automation_worker.finished.connect(self.automation_finished)
        self.automation_worker.start()
        
        self.progress_text.append("🚀 Bắt đầu automation...")
    
    def stop_automation(self):
        """Dừng automation"""
        if hasattr(self, 'automation_worker') and self.automation_worker.isRunning():
            self.automation_worker.stop()
            self.automation_worker.wait()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        self.progress_text.append("⏹️ Đã dừng automation.")
    
    def update_progress(self, message):
        """Cập nhật tiến trình"""
        self.progress_text.append(message)
        # Auto scroll to bottom
        scrollbar = self.progress_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def automation_finished(self):
        """Automation hoàn thành"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_text.append("✅ Automation hoàn thành!")
        QMessageBox.information(self, "Hoàn thành", "Automation đã hoàn thành!")
    
    # Import required classes
    def __init__(self):
        super().__init__()
        self.device_checkboxes = []
        self.conversation_texts = []
        self.device_pairs = []
        self.automation_worker = None
        self.all_devices = []
        self.init_ui()
        self.load_devices()
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
        """)
        self.stop_btn.setEnabled(False)
    
    def create_progress_section(self):
        """Tạo section hiển thị progress"""
        progress_group = QGroupBox("📊 Trạng Thái")
        progress_group.setStyleSheet(self.get_group_style())
        progress_group.setFixedHeight(100)
        
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(20, 25, 20, 15)
        progress_layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 8px;
                text-align: center;
                color: #ecf0f1;
                font-weight: bold;
                background-color: #2c3e50;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 6px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        return progress_group
    
    # Các method khác giữ nguyên từ code cũ
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
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.status_label.setText("⚠️ Không tìm thấy device nào. Vui lòng kết nối devices và nhấn Refresh.")
                self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
                
        except Exception as e:
            # Clear devices on error
            self.all_devices = []
            self.display_devices([])
            
            # Show error in status
            error_msg = f"❌ Lỗi load devices: {str(e)}"
            self.status_label.setText(error_msg)
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
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
                    color: #e74c3c;
                    font-size: 16px;
                    padding: 30px;
                    text-align: center;
                    background-color: #34495e;
                    border-radius: 10px;
                    margin: 15px;
                    font-weight: bold;
                    border: 2px solid #e74c3c;
                }
            """)
            no_device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.device_layout.addWidget(no_device_label)
        else:
            for device in devices:
                phone_number = device['phone'] if device['phone'] else "Chưa có số"
                # Lấy note từ device data, sử dụng 'Không có' nếu trống
                note = device.get('note', '') or 'Không có'
                
                checkbox = DeviceCheckBox(device['ip'], phone_number, note)
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
                # Search in IP, phone number and note
                ip_text = device.get('ip', '').lower()
                phone_text = device.get('phone', '').lower()
                note_text = device.get('note', '').lower()
                
                # Check if search text matches IP, phone or note
                if (search_text in ip_text or 
                    search_text in phone_text or
                    search_text in note_text or
                    search_text in f"{ip_text} {phone_text} {note_text}"):
                    filtered_devices.append(device)
            
            self.display_devices(filtered_devices)
            
            # Update search status
            if filtered_devices:
                self.status_label.setText(f"🔍 Tìm thấy {len(filtered_devices)}/{len(self.all_devices)} devices")
            else:
                self.status_label.setText(f"🔍 Không tìm thấy device nào với từ khóa '{search_text}'")
                self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
    
    def update_device_counter(self):
        """Update device counter and validate even number"""
        selected_count = len(self.get_selected_devices())
        
        if selected_count % 2 == 0:
            self.device_counter_label.setText(f"Đã chọn: {selected_count} devices ✓")
            self.device_counter_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 10px;
                    background-color: #34495e;
                    border-radius: 6px;
                    border: 2px solid #27ae60;
                }
            """)
        else:
            self.device_counter_label.setText(f"Đã chọn: {selected_count} devices (cần số chẵn!)")
            self.device_counter_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-weight: bold;
                    font-size: 16px;
                    padding: 10px;
                    background-color: #34495e;
                    border-radius: 6px;
                    border: 2px solid #e74c3c;
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
    
    def update_conversation_inputs(self, num_groups):
        """Cập nhật số lượng conversation inputs theo số nhóm"""
        # Clear existing inputs
        for text_widget in self.conversation_texts:
            text_widget.setParent(None)
            text_widget.deleteLater()
        self.conversation_texts.clear()
        
        # Clear layout
        while self.conversation_layout.count():
            child = self.conversation_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create new inputs
        for i in range(num_groups):
            # Group label
            group_label = QLabel(f"Nhóm {i+1}:")
            group_label.setMinimumWidth(550)
            group_label.setStyleSheet("""
                QLabel {
                    color: #3498db;
                    font-weight: bold;
                    font-size: 18px;
                    margin-top: 15px;
                    padding: 12px;
                    background-color: #34495e;
                    border-radius: 8px;
                    min-width: 550px;
                }
            """)
            self.conversation_layout.addWidget(group_label)
            
            # Text input
            text_edit = QTextEdit()
            text_edit.setPlaceholderText(f"Nhập đoạn hội thoại cho nhóm {i+1}...\nVí dụ: Xin chào! Bạn khỏe không?")
            text_edit.setMaximumHeight(180)
            text_edit.setMinimumHeight(150)
            text_edit.setMinimumWidth(550)
            text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 2px solid #2c3e50;
                    border-radius: 10px;
                    padding: 18px;
                    font-size: 16px;
                    line-height: 1.5;
                    min-width: 550px;
                }
                QTextEdit:focus {
                    border-color: #3498db;
                    background-color: #3a526b;
                }
                QTextEdit:hover {
                    border-color: #5dade2;
                }
            """)
            
            self.conversation_texts.append(text_edit)
            self.conversation_layout.addWidget(text_edit)
        
        # Add spacer
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.conversation_layout.addItem(spacer)
    
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
        
        # Update conversation inputs based on number of pairs
        num_groups = len(self.device_pairs)
        self.update_conversation_inputs(num_groups)
        
        # Display pairs with phone numbers
        pairs_text = "🔗 Kết quả ghép cặp:\n\n"
        for i, (device1, device2) in enumerate(self.device_pairs, 1):
            phone1 = device1.get('phone', 'Chưa có số')
            phone2 = device2.get('phone', 'Chưa có số')
            pairs_text += f"Cặp {i}: {device1['ip']} ({phone1}) ↔ {device2['ip']} ({phone2})\n"
        
        self.pairing_info.setText(pairs_text)
        
        QMessageBox.information(self, "Thành công", f"Đã ghép {len(self.device_pairs)} cặp devices!\nĐã tạo {num_groups} đoạn hội thoại tương ứng.")
        
        self.status_label.setText(f"✅ Đã ghép {len(self.device_pairs)} cặp devices")
    
    def start_automation(self):
        """Bắt đầu automation với validation và tích hợp core1.py"""
        selected_devices = self.get_selected_devices()
        
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
        
        # Validate conversations
        conversations = []
        for i, text_edit in enumerate(self.conversation_texts):
            conversation = text_edit.toPlainText().strip()
            if not conversation:
                QMessageBox.warning(self, "Cảnh báo", f"Vui lòng nhập đoạn hội thoại cho nhóm {i+1}!")
                return
            conversations.append(conversation)
        
        if len(conversations) != len(self.device_pairs):
            QMessageBox.warning(self, "Cảnh báo", "Số đoạn hội thoại không khớp với số cặp devices!")
            return
        
        # Prepare data for core1.py
        automation_data = {
            'device_pairs': self.device_pairs,
            'conversations': conversations,
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
        self.automation_worker.message_status_updated.connect(self.update_message_status)
        self.automation_worker.device_status_updated.connect(self.update_device_status)
        
        # Start status tracking
        self.start_status_tracking()
        
        self.automation_worker.start()
        
        self.status_label.setText("🚀 Đang chạy automation...")
        self.status_label.setVisible(True)
    
    def stop_automation(self):
        """Dừng automation"""
        if hasattr(self, 'automation_worker') and self.automation_worker:
            self.automation_worker.stop()
            self.automation_worker = None
        
        # Stop status tracking
        self.stop_status_tracking()
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("⏹️ Đã dừng automation")
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
    
    def update_progress(self, message):
        """Cập nhật progress"""
        self.status_label.setText(message)
    
    def automation_finished(self, results):
        """Automation hoàn thành"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Stop status tracking
        self.stop_status_tracking()
        
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