from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QGroupBox, QCheckBox, QComboBox,
    QPlainTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette
from datetime import datetime
from ui.log_worker import LogWorker

class TerminalLogTab(QWidget):
    """Terminal Log tab widget for displaying real-time logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_worker = None
        self.auto_scroll_enabled = True
        self.max_lines = 1000  # Maximum number of lines to keep
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Initialize auto-scroll (enabled by default)
        self.auto_scroll_enabled = True
        
        # Log display area
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout(log_group)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                padding: 4px;
            }
        """)
        
        # Log text area
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(self.max_lines)
        
        # Set monospace font for better log readability
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.log_text.setFont(font)
        
        # Set dark theme for log area
        self.log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                selection-background-color: #264f78;
            }
        """)
        
        log_layout.addWidget(self.status_label)
        log_layout.addWidget(self.log_text)
        
        # Add log group to main layout
        layout.addWidget(log_group, 1)  # Give log area more space
        
        # Initialize log worker
        self.log_worker = LogWorker()
        
    def setup_connections(self):
        """Setup signal connections"""
        # Log worker connections
        if self.log_worker:
            self.log_worker.log_received.connect(self.append_log)
            self.log_worker.error_occurred.connect(self.handle_error)
            

        
    def append_log(self, message: str, level: str = "info"):
        """Append log message to display"""
        if not message.strip():
            return
            
        # Format timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on level
        color_map = {
            "error": "#ff6b6b",
            "stderr": "#ff6b6b", 
            "warning": "#ffa726",
            "info": "#66bb6a",
            "stdout": "#e0e0e0",
            "debug": "#90a4ae",
            "system": "#42a5f5"
        }
        
        color = color_map.get(level.lower(), "#e0e0e0")
        
        # Format message with timestamp and color
        formatted_message = f'<span style="color: #90a4ae;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        
        # Check if we're at the bottom before adding new content
        scrollbar = self.log_text.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
        
        # Append to log area
        self.log_text.appendHtml(formatted_message)
        
        # Auto-scroll if enabled and was at bottom, or force scroll if auto-scroll is enabled
        if self.auto_scroll_enabled and (was_at_bottom or scrollbar.value() == 0):
            # Use QTimer to ensure scroll happens after text is rendered
            QTimer.singleShot(10, lambda: scrollbar.setValue(scrollbar.maximum()))
        
        # Limit log lines to prevent memory issues
        document = self.log_text.document()
        if document.blockCount() > 1000:  # Keep last 1000 lines
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            for _ in range(100):  # Remove first 100 lines
                cursor.select(cursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Remove the newline
            
    def handle_error(self, error_message):
        """Handle error messages"""
        self.append_log(f"[ERROR] {error_message}", "error")
        
        # Update status
        self.status_label.setText("Status: Error occurred")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-size: 12px;
                padding: 4px;
                font-weight: bold;
            }
        """)
        
    def stop_logging(self):
        """Stop logging worker - called when main window closes"""
        if self.log_worker:
            self.log_worker.stop()
            
    def closeEvent(self, event):
        """Handle widget close event"""
        if self.log_worker:
            self.log_worker.stop()
        event.accept()
        
    def __del__(self):
        """Cleanup when widget is destroyed"""
        if self.log_worker:
            self.log_worker.stop()