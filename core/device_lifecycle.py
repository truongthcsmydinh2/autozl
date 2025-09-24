#!/usr/bin/env python3
"""
Device Lifecycle Management

Xử lý vòng đời uiautomator2 để tránh lỗi "UiAutomationService already registered"
Theo task T1 trong task.md
"""

import time
import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def adb_s(serial: str, command: str) -> str:
    """Execute ADB command for specific device serial"""
    try:
        cmd = f"adb -s {serial} {command}"
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode != 0:
            logger.warning(f"ADB command failed: {cmd}, stderr: {result.stderr}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"ADB command timeout: {cmd}")
        raise
    except Exception as e:
        logger.error(f"ADB command error: {cmd}, error: {e}")
        raise

def kill_uiautomator_processes(serial: str) -> bool:
    """Kill all uiautomator related processes"""
    try:
        logger.info(f"Killing uiautomator processes on {serial}")
        
        # Kill uiautomator processes
        adb_s(serial, "shell 'pidof uiautomator | xargs -r kill -9'")
        
        # Kill atx-agent processes
        adb_s(serial, "shell 'pidof atx-agent | xargs -r kill -9'")
        
        # Force stop uiautomator packages
        adb_s(serial, "shell am force-stop com.github.uiautomator")
        adb_s(serial, "shell am force-stop com.github.uiautomator.test")
        
        logger.info(f"Successfully killed uiautomator processes on {serial}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to kill uiautomator processes on {serial}: {e}")
        return False

def start_atx_agent(serial: str) -> bool:
    """Start atx-agent server"""
    try:
        logger.info(f"Starting atx-agent on {serial}")
        
        # Stop any existing atx-agent
        adb_s(serial, "shell '/data/local/tmp/atx-agent server --stop || true'")
        time.sleep(0.5)
        
        # Start atx-agent in daemon mode
        adb_s(serial, "shell '/data/local/tmp/atx-agent server -d'")
        
        logger.info(f"Successfully started atx-agent on {serial}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start atx-agent on {serial}: {e}")
        return False

def check_atx_agent_ready(serial: str, timeout: int = 5) -> bool:
    """Check if atx-agent is ready on port 7912"""
    try:
        logger.info(f"Checking atx-agent readiness on {serial}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if port 7912 is listening
                result = adb_s(serial, "shell 'netstat -an | grep :7912'")
                if "7912" in result:
                    logger.info(f"atx-agent ready on {serial}")
                    return True
            except:
                pass
            time.sleep(0.5)
        
        logger.warning(f"atx-agent not ready on {serial} after {timeout}s")
        return False
        
    except Exception as e:
        logger.error(f"Failed to check atx-agent readiness on {serial}: {e}")
        return False

def ensure_uia2_ready(serial: str, retries: int = 2) -> bool:
    """
    Ensure uiautomator2 is ready for use
    
    Args:
        serial: Device serial number
        retries: Number of retry attempts
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        RuntimeError: If unable to prepare uia2 after all retries
    """
    logger.info(f"Ensuring uia2 ready for device {serial} (retries: {retries})")
    
    for attempt in range(retries + 1):
        try:
            logger.info(f"Attempt {attempt + 1}/{retries + 1} for {serial}")
            
            # Step 1: Kill existing processes
            if not kill_uiautomator_processes(serial):
                logger.warning(f"Failed to kill processes on attempt {attempt + 1}")
                if attempt < retries:
                    time.sleep(1.5)
                    continue
            
            # Step 2: Wait a bit for cleanup
            time.sleep(1)
            
            # Step 3: Start atx-agent
            if not start_atx_agent(serial):
                logger.warning(f"Failed to start atx-agent on attempt {attempt + 1}")
                if attempt < retries:
                    time.sleep(1.5)
                    continue
            
            # Step 4: Check if atx-agent is ready
            if not check_atx_agent_ready(serial):
                logger.warning(f"atx-agent not ready on attempt {attempt + 1}")
                if attempt < retries:
                    time.sleep(1.5)
                    continue
            
            logger.info(f"Successfully prepared uia2 for {serial}")
            return True
            
        except Exception as e:
            logger.error(f"Error on attempt {attempt + 1} for {serial}: {e}")
            if attempt < retries:
                time.sleep(1.5)
                continue
    
    error_msg = f"uia2 not ready for {serial} after {retries + 1} attempts"
    logger.error(error_msg)
    raise RuntimeError(error_msg)

def cleanup_device(serial: str) -> bool:
    """Cleanup device resources"""
    try:
        logger.info(f"Cleaning up device {serial}")
        
        # Kill processes
        kill_uiautomator_processes(serial)
        
        # Stop atx-agent
        adb_s(serial, "shell '/data/local/tmp/atx-agent server --stop || true'")
        
        logger.info(f"Successfully cleaned up device {serial}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to cleanup device {serial}: {e}")
        return False

if __name__ == "__main__":
    # Test script
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) != 2:
        print("Usage: python device_lifecycle.py <device_serial>")
        sys.exit(1)
    
    serial = sys.argv[1]
    
    try:
        ensure_uia2_ready(serial)
        print(f"✅ Device {serial} is ready")
    except RuntimeError as e:
        print(f"❌ Failed to prepare device {serial}: {e}")
        sys.exit(1)