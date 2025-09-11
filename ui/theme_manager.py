# -*- coding: utf-8 -*-
"""
Theme Manager
Quản lý theme nhất quán cho toàn bộ ứng dụng
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor

class ThemeManager(QObject):
    """Manager cho theme ứng dụng"""
    
    theme_changed = pyqtSignal(str)  # Emit theme name when changed
    
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"
        
    def get_dark_theme_stylesheet(self):
        """Get dark theme stylesheet"""
        return """
            /* Main Application */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 4px;
                font-size: 13px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
                color: #ffffff;
            }
            
            QMenuBar::item:selected {
                background-color: #4a90e2;
                color: #ffffff;
            }
            
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 8px 20px;
                color: #ffffff;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #4a90e2;
                color: #ffffff;
            }
            
            /* Tool Bar */
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                spacing: 6px;
                padding: 6px;
            }
            
            QToolBar QToolButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            
            QToolBar QToolButton:hover {
                background-color: #5ba0f2;
            }
            
            QToolBar QToolButton:pressed {
                background-color: #3a80d2;
            }
            
            QToolBar QToolButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-top: 1px solid #555555;
                font-size: 12px;
            }
            
            QStatusBar QLabel {
                color: #ffffff;
                padding: 4px 12px;
                background-color: transparent;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #4a90e2;
                color: #ffffff;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
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
            
            /* Input Fields */
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border-color: #4a90e2;
            }
            
            /* Combo Box */
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                min-width: 100px;
            }
            
            QComboBox:focus {
                border-color: #4a90e2;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #4a90e2;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                gridline-color: #555555;
                border: 1px solid #555555;
                border-radius: 6px;
                selection-background-color: #4a90e2;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            
            QTableWidget::item:selected {
                background-color: #4a90e2;
                color: #ffffff;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #4a90e2;
                font-weight: bold;
            }
            
            /* Quick Setup Button styles removed */
            
            /* Sidebar Styling */
            SidebarWidget {
                background-color: #2d2d2d;
                border-right: 1px solid #555555;
                min-width: 200px;
                max-width: 300px;
            }
            
            #titleFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #555555;
                padding: 20px 0;
                min-height: 80px;
            }
            
            #titleLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
            }
            
            #navButton {
                background-color: transparent;
                color: #ffffff;
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 14px;
                border-radius: 8px;
                min-height: 40px;
                margin: 2px 8px;
                font-weight: 500;
            }
            
            #navButton:hover {
                background-color: #404040;
                color: #ffffff;
            }
            
            #navButton:checked,
            #navButton[active="true"] {
                background-color: #4a90e2;
                color: #ffffff;
                border-left: 4px solid #ffffff;
                font-weight: bold;
            }
            
            #navButton[active="true"]:hover {
                background-color: #5ba0f2;
            }
            
            #statusFrame {
                background-color: #1e1e1e;
                border-top: 1px solid #555555;
                padding: 10px 0;
                min-height: 60px;
            }
            
            #statusLabel {
                 color: #ffffff;
                 font-size: 12px;
                 padding: 10px;
                 text-align: center;
                 font-weight: 500;
             }
             
             /* Dashboard Styling */
             #pageHeader {
                 color: #ffffff;
                 font-size: 26px;
                 font-weight: bold;
                 padding: 24px;
                 background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #1e1e1e);
                 border-radius: 8px;
                 margin-bottom: 24px;
                 border: 1px solid #4a90e2;
             }
             
             #sectionHeader {
                 color: #ffffff;
                 font-size: 18px;
                 font-weight: bold;
                 padding: 16px 0 12px 0;
                 margin-top: 24px;
                 border-bottom: 1px solid #555555;
             }
             
             #statTitle {
                 color: #ffffff;
                 font-size: 14px;
                 margin-bottom: 10px;
                 font-weight: 500;
             }
             
             #actionButton {
                 background-color: #4a90e2;
                 color: #ffffff;
                 border: none;
                 padding: 14px 28px;
                 border-radius: 8px;
                 font-size: 14px;
                 font-weight: bold;
                 margin: 5px;
                 min-width: 120px;
             }
             
             #actionButton:hover {
                 background-color: #5ba0f2;
             }
             
             #actionButton:pressed {
                 background-color: #3a80d2;
             }
             
             #activityText {
                 color: #cccccc;
                 font-style: italic;
                 padding: 20px;
                 background-color: #2b2b2b;
                 border-radius: 6px;
                 margin-top: 10px;
                 border: 1px solid #404040;
             }
             
             #statCard {
                 background-color: #2d2d2d;
                 border: 2px solid #555555;
                 border-radius: 12px;
                 padding: 24px;
                 margin: 10px;
             }
             
             #placeholderPage {
                 color: #888888;
                 font-size: 18px;
                 background-color: #1e1e1e;
             }
             
             /* List Widgets */
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #4a90e2;
            }
            
            QListWidget::item {
                background-color: #1e1e1e;
                color: #ffffff;
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            
            QListWidget::item:selected {
                background-color: #4a90e2;
                color: #ffffff;
            }
            
            /* Group Box */
            QGroupBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #555555;
                width: 2px;
                height: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #4a90e2;
            }
            
            /* Stacked Widget */
            QStackedWidget {
                background-color: #1e1e1e;
            }
            
            /* Labels */
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #4a90e2;
            }
            
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #555555;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #4a90e2;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                background-color: #1e1e1e;
                border: 1px solid #555555;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555555;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: #4a90e2;
                color: #ffffff;
            }
            
            QTabBar::tab:hover {
                background-color: #404040;
            }
            
            /* Special Buttons */
            QPushButton[buttonType="success"] {
                background-color: #4caf50;
            }
            
            QPushButton[buttonType="success"]:hover {
                background-color: #45a049;
            }
            
            QPushButton[buttonType="danger"] {
                background-color: #f44336;
            }
            
            QPushButton[buttonType="danger"]:hover {
                background-color: #d32f2f;
            }
            
            QPushButton[buttonType="warning"] {
                background-color: #ff9800;
            }
            
            QPushButton[buttonType="warning"]:hover {
                background-color: #f57c00;
            }
        """
    
    def get_light_theme_stylesheet(self):
        """Get light theme stylesheet"""
        return """
            /* Main Application */
            QMainWindow {
                background-color: #ffffff;
                color: #000000;
            }
            
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #f0f0f0;
                color: #000000;
                border: none;
                padding: 4px;
                font-size: 13px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
                color: #000000;
            }
            
            QMenuBar::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QMenu {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 8px 20px;
                color: #000000;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            /* Tool Bar */
            QToolBar {
                background-color: #f0f0f0;
                border: none;
                spacing: 6px;
                padding: 6px;
            }
            
            QToolBar QToolButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            
            QToolBar QToolButton:hover {
                background-color: #106ebe;
            }
            
            QToolBar QToolButton:pressed {
                background-color: #005a9e;
            }
            
            QToolBar QToolButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #f0f0f0;
                color: #000000;
                border-top: 1px solid #cccccc;
                font-size: 12px;
            }
            
            QStatusBar QLabel {
                color: #000000;
                padding: 4px 12px;
                background-color: transparent;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            /* Input Fields */
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border-color: #0078d4;
            }
            
            /* Combo Box */
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                min-width: 100px;
            }
            
            QComboBox:focus {
                border-color: #0078d4;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #000000;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                selection-background-color: #0078d4;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                gridline-color: #cccccc;
                selection-background-color: #0078d4;
            }
            
            QTableWidget::item {
                background-color: #ffffff;
                color: #000000;
                padding: 8px;
                border-bottom: 1px solid #cccccc;
            }
            
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #000000;
                border: 1px solid #cccccc;
                padding: 8px;
                font-weight: bold;
            }
            
            /* List Widgets */
            QListWidget {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                selection-background-color: #0078d4;
            }
            
            QListWidget::item {
                background-color: #ffffff;
                color: #000000;
                padding: 8px;
                border-bottom: 1px solid #cccccc;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            /* Group Box */
            QGroupBox {
                background-color: #f8f8f8;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #000000;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #cccccc;
                width: 2px;
                height: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
            
            /* Stacked Widget */
            QStackedWidget {
                background-color: #ffffff;
            }
            
            /* Labels */
            QLabel {
                color: #000000;
                background-color: transparent;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #cccccc;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #0078d4;
            }
            
            QScrollBar:horizontal {
                background-color: #f0f0f0;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #cccccc;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #0078d4;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #000000;
                padding: 8px 16px;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
            
            /* Special Buttons */
            QPushButton[buttonType="success"] {
                background-color: #107c10;
            }
            
            QPushButton[buttonType="success"]:hover {
                background-color: #0e6e0e;
            }
            
            QPushButton[buttonType="danger"] {
                background-color: #d13438;
            }
            
            QPushButton[buttonType="danger"]:hover {
                background-color: #b92b2f;
            }
            
            QPushButton[buttonType="warning"] {
                background-color: #ff8c00;
            }
            
            QPushButton[buttonType="warning"]:hover {
                background-color: #e67c00;
            }
        """
    
    def apply_theme(self, theme_name="dark"):
        """Apply theme to application"""
        app = QApplication.instance()
        if not app:
            return
            
        self.current_theme = theme_name
        
        if theme_name == "dark":
            stylesheet = self.get_dark_theme_stylesheet()
        elif theme_name == "light":
            stylesheet = self.get_light_theme_stylesheet()
        else:
            stylesheet = self.get_dark_theme_stylesheet()  # Default to dark
            
        app.setStyleSheet(stylesheet)
        self.theme_changed.emit(theme_name)
    
    def get_current_theme(self):
        """Get current theme name"""
        return self.current_theme
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if self.current_theme == "dark":
            self.apply_theme("light")
        else:
            self.apply_theme("dark")