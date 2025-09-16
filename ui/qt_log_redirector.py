from PyQt6.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication
import sys
import io
import queue
import threading
from datetime import datetime

class QtLogRedirector(QObject):
    """Redirects stdout/stderr to Qt signals for display in Terminal Log tab"""
    
    # Signal emitted when log is received
    log_received = pyqtSignal(str, str)  # message, level
    
    def __init__(self):
        super().__init__()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.log_queue = queue.Queue()
        self.is_redirecting = False
        
        # Timer to process log queue
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_log_queue)
        self.timer.start(100)  # Process every 100ms
        
    def start_redirection(self):
        """Start redirecting stdout and stderr"""
        if self.is_redirecting:
            return
            
        try:
            # Store original streams
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr
            
            # Create redirectors with original streams
            self.stdout_redirector = StreamRedirector(self.log_queue, "stdout", self.original_stdout)
            self.stderr_redirector = StreamRedirector(self.log_queue, "stderr", self.original_stderr)
            
            # Replace system streams
            sys.stdout = self.stdout_redirector
            sys.stderr = self.stderr_redirector
            
            # Start processing timer
            self.timer.start(100)  # Process queue every 100ms
            
            self.is_redirecting = True
            self.log_received.emit("[REDIRECTOR] Started capturing stdout/stderr", "system")
            
        except Exception as e:
            self.log_received.emit(f"[REDIRECTOR ERROR] Failed to start redirection: {str(e)}", "error")
            
    def stop_redirection(self):
        """Stop redirecting stdout and stderr"""
        if not self.is_redirecting:
            return
            
        try:
            # Stop timer
            self.timer.stop()
            
            # Restore original streams
            if self.original_stdout:
                sys.stdout = self.original_stdout
            if self.original_stderr:
                sys.stderr = self.original_stderr
                
            # Clean up redirectors
            self.stdout_redirector = None
            self.stderr_redirector = None
            
            # Process remaining messages in queue
            self.process_log_queue()
            
            self.is_redirecting = False
            self.log_received.emit("[REDIRECTOR] Stopped capturing stdout/stderr", "system")
            
        except Exception as e:
            # Use original stderr if available, otherwise print to console
            error_msg = f"[REDIRECTOR ERROR] Failed to stop redirection: {str(e)}"
            if self.original_stderr:
                self.original_stderr.write(error_msg + "\n")
            else:
                print(error_msg)
                
    def process_log_queue(self):
        """Process logs from queue and emit signals"""
        try:
            while not self.log_queue.empty():
                message, level = self.log_queue.get_nowait()
                # Emit signal to Terminal Log tab
                self.log_received.emit(message, level)
        except queue.Empty:
            pass
                
    def write_log(self, message: str, level: str = "info"):
        """Manually write a log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_received.emit(formatted_message, level)
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_redirection()


class StreamRedirector(io.TextIOBase):
    """Custom stream redirector that captures output and puts it in a queue while preserving original output"""
    
    def __init__(self, log_queue: queue.Queue, stream_type: str, original_stream):
        super().__init__()
        self.log_queue = log_queue
        self.stream_type = stream_type
        self.original_stream = original_stream
        self.buffer = ""
        self.lock = threading.Lock()
        
    def write(self, text: str) -> int:
        """Write text to both original stream and redirector queue"""
        if not text:
            return 0
            
        # First, write to original stream to preserve terminal output
        try:
            if self.original_stream and hasattr(self.original_stream, 'write'):
                self.original_stream.write(text)
                self.original_stream.flush()
        except Exception:
            # Silently ignore errors to prevent infinite recursion
            pass
            
        # Then, capture for Qt application
        try:
            with self.lock:
                self.buffer += text
                
                # Process complete lines
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    if line.strip():  # Only queue non-empty lines
                        try:
                            self.log_queue.put_nowait((line, self.stream_type))
                        except queue.Full:
                            # If queue is full, skip this message to prevent blocking
                            pass
                            
        except Exception:
            # Silently ignore errors to prevent infinite recursion
            pass
            
        return len(text)
        
    def flush(self):
        """Flush any remaining buffer content and original stream"""
        # Flush original stream first
        try:
            if self.original_stream and hasattr(self.original_stream, 'flush'):
                self.original_stream.flush()
        except Exception:
            pass
            
        # Then flush our buffer
        try:
            with self.lock:
                if self.buffer.strip():
                    try:
                        self.log_queue.put_nowait((self.buffer, self.stream_type))
                    except queue.Full:
                        pass
                    self.buffer = ""
        except Exception:
            pass
            
    def readable(self) -> bool:
        return False
        
    def writable(self) -> bool:
        return True
        
    def seekable(self) -> bool:
        return False


class LogCapture:
    """Context manager for temporarily capturing logs"""
    
    def __init__(self, redirector: QtLogRedirector):
        self.redirector = redirector
        self.was_redirecting = False
        
    def __enter__(self):
        self.was_redirecting = self.redirector.is_redirecting
        if not self.was_redirecting:
            self.redirector.start_redirection()
        return self.redirector
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.was_redirecting:
            self.redirector.stop_redirection()


class FilteredLogRedirector(QtLogRedirector):
    """Extended log redirector with filtering capabilities"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filters = []
        self.log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        
    def add_filter(self, filter_func):
        """Add a filter function that returns True if message should be logged"""
        self.filters.append(filter_func)
        
    def remove_filter(self, filter_func):
        """Remove a filter function"""
        if filter_func in self.filters:
            self.filters.remove(filter_func)
            
    def clear_filters(self):
        """Clear all filters"""
        self.filters.clear()
        
    def _process_log_queue(self):
        """Process messages from the log queue with filtering"""
        try:
            while not self.log_queue.empty():
                try:
                    message, level = self.log_queue.get_nowait()
                    if message.strip():
                        # Apply filters
                        should_log = True
                        for filter_func in self.filters:
                            try:
                                if not filter_func(message, level):
                                    should_log = False
                                    break
                            except Exception:
                                # If filter fails, log the message anyway
                                continue
                                
                        if should_log:
                            self.log_captured.emit(message.strip(), level)
                except queue.Empty:
                    break
        except Exception as e:
            if self.original_stderr:
                self.original_stderr.write(f"Error processing filtered log queue: {str(e)}\n")
                
    def set_log_level_filter(self, min_level: str):
        """Set minimum log level filter"""
        level_order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if min_level not in level_order:
            return
            
        min_index = level_order.index(min_level)
        
        def level_filter(message: str, stream_type: str) -> bool:
            # Try to extract log level from message
            for i, level in enumerate(level_order):
                if level in message.upper():
                    return i >= min_index
            return True  # If no level found, allow message
            
        # Remove existing level filters
        self.filters = [f for f in self.filters if not hasattr(f, '_is_level_filter')]
        
        # Add new level filter
        level_filter._is_level_filter = True
        self.add_filter(level_filter)