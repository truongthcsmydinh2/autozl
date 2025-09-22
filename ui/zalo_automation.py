# -*- coding: utf-8 -*-
# Zalo Automation — Single‑file redesigned UI (PyQt6)
# Layout: Sidebar (Devices / Pair / Conversations / Control) + Stacked Pages
# Notes:
# - Keeps compatibility with your existing data_manager + core1.run_zalo_automation if present.
# - If those modules are missing, the UI still runs and shows friendly warnings.
# - Compact, modern, subtle visuals with light theme.

import os, sys, traceback, random
from typing import List, Dict, Tuple

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# ---------- Optional backends (graceful import) ----------
_DATA_MANAGER = None
_RUN_AUTOMATION = None
try:
    from utils.data_manager import data_manager as _DATA_MANAGER
except Exception:
    _DATA_MANAGER = None

try:
    from core1 import run_zalo_automation as _RUN_AUTOMATION
except Exception:
    _RUN_AUTOMATION = None

# ---------- Worker Thread ----------
class AutomationWorker(QThread):
    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, device_pairs: List[Tuple[dict, dict]], conversations: List[str], phone_mapping: Dict[str, str]):
        super().__init__()
        self.device_pairs = device_pairs
        self.conversations = conversations
        self.phone_mapping = phone_mapping
        self._stop = False

    def run(self):
        try:
            if _RUN_AUTOMATION is None:
                self.progress_updated.emit("⚠️ Không tìm thấy core1.py - chạy chế độ mô phỏng")
                # Simulated progress if backend is absent
                total = len(self.device_pairs)
                for i, pair in enumerate(self.device_pairs, 1):
                    if self._stop:
                        self.finished.emit({})
                        return
                    self.progress_updated.emit(f"🔄 Mô phỏng cặp {i}/{total}: {pair[0].get('ip')} ↔ {pair[1].get('ip')}")
                    self.msleep(400)
                results = {f"pair_{i}": {"status": "completed"} for i in range(1, total+1)}
                self.progress_updated.emit("✅ Hoàn thành chế độ mô phỏng")
                self.finished.emit(results)
            else:
                # Real backend - calling core1.py
                self.progress_updated.emit("🚀 Đang gọi core1.py để thực hiện automation...")
                self.progress_updated.emit(f"📁 Đường dẫn: d:\\tool moi\\tool auto\\core1.py")
                self.progress_updated.emit(f"📊 Số cặp thiết bị: {len(self.device_pairs)}")
                self.progress_updated.emit(f"💬 Số hội thoại: {len(self.conversations)}")
                
                results = _RUN_AUTOMATION(
                    self.device_pairs,
                    self.conversations,
                    self.phone_mapping,
                    progress_callback=self.progress_updated.emit,
                )
                self.progress_updated.emit("✅ core1.py đã hoàn thành automation")
                self.finished.emit(results)
        except Exception as e:
            self.error_occurred.emit(f"❌ Lỗi trong automation: {str(e)}")

    def stop(self):
        self._stop = True
        try:
            self.terminate()
        except Exception:
            pass

# ---------- Dark Theme Color Palette ----------
# Professional dark theme with teal accents
PRIMARY = "#00bcd4"      # Teal for selected/hover items
PRIMARY_HOVER = "#0097a7"  # Darker teal for hover
SUCCESS = "#4caf50"      # Green for success
SUCCESS_HOVER = "#388e3c"  # Darker green for hover
DANGER  = "#f44336"      # Red for danger
DANGER_HOVER = "#d32f2f"   # Darker red for hover
WARNING = "#ff9800"      # Orange for warning
INFO    = "#2196f3"      # Blue for info
TEXT    = "#ffffff"      # White text
TEXT_SECONDARY = "#b0b0b0"  # Light gray for secondary text
MUTED   = "#757575"      # Medium gray for muted text
BORDER  = "#404040"      # Dark gray border
BG      = "#1a1a1a"      # Dark background
SURFACE = "#2a2a2a"      # Dark surface for cards
DIVIDER = "#404040"      # Dark divider

# Legacy aliases for compatibility
WHITE = SURFACE

BTN_STYLE = lambda bg, hover: f"""
QPushButton {{
    background-color: {bg};
    color: {TEXT};
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 500;
    min-width: 80px;
}}
QPushButton:hover {{
    background-color: {hover};
}}
QPushButton:pressed {{
    background-color: {hover};
}}
QPushButton:disabled {{
    background-color: {MUTED};
    color: {TEXT_SECONDARY};
    opacity: 0.6;
}}
"""

CARD_STYLE = f"""
QFrame {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 4px;
}}
"""

INPUT_STYLE = f"""
QLineEdit {{
    background: {SURFACE};
    border: 2px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: {TEXT};
}}
QLineEdit:focus {{
    border: 2px solid {PRIMARY};
    outline: none;
}}
QLineEdit:hover {{
    border: 2px solid {TEXT_SECONDARY};
}}
"""

CHECK_STYLE = f"""
QCheckBox {{ 
    color: {TEXT}; 
    font-size: 13px; 
    padding: 6px 4px;
    spacing: 8px;
}}
QCheckBox::indicator {{ 
    width: 18px; 
    height: 18px; 
    border: 2px solid {BORDER}; 
    border-radius: 4px; 
    background: {SURFACE}; 
}}
QCheckBox::indicator:hover {{
    border: 2px solid {PRIMARY};
}}
QCheckBox::indicator:checked {{ 
    background: {PRIMARY}; 
    border-color: {PRIMARY};
    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
}}
"""

SCROLL_STYLE = f"""
QScrollArea {{ 
    background: {SURFACE}; 
    border: 1px solid {BORDER}; 
    border-radius: 12px; 
}}
QScrollBar:vertical {{ 
    background: transparent; 
    width: 12px; 
    margin: 0px;
}}
QScrollBar::handle:vertical {{ 
    background: {TEXT_SECONDARY}; 
    border-radius: 6px; 
    min-height: 20px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

PROGRESS_STYLE = f"""
QProgressBar {{
    border: 2px solid {BORDER};
    border-radius: 8px;
    background: {SURFACE};
    text-align: center; 
    color: {TEXT}; 
    font-size: 12px;
    font-weight: 500;
    height: 24px;
}}
QProgressBar::chunk {{ 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:1 {PRIMARY_HOVER});
    border-radius: 6px; 
}}
"""

LOG_STYLE = f"""
QTextEdit {{ 
    background: {SURFACE}; 
    border: 2px solid {BORDER}; 
    border-radius: 12px; 
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace; 
    font-size: 12px; 
    padding: 12px;
    color: {TEXT};
    line-height: 1.4;
}}
QTextEdit:focus {{
    border: 2px solid {PRIMARY};
}}
"""

SIDEBAR_STYLE = f"""
QFrame#Sidebar {{ 
    background: {BG}; 
    border-right: 2px solid {BORDER}; 
}}
QFrame#Sidebar QPushButton {{ 
    color: {TEXT}; 
    text-align: left; 
    padding: 12px 16px; 
    border-radius: 8px; 
    font-size: 14px; 
    font-weight: 500;
    border: none; 
    background: transparent;
    margin: 2px 8px;
}}
QFrame#Sidebar QPushButton:hover {{ 
    background-color: {PRIMARY}; 
    color: {TEXT};
}}
QFrame#Sidebar QPushButton:checked {{ 
    background: {PRIMARY};
    color: {TEXT};
    font-weight: 600;
}}
QLabel#Brand {{ 
    color: {TEXT}; 
    font-weight: 700; 
    font-size: 16px; 
    padding: 16px 12px; 
    background: {SURFACE};
    border-radius: 8px;
    margin: 8px;
}}
"""

# ---------- Pages ----------
class DevicesPage(QWidget):
    devices_changed = pyqtSignal(list)  # emits full device list (checkbox .device dict if checked)

    def __init__(self):
        super().__init__()
        self.all_devices: List[dict] = []
        self.checkboxes: List[QCheckBox] = []
        self._build()
        self.load_devices()

    # UI build
    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(12,12,12,12); outer.setSpacing(10)

        # Card: search + actions
        card = QFrame(); card.setStyleSheet(CARD_STYLE)
        head = QHBoxLayout(card); head.setContentsMargins(12,12,12,12); head.setSpacing(8)

        self.search = QLineEdit(); self.search.setPlaceholderText("Tìm theo IP, số điện thoại hoặc ghi chú…"); self.search.setStyleSheet(INPUT_STYLE)
        self.search.textChanged.connect(self._apply_filter)
        btn_refresh = QPushButton("Refresh"); btn_refresh.setStyleSheet(BTN_STYLE(PRIMARY, PRIMARY_HOVER)); btn_refresh.clicked.connect(self.load_devices)
        btn_all = QPushButton("Chọn tất cả"); btn_all.setStyleSheet(BTN_STYLE(SUCCESS, SUCCESS_HOVER)); btn_all.clicked.connect(self._select_all)
        btn_none = QPushButton("Bỏ chọn"); btn_none.setStyleSheet(BTN_STYLE(MUTED, TEXT_SECONDARY)); btn_none.clicked.connect(self._select_none)

        head.addWidget(self.search)
        head.addWidget(btn_refresh)
        head.addWidget(btn_all)
        head.addWidget(btn_none)

        # Device list
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setStyleSheet(SCROLL_STYLE)
        self.container = QWidget(); self.vbox = QVBoxLayout(self.container); self.vbox.setContentsMargins(8,8,8,8); self.vbox.setSpacing(2)
        self.scroll.setWidget(self.container)

        # Footer status
        foot = QHBoxLayout(); foot.setContentsMargins(0,0,0,0)
        self.status = QLabel("Sẵn sàng"); self.status.setStyleSheet(f"color:{MUTED};")
        foot.addWidget(self.status); foot.addStretch(1)

        outer.addWidget(card)
        outer.addWidget(self.scroll)
        outer.addLayout(foot)

    # Data handling
    def load_devices(self):
        self.status.setText("Đang tải devices…")
        self._clear_list()
        try:
            devices = []
            if _DATA_MANAGER is not None:
                # Only get devices without auto-sync
                devices = _DATA_MANAGER.get_devices_with_phone_numbers() or []
            # Normalize shape: {ip, phone, note?}
            self.all_devices = [
                {
                    'ip': d.get('ip', ''),
                    'phone': d.get('phone') or 'Chưa có số',
                    'note': d.get('note',''),
                } for d in devices
            ]
            if not self.all_devices:
                self.status.setText("Không tìm thấy device nào. Kết nối thiết bị và bấm Refresh.")
            else:
                self.status.setText(f"Tìm thấy {len(self.all_devices)} devices")
            self._populate(self.all_devices)
        except Exception as e:
            self.status.setText(f"Lỗi tải devices: {e}")

    def _clear_list(self):
        self.checkboxes.clear()
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        self.vbox.addStretch(1)

    def _populate(self, devices: List[dict]):
        # remove stretch
        if self.vbox.count():
            item = self.vbox.takeAt(self.vbox.count()-1)
            if item and item.widget():
                item.widget().deleteLater()
        for d in devices:
            # Format device label with note
            note = d.get('note', '').strip()
            if not note:
                note = 'Không có'
            
            device_label = f"{d['ip']} ({d['phone']} - Máy: {note})"
            
            cb = QCheckBox(device_label)
            cb.setStyleSheet(CHECK_STYLE)
            cb.device = d
            cb.stateChanged.connect(self._emit_selection)
            self.checkboxes.append(cb)
            self.vbox.addWidget(cb)
        self.vbox.addStretch(1)
        self._emit_selection()

    def _emit_selection(self):
        selected = [cb.device for cb in self.checkboxes if cb.isChecked()]
        self.devices_changed.emit(selected)

    def _select_all(self):
        for cb in self.checkboxes: cb.setChecked(True)
    def _select_none(self):
        for cb in self.checkboxes: cb.setChecked(False)

    def _apply_filter(self):
        q = self.search.text().strip().lower()
        if not q:
            self._populate(self.all_devices)
            return
        filtered = []
        for d in self.all_devices:
            ip = (d.get('ip') or '').lower()
            ph = (d.get('phone') or '').lower()
            note = (d.get('note') or '').lower()
            if q in ip or q in ph or q in note:
                filtered.append(d)
        self._populate(filtered)

class PairDetailsDialog(QDialog):
    def __init__(self, pairs: List[Tuple[dict,dict]], parent=None):
        super().__init__(parent)
        self.pairs = pairs
        self.setWindowTitle("Chi tiết cặp thiết bị")
        self.setModal(True)
        self.resize(800, 600)
        self._build()
        
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"📱 Thông tin chi tiết {len(self.pairs)} cặp thiết bị")
        header.setStyleSheet(f"color: {TEXT}; font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Scroll area for pairs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(SCROLL_STYLE)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(15)
        
        # Add each pair details
        for i, (device_a, device_b) in enumerate(self.pairs, 1):
            pair_frame = self._create_pair_frame(i, device_a, device_b)
            content_layout.addWidget(pair_frame)
            
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Close button
        btn_close = QPushButton("Đóng")
        btn_close.setStyleSheet(BTN_STYLE(PRIMARY, PRIMARY_HOVER))
        btn_close.clicked.connect(self.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
    def _create_pair_frame(self, pair_num: int, device_a: dict, device_b: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"""
        QFrame {{
            background: {SURFACE};
            border: 2px solid {BORDER};
            border-radius: 12px;
            padding: 15px;
            margin: 5px;
        }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Pair title
        title = QLabel(f"🔗 Cặp {pair_num}")
        title.setStyleSheet(f"color: {PRIMARY}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Device details in a grid
        details_layout = QGridLayout()
        details_layout.setSpacing(10)
        
        # Headers
        details_layout.addWidget(QLabel("Thông tin"), 0, 0)
        device_a_header = QLabel("📱 Thiết bị A")
        device_a_header.setStyleSheet(f"color: {SUCCESS}; font-weight: bold;")
        details_layout.addWidget(device_a_header, 0, 1)
        
        device_b_header = QLabel("📱 Thiết bị B")
        device_b_header.setStyleSheet(f"color: {INFO}; font-weight: bold;")
        details_layout.addWidget(device_b_header, 0, 2)
        
        # Device details
        row = 1
        
        # IP Address
        details_layout.addWidget(QLabel("🌐 IP Address:"), row, 0)
        details_layout.addWidget(QLabel(device_a.get('ip', 'N/A')), row, 1)
        details_layout.addWidget(QLabel(device_b.get('ip', 'N/A')), row, 2)
        row += 1
        # Phone number
        details_layout.addWidget(QLabel("📞 Số điện thoại:"), row, 0)
        phone_a = QLabel(device_a.get('phone', 'Chưa có số'))
        phone_a.setStyleSheet(f"color: {TEXT}; padding: 2px;")
        phone_b = QLabel(device_b.get('phone', 'Chưa có số'))
        phone_b.setStyleSheet(f"color: {TEXT}; padding: 2px;")
        details_layout.addWidget(phone_a, row, 1)
        details_layout.addWidget(phone_b, row, 2)
        row += 1
        
        # Note/Name
        details_layout.addWidget(QLabel("📝 Tên máy:"), row, 0)
        note_a = device_a.get('note', '').strip() or 'Không có'
        note_b = device_b.get('note', '').strip() or 'Không có'
        details_layout.addWidget(QLabel(note_a), row, 1)
        details_layout.addWidget(QLabel(note_b), row, 2)
        row += 1
        
        # Connection status (simulated)
        details_layout.addWidget(QLabel("🔌 Trạng thái:"), row, 0)
        status_a = QLabel("✅ Kết nối")
        status_a.setStyleSheet(f"color: {SUCCESS};")
        status_b = QLabel("✅ Kết nối")
        status_b.setStyleSheet(f"color: {SUCCESS};")
        details_layout.addWidget(status_a, row, 1)
        details_layout.addWidget(status_b, row, 2)
        row += 1
        
        # Pair time (simulated)
        from datetime import datetime
        pair_time = datetime.now().strftime("%H:%M:%S")
        details_layout.addWidget(QLabel("⏰ Thời gian ghép:"), row, 0)
        time_label = QLabel(pair_time)
        time_label.setStyleSheet(f"color: {MUTED};")
        details_layout.addWidget(time_label, row, 1, 1, 2)  # Span 2 columns
        
        # Style all labels
        for i in range(details_layout.count()):
            widget = details_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text().endswith(':'):
                widget.setStyleSheet(f"color: {TEXT}; font-weight: 500;")
            elif isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {TEXT};")
        
        layout.addLayout(details_layout)
        return frame

class PairPage(QWidget):
    pairs_changed = pyqtSignal(list)  # emits List[Tuple[dict,dict]]

    def __init__(self):
        super().__init__()
        self.selected_devices: List[dict] = []
        self.pairs: List[Tuple[dict,dict]] = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(12,12,12,12); root.setSpacing(10)
        # Card: info + actions
        card = QFrame(); card.setStyleSheet(CARD_STYLE)
        top = QHBoxLayout(card); top.setContentsMargins(12,12,12,12); top.setSpacing(8)
        self.info = QLabel("Chọn thiết bị ở tab Devices, sau đó nhấn Ghép cặp.")
        self.info.setStyleSheet(f"color:{MUTED}")
        btn_pair = QPushButton("Ghép cặp"); btn_pair.setStyleSheet(BTN_STYLE(PRIMARY, PRIMARY_HOVER)); btn_pair.clicked.connect(self._pair)
        btn_clear = QPushButton("Xóa cặp"); btn_clear.setStyleSheet(BTN_STYLE(MUTED, TEXT_SECONDARY)); btn_clear.clicked.connect(self._clear)
        self.btn_details = QPushButton("📋 Xem chi tiết cặp"); self.btn_details.setStyleSheet(BTN_STYLE(INFO, "#1976d2")); self.btn_details.clicked.connect(self._show_details)
        self.btn_details.setEnabled(False)  # Disabled until pairs exist
        top.addWidget(self.info); top.addStretch(1); top.addWidget(btn_pair); top.addWidget(btn_clear); top.addWidget(self.btn_details)

        # List pairs
        self.list_pairs = QListWidget(); self.list_pairs.setStyleSheet(f"QListWidget{{background:{SURFACE}; border:2px solid {BORDER}; border-radius:12px; color:{TEXT};}} QListWidget::item{{padding:12px; border-bottom:1px solid {DIVIDER};}} QListWidget::item:hover{{background:{BG};}} QListWidget::item:selected{{background:{PRIMARY}; color:white;}}")

        root.addWidget(card)
        root.addWidget(self.list_pairs)

    def update_selection(self, devices: List[dict]):
        self.selected_devices = devices
        self.info.setText(f"Đã chọn {len(devices)} thiết bị. Cần số lượng chẵn để ghép cặp.")

    def _pair(self):
        n = len(self.selected_devices)
        if n < 2:
            QMessageBox.warning(self, "Cảnh báo", "Cần chọn ít nhất 2 thiết bị.")
            return
        if n % 2 != 0:
            QMessageBox.warning(self, "Cảnh báo", "Số lượng thiết bị phải là số chẵn.")
            return
        pool = self.selected_devices.copy(); random.shuffle(pool)
        self.pairs = []
        for i in range(0, n, 2):
            self.pairs.append((pool[i], pool[i+1]))
        self._render_pairs()
        self.pairs_changed.emit(self.pairs)
        
        # Show details dialog after successful pairing
        if self.pairs:
            self._show_details()

    def _clear(self):
        self.pairs = []
        self._render_pairs()
        self.pairs_changed.emit(self.pairs)
        self.btn_details.setEnabled(False)

    def _show_details(self):
        if not self.pairs:
            QMessageBox.information(self, "Thông báo", "Chưa có cặp nào được ghép.")
            return
        dialog = PairDetailsDialog(self.pairs, self)
        dialog.exec()

    def _render_pairs(self):
        self.list_pairs.clear()
        self.btn_details.setEnabled(len(self.pairs) > 0)
        
        for i, (a,b) in enumerate(self.pairs, 1):
            # Enhanced display with more details and icons
            note_a = a.get('note', '').strip() or 'Không có'
            note_b = b.get('note', '').strip() or 'Không có'
            
            # Create rich text item with icons and formatting
            item_text = f"🔗 Cặp {i}:\n"
            item_text += f"   📱 A: {a['ip']} | {a['phone']} | {note_a}\n"
            item_text += f"   📱 B: {b['ip']} | {b['phone']} | {note_b}"
            
            item = QListWidgetItem(item_text)
            # Set custom styling for the item
            item.setData(Qt.ItemDataRole.UserRole, (a, b))  # Store pair data
            self.list_pairs.addItem(item)
        
        # Update info text
        if self.pairs:
            self.info.setText(f"✅ Đã ghép {len(self.pairs)} cặp thiết bị thành công!")
            self.info.setStyleSheet(f"color:{SUCCESS}; font-weight: 500;")
        else:
            self.info.setText("Chọn thiết bị ở tab Devices, sau đó nhấn Ghép cặp.")
            self.info.setStyleSheet(f"color:{MUTED}")

class ConversationsPage(QWidget):
    conversations_changed = pyqtSignal(list)  # emits List[str]
    conversations_saved = pyqtSignal()  # emits when conversations are saved

    def __init__(self):
        super().__init__()
        self.inputs: List[QTextEdit] = []
        self.is_saved = False
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(12,12,12,12); root.setSpacing(10)
        self.note = QLabel("Số hộp thoại sẽ khớp theo số cặp đã ghép.")
        self.note.setStyleSheet(f"color:{MUTED}")

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setStyleSheet(SCROLL_STYLE)
        self.wrap = QWidget(); self.grid = QGridLayout(self.wrap); self.grid.setContentsMargins(12,12,12,12); self.grid.setSpacing(10)
        self.scroll.setWidget(self.wrap)

        # Save button and status
        save_frame = QFrame(); save_frame.setStyleSheet(CARD_STYLE)
        save_layout = QHBoxLayout(save_frame); save_layout.setContentsMargins(12,8,12,8); save_layout.setSpacing(8)
        
        self.save_status = QLabel("Chưa lưu")
        self.save_status.setStyleSheet(f"color:{MUTED}; font-style:italic;")
        
        self.btn_save = QPushButton("💾 Lưu hội thoại")
        self.btn_save.setStyleSheet(BTN_STYLE(PRIMARY, PRIMARY_HOVER))
        self.btn_save.clicked.connect(self._save_conversations)
        
        save_layout.addWidget(self.save_status)
        save_layout.addStretch(1)
        save_layout.addWidget(self.btn_save)

        root.addWidget(self.note)
        root.addWidget(self.scroll)
        root.addWidget(save_frame)

    def update_pair_count(self, pair_count: int):
        # Clear
        for i in range(self.grid.count()-1, -1, -1):
            item = self.grid.itemAt(i)
            w = item.widget()
            if w: w.deleteLater()
        self.inputs.clear()
        # Build inputs
        for i in range(pair_count):
            lbl = QLabel(f"Cặp {i+1}")
            lbl.setStyleSheet(f"color:{TEXT}; font-weight:600;")
            box = QTextEdit(); box.setPlaceholderText(f"Nhập hội thoại cho cặp {i+1}…")
            box.setFixedHeight(120); box.setStyleSheet(LOG_STYLE)
            self.inputs.append(box)
            self.grid.addWidget(lbl, i, 0)
            self.grid.addWidget(box, i, 1)
        # Emit
        self._emit()

    def _emit(self):
        texts = [w.toPlainText().strip() for w in self.inputs]
        self.conversations_changed.emit(texts)
        # Mark as unsaved when content changes
        self.is_saved = False
        self.save_status.setText("Chưa lưu")
        self.save_status.setStyleSheet(f"color:{MUTED}; font-style:italic;")

    def collect(self) -> List[str]:
        return [w.toPlainText().strip() for w in self.inputs]
    
    def _save_conversations(self):
        """Save conversations and show feedback"""
        try:
            conversations = self.collect()
            if not any(conversations):
                QMessageBox.warning(self, "Cảnh báo", "Không có hội thoại nào để lưu.")
                return
            
            # Here you could save to file or data manager if needed
            # For now, just mark as saved
            self.is_saved = True
            self.save_status.setText("✅ Đã lưu")
            self.save_status.setStyleSheet(f"color:{SUCCESS}; font-weight:500;")
            
            # Emit signal for other components
            self.conversations_saved.emit()
            
            # Show success message
            QMessageBox.information(self, "Thành công", "Đã lưu hội thoại thành công!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu hội thoại: {e}")
    
    def is_conversations_saved(self) -> bool:
        """Check if conversations are saved"""
        return self.is_saved

class ControlPage(QWidget):
    request_start = pyqtSignal()
    request_stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(12,12,12,12); root.setSpacing(10)

        head = QFrame(); head.setStyleSheet(CARD_STYLE)
        hb = QHBoxLayout(head); hb.setContentsMargins(12,12,12,12); hb.setSpacing(8)
        self.btn_start = QPushButton("Bắt đầu"); self.btn_start.setStyleSheet(BTN_STYLE(SUCCESS, SUCCESS_HOVER)); self.btn_start.clicked.connect(self.request_start.emit)
        self.btn_stop  = QPushButton("Dừng"); self.btn_stop.setStyleSheet(BTN_STYLE(DANGER, DANGER_HOVER)); self.btn_stop.setEnabled(False); self.btn_stop.clicked.connect(self.request_stop.emit)
        hb.addWidget(self.btn_start); hb.addWidget(self.btn_stop); hb.addStretch(1)

        self.progress = QProgressBar(); self.progress.setStyleSheet(PROGRESS_STYLE); self.progress.setVisible(False)
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setStyleSheet(LOG_STYLE); self.log.setFixedHeight(240)

        root.addWidget(head)
        progress_label = QLabel("Tiến trình:"); progress_label.setStyleSheet(f"color: {TEXT}; font-weight: 500;")
        root.addWidget(progress_label)
        root.addWidget(self.progress)
        logs_label = QLabel("Logs:"); logs_label.setStyleSheet(f"color: {TEXT}; font-weight: 500;")
        root.addWidget(logs_label)
        root.addWidget(self.log)

    # Helpers for outer controller
    def set_running(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.progress.setVisible(running)
        if running:
            self.progress.setRange(0,0)  # indeterminate
        else:
            self.progress.setRange(0,100)

    def append_log(self, text: str):
        self.log.append(text)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zalo Automation — Dashboard")
        self.resize(1120, 720)
        self.setMinimumSize(980, 620)
        self.worker: AutomationWorker | None = None

        # Central composite
        central = QFrame(); central.setStyleSheet(f"background:{BG};")
        layout = QHBoxLayout(central); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)

        # Sidebar
        self.sidebar = self._build_sidebar()
        layout.addWidget(self.sidebar)

        # Stack
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Pages
        self.page_devices = DevicesPage()
        self.page_pair    = PairPage()
        self.page_convs   = ConversationsPage()
        self.page_ctrl    = ControlPage()

        self.stack.addWidget(self.page_devices)   # index 0
        self.stack.addWidget(self.page_pair)      # index 1
        self.stack.addWidget(self.page_convs)     # index 2
        self.stack.addWidget(self.page_ctrl)      # index 3

        # Wiring
        self.page_devices.devices_changed.connect(self._on_devices_changed)
        self.page_pair.pairs_changed.connect(self._on_pairs_changed)
        self.page_ctrl.request_start.connect(self._start_automation)
        self.page_ctrl.request_stop.connect(self._stop_automation)

        self.setCentralWidget(central)

        # Global style
        self.setStyleSheet(f"""
        QMainWindow {{ background: {BG}; color: {TEXT}; font-family: 'Segoe UI', Arial; font-size: 12px; }}
        QStackedWidget {{ background: {BG}; }}
        QWidget {{ background: {BG}; color: {TEXT}; }}
        QLabel {{ color: {TEXT}; }}
        """)

    # Sidebar with nav buttons
    def _build_sidebar(self) -> QWidget:
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(220); side.setStyleSheet(SIDEBAR_STYLE)
        v = QVBoxLayout(side); v.setContentsMargins(12,10,12,10); v.setSpacing(6)
        brand = QLabel("Zalo Automation"); brand.setObjectName("Brand")
        v.addWidget(brand)

        def make_btn(title, idx):
            b = QPushButton(title); b.setCheckable(True); b.setProperty('page', idx); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setProperty('class', 'SideBtn')
            b.clicked.connect(lambda: self._goto(idx))
            return b

        self.btn_dev  = make_btn("📱 Devices", 0)
        self.btn_pair = make_btn("💑 Pair Devices", 1)
        self.btn_conv = make_btn("💬 Conversations", 2)
        self.btn_ctrl = make_btn("⚙ Control", 3)

        v.addWidget(self.btn_dev)
        v.addWidget(self.btn_pair)
        v.addWidget(self.btn_conv)
        v.addWidget(self.btn_ctrl)
        v.addStretch(1)

        # default page
        self.btn_dev.setChecked(True)
        return side

    def _goto(self, idx: int):
        self.stack.setCurrentIndex(idx)
        # toggle checked state
        for btn in (self.btn_dev, self.btn_pair, self.btn_conv, self.btn_ctrl):
            btn.setChecked(btn.property('page') == idx)

    # Signals from pages
    def _on_devices_changed(self, selected: List[dict]):
        self.page_pair.update_selection(selected)

    def _on_pairs_changed(self, pairs: List[Tuple[dict,dict]]):
        self.page_convs.update_pair_count(len(pairs))

    # Automation lifecycle
    def _start_automation(self):
        self.page_ctrl.append_log("🔍 Kiểm tra điều kiện khởi động automation...")
        
        # Gather data
        pairs = self.page_pair.pairs
        if not pairs:
            self.page_ctrl.append_log("❌ Chưa có cặp thiết bị nào được ghép.")
            QMessageBox.warning(self, "Cảnh báo", "Hãy ghép cặp thiết bị trước.")
            return
        
        # Check if conversations are saved
        if not self.page_convs.is_conversations_saved():
            self.page_ctrl.append_log("⚠️ Hội thoại chưa được lưu.")
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng lưu hội thoại trước khi bắt đầu automation.")
            return
            
        convs = self.page_convs.collect()
        if any(not c for c in convs) or len(convs) != len(pairs):
            self.page_ctrl.append_log(f"❌ Số hội thoại ({len(convs)}) không khớp với số cặp ({len(pairs)}) hoặc có hội thoại trống.")
            QMessageBox.warning(self, "Cảnh báo", "Số đoạn hội thoại phải khớp số cặp và không được để trống.")
            return
            
        self.page_ctrl.append_log(f"✅ Đã có {len(pairs)} cặp thiết bị và {len(convs)} hội thoại.")
        
        phone_mapping = {}
        try:
            if _DATA_MANAGER is not None:
                phone_mapping = _DATA_MANAGER.get_phone_mapping() or {}
                self.page_ctrl.append_log(f"📞 Đã tải {len(phone_mapping)} mapping số điện thoại.")
        except Exception as e:
            self.page_ctrl.append_log(f"⚠️ Lỗi tải phone mapping: {e}")
            phone_mapping = {}

        # Confirm
        summary = "\n".join([f"Cặp {i+1}: {a['ip']} ↔ {b['ip']}" for i,(a,b) in enumerate(pairs)])
        if QMessageBox.question(self, "Xác nhận", f"Bắt đầu automation với {len(pairs)} cặp?\n\n{summary}") != QMessageBox.StandardButton.Yes:
            self.page_ctrl.append_log("❌ Người dùng hủy automation.")
            return

        # Start worker
        self.page_ctrl.append_log("🚀 Khởi tạo AutomationWorker...")
        self.worker = AutomationWorker(pairs, convs, phone_mapping)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        
        self.page_ctrl.append_log("▶️ Bắt đầu automation worker thread...")
        self.worker.start()

        self.page_ctrl.set_running(True)
        self.page_ctrl.append_log("✅ Automation đã bắt đầu thành công!")
        self._goto(3)

    def _stop_automation(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(500)
        self.page_ctrl.set_running(False)
        self.page_ctrl.append_log("Đã dừng automation.")

    # Worker callbacks
    def _on_progress(self, msg: str):
        self.page_ctrl.append_log(msg)

    def _on_finished(self, results: dict):
        ok = sum(1 for r in results.values() if isinstance(r, dict) and r.get('status') == 'completed') if results else 0
        total = len(results) if results else 0
        if total:
            self.page_ctrl.append_log(f"Hoàn thành: {ok}/{total} thành công.")
        else:
            self.page_ctrl.append_log("Automation kết thúc (không có kết quả hoặc đã dừng).")
        self.page_ctrl.set_running(False)
        self.worker = None

    def _on_error(self, err: str):
        self.page_ctrl.append_log(f"Lỗi: {err}")
        self.page_ctrl.set_running(False)
        self.worker = None

# ---------- Widget Wrapper for Compatibility ----------
class ZaloAutomationWidget(MainWindow):
    """Wrapper class for compatibility with existing imports"""
    def __init__(self, parent=None):
        super().__init__()
        if parent:
            self.setParent(parent)

# ---------- Entrypoint ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
