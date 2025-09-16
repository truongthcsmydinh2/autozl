#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to verify dual logging functionality
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.qt_log_redirector import StreamRedirector
import queue

def test_dual_logging():
    """Test that logs appear in both terminal and capture queue"""
    
    print("=== Testing Dual Logging ===")
    print("Before redirection - this should appear in terminal only")
    
    # Create log queue and redirector
    log_queue = queue.Queue()
    original_stdout = sys.stdout
    
    # Create dual redirector
    redirector = StreamRedirector(log_queue, "stdout", original_stdout)
    
    # Replace stdout
    sys.stdout = redirector
    
    print("After redirection - this should appear in BOTH terminal and queue")
    print("Testing stdout output with dual logging")
    
    # Restore stdout
    sys.stdout = original_stdout
    
    print("After restoring - this should appear in terminal only")
    
    # Check what was captured in queue
    print("\n=== Captured Messages ===")
    while not log_queue.empty():
        try:
            message, level = log_queue.get_nowait()
            print(f"[CAPTURED] {level}: {message}")
        except queue.Empty:
            break
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_dual_logging()