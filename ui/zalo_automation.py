from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QScrollArea, QTextEdit, QLineEdit, QProgressBar,
    QMessageBox, QGroupBox, QSplitter, QSpacerItem, QSizePolicy,
    QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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
    
    def __init__(self, automation_data):
        super().__init__()
        self.automation_data = automation_data
        self.should_stop = False
    
    def run(self):
        try:
            # Import and run automation
            from core1 import run_zalo_automation
            results = run_zalo_automation(
                self.automation_data['device_pairs'],
                self.automation_data['conversations'],
                self.automation_data['phone_mapping'],
                progress_callback=self.progress_updated.emit
            )
            self.finished.emit(results)
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        self.should_stop = True
        self.terminate()

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
        
        self.init_ui()
        self.load_devices()
    
    def init_ui(self):
        """Khởi tạo giao diện với thiết kế mới hoàn toàn"""
        # Set window properties
        self.setWindowTitle("🔥 Zalo Automation Tool - Phiên Bản Mới")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Set dark theme for entire widget
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Title section
        title_section = self.create_title_section()
        main_layout.addWidget(title_section)
        
        # Content splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #34495e;
                width: 3px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
        
        # Left panel - Device selection
        left_panel = self.create_device_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Controls and conversations
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([600, 800])
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.status_label = QLabel("🚀 Sẵn sàng để bắt đầu automation")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #2c3e50;
            }
        """)
        main_layout.addWidget(self.status_label)
    
    def create_title_section(self):
        """Tạo section tiêu đề"""
        title_frame = QFrame()
        title_frame.setFixedHeight(80)
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 12px;
                border: 2px solid #2980b9;
            }
        """)
        
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        title_label = QLabel("🔥 ZALO AUTOMATION TOOL")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("Công cụ tự động hóa chat Zalo - Phiên bản nâng cấp")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                background: transparent;
                border: none;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        return title_frame
    
    def create_device_panel(self):
        """Tạo panel chọn device với thiết kế mới"""
        device_group = QGroupBox("📱 Chọn Devices")
        device_group.setStyleSheet(self.get_group_style())
        
        device_layout = QVBoxLayout(device_group)
        device_layout.setContentsMargins(15, 25, 15, 15)
        device_layout.setSpacing(15)
        
        # Control buttons
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(10)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_devices)
        self.refresh_btn.setFixedHeight(40)
        self.refresh_btn.setStyleSheet(self.get_button_style("#3498db", "#2980b9"))
        
        self.select_all_btn = QPushButton("✅ Chọn Tất Cả")
        self.select_all_btn.clicked.connect(self.select_all_devices)
        self.select_all_btn.setFixedHeight(40)
        self.select_all_btn.setStyleSheet(self.get_button_style("#27ae60", "#229954"))
        
        self.select_none_btn = QPushButton("❌ Bỏ Chọn")
        self.select_none_btn.clicked.connect(self.select_none_devices)
        self.select_none_btn.setFixedHeight(40)
        self.select_none_btn.setStyleSheet(self.get_button_style("#e74c3c", "#c0392b"))
        
        control_layout.addWidget(self.refresh_btn)
        control_layout.addWidget(self.select_all_btn)
        control_layout.addWidget(self.select_none_btn)
        
        device_layout.addWidget(control_frame)
        
        # Search section
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        search_label = QLabel("🔍 Tìm kiếm:")
        search_label.setStyleSheet("color: #bdc3c7; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập IP hoặc số điện thoại...")
        self.search_input.textChanged.connect(self.filter_devices)
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #2c3e50;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        device_layout.addWidget(search_frame)
        
        # Counter section
        self.device_counter_label = QLabel("Đã chọn: 0 devices")
        self.device_counter_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                background-color: #34495e;
                border-radius: 6px;
                border: 2px solid #2c3e50;
            }
        """)
        device_layout.addWidget(self.device_counter_label)
        
        # Scroll area for devices
        self.device_scroll = QScrollArea()
        self.device_scroll.setWidgetResizable(True)
        self.device_scroll.setMinimumHeight(400)
        self.device_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
            QScrollBar:vertical {
                background-color: #34495e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9;
            }
        """)
        
        self.device_container = QWidget()
        self.device_layout = QVBoxLayout(self.device_container)
        self.device_layout.setContentsMargins(10, 10, 10, 10)
        self.device_layout.setSpacing(5)
        
        self.device_scroll.setWidget(self.device_container)
        device_layout.addWidget(self.device_scroll)
        
        return device_group
    
    def create_right_panel(self):
        """Tạo panel bên phải với conversation và controls"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Pairing section
        pairing_group = self.create_pairing_section()
        right_layout.addWidget(pairing_group)
        
        # Conversation section
        conversation_group = self.create_conversation_section()
        right_layout.addWidget(conversation_group)
        
        # Control section
        control_group = self.create_control_section()
        right_layout.addWidget(control_group)
        
        # Progress section
        progress_group = self.create_progress_section()
        right_layout.addWidget(progress_group)
        
        return right_widget
    
    def get_button_style(self, bg_color, hover_color):
        """Trả về style cho button với màu tùy chỉnh"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                transform: scale(1.02);
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                transform: scale(0.98);
            }}
        """
    
    def get_group_style(self):
        """Trả về style chung cho QGroupBox"""
        return """
            QGroupBox {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 15px 0 15px;
                background-color: #2c3e50;
                color: #3498db;
            }
        """
    
    def create_pairing_section(self):
        """Tạo section ghép cặp"""
        pairing_group = QGroupBox("💑 Ghép Cặp Devices")
        pairing_group.setStyleSheet(self.get_group_style())
        pairing_group.setFixedHeight(140)
        
        pairing_layout = QVBoxLayout(pairing_group)
        pairing_layout.setContentsMargins(20, 25, 20, 15)
        pairing_layout.setSpacing(12)
        
        self.pairing_info = QLabel("Chọn devices và nhấn 'Ghép cặp' để tự động pair")
        self.pairing_info.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 13px;
                padding: 8px;
                border: none;
                background-color: #34495e;
                border-radius: 6px;
            }
        """)
        pairing_layout.addWidget(self.pairing_info)
        
        self.pair_btn = QPushButton("💕 Ghép Cặp")
        self.pair_btn.clicked.connect(self.pair_devices)
        self.pair_btn.setFixedHeight(50)
        self.pair_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #a93226;
                transform: scale(0.98);
            }
        """)
        pairing_layout.addWidget(self.pair_btn)
        
        return pairing_group
    
    def create_conversation_section(self):
        """Tạo section nhập hội thoại với dynamic inputs"""
        conv_group = QGroupBox("💬 Đoạn Hội Thoại")
        conv_group.setStyleSheet(self.get_group_style())
        conv_group.setMinimumHeight(300)
        
        conv_layout = QVBoxLayout(conv_group)
        conv_layout.setContentsMargins(20, 25, 20, 15)
        conv_layout.setSpacing(12)
        
        # Info label
        info_label = QLabel("Số đoạn hội thoại tự động cập nhật theo số nhóm")
        info_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 13px;
                font-style: italic;
                padding: 8px;
                border: none;
                background-color: #34495e;
                border-radius: 6px;
            }
        """)
        conv_layout.addWidget(info_label)
        
        # Scroll area for conversation inputs
        self.conversation_scroll = QScrollArea()
        self.conversation_scroll.setWidgetResizable(True)
        self.conversation_scroll.setMinimumHeight(200)
        self.conversation_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
            }
            QScrollBar:vertical {
                background-color: #34495e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        
        # Container for conversation inputs
        self.conversation_container = QWidget()
        self.conversation_layout = QVBoxLayout(self.conversation_container)
        self.conversation_layout.setSpacing(12)
        self.conversation_layout.setContentsMargins(15, 15, 15, 15)
        
        self.conversation_scroll.setWidget(self.conversation_container)
        conv_layout.addWidget(self.conversation_scroll)
        
        # List to store conversation text widgets
        self.conversation_texts = []
        
        # Initially create one conversation input
        self.update_conversation_inputs(1)
        
        return conv_group
    
    def create_control_section(self):
        """Tạo section điều khiển"""
        control_group = QGroupBox("🎮 Điều Khiển")
        control_group.setStyleSheet(self.get_group_style())
        control_group.setFixedHeight(120)
        
        control_layout = QVBoxLayout(control_group)
        control_layout.setContentsMargins(20, 25, 20, 15)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.start_btn = QPushButton("🚀 Bắt Đầu Auto")
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setFixedHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #1e8449;
                transform: scale(0.98);
            }
        """)
        
        self.stop_btn = QPushButton("⏹️ Dừng Auto")
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setFixedHeight(50)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                padding: 12px 24px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #a93226;
                transform: scale(0.98);
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
        """)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        control_layout.addLayout(button_layout)
        
        return control_group
    
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
            group_label.setStyleSheet("""
                QLabel {
                    color: #3498db;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 10px;
                    padding: 8px;
                    background-color: #34495e;
                    border-radius: 6px;
                }
            """)
            self.conversation_layout.addWidget(group_label)
            
            # Text input
            text_edit = QTextEdit()
            text_edit.setPlaceholderText(f"Nhập đoạn hội thoại cho nhóm {i+1}...\nVí dụ: Xin chào! Bạn khỏe không?")
            text_edit.setMaximumHeight(120)
            text_edit.setMinimumHeight(100)
            text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 2px solid #2c3e50;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    line-height: 1.4;
                }
                QTextEdit:focus {
                    border-color: #3498db;
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
        self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
    
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