#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Package
Chứa các core modules cho Android Automation GUI
"""

__version__ = "1.0.0"
__author__ = "Android Automation Team"

from .device_manager import DeviceManager, Device, DeviceWorker
from .flow_manager import FlowManager, FlowExecutionHandler
from .config_manager import ConfigManager

__all__ = [
    'DeviceManager',
    'Device', 
    'DeviceWorker',
    'FlowManager',
    'FlowExecutionHandler',
    'ConfigManager'
]