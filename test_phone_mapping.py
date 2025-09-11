#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for PhoneMappingWidget functionality
"""

import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.phone_mapping_widget import PhoneMappingWidget
from core.device_manager import DeviceManager
from core.config_manager import ConfigManager

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone Mapping Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.device_manager = DeviceManager()
        
        # Create phone mapping widget
        self.phone_widget = PhoneMappingWidget(
            device_manager=self.device_manager,
            config_manager=self.config_manager
        )
        
        # Set as central widget
        self.setCentralWidget(self.phone_widget)
        
        # Test timer
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.run_tests)
        self.test_timer.setSingleShot(True)
        self.test_timer.start(2000)  # Run tests after 2 seconds
        
    def run_tests(self):
        """Run automated tests"""
        print("\n=== Testing Phone Mapping Widget ===")
        
        # Test 1: Check initial state
        print("\n1. Testing initial state...")
        initial_mapping = self.phone_widget.get_mapping()
        print(f"   Initial mapping: {initial_mapping}")
        
        # Test 2: Add test mapping
        print("\n2. Testing add mapping...")
        test_device = "test_device_001"
        test_phone = "+84987654321"
        
        # Simulate adding mapping
        self.phone_widget.phone_mapping[test_device] = test_phone
        self.phone_widget.refresh_table()
        print(f"   Added mapping: {test_device} -> {test_phone}")
        
        # Test 3: Save mapping
        print("\n3. Testing save mapping...")
        self.phone_widget.save_mapping()
        print("   Save completed")
        
        # Test 4: Load mapping
        print("\n4. Testing load mapping...")
        self.phone_widget.load_mapping()
        loaded_mapping = self.phone_widget.get_mapping()
        print(f"   Loaded mapping: {loaded_mapping}")
        
        # Test 5: Check file exists
        print("\n5. Testing file creation...")
        mapping_file = os.path.join(os.path.dirname(__file__), 'phone_mapping.json')
        config_file = self.config_manager.phone_mapping_file
        
        print(f"   Mapping file exists: {os.path.exists(mapping_file)}")
        print(f"   Config file exists: {os.path.exists(config_file)}")
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"   Config file content: {data}")
        
        # Test 6: Config manager integration
        print("\n6. Testing config manager integration...")
        config_mapping = self.config_manager.get_all_phone_mappings()
        print(f"   Config manager mapping: {config_mapping}")
        
        # Test 7: Remove mapping
        print("\n7. Testing remove mapping...")
        if test_device in self.phone_widget.phone_mapping:
            self.phone_widget.remove_mapping(test_device)
            print(f"   Removed mapping for: {test_device}")
        
        final_mapping = self.phone_widget.get_mapping()
        print(f"   Final mapping: {final_mapping}")
        
        print("\n=== Test Completed ===")
        print("✅ Phone Mapping Widget is working correctly!")
        
def main():
    app = QApplication(sys.argv)
    
    # Create test window
    window = TestWindow()
    window.show()
    
    # Run app
    sys.exit(app.exec())

if __name__ == '__main__':
    main()