from typing import Dict, List, Optional, Tuple, Any
import subprocess
import time
import json
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DeviceConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNAUTHORIZED = "unauthorized"
    OFFLINE = "offline"
    UNKNOWN = "unknown"

@dataclass
class DeviceInfo:
    """Device information structure"""
    device_id: str
    model: str
    android_version: str
    api_level: int
    status: DeviceConnectionStatus
    screen_resolution: Optional[Tuple[int, int]] = None
    battery_level: Optional[int] = None
    is_screen_on: Optional[bool] = None

class DeviceUtils:
    """Utility class for device management and ADB operations"""
    
    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.connected_devices: Dict[str, DeviceInfo] = {}
    
    async def execute_adb_command(self, device_id: str, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Execute ADB command on specific device"""
        try:
            full_command = [self.adb_path, "-s", device_id] + command
            logger.debug(f"Executing ADB command: {' '.join(full_command)}")
            
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            success = process.returncode == 0
            
            if not success:
                logger.error(f"ADB command failed: {stderr}")
            
            return success, stdout.strip(), stderr.strip()
            
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error(f"ADB command timeout after {timeout}s")
            return False, "", "Command timeout"
        except Exception as e:
            logger.error(f"ADB command error: {str(e)}")
            return False, "", str(e)
    
    async def get_connected_devices(self) -> List[DeviceInfo]:
        """Get list of connected devices"""
        try:
            process = subprocess.run(
                [self.adb_path, "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if process.returncode != 0:
                logger.error(f"Failed to get devices: {process.stderr}")
                return []
            
            devices = []
            lines = process.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        status_str = parts[1]
                        
                        # Map status
                        status_map = {
                            "device": DeviceConnectionStatus.CONNECTED,
                            "offline": DeviceConnectionStatus.OFFLINE,
                            "unauthorized": DeviceConnectionStatus.UNAUTHORIZED
                        }
                        status = status_map.get(status_str, DeviceConnectionStatus.UNKNOWN)
                        
                        # Get device info if connected
                        if status == DeviceConnectionStatus.CONNECTED:
                            device_info = await self._get_device_details(device_id)
                            if device_info:
                                devices.append(device_info)
                        else:
                            devices.append(DeviceInfo(
                                device_id=device_id,
                                model="Unknown",
                                android_version="Unknown",
                                api_level=0,
                                status=status
                            ))
            
            self.connected_devices = {d.device_id: d for d in devices}
            return devices
            
        except Exception as e:
            logger.error(f"Error getting connected devices: {str(e)}")
            return []
    
    async def _get_device_details(self, device_id: str) -> Optional[DeviceInfo]:
        """Get detailed information about a specific device"""
        try:
            # Get model
            success, model, _ = await self.execute_adb_command(
                device_id, ["shell", "getprop", "ro.product.model"]
            )
            if not success:
                model = "Unknown"
            
            # Get Android version
            success, version, _ = await self.execute_adb_command(
                device_id, ["shell", "getprop", "ro.build.version.release"]
            )
            if not success:
                version = "Unknown"
            
            # Get API level
            success, api_str, _ = await self.execute_adb_command(
                device_id, ["shell", "getprop", "ro.build.version.sdk"]
            )
            api_level = int(api_str) if success and api_str.isdigit() else 0
            
            # Get screen resolution
            screen_resolution = await self._get_screen_resolution(device_id)
            
            # Get battery level
            battery_level = await self._get_battery_level(device_id)
            
            # Check if screen is on
            is_screen_on = await self._is_screen_on(device_id)
            
            return DeviceInfo(
                device_id=device_id,
                model=model,
                android_version=version,
                api_level=api_level,
                status=DeviceConnectionStatus.CONNECTED,
                screen_resolution=screen_resolution,
                battery_level=battery_level,
                is_screen_on=is_screen_on
            )
            
        except Exception as e:
            logger.error(f"Error getting device details for {device_id}: {str(e)}")
            return None
    
    async def _get_screen_resolution(self, device_id: str) -> Optional[Tuple[int, int]]:
        """Get device screen resolution"""
        try:
            success, output, _ = await self.execute_adb_command(
                device_id, ["shell", "wm", "size"]
            )
            if success and "Physical size:" in output:
                size_part = output.split("Physical size:")[1].strip()
                if "x" in size_part:
                    width, height = map(int, size_part.split("x"))
                    return (width, height)
            return None
        except Exception:
            return None
    
    async def _get_battery_level(self, device_id: str) -> Optional[int]:
        """Get device battery level"""
        try:
            success, output, _ = await self.execute_adb_command(
                device_id, ["shell", "dumpsys", "battery", "|", "grep", "level"]
            )
            if success and "level:" in output:
                level_str = output.split("level:")[1].strip()
                return int(level_str)
            return None
        except Exception:
            return None
    
    async def _is_screen_on(self, device_id: str) -> Optional[bool]:
        """Check if device screen is on"""
        try:
            success, output, _ = await self.execute_adb_command(
                device_id, ["shell", "dumpsys", "power", "|", "grep", "mHoldingDisplaySuspendBlocker"]
            )
            if success:
                return "true" in output.lower()
            return None
        except Exception:
            return None
    
    async def wake_device(self, device_id: str) -> bool:
        """Wake up device screen"""
        try:
            # Check if already awake
            is_awake = await self._is_screen_on(device_id)
            if is_awake:
                return True
            
            # Wake up device
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "input", "keyevent", "KEYCODE_WAKEUP"]
            )
            
            if success:
                # Wait a bit and verify
                await asyncio.sleep(1)
                return await self._is_screen_on(device_id) or False
            
            return False
            
        except Exception as e:
            logger.error(f"Error waking device {device_id}: {str(e)}")
            return False
    
    async def unlock_device(self, device_id: str, pin: Optional[str] = None) -> bool:
        """Unlock device (swipe up or enter PIN)"""
        try:
            # First wake the device
            if not await self.wake_device(device_id):
                return False
            
            # Swipe up to unlock
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "input", "swipe", "500", "1000", "500", "500"]
            )
            
            if not success:
                return False
            
            await asyncio.sleep(1)
            
            # If PIN is provided, enter it
            if pin:
                success, _, _ = await self.execute_adb_command(
                    device_id, ["shell", "input", "text", pin]
                )
                if success:
                    # Press enter
                    await self.execute_adb_command(
                        device_id, ["shell", "input", "keyevent", "KEYCODE_ENTER"]
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking device {device_id}: {str(e)}")
            return False
    
    async def launch_app(self, device_id: str, package_name: str) -> bool:
        """Launch application by package name"""
        try:
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"]
            )
            
            if success:
                await asyncio.sleep(2)  # Wait for app to launch
                return await self.is_app_running(device_id, package_name)
            
            return False
            
        except Exception as e:
            logger.error(f"Error launching app {package_name} on {device_id}: {str(e)}")
            return False
    
    async def is_app_running(self, device_id: str, package_name: str) -> bool:
        """Check if application is currently running"""
        try:
            success, output, _ = await self.execute_adb_command(
                device_id, ["shell", "dumpsys", "activity", "activities", "|", "grep", package_name]
            )
            
            return success and package_name in output
            
        except Exception as e:
            logger.error(f"Error checking if app {package_name} is running on {device_id}: {str(e)}")
            return False
    
    async def get_current_activity(self, device_id: str) -> Optional[str]:
        """Get current foreground activity"""
        try:
            success, output, _ = await self.execute_adb_command(
                device_id, ["shell", "dumpsys", "activity", "activities", "|", "grep", "mResumedActivity"]
            )
            
            if success and output:
                # Parse activity name from output
                parts = output.split()
                for part in parts:
                    if "/" in part and "." in part:
                        return part
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current activity on {device_id}: {str(e)}")
            return None
    
    async def take_screenshot(self, device_id: str, save_path: str) -> bool:
        """Take screenshot and save to file"""
        try:
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "screencap", "/sdcard/screenshot.png"]
            )
            
            if not success:
                return False
            
            success, _, _ = await self.execute_adb_command(
                device_id, ["pull", "/sdcard/screenshot.png", save_path]
            )
            
            if success:
                # Clean up device screenshot
                await self.execute_adb_command(
                    device_id, ["shell", "rm", "/sdcard/screenshot.png"]
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error taking screenshot on {device_id}: {str(e)}")
            return False
    
    async def tap_coordinate(self, device_id: str, x: int, y: int) -> bool:
        """Tap at specific coordinates"""
        try:
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "input", "tap", str(x), str(y)]
            )
            return success
        except Exception as e:
            logger.error(f"Error tapping at ({x}, {y}) on {device_id}: {str(e)}")
            return False
    
    async def swipe(self, device_id: str, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """Swipe from one point to another"""
        try:
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)]
            )
            return success
        except Exception as e:
            logger.error(f"Error swiping on {device_id}: {str(e)}")
            return False
    
    async def send_text(self, device_id: str, text: str) -> bool:
        """Send text input to device"""
        try:
            # Escape special characters
            escaped_text = text.replace(" ", "%s").replace("&", "\\&")
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "input", "text", escaped_text]
            )
            return success
        except Exception as e:
            logger.error(f"Error sending text '{text}' to {device_id}: {str(e)}")
            return False
    
    async def press_key(self, device_id: str, keycode: str) -> bool:
        """Press a key by keycode"""
        try:
            success, _, _ = await self.execute_adb_command(
                device_id, ["shell", "input", "keyevent", keycode]
            )
            return success
        except Exception as e:
            logger.error(f"Error pressing key {keycode} on {device_id}: {str(e)}")
            return False
    
    def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Get cached device information"""
        return self.connected_devices.get(device_id)
    
    async def refresh_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Refresh and get updated device information"""
        device_info = await self._get_device_details(device_id)
        if device_info:
            self.connected_devices[device_id] = device_info
        return device_info

# Import asyncio at the end to avoid circular imports
import asyncio