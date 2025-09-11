#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Package for Android Automation GUI
Version: 1.0.0
Author: Android Automation Team

This package contains all UI components for the Android automation application.
"""

from .main_window import MainWindow
from .device_management import DeviceManagementWidget
from .flow_editor import FlowEditorWidget
from .execution_control import ExecutionControlWidget
from .settings import SettingsWidget

__all__ = [
    'MainWindow',
    'DeviceManagementWidget', 
    'FlowEditorWidget',
    'ExecutionControlWidget',
    'SettingsWidget'
]

__version__ = "1.0.0"
__author__ = "Android Automation Team"