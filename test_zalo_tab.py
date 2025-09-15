#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
from ui.main_window import MainWindow

def test_zalo_tab():
    """Test if Zalo tab displays correctly"""
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    window.show()
    
    print("✅ Main window created and shown")
    
    # Check if zalo_automation page exists
    if "zalo_automation" in window.pages:
        print("✅ zalo_automation page found in pages")
        
        # Get the widget
        zalo_widget = window.pages["zalo_automation"]
        print(f"✅ ZaloAutomationWidget: {type(zalo_widget)}")
        
        # Check if widget has content
        if hasattr(zalo_widget, 'children'):
            children = zalo_widget.children()
            print(f"✅ Widget has {len(children)} children")
            
            # Try to switch to zalo page
            window.switch_page("zalo_automation")
            print("✅ Switched to zalo_automation page")
            
            # Check current widget in stack
            current_widget = window.content_stack.currentWidget()
            print(f"✅ Current widget: {type(current_widget)}")
            
            if current_widget == zalo_widget:
                print("✅ SUCCESS: Zalo tab is displaying correctly!")
            else:
                print("❌ ERROR: Zalo tab is not the current widget")
        else:
            print("❌ ERROR: Widget has no children")
    else:
        print("❌ ERROR: zalo_automation page not found")
        print(f"Available pages: {list(window.pages.keys())}")
    
    # Close after 3 seconds
    QTimer.singleShot(3000, app.quit)
    
    return app.exec()

if __name__ == "__main__":
    test_zalo_tab()