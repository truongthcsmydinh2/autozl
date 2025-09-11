#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main GUI Entry Point
Điểm khởi động chính cho ứng dụng Android Automation GUI
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add ui directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
from main_window import MainWindow

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Android Automation GUI")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Android Automation")
    
    # Set default font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Create and show main window
    print("🚀 Android Automation GUI starting...")
    print("📱 Ready to manage Android devices")
    
    try:
        window = MainWindow()
        window.show()
        
        print("✅ Main window loaded successfully")
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Startup Error")
        msg.setText(f"Failed to start application:\n\n{str(e)}")
        msg.exec()
        return 1

if __name__ == "__main__":
    sys.exit(main())