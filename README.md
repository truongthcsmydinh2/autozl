# Android Automation GUI Application

🚀 **Ứng dụng Windows GUI cho Android Automation Tool**

Ứng dụng PyQt6 hiện đại để quản lý và điều khiển các thiết bị Android thông qua ADB với giao diện đồ họa trực quan.

## ✨ Tính năng chính

### 🏠 Dashboard
- Tổng quan hệ thống với thống kê thiết bị và flows
- Hiển thị trạng thái kết nối real-time
- Quick actions cho các tác vụ thường dùng

### 📱 Device Management
- Quản lý danh sách thiết bị Android kết nối
- Kết nối/ngắt kết nối thiết bị
- Xem thông tin chi tiết thiết bị
- Chụp screenshot và mở ADB shell
- Phone mapping configuration

### 📝 Flow Editor
- Editor với syntax highlighting cho automation scripts
- Hot-reload functionality
- Auto-save và backup
- Template và snippet management

### ▶️ Execution Control
- Điều khiển thực thi flows trên nhiều thiết bị
- Real-time monitoring và progress tracking
- Pause/resume/stop execution
- Batch execution support

### 📊 Logs Viewer
- Xem logs real-time với filtering
- Export logs ra file
- Search và highlight
- Multiple log levels support

### ⚙️ Settings Configuration
- Cấu hình ứng dụng toàn diện
- Theme và appearance settings
- Device connection settings
- Advanced configuration options
- Import/export settings

## 🛠️ Cài đặt

### Yêu cầu hệ thống
- Windows 10/11
- Python 3.8+
- ADB (Android Debug Bridge)

### Cài đặt dependencies
```bash
pip install -r requirements_gui.txt
```

### Chạy ứng dụng
```bash
python main_gui.py
```

## 📦 Đóng gói thành .exe

### Sử dụng build script
```bash
# Cài đặt dependencies và build
python build_exe.py

# Hoặc từng bước
python build_exe.py --install-deps
python build_exe.py --clean
python build_exe.py --build
```

### Manual build với PyInstaller
```bash
pyinstaller --onefile --windowed --name=AndroidAutomationGUI main_gui.py
```

## 🏗️ Cấu trúc project

```
android-automation-gui/
├── main_gui.py              # Entry point
├── requirements_gui.txt     # Dependencies
├── build_exe.py            # Build script
├── README.md               # Documentation
│
├── ui/                     # UI Components
│   ├── main_window.py      # Main window
│   ├── device_management.py # Device management UI
│   ├── flow_editor.py      # Flow editor UI
│   ├── execution_control.py # Execution control UI
│   └── settings.py         # Settings UI
│
├── core/                   # Business Logic
│   ├── device_manager.py   # Device management
│   ├── flow_manager.py     # Flow management
│   └── config_manager.py   # Configuration
│
├── config/                 # Configuration Files
│   ├── default_config.json
│   └── user_config.json
│
├── flows/                  # Automation Scripts
│   └── examples/
│
└── assets/                 # Resources
    ├── icons/
    └── themes/
```

## 🚀 Sử dụng

### 1. Kết nối thiết bị
1. Mở ứng dụng
2. Vào tab "Devices"
3. Bật USB Debugging trên Android
4. Kết nối thiết bị qua USB
5. Click "Refresh" để phát hiện thiết bị

### 2. Tạo automation flow
1. Vào tab "Flow Editor"
2. Tạo file .py mới hoặc mở file có sẵn
3. Viết automation script
4. Save file (auto-save enabled)

### 3. Thực thi flow
1. Vào tab "Execution"
2. Chọn flow file
3. Chọn thiết bị target
4. Click "Start Execution"
5. Monitor progress trong Logs

### 4. Cấu hình settings
1. Vào tab "Settings"
2. Điều chỉnh các tùy chọn
3. Click "Save" để lưu

## 🔧 Tính năng nâng cao

### Hot-reload
- Tự động reload flows khi file thay đổi
- Không cần restart ứng dụng
- Preserve execution state

### Batch execution
- Chạy multiple flows đồng thời
- Queue management
- Resource allocation

### Phone mapping
- Map logical names cho thiết bị
- Quick setup wizard
- Persistent configuration

## 🐛 Troubleshooting

### Thiết bị không được phát hiện
1. Kiểm tra USB Debugging enabled
2. Kiểm tra ADB path trong Settings
3. Thử disconnect/reconnect USB
4. Restart ADB server: `adb kill-server && adb start-server`

### Lỗi execution
1. Kiểm tra syntax trong Flow Editor
2. Xem logs chi tiết trong Logs tab
3. Verify device permissions
4. Check flow file path

### Performance issues
1. Giảm refresh interval trong Settings
2. Disable auto-save nếu không cần
3. Clear logs periodically
4. Close unused tabs

## 📄 License

MIT License - Xem file LICENSE để biết chi tiết.

## 🤝 Contributing

Welcome contributions! Please read CONTRIBUTING.md for guidelines.

## 📞 Support

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.

---

**Phát triển bởi SOLO Coding** 🚀