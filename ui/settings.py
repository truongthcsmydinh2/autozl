# -*- coding: utf-8 -*-
"""
Settings Configuration UI
Quản lý cấu hình ứng dụng
"""

import sys
import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QGroupBox, QCheckBox, QSpinBox, QSlider, QTabWidget,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QFrame, QScrollArea, QFormLayout, QDoubleSpinBox,
    QColorDialog, QFontDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor

class GeneralSettingsWidget(QWidget):
    """General application settings"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Application settings
        app_group = QGroupBox("🔧 Application Settings")
        app_layout = QFormLayout()
        
        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Tiếng Việt", "中文", "日本語"])
        self.language_combo.currentTextChanged.connect(self.settings_changed.emit)
        app_layout.addRow("Language:", self.language_combo)
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        self.theme_combo.currentTextChanged.connect(self.settings_changed.emit)
        app_layout.addRow("Theme:", self.theme_combo)
        
        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(0, 60)
        self.autosave_spin.setValue(5)
        self.autosave_spin.setSuffix(" minutes")
        self.autosave_spin.setSpecialValueText("Disabled")
        self.autosave_spin.valueChanged.connect(self.settings_changed.emit)
        app_layout.addRow("Auto-save interval:", self.autosave_spin)
        
        # Check for updates
        self.check_updates_cb = QCheckBox("Check for updates on startup")
        self.check_updates_cb.setChecked(True)
        self.check_updates_cb.toggled.connect(self.settings_changed.emit)
        app_layout.addRow(self.check_updates_cb)
        
        # Show splash screen
        self.splash_cb = QCheckBox("Show splash screen on startup")
        self.splash_cb.setChecked(True)
        self.splash_cb.toggled.connect(self.settings_changed.emit)
        app_layout.addRow(self.splash_cb)
        
        # Minimize to tray
        self.tray_cb = QCheckBox("Minimize to system tray")
        self.tray_cb.toggled.connect(self.settings_changed.emit)
        app_layout.addRow(self.tray_cb)
        
        app_group.setLayout(app_layout)
        layout.addWidget(app_group)
        
        # Workspace settings
        workspace_group = QGroupBox("📁 Workspace Settings")
        workspace_layout = QFormLayout()
        
        # Default workspace
        workspace_path_layout = QHBoxLayout()
        self.workspace_path = QLineEdit()
        self.workspace_path.setPlaceholderText("Select default workspace directory...")
        self.workspace_path.textChanged.connect(self.settings_changed.emit)
        
        self.browse_workspace_btn = QPushButton("📁 Browse")
        self.browse_workspace_btn.clicked.connect(self.browse_workspace)
        
        workspace_path_layout.addWidget(self.workspace_path)
        workspace_path_layout.addWidget(self.browse_workspace_btn)
        workspace_layout.addRow("Default workspace:", workspace_path_layout)
        
        # Recent files limit
        self.recent_files_spin = QSpinBox()
        self.recent_files_spin.setRange(0, 50)
        self.recent_files_spin.setValue(10)
        self.recent_files_spin.setSpecialValueText("Disabled")
        self.recent_files_spin.valueChanged.connect(self.settings_changed.emit)
        workspace_layout.addRow("Recent files limit:", self.recent_files_spin)
        
        # Auto-backup
        self.backup_cb = QCheckBox("Enable automatic backup")
        self.backup_cb.setChecked(True)
        self.backup_cb.toggled.connect(self.settings_changed.emit)
        workspace_layout.addRow(self.backup_cb)
        
        workspace_group.setLayout(workspace_layout)
        layout.addWidget(workspace_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def browse_workspace(self):
        """Browse for workspace directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Workspace Directory", self.workspace_path.text()
        )
        
        if directory:
            self.workspace_path.setText(directory)
            
    def get_settings(self):
        """Get current settings"""
        return {
            'language': self.language_combo.currentText(),
            'theme': self.theme_combo.currentText(),
            'autosave_interval': self.autosave_spin.value(),
            'check_updates': self.check_updates_cb.isChecked(),
            'show_splash': self.splash_cb.isChecked(),
            'minimize_to_tray': self.tray_cb.isChecked(),
            'workspace_path': self.workspace_path.text(),
            'recent_files_limit': self.recent_files_spin.value(),
            'auto_backup': self.backup_cb.isChecked()
        }
        
    def set_settings(self, settings):
        """Set settings values"""
        if 'language' in settings:
            index = self.language_combo.findText(settings['language'])
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
                
        if 'theme' in settings:
            index = self.theme_combo.findText(settings['theme'])
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
                
        if 'autosave_interval' in settings:
            self.autosave_spin.setValue(settings['autosave_interval'])
            
        if 'check_updates' in settings:
            self.check_updates_cb.setChecked(settings['check_updates'])
            
        if 'show_splash' in settings:
            self.splash_cb.setChecked(settings['show_splash'])
            
        if 'minimize_to_tray' in settings:
            self.tray_cb.setChecked(settings['minimize_to_tray'])
            
        if 'workspace_path' in settings:
            self.workspace_path.setText(settings['workspace_path'])
            
        if 'recent_files_limit' in settings:
            self.recent_files_spin.setValue(settings['recent_files_limit'])
            
        if 'auto_backup' in settings:
            self.backup_cb.setChecked(settings['auto_backup'])

class DeviceSettingsWidget(QWidget):
    """Device-related settings"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Connection settings
        connection_group = QGroupBox("🔌 Connection Settings")
        connection_layout = QFormLayout()
        
        # ADB path
        adb_path_layout = QHBoxLayout()
        self.adb_path = QLineEdit()
        self.adb_path.setPlaceholderText("Auto-detect ADB path...")
        self.adb_path.textChanged.connect(self.settings_changed.emit)
        
        self.browse_adb_btn = QPushButton("📁 Browse")
        self.browse_adb_btn.clicked.connect(self.browse_adb)
        
        self.detect_adb_btn = QPushButton("🔍 Auto-detect")
        self.detect_adb_btn.clicked.connect(self.detect_adb)
        
        adb_path_layout.addWidget(self.adb_path)
        adb_path_layout.addWidget(self.browse_adb_btn)
        adb_path_layout.addWidget(self.detect_adb_btn)
        connection_layout.addRow("ADB Path:", adb_path_layout)
        
        # Connection timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(10)
        self.timeout_spin.setSuffix(" seconds")
        self.timeout_spin.valueChanged.connect(self.settings_changed.emit)
        connection_layout.addRow("Connection timeout:", self.timeout_spin)
        
        # Retry attempts
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(0, 10)
        self.retry_spin.setValue(3)
        self.retry_spin.valueChanged.connect(self.settings_changed.emit)
        connection_layout.addRow("Retry attempts:", self.retry_spin)
        
        # Auto-refresh interval
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(0, 60)
        self.refresh_spin.setValue(5)
        self.refresh_spin.setSuffix(" seconds")
        self.refresh_spin.setSpecialValueText("Disabled")
        self.refresh_spin.valueChanged.connect(self.settings_changed.emit)
        connection_layout.addRow("Auto-refresh devices:", self.refresh_spin)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Execution settings
        execution_group = QGroupBox("⚡ Execution Settings")
        execution_layout = QFormLayout()
        
        # Default execution mode
        self.execution_mode_combo = QComboBox()
        self.execution_mode_combo.addItems(["Sequential", "Parallel", "Single Device"])
        self.execution_mode_combo.currentTextChanged.connect(self.settings_changed.emit)
        execution_layout.addRow("Default execution mode:", self.execution_mode_combo)
        
        # Default delay
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.0, 10.0)
        self.delay_spin.setValue(1.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setSuffix(" seconds")
        self.delay_spin.valueChanged.connect(self.settings_changed.emit)
        execution_layout.addRow("Default delay:", self.delay_spin)
        
        # Screenshot on error
        self.screenshot_cb = QCheckBox("Take screenshot on error")
        self.screenshot_cb.setChecked(True)
        self.screenshot_cb.toggled.connect(self.settings_changed.emit)
        execution_layout.addRow(self.screenshot_cb)
        
        # Stop on first error
        self.stop_on_error_cb = QCheckBox("Stop execution on first error")
        self.stop_on_error_cb.toggled.connect(self.settings_changed.emit)
        execution_layout.addRow(self.stop_on_error_cb)
        
        execution_group.setLayout(execution_layout)
        layout.addWidget(execution_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def browse_adb(self):
        """Browse for ADB executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ADB Executable", "",
            "Executable Files (*.exe);;All Files (*)"
        )
        
        if file_path:
            self.adb_path.setText(file_path)
            
    def detect_adb(self):
        """Auto-detect ADB path"""
        # Common ADB locations
        common_paths = [
            r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
            r"C:\Android\android-sdk\platform-tools\adb.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools\adb.exe",
            "adb.exe"  # In PATH
        ]
        
        for path in common_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                self.adb_path.setText(expanded_path)
                QMessageBox.information(self, "Success", f"ADB found at: {expanded_path}")
                return
                
        # Try to find in PATH
        import shutil
        adb_path = shutil.which("adb")
        if adb_path:
            self.adb_path.setText(adb_path)
            QMessageBox.information(self, "Success", f"ADB found in PATH: {adb_path}")
        else:
            QMessageBox.warning(self, "Not Found", "ADB not found. Please install Android SDK or specify path manually.")
            
    def get_settings(self):
        """Get current settings"""
        return {
            'adb_path': self.adb_path.text(),
            'connection_timeout': self.timeout_spin.value(),
            'retry_attempts': self.retry_spin.value(),
            'auto_refresh_interval': self.refresh_spin.value(),
            'default_execution_mode': self.execution_mode_combo.currentText(),
            'default_delay': self.delay_spin.value(),
            'screenshot_on_error': self.screenshot_cb.isChecked(),
            'stop_on_error': self.stop_on_error_cb.isChecked()
        }
        
    def set_settings(self, settings):
        """Set settings values"""
        if 'adb_path' in settings:
            self.adb_path.setText(settings['adb_path'])
            
        if 'connection_timeout' in settings:
            self.timeout_spin.setValue(settings['connection_timeout'])
            
        if 'retry_attempts' in settings:
            self.retry_spin.setValue(settings['retry_attempts'])
            
        if 'auto_refresh_interval' in settings:
            self.refresh_spin.setValue(settings['auto_refresh_interval'])
            
        if 'default_execution_mode' in settings:
            index = self.execution_mode_combo.findText(settings['default_execution_mode'])
            if index >= 0:
                self.execution_mode_combo.setCurrentIndex(index)
                
        if 'default_delay' in settings:
            self.delay_spin.setValue(settings['default_delay'])
            
        if 'screenshot_on_error' in settings:
            self.screenshot_cb.setChecked(settings['screenshot_on_error'])
            
        if 'stop_on_error' in settings:
            self.stop_on_error_cb.setChecked(settings['stop_on_error'])

