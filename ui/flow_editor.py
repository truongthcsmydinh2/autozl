# -*- coding: utf-8 -*-
"""
Flow Editor UI
Editor cho automation flows với syntax highlighting
"""

import sys
import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QGroupBox, QLineEdit, QComboBox, QTextEdit,
    QProgressBar, QFrame, QSplitter, QMessageBox,
    QFileDialog, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QToolBar, QMenuBar, QMenu, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QFileSystemWatcher
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QAction, QSyntaxHighlighter, QTextCharFormat

try:
    from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerJSON
except ImportError:
    # Fallback if QScintilla not available
    QsciScintilla = QTextEdit
    QsciLexerPython = None
    QsciLexerJSON = None

class FlowSyntaxHighlighter(QSyntaxHighlighter):
    """Custom syntax highlighter for flow files"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_highlighting_rules()
        
    def setup_highlighting_rules(self):
        """Setup highlighting rules for flow syntax"""
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            "click", "swipe", "text", "wait", "screenshot", "assert",
            "if", "else", "for", "while", "return", "break", "continue"
        ]
        
        for keyword in keywords:
            pattern = f"\\b{keyword}\\b"
            self.highlighting_rules.append((pattern, keyword_format))
            
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append(('".*"', string_format))
        self.highlighting_rules.append(("'.*'", string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append(("#.*", comment_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF6600"))
        self.highlighting_rules.append(("\\b\\d+\\b", number_format))
        
    def highlightBlock(self, text):
        """Apply highlighting to text block"""
        import re
        
        for pattern, format_obj in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format_obj)

class FlowCodeEditor(QWidget):
    """Code editor với syntax highlighting"""
    
    content_changed = pyqtSignal(str)  # Emit when content changes
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QToolBar()
        
        # Font size controls
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["8", "10", "12", "14", "16", "18", "20"])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self.change_font_size)
        
        toolbar.addWidget(QLabel("Font Size:"))
        toolbar.addWidget(self.font_size_combo)
        toolbar.addSeparator()
        
        # Word wrap toggle
        self.word_wrap_btn = QPushButton("📄 Word Wrap")
        self.word_wrap_btn.setCheckable(True)
        self.word_wrap_btn.clicked.connect(self.toggle_word_wrap)
        toolbar.addWidget(self.word_wrap_btn)
        
        layout.addWidget(toolbar)
        
        # Code editor
        if QsciScintilla != QTextEdit:
            # Use QScintilla if available
            self.editor = QsciScintilla()
            self.setup_qscintilla()
        else:
            # Fallback to QTextEdit
            self.editor = QTextEdit()
            self.setup_qtextedit()
            
        layout.addWidget(self.editor)
        self.setLayout(layout)
        
    def setup_qscintilla(self):
        """Setup QScintilla editor"""
        # Set lexer for Python syntax highlighting
        lexer = QsciLexerPython()
        self.editor.setLexer(lexer)
        
        # Set font
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        lexer.setFont(font)
        
        # Line numbers
        self.editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.editor.setMarginWidth(0, "0000")
        self.editor.setMarginLineNumbers(0, True)
        self.editor.setMarginsBackgroundColor(QColor("#404040"))
        self.editor.setMarginsForegroundColor(QColor("#ffffff"))
        
        # Set editor colors for dark theme
        self.editor.setPaper(QColor("#2d2d2d"))
        self.editor.setColor(QColor("#ffffff"))
        
        # Current line highlighting
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#404040"))
        
        # Set selection colors
        self.editor.setSelectionBackgroundColor(QColor("#4a90e2"))
        
        # Enable brace matching
        self.editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        
        # Auto-indentation
        self.editor.setAutoIndent(True)
        self.editor.setIndentationsUseTabs(False)
        self.editor.setIndentationWidth(4)
        
        # Connect signals
        self.editor.textChanged.connect(self.on_text_changed)
        
    def setup_qtextedit(self):
        """Setup QTextEdit fallback"""
        # Set font
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.editor.setFont(font)
        
        # Apply syntax highlighter
        self.highlighter = FlowSyntaxHighlighter(self.editor.document())
        
        # Connect signals
        self.editor.textChanged.connect(self.on_text_changed)
        
    def change_font_size(self, size_str):
        """Change editor font size"""
        try:
            size = int(size_str)
            font = self.editor.font()
            font.setPointSize(size)
            self.editor.setFont(font)
        except ValueError:
            pass
            
    def toggle_word_wrap(self, checked):
        """Toggle word wrap"""
        if hasattr(self.editor, 'setWrapMode'):
            # QScintilla
            wrap_mode = QsciScintilla.WrapMode.WrapWord if checked else QsciScintilla.WrapMode.WrapNone
            self.editor.setWrapMode(wrap_mode)
        else:
            # QTextEdit
            wrap_mode = QTextEdit.WrapMode.WidgetWidth if checked else QTextEdit.WrapMode.NoWrap
            self.editor.setLineWrapMode(wrap_mode)
            
    def on_text_changed(self):
        """Handle text changes"""
        content = self.get_text()
        self.content_changed.emit(content)
        
    def set_text(self, text):
        """Set editor text"""
        if hasattr(self.editor, 'setText'):
            self.editor.setText(text)
        else:
            self.editor.setPlainText(text)
            
    def get_text(self):
        """Get editor text"""
        if hasattr(self.editor, 'text'):
            return self.editor.text()
        else:
            return self.editor.toPlainText()
            
    def clear(self):
        """Clear editor"""
        self.editor.clear()

class FlowTreeWidget(QTreeWidget):
    """Tree widget for flow files"""
    
    flow_selected = pyqtSignal(str)  # Emit flow file path
    flow_double_clicked = pyqtSignal(str)  # Emit when flow double-clicked
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setHeaderLabel("📁 Flow Files")
        self.setStyleSheet("""
            QTreeWidget {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 6px;
                border-bottom: 1px solid #404040;
            }
            QTreeWidget::item:selected {
                background-color: #4a90e2;
                color: #ffffff;
                border-left: 4px solid #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #404040;
                color: #ffffff;
            }
            QTreeWidget::branch {
                background-color: #2d2d2d;
            }
        """)
        
        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
    def load_flows(self, flows_dir):
        """Load flows from directory"""
        self.clear()
        
        if not os.path.exists(flows_dir):
            return
            
        # Add flows directory as root
        root_item = QTreeWidgetItem(self)
        root_item.setText(0, "📁 flows")
        root_item.setData(0, Qt.ItemDataRole.UserRole, flows_dir)
        
        # Load flow files
        self.load_directory(root_item, flows_dir)
        
        # Expand root
        root_item.setExpanded(True)
        
    def load_directory(self, parent_item, dir_path):
        """Recursively load directory contents"""
        try:
            for item_name in sorted(os.listdir(dir_path)):
                item_path = os.path.join(dir_path, item_name)
                
                if os.path.isdir(item_path):
                    # Directory
                    dir_item = QTreeWidgetItem(parent_item)
                    dir_item.setText(0, f"📁 {item_name}")
                    dir_item.setData(0, Qt.ItemDataRole.UserRole, item_path)
                    self.load_directory(dir_item, item_path)
                    
                elif item_name.endswith(('.py', '.json', '.flow')):
                    # Flow file
                    file_item = QTreeWidgetItem(parent_item)
                    icon = "🐍" if item_name.endswith('.py') else "📄"
                    file_item.setText(0, f"{icon} {item_name}")
                    file_item.setData(0, Qt.ItemDataRole.UserRole, item_path)
                    
        except PermissionError:
            pass
            
    def on_item_clicked(self, item, column):
        """Handle item click"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.isfile(file_path):
            self.flow_selected.emit(file_path)
            
    def on_item_double_clicked(self, item, column):
        """Handle item double click"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path and os.path.isfile(file_path):
            self.flow_double_clicked.emit(file_path)

class NewFlowDialog(QDialog):
    """Dialog for creating new flow"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Create New Flow")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout()
        
        # Flow name
        layout.addWidget(QLabel("Flow Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter flow name (without extension)")
        layout.addWidget(self.name_input)
        
        # Flow type
        layout.addWidget(QLabel("Flow Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Python (.py)", "JSON (.json)", "Flow (.flow)"])
        layout.addWidget(self.type_combo)
        
        # Template
        layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Empty", "Basic Flow", "Zalo Flow", "WhatsApp Flow"])
        layout.addWidget(self.template_combo)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def get_flow_info(self):
        """Get flow creation info"""
        name = self.name_input.text().strip()
        type_text = self.type_combo.currentText()
        template = self.template_combo.currentText()
        
        # Determine extension
        if "Python" in type_text:
            extension = ".py"
        elif "JSON" in type_text:
            extension = ".json"
        else:
            extension = ".flow"
            
        return {
            'name': name,
            'extension': extension,
            'template': template
        }

class FlowEditorWidget(QWidget):
    """Main flow editor widget"""
    
    flow_saved = pyqtSignal(str)  # Emit when flow is saved
    flow_executed = pyqtSignal(str)  # Emit when flow is executed
    
    def __init__(self, flow_manager=None):
        super().__init__()
        self.flow_manager = flow_manager
        self.current_file_path = None
        self.is_modified = False
        self.flows_dir = "flows"
        
        self.setup_ui()
        self.setup_connections()
        self.setup_file_watcher()
        
        # Load flows
        self.refresh_flows()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Left panel - Flow tree
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Flow tree header
        tree_header = QHBoxLayout()
        tree_title = QLabel("📁 Flow Files")
        tree_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.new_flow_btn = QPushButton("➕ New")
        self.refresh_flows_btn = QPushButton("🔄")
        
        tree_header.addWidget(tree_title)
        tree_header.addStretch()
        tree_header.addWidget(self.new_flow_btn)
        tree_header.addWidget(self.refresh_flows_btn)
        
        left_layout.addLayout(tree_header)
        
        # Flow tree
        self.flow_tree = FlowTreeWidget()
        left_layout.addWidget(self.flow_tree)
        
        left_panel.setLayout(left_layout)
        
        # Right panel - Editor
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Editor header
        editor_header = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.save_btn = QPushButton("💾 Save")
        self.save_as_btn = QPushButton("💾 Save As")
        self.run_btn = QPushButton("▶️ Run")
        self.validate_btn = QPushButton("✅ Validate")
        
        # Style buttons
        for btn in [self.save_btn, self.save_as_btn, self.run_btn, self.validate_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border: none;
                    border-radius: 4px;
                    background-color: #2196f3;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976d2;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                }
            """)
            
        self.run_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background-color: #4caf50;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        editor_header.addWidget(self.file_label)
        editor_header.addStretch()
        editor_header.addWidget(self.validate_btn)
        editor_header.addWidget(self.save_btn)
        editor_header.addWidget(self.save_as_btn)
        editor_header.addWidget(self.run_btn)
        
        right_layout.addLayout(editor_header)
        
        # Code editor
        self.code_editor = FlowCodeEditor()
        right_layout.addWidget(self.code_editor)
        
        right_panel.setLayout(right_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])  # Set initial sizes
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        # Initially disable editor buttons
        self.set_editor_buttons_enabled(False)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Flow tree
        self.flow_tree.flow_selected.connect(self.load_flow)
        self.flow_tree.flow_double_clicked.connect(self.load_flow)
        
        # Buttons
        self.new_flow_btn.clicked.connect(self.create_new_flow)
        self.refresh_flows_btn.clicked.connect(self.refresh_flows)
        self.save_btn.clicked.connect(self.save_flow)
        self.save_as_btn.clicked.connect(self.save_flow_as)
        self.run_btn.clicked.connect(self.run_flow)
        self.validate_btn.clicked.connect(self.validate_flow)
        
        # Editor
        self.code_editor.content_changed.connect(self.on_content_changed)
        
    def setup_file_watcher(self):
        """Setup file system watcher for hot reload"""
        self.file_watcher = QFileSystemWatcher()
        if os.path.exists(self.flows_dir):
            self.file_watcher.addPath(self.flows_dir)
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)
        
    def refresh_flows(self):
        """Refresh flow tree"""
        self.flow_tree.load_flows(self.flows_dir)
        
    def on_directory_changed(self, path):
        """Handle directory changes for hot reload"""
        self.refresh_flows()
        
    def create_new_flow(self):
        """Create new flow"""
        dialog = NewFlowDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            flow_info = dialog.get_flow_info()
            
            if not flow_info['name']:
                QMessageBox.warning(self, "Warning", "Please enter a flow name")
                return
                
            # Create flow file
            filename = flow_info['name'] + flow_info['extension']
            file_path = os.path.join(self.flows_dir, filename)
            
            if os.path.exists(file_path):
                QMessageBox.warning(self, "Warning", f"File {filename} already exists")
                return
                
            # Create flows directory if not exists
            os.makedirs(self.flows_dir, exist_ok=True)
            
            # Generate template content
            content = self.generate_template_content(flow_info)
            
            # Save file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # Load the new file
                self.load_flow(file_path)
                self.refresh_flows()
                
                QMessageBox.information(self, "Success", f"Flow {filename} created successfully")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create flow: {str(e)}")
                
    def generate_template_content(self, flow_info):
        """Generate template content based on flow info"""
        template = flow_info['template']
        extension = flow_info['extension']
        
        if extension == '.py':
            if template == "Basic Flow":
                return '''# -*- coding: utf-8 -*-
"""
Basic Flow Template
"""

def main(device):
    """
    Main flow function
    Args:
        device: Device object for automation
    """
    print("Starting flow...")
    
    # Your automation code here
    # Example:
    # device.click(100, 200)
    # device.text("Hello World")
    # device.wait(2)
    
    print("Flow completed")
    return "SUCCESS"

if __name__ == "__main__":
    # Test code
    print("Flow template created")
'''
            elif template == "Zalo Flow":
                return '''# -*- coding: utf-8 -*-
"""
Zalo Automation Flow
"""

def main(device):
    """
    Zalo automation flow
    """
    print("Starting Zalo flow...")
    
    # Open Zalo app
    device.app_start("com.zing.zalo")
    device.wait(3)
    
    # Your Zalo automation code here
    
    print("Zalo flow completed")
    return "SUCCESS"
'''
            else:
                return f'''# -*- coding: utf-8 -*-
"""
{flow_info['name']} Flow
"""

def main(device):
    """
    Flow main function
    """
    print("Flow started")
    
    # Add your automation code here
    
    return "SUCCESS"
'''
        elif extension == '.json':
            return '''{
    "name": "''' + flow_info['name'] + '''",
    "description": "Flow description",
    "steps": [
        {
            "action": "click",
            "x": 100,
            "y": 200,
            "description": "Click button"
        },
        {
            "action": "wait",
            "duration": 2,
            "description": "Wait 2 seconds"
        }
    ]
}
'''
        else:
            return f"# {flow_info['name']} Flow\n# Add your flow steps here\n"
            
    def load_flow(self, file_path):
        """Load flow file into editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.code_editor.set_text(content)
            self.current_file_path = file_path
            self.is_modified = False
            
            # Update UI
            filename = os.path.basename(file_path)
            self.file_label.setText(f"📄 {filename}")
            self.set_editor_buttons_enabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load flow: {str(e)}")
            
    def save_flow(self):
        """Save current flow"""
        if not self.current_file_path:
            self.save_flow_as()
            return
            
        try:
            content = self.code_editor.get_text()
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.is_modified = False
            self.update_file_label()
            
            QMessageBox.information(self, "Success", "Flow saved successfully")
            self.flow_saved.emit(self.current_file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save flow: {str(e)}")
            
    def save_flow_as(self):
        """Save flow as new file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Flow As", self.flows_dir,
            "Python Files (*.py);;JSON Files (*.json);;Flow Files (*.flow);;All Files (*)"
        )
        
        if file_path:
            try:
                content = self.code_editor.get_text()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                self.current_file_path = file_path
                self.is_modified = False
                
                filename = os.path.basename(file_path)
                self.file_label.setText(f"📄 {filename}")
                
                self.refresh_flows()
                QMessageBox.information(self, "Success", "Flow saved successfully")
                self.flow_saved.emit(file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save flow: {str(e)}")
                
    def run_flow(self):
        """Run current flow"""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "No flow selected")
            return
            
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Save Changes", 
                "Flow has unsaved changes. Save before running?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_flow()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
                
        # Emit signal to run flow
        self.flow_executed.emit(self.current_file_path)
        
    def validate_flow(self):
        """Validate current flow syntax"""
        if not self.current_file_path:
            QMessageBox.warning(self, "Warning", "No flow selected")
            return
            
        content = self.code_editor.get_text()
        
        # Basic validation
        if self.current_file_path.endswith('.py'):
            try:
                compile(content, self.current_file_path, 'exec')
                QMessageBox.information(self, "Validation", "✅ Python syntax is valid")
            except SyntaxError as e:
                QMessageBox.warning(self, "Validation Error", f"❌ Python syntax error:\n{str(e)}")
        elif self.current_file_path.endswith('.json'):
            try:
                json.loads(content)
                QMessageBox.information(self, "Validation", "✅ JSON syntax is valid")
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Validation Error", f"❌ JSON syntax error:\n{str(e)}")
        else:
            QMessageBox.information(self, "Validation", "✅ Flow file format is valid")
            
    def on_content_changed(self, content):
        """Handle content changes"""
        self.is_modified = True
        self.update_file_label()
        
    def update_file_label(self):
        """Update file label with modification status"""
        if self.current_file_path:
            filename = os.path.basename(self.current_file_path)
            modified_indicator = " *" if self.is_modified else ""
            self.file_label.setText(f"📄 {filename}{modified_indicator}")
            
    def set_editor_buttons_enabled(self, enabled):
        """Enable/disable editor buttons"""
        self.save_btn.setEnabled(enabled)
        self.save_as_btn.setEnabled(enabled)
        self.run_btn.setEnabled(enabled)
        self.validate_btn.setEnabled(enabled)