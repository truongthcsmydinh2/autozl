#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window Module
Cửa sổ chính của ứng dụng Android Automation GUI
"""

import os
import sys
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QStackedWidget, QLabel, QFrame,
    QMenuBar, QMenu, QStatusBar, QToolBar, QMessageBox,
    QPushButton, QApplication, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QFont, QPalette, QColor

# Import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.device_manager import DeviceManager
from core.config_manager import ConfigManager

# Import UI components
from ui.device_management import DeviceManagementWidget
from ui.phone_mapping_widget import PhoneMappingWidget
from ui.zalo_automation import ZaloAutomationWidget
from ui.theme_manager import ThemeManager

class SidebarWidget(QWidget):
    """Sidebar navigation widget"""
    
    page_changed = pyqtSignal(str)  # page_name
    
    def __init__(self):
        super().__init__()
        self.current_page = "dashboard"
        self.setup_ui()
    
    def setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Title
        title_frame = QFrame()
        title_frame.setObjectName("titleFrame")
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("Android\nAutomation")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        
        layout.addWidget(title_frame)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("devices", "📱 Devices", "Quản lý thiết bị"),
            ("phone_mapping", "📞 Phone Manage", "Quản lý thông tin thiết bị"),
            ("zalo_automation", "🤖 Nuôi Zalo", "Automation Zalo")
        ]
        
        for page_id, text, tooltip in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, p=page_id: self.switch_page(p))
            
            self.nav_buttons[page_id] = btn
            layout.addWidget(btn)
        
        # Spacer
        layout.addStretch()
        
        # Status info
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)
        
        self.status_label = QLabel("🔴 Disconnected")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_frame)
        
        self.setLayout(layout)
        
        # Set initial active button
        self.set_active_button("devices")
    

    
    def switch_page(self, page_name: str):
        """Switch to specified page"""
        if page_name != self.current_page:
            self.current_page = page_name
            self.set_active_button(page_name)
            self.page_changed.emit(page_name)
    
    def set_active_button(self, page_name: str):
        """Set active navigation button"""
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_name:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    def update_status(self, status: str, color: str = "#cccccc"):
        """Update status display"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color};")


    


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.device_manager = DeviceManager()
        self.theme_manager = ThemeManager()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Apply theme after UI setup
        self.theme_manager.apply_theme("dark")
        
        # Load window state
        self.load_window_state()
        
        # Start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent collapsing
        
        # Sidebar
        self.sidebar = SidebarWidget()
        sidebar_width = self.config_manager.get("ui.sidebar_width", 250)
        self.sidebar.setMinimumWidth(200)  # Minimum width
        self.sidebar.setMaximumWidth(300)  # Maximum width
        self.sidebar.setFixedWidth(sidebar_width)
        splitter.addWidget(self.sidebar)
        
        # Main content area
        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(400)  # Ensure content area has minimum width
        
        # Add pages
        self.pages = {}
        
        # Create pages with actual UI components
        self.add_page("devices", DeviceManagementWidget(self.device_manager))
        self.add_page("phone_mapping", PhoneMappingWidget(self.device_manager, self.config_manager))
        self.add_page("zalo_automation", ZaloAutomationWidget())
        
        splitter.addWidget(self.content_stack)
        
        # Set splitter proportions and sizes
        splitter.setStretchFactor(0, 0)  # Sidebar fixed
        splitter.setStretchFactor(1, 1)  # Content area expandable
        
        # Set initial splitter sizes
        splitter.setSizes([sidebar_width, 650])  # Explicit sizes
        
        main_layout.addWidget(splitter)
        
        # Store splitter reference for later use
        self.main_splitter = splitter
        
        # Set window properties
        self.setWindowTitle("Android Automation GUI v1.0")
        self.setMinimumSize(700, 500)
        # Set default window size to be smaller for better initial usability
        self.resize(900, 650)
        
        # Center window on screen
        self.center_window()
    
    def add_page(self, page_id: str, widget: QWidget):
        """Add page to content stack"""
        self.pages[page_id] = widget
        self.content_stack.addWidget(widget)
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def switch_page(self, page_name: str):
        """Switch to specified page"""
        if page_name in self.pages:
            widget = self.pages[page_name]
            self.content_stack.setCurrentWidget(widget)
            
            # Update window title
            page_titles = {
                "devices": "Device Management - Android Automation", 
                "phone_mapping": "Phone Mapping - Android Automation",
                "zalo_automation": "Zalo Automation - Android Automation"
            }
            
            title = page_titles.get(page_name, "Android Automation GUI v1.0")
            self.setWindowTitle(title)
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_flow_action = QAction("&New Flow", self)
        new_flow_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_flow_action)
        
        open_flow_action = QAction("&Open Flow", self)
        open_flow_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_flow_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Device menu
        device_menu = menubar.addMenu("&Device")
        
        connect_action = QAction("&Connect Devices", self)
        connect_action.setShortcut("Ctrl+D")
        device_menu.addAction(connect_action)
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        device_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    

    
    def setup_status_bar(self):
        """Setup status bar"""
        if not self.config_manager.get("ui.show_statusbar", True):
            return
        
        self.status_bar = self.statusBar()
        
        # Status labels
        self.device_status_label = QLabel("Devices: 0")
        self.flow_status_label = QLabel("Flows: 0")
        self.execution_status_label = QLabel("Ready")
        
        self.status_bar.addWidget(self.device_status_label)
        self.status_bar.addPermanentWidget(self.flow_status_label)
        self.status_bar.addPermanentWidget(self.execution_status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Sidebar navigation
        self.sidebar.page_changed.connect(self.switch_page)
        
        # Manager signals
        self.config_manager.log_message.connect(self.show_message)
        self.device_manager.log_message.connect(self.show_message)
        
        # Connect UI component signals
        if "devices" in self.pages and hasattr(self.pages["devices"], 'device_connected'):
            self.pages["devices"].device_connected.connect(self.on_device_connected)
        
        # Flow editor, execution and settings pages removed
    

    
    def switch_page(self, page_name: str):
        """Switch to specified page"""
        if page_name in self.pages:
            widget = self.pages[page_name]
            self.content_stack.setCurrentWidget(widget)
            
            # Update window title
            page_title = page_name.replace('_', ' ').title()
            self.setWindowTitle(f"Android Automation GUI - {page_title}")
    
    def update_status(self):
        """Update status information"""
        # Update device count
        device_count = len(self.device_manager.get_connected_devices())
        self.device_status_label.setText(f"Devices: {device_count}")
        
        # Update sidebar status
        if device_count > 0:
            self.sidebar.update_status(f"🟢 {device_count} Connected", "#107c10")
        else:
            self.sidebar.update_status("🔴 Disconnected", "#d13438")
        
        # Flow functionality removed
        self.flow_status_label.setText("Flows: 0")
        
    def on_device_connected(self, device_id):
        """Handle device connection"""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"Device connected: {device_id}", 3000)
        self.update_status()
        
    def on_flow_saved(self, flow_name):
        """Handle flow save"""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"Flow saved: {flow_name}", 3000)
        self.update_status()
        
    def on_execution_started(self, flow_name):
        """Handle execution start"""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(f"Executing: {flow_name}")
        
    def on_settings_changed(self):
        """Handle settings change"""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("Settings changed", 2000)
    
    def show_message(self, message: str, level: str = "INFO"):
        """Show message in status bar"""
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage(message, 3000)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
            "Android Automation GUI v1.0\n\n"
            "Ứng dụng quản lý và thực thi automation cho Android devices.\n\n"
            "Developed with PyQt6")
    
    def load_window_state(self):
        """Load window state from config"""
        if self.config_manager.get("ui.remember_window_state", True):
            width = self.config_manager.get("ui.window_width", 900)
            height = self.config_manager.get("ui.window_height", 650)
            self.resize(width, height)
    
    def save_window_state(self):
        """Save window state to config"""
        if self.config_manager.get("ui.remember_window_state", True):
            self.config_manager.set("ui.window_width", self.width(), save=False)
            self.config_manager.set("ui.window_height", self.height(), save=False)
            self.config_manager.save_config()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_window_state()
        
        # Stop any running processes
        self.device_manager.disconnect_all_devices()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Android Automation GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Android Automation")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())