#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Phone Mapping in Main Window
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def test_phone_mapping_in_main_window():
    """Test phone mapping functionality in main window"""
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = MainWindow()
    main_window.show()
    
    # Test timer
    def run_test():
        print("\n=== Testing Phone Mapping in Main Window ===")
        
        # Test 1: Check if phone mapping page exists
        print("\n1. Checking phone mapping page...")
        if hasattr(main_window, 'content_stack'):
            page_count = main_window.content_stack.count()
            print(f"   Total pages in stack: {page_count}")
            
            # Try to switch to phone mapping page
            try:
                main_window.switch_page('phone_mapping')
                current_index = main_window.content_stack.currentIndex()
                current_widget = main_window.content_stack.currentWidget()
                print(f"   Current page index: {current_index}")
                print(f"   Current widget type: {type(current_widget).__name__}")
                
                # Check if it's PhoneMappingWidget
                from ui.phone_mapping_widget import PhoneMappingWidget
                if isinstance(current_widget, PhoneMappingWidget):
                    print("   ✅ PhoneMappingWidget loaded successfully!")
                    
                    # Test widget functionality
                    print("\n2. Testing widget functionality...")
                    initial_mapping = current_widget.get_mapping()
                    print(f"   Initial mapping: {initial_mapping}")
                    
                    # Test add mapping
                    current_widget.phone_mapping['test_main_001'] = '+84123456789'
                    current_widget.refresh_table()
                    current_widget.save_mapping()
                    print("   ✅ Add and save mapping successful!")
                    
                    # Test load mapping
                    current_widget.load_mapping()
                    loaded_mapping = current_widget.get_mapping()
                    print(f"   Loaded mapping: {loaded_mapping}")
                    
                    if 'test_main_001' in loaded_mapping:
                        print("   ✅ Load mapping successful!")
                    
                    # Clean up test data
                    if 'test_main_001' in current_widget.phone_mapping:
                        del current_widget.phone_mapping['test_main_001']
                        current_widget.refresh_table()
                        current_widget.save_mapping()
                        print("   ✅ Cleanup successful!")
                    
                else:
                    print(f"   ❌ Expected PhoneMappingWidget, got {type(current_widget).__name__}")
                    
            except Exception as e:
                print(f"   ❌ Error switching to phone mapping: {e}")
        else:
            print("   ❌ Main window doesn't have content_stack")
        
        print("\n=== Test Completed ===")
        print("✅ Phone Mapping in Main Window test finished!")
        
        # Close application after test
        QTimer.singleShot(1000, app.quit)
    
    # Run test after window is shown
    QTimer.singleShot(2000, run_test)
    
    # Start application
    sys.exit(app.exec())

if __name__ == '__main__':
    test_phone_mapping_in_main_window()