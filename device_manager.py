#!/usr/bin/env python3
"""
Device Manager - Simple device management for API compatibility
"""

import sys
import json
from utils.data_manager import DataManager

def get_devices():
    """Get all connected devices"""
    try:
        data_manager = DataManager()
        devices = data_manager.get_all_devices()
        print(json.dumps(devices))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1

def connect_device(device_id, device_type):
    """Connect to a device"""
    try:
        # For now, just return success
        result = {
            "device_id": device_id,
            "device_type": device_type,
            "status": "connected",
            "message": "Device connected successfully"
        }
        print(json.dumps(result))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1

def disconnect_device(device_id):
    """Disconnect from a device"""
    try:
        # For now, just return success
        result = {
            "device_id": device_id,
            "status": "disconnected",
            "message": "Device disconnected successfully"
        }
        print(json.dumps(result))
        return 0
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}), file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "get_devices":
        sys.exit(get_devices())
    elif command == "connect_device":
        if len(sys.argv) < 4:
            print(json.dumps({"error": "Device ID and type required"}), file=sys.stderr)
            sys.exit(1)
        sys.exit(connect_device(sys.argv[2], sys.argv[3]))
    elif command == "disconnect_device":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Device ID required"}), file=sys.stderr)
            sys.exit(1)
        sys.exit(disconnect_device(sys.argv[2]))
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}), file=sys.stderr)
        sys.exit(1)