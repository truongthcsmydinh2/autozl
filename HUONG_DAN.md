# 📱 Hướng Dẫn Sử Dụng Tool Automation Zalo

## 🎯 Giới Thiệu Tool

**UIAutomator2 Zalo Automation Tool** là công cụ tự động hóa cuộc hội thoại trên Zalo sử dụng UIAutomator2. Tool hỗ trợ:

- ✅ Tự động gửi tin nhắn theo kịch bản
- ✅ Đồng bộ hóa tin nhắn giữa nhiều devices
- ✅ CLI phone mapping linh hoạt
- ✅ Smart delay và message_id synchronization
- ✅ Multi-device conversation automation

### 🔧 Yêu Cầu Hệ Thống

- **Python**: 3.7+
- **ADB**: Android Debug Bridge
- **Android devices**: API 18+ (Android 4.3+)
- **Network**: Devices cùng mạng LAN hoặc USB connection

---

## 📦 Hướng Dẫn Cài Đặt

### 1. Cài Đặt Python Packages

```bash
# Cài đặt UIAutomator2
pip install uiautomator2

# Cài đặt các dependencies khác (nếu cần)
pip install -r requirements.txt
```

### 2. Cài Đặt ADB

**Windows:**
```bash
# Download Android SDK Platform Tools
# Thêm ADB vào PATH environment variable
adb version  # Kiểm tra cài đặt
```

**macOS:**
```bash
brew install android-platform-tools
```

**Linux:**
```bash
sudo apt install android-tools-adb
```

### 3. Cài Đặt UIAutomator2 trên Devices

```bash
# Kết nối device qua USB hoặc WiFi
adb connect 192.168.5.74:5555

# Cài đặt UIAutomator2 server
python -m uiautomator2 init
```

### 4. Kết Nối Devices

**USB Connection:**
```bash
adb devices  # Kiểm tra devices kết nối
```

**WiFi Connection:**
```bash
# Bật ADB over WiFi trên device
adb tcpip 5555
adb connect 192.168.5.74:5555
```

---

## 📞 Cấu Hình Phone Mapping

Phone mapping là việc liên kết IP address của device với số điện thoại Zalo tương ứng.

### 🎯 Các Cách Cấu Hình

#### 1. CLI Arguments (Ưu tiên cao nhất)

```bash
# Thêm một device
python core1.py --add-device 192.168.5.74 569924311

# Thêm nhiều devices
python core1.py --devices 192.168.5.74:569924311 192.168.5.82:583563439

# Device mapping string
python core1.py -dm "192.168.5.74:569924311,192.168.5.82:583563439"
```

#### 2. Quick Setup Mode

```bash
# Tự động detect devices và nhập số điện thoại
python core1.py --quick-setup
```

**Output:**
```
🚀 QUICK SETUP MODE
=========================
📱 Phát hiện 2 device(s) từ ADB:

📱 Device 1/2: 192.168.5.74:5555
📞 Nhập số điện thoại: 569924311
  ✅ 192.168.5.74 -> 569924311

📱 Device 2/2: 192.168.5.82:5555
📞 Nhập số điện thoại: 583563439
  ✅ 192.168.5.82 -> 583563439

💾 Lưu vào file config? (Y/n): Y
✅ Đã lưu phone mapping vào phone_mapping.json
```

#### 3. Interactive Mode

```bash
python core1.py --interactive
```

**Features:**
- Hiển thị devices hiện có
- Nhập nhanh format `IP:PHONE`
- Validation số điện thoại
- Lưu vào file config

#### 4. File Config (phone_mapping.json)

```json
{
  "phone_mapping": {
    "192.168.5.74": "569924311",
    "192.168.5.82": "583563439"
  },
  "timestamp": 1699123456.789,
  "created_by": "core1.py CLI"
}
```

### 📋 Quản Lý Phone Mapping

```bash
# Xem danh sách devices và mapping
python core1.py --list-devices

# Xem config hiện tại
python core1.py --show-config

# Reset config về default
python core1.py --reset-config
```

---

## 🚀 Cách Sử Dụng

### 1. Chế Độ Bình Thường

```bash
# Chạy với config mặc định
python core1.py

# Sử dụng biến môi trường
set DEVICES=192.168.5.74:5555,192.168.5.82:5555
python core1.py
```

### 2. Multi-Device Mode

```bash
# Thiết lập nhiều devices
python core1.py --devices 192.168.5.74:569924311 192.168.5.82:583563439 192.168.5.100:123456789 192.168.5.101:987654321

# Chạy conversation automation
python core1.py
```

**Cách hoạt động:**
- Devices được chia thành các nhóm 2 máy
- Mỗi nhóm chạy conversation riêng biệt
- Đồng bộ hóa tin nhắn qua message_id
- Smart delay dựa trên độ dài tin nhắn

### 3. Single Device Mode

```bash
# Chỉ định một device
set DEVICE=192.168.5.74:5555
python core1.py
```

---

## 💬 Conversation Data

### Format Conversation

File `conversation_data.json`:

```json
{
  "timestamp": "2025-09-10 23:28:10",
  "total_pairs": 2,
  "conversations": {
    "pair_1": {
      "devices": [
        {"id": "192.168.5.74", "type": "LAN", "status": "Connected"},
        {"id": "192.168.5.82", "type": "LAN", "status": "Connected"}
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Cậu đang làm gì đấy"},
        {"message_id": 2, "device_number": 2, "content": "Đang xem phim nè"},
        {"message_id": 3, "device_number": 1, "content": "Phim gì thế"}
      ]
    },
    "pair_2": {
      "devices": [
        {"id": "192.168.5.100", "type": "LAN", "status": "Connected"},
        {"id": "192.168.5.101", "type": "LAN", "status": "Connected"}
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Chào bạn"},
        {"message_id": 2, "device_number": 2, "content": "Chào cậu"}
      ]
    }
  }
}
```

### Message ID Synchronization

- **message_id**: Đảm bảo tin nhắn được gửi theo đúng thứ tự
- **device_number**: 1 hoặc 2 (role trong nhóm)
- **content**: Nội dung tin nhắn

### Sync Files

Tool tạo file sync tạm thời: `sync_group_{group_id}.json`

```json
{
  "current_message_id": 5,
  "timestamp": 1699123456.789
}
```

---

## 📝 Ví Dụ Commands

### Cơ Bản

```bash
# Xem help
python core1.py --help

# Liệt kê devices
python core1.py -ld

# Quick setup
python core1.py --quick-setup

# Chạy bình thường
python core1.py
```

### Nâng Cao

```bash
# Kết hợp nhiều options
python core1.py -ad 192.168.5.74 569924311 --show-config

# Batch setup nhiều devices
python core1.py --devices 192.168.5.74:569924311 192.168.5.82:583563439 192.168.5.100:123456789

# Interactive với validation
python core1.py -i

# Reset và setup lại
python core1.py --reset-config
python core1.py --quick-setup
```

### Workflow Hoàn Chỉnh

```bash
# 1. Kiểm tra devices kết nối
adb devices

# 2. Setup phone mapping
python core1.py --quick-setup

# 3. Kiểm tra config
python core1.py --show-config

# 4. Chạy automation
python core1.py
```

---

## 📁 Cấu Trúc Files

```
tool auto/
├── core1.py                 # Main automation script
├── main.py                  # Alternative main script
├── conversation_data.json   # Conversation scenarios
├── phone_mapping.json       # Phone mapping config
├── device_data.json         # Device information
├── sync_group_*.json        # Temporary sync files
├── requirements.txt         # Python dependencies
└── HUONG_DAN.md            # This guide
```

### File Descriptions

| File | Mô Tả | Format |
|------|-------|--------|
| `core1.py` | Script chính với UIAutomator2 | Python |
| `conversation_data.json` | Kịch bản hội thoại | JSON |
| `phone_mapping.json` | Mapping IP → Phone | JSON |
| `sync_group_*.json` | Đồng bộ message_id | JSON (temp) |

---

## ❓ FAQ & Troubleshooting

### Lỗi Thường Gặp

#### 1. "UIAutomator2 chưa được cài đặt"

```bash
# Giải pháp
pip install uiautomator2
python -m uiautomator2 init
```

#### 2. "Không có device nào kết nối"

```bash
# Kiểm tra ADB
adb devices

# Kết nối lại
adb connect 192.168.5.74:5555

# Restart ADB server
adb kill-server
adb start-server
```

#### 3. "Permission denied for table"

- Đảm bảo Zalo đã đăng nhập
- Kiểm tra quyền accessibility
- Restart UIAutomator2 service

#### 4. "Device mapping không hợp lệ"

```bash
# Kiểm tra format
python core1.py -ad 192.168.5.74 569924311  # ✅ Đúng
python core1.py -ad 192.168.5.74 abc123     # ❌ Sai
```

#### 5. "Timeout đợi message_id"

- Kiểm tra network connection
- Restart devices
- Xóa sync files: `del sync_group_*.json`

### Tips Sử Dụng

#### 🎯 Performance Tips

1. **Sử dụng WiFi connection** thay vì USB cho nhiều devices
2. **Đảm bảo devices cùng mạng** để sync tốt hơn
3. **Không chạy quá nhiều devices** cùng lúc (max 4-6)
4. **Kiểm tra battery optimization** trên Android

#### 🔧 Configuration Tips

1. **Backup phone_mapping.json** trước khi thay đổi
2. **Sử dụng --show-config** để verify setup
3. **Test với 2 devices** trước khi scale up
4. **Monitor sync files** nếu có vấn đề timing

#### 🐛 Debugging Tips

1. **Chạy với debug mode:**
   ```bash
   # Thêm debug prints trong code
   python core1.py  # Check console output
   ```

2. **Kiểm tra UIAutomator2 service:**
   ```bash
   python -c "import uiautomator2 as u2; print(u2.connect('192.168.5.74:5555').info)"
   ```

3. **Monitor ADB logs:**
   ```bash
   adb logcat | grep -i uiautomator
   ```

### Validation Rules

#### IP Address
- Format: `192.168.x.x` hoặc `192.168.x.x:5555`
- Valid: `192.168.5.74`, `192.168.5.74:5555`
- Invalid: `192.168.5`, `256.256.256.256`

#### Phone Number
- Format: 9-15 chữ số, có thể có `+` ở đầu
- Valid: `569924311`, `+84569924311`, `0569924311`
- Invalid: `abc123`, `123`, `++123456789`

---

## 🎉 Kết Luận

Tool automation này cung cấp giải pháp hoàn chỉnh cho việc tự động hóa cuộc hội thoại Zalo với:

- ✅ **CLI phone mapping** linh hoạt
- ✅ **Message synchronization** chính xác
- ✅ **Multi-device support** mạnh mẽ
- ✅ **Smart timing** tự nhiên
- ✅ **Error handling** robust

### 📞 Hỗ Trợ

Nếu gặp vấn đề, hãy:
1. Kiểm tra FAQ section
2. Verify device connections
3. Check phone mapping config
4. Monitor console output

**Happy Automation! 🚀**