#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to check ZaloAutomationWidget display
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

# Add ui directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

def test_zalo_widget():
    """Test ZaloAutomationWidget display"""
    try:
        print("🔍 Testing ZaloAutomationWidget display...")
        
        # Import using importlib like in main_window.py
        import importlib
        zalo_module = importlib.import_module('ui.1zalo_automation')
        ZaloAutomationWidget = zalo_module.ZaloAutomationWidget
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = QMainWindow()
        main_window.setWindowTitle("Test Zalo Widget")
        main_window.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add test label
        test_label = QLabel("Test: ZaloAutomationWidget should appear below")
        test_label.setStyleSheet("color: white; background-color: red; padding: 10px; font-size: 16px;")
        layout.addWidget(test_label)
        
        # Create and add ZaloAutomationWidget
        zalo_widget = ZaloAutomationWidget()
        
        # Set explicit background color to test visibility
        zalo_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
        """)
        
        layout.addWidget(zalo_widget)
        
        # Show main window
        main_window.show()
        
        print("✅ ZaloAutomationWidget test window shown")
        print("🔍 Check if you can see the widget content...")
        
        # Run for 10 seconds then exit
        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(10000)  # Exit after 10 seconds
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error testing ZaloAutomationWidget: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_zalo_widget())