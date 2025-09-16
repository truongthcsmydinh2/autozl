from PyQt6.QtCore import QThread, pyqtSignal, QProcess
import subprocess
import sys
import os
from typing import Optional

class LogWorker(QThread):
    """Worker thread for streaming logs from ADB and internal tool operations"""
    
    log_received = pyqtSignal(str)  # Signal emitted when new log line is received
    error_occurred = pyqtSignal(str)  # Signal emitted when error occurs
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.adb_process: Optional[subprocess.Popen] = None
        self.internal_process: Optional[QProcess] = None
        self.is_running = False
        self.device_id: Optional[str] = None
        
    def set_device_id(self, device_id: str):
        """Set the device ID for ADB logcat"""
        self.device_id = device_id
        
    def start_adb_logcat(self, device_id: Optional[str] = None):
        """Start ADB logcat for specified device"""
        if device_id:
            self.device_id = device_id
            
        if not self.device_id:
            self.error_occurred.emit("No device ID specified for ADB logcat")
            return
            
        try:
            # Stop existing process if running
            self.stop_adb_logcat()
            
            # Start ADB logcat process
            cmd = ["adb", "-s", self.device_id, "logcat", "-v", "time"]
            self.adb_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log_received.emit(f"[ADB] Started logcat for device: {self.device_id}")
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to start ADB logcat: {str(e)}")
            
    def stop_adb_logcat(self):
        """Stop ADB logcat process"""
        if self.adb_process:
            try:
                self.adb_process.terminate()
                self.adb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.adb_process.kill()
            except Exception as e:
                self.error_occurred.emit(f"Error stopping ADB logcat: {str(e)}")
            finally:
                self.adb_process = None
                self.log_received.emit("[ADB] Logcat stopped")
                
    def start_internal_logging(self):
        """Start capturing internal tool logs"""
        try:
            # Create QProcess for internal logging
            self.internal_process = QProcess(self)
            self.internal_process.readyReadStandardOutput.connect(self._read_internal_output)
            self.internal_process.readyReadStandardError.connect(self._read_internal_error)
            
            # Start a simple process to monitor internal logs
            # This can be customized based on specific logging needs
            self.log_received.emit("[INTERNAL] Internal logging started")
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to start internal logging: {str(e)}")
            
    def stop_internal_logging(self):
        """Stop internal logging"""
        if self.internal_process:
            try:
                self.internal_process.kill()
                self.internal_process.waitForFinished(3000)
            except Exception as e:
                self.error_occurred.emit(f"Error stopping internal logging: {str(e)}")
            finally:
                self.internal_process = None
                self.log_received.emit("[INTERNAL] Internal logging stopped")
                
    def _read_internal_output(self):
        """Read standard output from internal process"""
        if self.internal_process:
            data = self.internal_process.readAllStandardOutput().data().decode('utf-8')
            for line in data.strip().split('\n'):
                if line.strip():
                    self.log_received.emit(f"[INTERNAL] {line}")
                    
    def _read_internal_error(self):
        """Read standard error from internal process"""
        if self.internal_process:
            data = self.internal_process.readAllStandardError().data().decode('utf-8')
            for line in data.strip().split('\n'):
                if line.strip():
                    self.log_received.emit(f"[INTERNAL ERROR] {line}")
                    
    def run(self):
        """Main thread execution"""
        self.is_running = True
        
        try:
            # Read ADB logcat output if process is running
            while self.is_running and self.adb_process:
                if self.adb_process.poll() is None:  # Process is still running
                    try:
                        line = self.adb_process.stdout.readline()
                        if line:
                            self.log_received.emit(f"[ADB] {line.strip()}")
                        else:
                            # No more output, small delay to prevent busy waiting
                            self.msleep(100)
                    except Exception as e:
                        self.error_occurred.emit(f"Error reading ADB output: {str(e)}")
                        break
                else:
                    # Process has terminated
                    break
                    
        except Exception as e:
            self.error_occurred.emit(f"LogWorker error: {str(e)}")
        finally:
            self.is_running = False
            
    def stop(self):
        """Stop the worker thread"""
        self.is_running = False
        self.stop_adb_logcat()
        self.stop_internal_logging()
        
        # Wait for thread to finish
        if self.isRunning():
            self.quit()
            self.wait(5000)  # Wait up to 5 seconds
            
    def add_custom_log(self, message: str, level: str = "INFO"):
        """Add custom log message"""
        timestamp = self.get_timestamp()
        formatted_message = f"[{timestamp}] [{level}] {message}"
        self.log_received.emit(formatted_message)
        
    def get_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop()