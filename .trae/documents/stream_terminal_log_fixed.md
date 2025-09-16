
# Hướng Dẫn Stream Toàn Bộ Log Hoạt Động Vào Tab Terminal Trong AutoZL

## 1. Mục Tiêu
- Thêm **tab "Terminal Log"** trong giao diện tool AutoZL.
- Hiển thị **toàn bộ log hoạt động real-time**, bao gồm:
  - Log ADB (`adb logcat`).
  - Log nội bộ của tool (`print`, `logger.debug`, vv...).
  - Trạng thái nuôi nick Zalo.
- **Chỉ xem log**, không có tính năng nhập lệnh hay tương tác.

---

## 2. Kiến Trúc Tổng Quan
```
[Tool auto Zalo]
 └── GUI (PyQt5/Tkinter)
      └── Tab "Terminal Log"
           └── QPlainTextEdit (ReadOnly)
                ↑
           Worker Thread (subprocess.Popen → đọc stdout → emit signal)
```
- **Worker thread** chạy lệnh log như `adb logcat` hoặc `python core1.py --debug`.
- Log đọc được sẽ emit ra **UI thread** qua `PyQt Signal`.
- UI chỉ **hiển thị log**, không cần input ngược lại.

---

## 3. Code Mẫu PyQt5

### A. Worker Đọc Log
```python
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess

class LogWorker(QThread):
    new_log = pyqtSignal(str)

    def run(self):
        # Lệnh muốn stream log (ví dụ adb logcat)
        process = subprocess.Popen(
            ["adb", "logcat"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Đọc log liên tục từng dòng
        for line in iter(process.stdout.readline, ''):
            self.new_log.emit(line.strip())

        process.stdout.close()
        process.wait()
```

### B. Tạo Tab Terminal Log
```python
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton

class TerminalLogTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Widget hiển thị log
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)

        # Nút Clear log
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.log_view.clear)

        layout.addWidget(self.log_view)
        layout.addWidget(self.clear_btn)

        # Khởi tạo worker
        self.worker = LogWorker()
        self.worker.new_log.connect(self.update_log)
        self.worker.start()

    def update_log(self, text):
        # Nhận log từ worker và hiển thị lên UI
        self.log_view.appendPlainText(text)
        # Auto scroll xuống cuối
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )
```

### C. Nhúng Tab Vào Giao Diện Chính
Trong `main_gui.py` hoặc nơi setup `QTabWidget`:
```python
from terminal_log_tab import TerminalLogTab

# Giả sử self.tabs là QTabWidget
terminal_tab = TerminalLogTab()
self.tabs.addTab(terminal_tab, "Terminal Log")
```

---

## 4. Stream Log Nội Bộ Tool
Để stream **toàn bộ log nội bộ** (`print`, `logger.debug`) lên cùng tab:

```python
import sys

class QtLogRedirector:
    def __init__(self, signal):
        self.signal = signal

    def write(self, text):
        if text.strip():
            self.signal.emit(text)

    def flush(self):
        pass
```

Trong `TerminalLogTab.__init__`:
```python
import sys
sys.stdout = QtLogRedirector(self.worker.new_log)
sys.stderr = QtLogRedirector(self.worker.new_log)
```

Bây giờ mọi `print()` hoặc `logger.debug()` trong tool đều sẽ tự động hiển thị lên tab "Terminal Log".

---

## 5. Tùy Chỉnh Lệnh Log
| Mục đích | Lệnh trong code |
|----------|----------------|
| Stream log toàn bộ thiết bị ADB | `["adb", "logcat"]` |
| Log 1 thiết bị cụ thể | `["adb", "-s", "192.168.5.74:5555", "logcat"]` |
| Log nội bộ tool nuôi nick | `["python", "core1.py", "--debug"]` |
| Log đa nguồn (ADB + tool) | Chạy nhiều `LogWorker` song song |

---

## 6. Tính Năng Nâng Cao
- **Highlight log**:
  - Error → màu đỏ
  - Warning → màu vàng
  - Info → màu trắng
- **Save log ra file**:
  - Thêm nút "Save Log" để export log ra `.txt`.
- **Filter log**:
  - Thêm ô tìm kiếm lọc keyword như `"uiautomator"`, `"error"`. 

---

## 7. Kết Quả Cuối Cùng
- Tab "Terminal Log" sẽ hiển thị **real-time log**:
  - ADB logcat
  - Log nội bộ của tool
  - Thao tác và trạng thái nuôi nick Zalo
- Không cần mở terminal ngoài → tiện theo dõi, gọn gàng.
- Có nút **Clear** và khả năng auto scroll.

---

## 8. Tóm Tắt Quy Trình
1. **Tạo LogWorker** dùng `subprocess.Popen` để đọc stdout liên tục.
2. Emit từng dòng log ra UI qua `signal`.
3. Trong Tab Terminal Log, **append log vào QPlainTextEdit** và auto scroll.
4. Redirect `stdout` + `stderr` → tất cả log nội bộ sẽ hiển thị chung.
5. Nhúng tab vào giao diện chính thông qua `QTabWidget`.