class UISettingsWidget(QWidget):
    """UI appearance settings"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Font settings
        font_group = QGroupBox("🔤 Font Settings")
        font_layout = QFormLayout()
        
        # Editor font
        editor_font_layout = QHBoxLayout()
        self.editor_font_label = QLabel("Consolas, 10pt")
        self.editor_font_btn = QPushButton("📝 Change")
        self.editor_font_btn.clicked.connect(self.change_editor_font)
        
        editor_font_layout.addWidget(self.editor_font_label)
        editor_font_layout.addWidget(self.editor_font_btn)
        font_layout.addRow("Editor font:", editor_font_layout)
        
        # UI font
        ui_font_layout = QHBoxLayout()
        self.ui_font_label = QLabel("Arial, 9pt")
        self.ui_font_btn = QPushButton("📝 Change")
        self.ui_font_btn.clicked.connect(self.change_ui_font)
        
        ui_font_layout.addWidget(self.ui_font_label)
        ui_font_layout.addWidget(self.ui_font_btn)
        font_layout.addRow("UI font:", ui_font_layout)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Color settings
        color_group = QGroupBox("🎨 Color Settings")
        color_layout = QFormLayout()
        
        # Accent color
        accent_color_layout = QHBoxLayout()
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setFixedSize(50, 30)
        self.accent_color_btn.setStyleSheet("background-color: #4a90e2; border: 2px solid #555555; border-radius: 4px;")
        self.accent_color_btn.clicked.connect(self.change_accent_color)
        
        accent_color_layout.addWidget(self.accent_color_btn)
        accent_color_layout.addStretch()
        color_layout.addRow("Accent color:", accent_color_layout)
        
        # Success color
        success_color_layout = QHBoxLayout()
        self.success_color_btn = QPushButton()
        self.success_color_btn.setFixedSize(50, 30)
        self.success_color_btn.setStyleSheet("background-color: #4caf50; border: 1px solid #ccc;")
        self.success_color_btn.clicked.connect(self.change_success_color)
        
        success_color_layout.addWidget(self.success_color_btn)
        success_color_layout.addStretch()
        color_layout.addRow("Success color:", success_color_layout)
        
        # Error color
        error_color_layout = QHBoxLayout()
        self.error_color_btn = QPushButton()
        self.error_color_btn.setFixedSize(50, 30)
        self.error_color_btn.setStyleSheet("background-color: #f44336; border: 1px solid #ccc;")
        self.error_color_btn.clicked.connect(self.change_error_color)
        
        error_color_layout.addWidget(self.error_color_btn)
        error_color_layout.addStretch()
        color_layout.addRow("Error color:", error_color_layout)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Layout settings
        layout_group = QGroupBox("📐 Layout Settings")
        layout_layout = QFormLayout()
        
        # Sidebar width
        self.sidebar_width_spin = QSpinBox()
        self.sidebar_width_spin.setRange(150, 400)
        self.sidebar_width_spin.setValue(250)
        self.sidebar_width_spin.setSuffix(" px")
        self.sidebar_width_spin.valueChanged.connect(self.settings_changed.emit)
        layout_layout.addRow("Sidebar width:", self.sidebar_width_spin)
        
        # Show toolbar
        self.toolbar_cb = QCheckBox("Show toolbar")
        self.toolbar_cb.setChecked(True)
        self.toolbar_cb.toggled.connect(self.settings_changed.emit)
        layout_layout.addRow(self.toolbar_cb)
        
        # Show status bar
        self.statusbar_cb = QCheckBox("Show status bar")
        self.statusbar_cb.setChecked(True)
        self.statusbar_cb.toggled.connect(self.settings_changed.emit)
        layout_layout.addRow(self.statusbar_cb)
        
        # Animation
        self.animation_cb = QCheckBox("Enable animations")
        self.animation_cb.setChecked(True)
        self.animation_cb.toggled.connect(self.settings_changed.emit)
        layout_layout.addRow(self.animation_cb)
        
        layout_group.setLayout(layout_layout)
        layout.addWidget(layout_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def change_editor_font(self):
        """Change editor font"""
        current_font = QFont("Consolas", 10)
        font, ok = QFontDialog.getFont(current_font, self)
        
        if ok:
            font_text = f"{font.family()}, {font.pointSize()}pt"
            self.editor_font_label.setText(font_text)
            self.settings_changed.emit()
            
    def change_ui_font(self):
        """Change UI font"""
        current_font = QFont("Arial", 9)
        font, ok = QFontDialog.getFont(current_font, self)
        
        if ok:
            font_text = f"{font.family()}, {font.pointSize()}pt"
            self.ui_font_label.setText(font_text)
            self.settings_changed.emit()
            
    def change_accent_color(self):
        """Change accent color"""
        color = QColorDialog.getColor(QColor("#2196f3"), self)
        
        if color.isValid():
            self.accent_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self.settings_changed.emit()
            
    def change_success_color(self):
        """Change success color"""
        color = QColorDialog.getColor(QColor("#4caf50"), self)
        
        if color.isValid():
            self.success_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self.settings_changed.emit()
            
    def change_error_color(self):
        """Change error color"""
        color = QColorDialog.getColor(QColor("#f44336"), self)
        
        if color.isValid():
            self.error_color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
            self.settings_changed.emit()
            
    def get_settings(self):
        """Get current settings"""
        return {
            'editor_font': self.editor_font_label.text(),
            'ui_font': self.ui_font_label.text(),
            'accent_color': self.accent_color_btn.styleSheet().split("background-color: ")[1].split(";")[0],
            'success_color': self.success_color_btn.styleSheet().split("background-color: ")[1].split(";")[0],
            'error_color': self.error_color_btn.styleSheet().split("background-color: ")[1].split(";")[0],
            'sidebar_width': self.sidebar_width_spin.value(),
            'show_toolbar': self.toolbar_cb.isChecked(),
            'show_statusbar': self.statusbar_cb.isChecked(),
            'enable_animations': self.animation_cb.isChecked()
        }
        
    def set_settings(self, settings):
        """Set settings values"""
        if 'editor_font' in settings:
            self.editor_font_label.setText(settings['editor_font'])
            
        if 'ui_font' in settings:
            self.ui_font_label.setText(settings['ui_font'])
            
        if 'accent_color' in settings:
            self.accent_color_btn.setStyleSheet(f"background-color: {settings['accent_color']}; border: 1px solid #ccc;")
            
        if 'success_color' in settings:
            self.success_color_btn.setStyleSheet(f"background-color: {settings['success_color']}; border: 1px solid #ccc;")
            
        if 'error_color' in settings:
            self.error_color_btn.setStyleSheet(f"background-color: {settings['error_color']}; border: 1px solid #ccc;")
            
        if 'sidebar_width' in settings:
            self.sidebar_width_spin.setValue(settings['sidebar_width'])
            
        if 'show_toolbar' in settings:
            self.toolbar_cb.setChecked(settings['show_toolbar'])
            
        if 'show_statusbar' in settings:
            self.statusbar_cb.setChecked(settings['show_statusbar'])
            
        if 'enable_animations' in settings:
            self.animation_cb.setChecked(settings['enable_animations'])

class AdvancedSettingsWidget(QWidget):
    """Advanced settings"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Logging settings
        logging_group = QGroupBox("📝 Logging Settings")
        logging_layout = QFormLayout()
        
        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.currentTextChanged.connect(self.settings_changed.emit)
        logging_layout.addRow("Log level:", self.log_level_combo)
        
        # Log file path
        log_path_layout = QHBoxLayout()
        self.log_path = QLineEdit()
        self.log_path.setText("logs/app.log")
        self.log_path.textChanged.connect(self.settings_changed.emit)
        
        self.browse_log_btn = QPushButton("📁 Browse")
        self.browse_log_btn.clicked.connect(self.browse_log_path)
        
        log_path_layout.addWidget(self.log_path)
        log_path_layout.addWidget(self.browse_log_btn)
        logging_layout.addRow("Log file:", log_path_layout)
        
        # Max log file size
        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(1, 1000)
        self.log_size_spin.setValue(10)
        self.log_size_spin.setSuffix(" MB")
        self.log_size_spin.valueChanged.connect(self.settings_changed.emit)
        logging_layout.addRow("Max log file size:", self.log_size_spin)
        
        # Log rotation
        self.log_rotation_spin = QSpinBox()
        self.log_rotation_spin.setRange(1, 50)
        self.log_rotation_spin.setValue(5)
        self.log_rotation_spin.setSuffix(" files")
        self.log_rotation_spin.valueChanged.connect(self.settings_changed.emit)
        logging_layout.addRow("Log rotation count:", self.log_rotation_spin)
        
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)
        
        # Performance settings
        performance_group = QGroupBox("⚡ Performance Settings")
        performance_layout = QFormLayout()
        
        # Thread pool size
        self.thread_pool_spin = QSpinBox()
        self.thread_pool_spin.setRange(1, 20)
        self.thread_pool_spin.setValue(4)
        self.thread_pool_spin.valueChanged.connect(self.settings_changed.emit)
        performance_layout.addRow("Thread pool size:", self.thread_pool_spin)
        
        # Memory limit
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(100, 4000)
        self.memory_limit_spin.setValue(1000)
        self.memory_limit_spin.setSuffix(" MB")
        self.memory_limit_spin.valueChanged.connect(self.settings_changed.emit)
        performance_layout.addRow("Memory limit:", self.memory_limit_spin)
        
        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 500)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" MB")
        self.cache_size_spin.valueChanged.connect(self.settings_changed.emit)
        performance_layout.addRow("Cache size:", self.cache_size_spin)
        
        performance_group.setLayout(performance_layout)
        layout.addWidget(performance_group)
        
        # Debug settings
        debug_group = QGroupBox("🐛 Debug Settings")
        debug_layout = QFormLayout()
        
        # Debug mode
        self.debug_mode_cb = QCheckBox("Enable debug mode")
        self.debug_mode_cb.toggled.connect(self.settings_changed.emit)
        debug_layout.addRow(self.debug_mode_cb)
        
        # Verbose logging
        self.verbose_cb = QCheckBox("Verbose logging")
        self.verbose_cb.toggled.connect(self.settings_changed.emit)
        debug_layout.addRow(self.verbose_cb)
        
        # Show internal errors
        self.show_errors_cb = QCheckBox("Show internal errors")
        self.show_errors_cb.toggled.connect(self.settings_changed.emit)
        debug_layout.addRow(self.show_errors_cb)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def browse_log_path(self):
        """Browse for log file path"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Log File", self.log_path.text(),
            "Log Files (*.log);;All Files (*)"
        )
        
        if file_path:
            self.log_path.setText(file_path)
            
    def get_settings(self):
        """Get current settings"""
        return {
            'log_level': self.log_level_combo.currentText(),
            'log_file_path': self.log_path.text(),
            'max_log_size': self.log_size_spin.value(),
            'log_rotation_count': self.log_rotation_spin.value(),
            'thread_pool_size': self.thread_pool_spin.value(),
            'memory_limit': self.memory_limit_spin.value(),
            'cache_size': self.cache_size_spin.value(),
            'debug_mode': self.debug_mode_cb.isChecked(),
            'verbose_logging': self.verbose_cb.isChecked(),
            'show_internal_errors': self.show_errors_cb.isChecked()
        }
        
    def set_settings(self, settings):
        """Set settings values"""
        if 'log_level' in settings:
            index = self.log_level_combo.findText(settings['log_level'])
            if index >= 0:
                self.log_level_combo.setCurrentIndex(index)
                
        if 'log_file_path' in settings:
            self.log_path.setText(settings['log_file_path'])
            
        if 'max_log_size' in settings:
            self.log_size_spin.setValue(settings['max_log_size'])
            
        if 'log_rotation_count' in settings:
            self.log_rotation_spin.setValue(settings['log_rotation_count'])
            
        if 'thread_pool_size' in settings:
            self.thread_pool_spin.setValue(settings['thread_pool_size'])
            
        if 'memory_limit' in settings:
            self.memory_limit_spin.setValue(settings['memory_limit'])
            
        if 'cache_size' in settings:
            self.cache_size_spin.setValue(settings['cache_size'])
            
        if 'debug_mode' in settings:
            self.debug_mode_cb.setChecked(settings['debug_mode'])
            
        if 'verbose_logging' in settings:
            self.verbose_cb.setChecked(settings['verbose_logging'])
            
        if 'show_internal_errors' in settings:
            self.show_errors_cb.setChecked(settings['show_internal_errors'])

class SettingsWidget(QWidget):
    """Main settings widget"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.setup_connections()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("⚙️ Settings")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Action buttons
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        
        self.export_btn = QPushButton("📤 Export")
        self.import_btn = QPushButton("📥 Import")
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.export_btn)
        header_layout.addWidget(self.import_btn)
        header_layout.addWidget(self.reset_btn)
        header_layout.addWidget(self.save_btn)
        
        layout.addLayout(header_layout)
        
        # Settings tabs
        self.tabs = QTabWidget()
        
        # General settings
        self.general_settings = GeneralSettingsWidget()
        self.tabs.addTab(self.general_settings, "🔧 General")
        
        # Device settings
        self.device_settings = DeviceSettingsWidget()
        self.tabs.addTab(self.device_settings, "📱 Devices")
        
        # UI settings
        self.ui_settings = UISettingsWidget()
        self.tabs.addTab(self.ui_settings, "🎨 Appearance")
        
        # Advanced settings
        self.advanced_settings = AdvancedSettingsWidget()
        self.tabs.addTab(self.advanced_settings, "⚙️ Advanced")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Buttons
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.export_btn.clicked.connect(self.export_settings)
        self.import_btn.clicked.connect(self.import_settings)
        
        # Settings changed signals
        self.general_settings.settings_changed.connect(self.settings_changed.emit)
        self.device_settings.settings_changed.connect(self.settings_changed.emit)
        self.ui_settings.settings_changed.connect(self.settings_changed.emit)
        self.advanced_settings.settings_changed.connect(self.settings_changed.emit)
        
    def load_settings(self):
        """Load settings from config manager"""
        if not self.config_manager:
            return
            
        try:
            config = self.config_manager.get_config()
            
            # Load each category
            if 'general' in config:
                self.general_settings.set_settings(config['general'])
                
            if 'devices' in config:
                self.device_settings.set_settings(config['devices'])
                
            if 'ui' in config:
                self.ui_settings.set_settings(config['ui'])
                
            if 'advanced' in config:
                self.advanced_settings.set_settings(config['advanced'])
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load settings: {str(e)}")
            
    def save_settings(self):
        """Save current settings"""
        if not self.config_manager:
            QMessageBox.warning(self, "Error", "No config manager available")
            return
            
        try:
            # Collect all settings
            settings = {
                'general': self.general_settings.get_settings(),
                'devices': self.device_settings.get_settings(),
                'ui': self.ui_settings.get_settings(),
                'advanced': self.advanced_settings.get_settings()
            }
            
            # Save to config manager
            self.config_manager.update_config(settings)
            self.config_manager.save_config()
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.config_manager:
                self.config_manager.reset_config()
                self.load_settings()
                QMessageBox.information(self, "Success", "Settings reset to defaults!")
                
    def export_settings(self):
        """Export settings to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "settings.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                settings = {
                    'general': self.general_settings.get_settings(),
                    'devices': self.device_settings.get_settings(),
                    'ui': self.ui_settings.get_settings(),
                    'advanced': self.advanced_settings.get_settings()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Success", f"Settings exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export settings: {str(e)}")
                
    def import_settings(self):
        """Import settings from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # Apply settings
                if 'general' in settings:
                    self.general_settings.set_settings(settings['general'])
                    
                if 'devices' in settings:
                    self.device_settings.set_settings(settings['devices'])
                    
                if 'ui' in settings:
                    self.ui_settings.set_settings(settings['ui'])
                    
                if 'advanced' in settings:
                    self.advanced_settings.set_settings(settings['advanced'])
                    
                QMessageBox.information(self, "Success", f"Settings imported from {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import settings: {str(e)}")