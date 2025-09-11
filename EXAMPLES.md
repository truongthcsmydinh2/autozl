# 📋 VÍ DỤ SỬ DỤNG CHI TIẾT

## 📞 1. GẮNG SỐ CHO DEVICE CỤ THỂ

### Tình huống: Đã có 2 IP gắn số, muốn thêm device mới

**Hiện tại có:**
- `192.168.5.74` → `569924311`
- `192.168.5.82` → `583563439`

**Muốn thêm:**
- `192.168.5.90` → `123456789`

### 🔧 Cách 1: Thêm device đơn lẻ
```bash
# Thêm device mới
python core1.py --add-device 192.168.5.90 123456789

# Kiểm tra kết quả
python core1.py --list-devices
```

### 🔧 Cách 2: Thêm nhiều devices cùng lúc
```bash
# Thêm nhiều devices
python core1.py --devices 192.168.5.90:123456789 192.168.5.91:987654321

# Hoặc dùng device-map
python core1.py -dm "192.168.5.90:123456789,192.168.5.91:987654321"
```

### 🔧 Cách 3: Override số cũ
```bash
# Thay đổi số của device đã có
python core1.py --add-device 192.168.5.74 999888777

# Kiểm tra thay đổi
python core1.py --show-config
```

### 🔧 Cách 4: Interactive mode
```bash
# Chế độ tương tác
python core1.py -i

# Trong interactive mode:
# 📞 192.168.5.90:5555 (hiện tại: chưa có): 123456789
# 📞 192.168.5.91:5555: 192.168.5.91:987654321  # Format nhanh IP:PHONE
```

### 🔧 Cách 5: Quick setup cho devices mới
```bash
# Tự động detect devices từ ADB và nhập số
python core1.py --quick-setup
```

---

## 💬 2. NHẬP CONVERSATION MỚI BẰNG CLI

### Format conversation_data.json

```json
{
  "timestamp": "2025-01-10 15:30:00",
  "total_pairs": 2,
  "conversations": {
    "pair_1": {
      "devices": [
        {
          "id": "192.168.5.74",
          "type": "LAN",
          "status": "Connected",
          "platform": "Android (ADB)"
        },
        {
          "id": "192.168.5.82",
          "type": "LAN", 
          "status": "Connected",
          "platform": "Android (ADB)"
        }
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Chào bạn!"},
        {"message_id": 2, "device_number": 2, "content": "Chào! Bạn khỏe không?"},
        {"message_id": 3, "device_number": 1, "content": "Mình khỏe, cảm ơn bạn"},
        {"message_id": 4, "device_number": 2, "content": "Hôm nay làm gì vậy?"},
        {"message_id": 5, "device_number": 1, "content": "Mình đang học code"}
      ]
    },
    "pair_2": {
      "devices": [
        {
          "id": "192.168.5.90",
          "type": "LAN",
          "status": "Connected", 
          "platform": "Android (ADB)"
        },
        {
          "id": "192.168.5.91",
          "type": "LAN",
          "status": "Connected",
          "platform": "Android (ADB)"
        }
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Hẹn gặp ở đâu?"},
        {"message_id": 2, "device_number": 2, "content": "Quán cà phê cũ nhé"},
        {"message_id": 3, "device_number": 1, "content": "Ok, mấy giờ?"},
        {"message_id": 4, "device_number": 2, "content": "3 giờ chiều được không?"}
      ]
    }
  }
}
```

### 📝 Tạo conversation mới

**Bước 1: Tạo file conversation_data.json**
```bash
# Backup file cũ (nếu có)
cp conversation_data.json conversation_data_backup.json

# Tạo file mới
echo '{
  "timestamp": "2025-01-10 15:30:00",
  "total_pairs": 1,
  "conversations": {
    "pair_1": {
      "devices": [
        {"id": "192.168.5.74", "type": "LAN", "status": "Connected", "platform": "Android (ADB)"},
        {"id": "192.168.5.82", "type": "LAN", "status": "Connected", "platform": "Android (ADB)"}
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Tin nhắn đầu tiên"},
        {"message_id": 2, "device_number": 2, "content": "Tin nhắn trả lời"}
      ]
    }
  }
}' > conversation_data.json
```

**Bước 2: Validate format**
```bash
# Kiểm tra JSON format
python -m json.tool conversation_data.json
```

**Bước 3: Test với tool**
```bash
# Chạy tool với conversation mới
python core1.py
```

---

## 🚀 3. WORKFLOW HOÀN CHỈNH

### Step 1: Setup devices và phone mapping

```bash
# 1.1 Kiểm tra devices hiện có
python core1.py --list-devices

# 1.2 Thêm phone mapping cho devices mới
python core1.py --devices 192.168.5.74:569924311 192.168.5.82:583563439 192.168.5.90:123456789

# 1.3 Xác nhận mapping
python core1.py --show-config
```

### Step 2: Tạo conversation data

```bash
# 2.1 Tạo conversation template
cat > conversation_template.json << 'EOF'
{
  "timestamp": "2025-01-10 15:30:00",
  "total_pairs": 2,
  "conversations": {
    "pair_1": {
      "devices": [
        {"id": "192.168.5.74", "type": "LAN", "status": "Connected", "platform": "Android (ADB)"},
        {"id": "192.168.5.82", "type": "LAN", "status": "Connected", "platform": "Android (ADB)"}
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Chào bạn!"},
        {"message_id": 2, "device_number": 2, "content": "Chào! Khỏe không?"},
        {"message_id": 3, "device_number": 1, "content": "Khỏe, cảm ơn!"}
      ]
    },
    "pair_2": {
      "devices": [
        {"id": "192.168.5.90", "type": "LAN", "status": "Connected", "platform": "Android (ADB)"},
        {"id": "192.168.5.91", "type": "LAN", "status": "Connected", "platform": "Android (ADB)"}
      ],
      "conversation": [
        {"message_id": 1, "device_number": 1, "content": "Hẹn gặp ở đâu?"},
        {"message_id": 2, "device_number": 2, "content": "Quán cà phê cũ"}
      ]
    }
  }
}
EOF

# 2.2 Copy template thành file chính
cp conversation_template.json conversation_data.json
```

### Step 3: Chạy tool với config mới

```bash
# 3.1 Set biến môi trường devices
set DEVICES=192.168.5.74:5555,192.168.5.82:5555,192.168.5.90:5555,192.168.5.91:5555

# 3.2 Chạy tool
python core1.py

# 3.3 Hoặc chạy với devices cụ thể
set DEVICES=192.168.5.74:5555,192.168.5.82:5555
python core1.py
```

### Step 4: Monitor và troubleshoot

```bash
# 4.1 Kiểm tra log files
dir sync_group_*.json

# 4.2 Kiểm tra phone mapping
python core1.py --show-config

# 4.3 Reset nếu cần
python core1.py --reset-config

# 4.4 Cleanup sync files
del sync_group_*.json
```

---

## 🎯 4. ADVANCED EXAMPLES

### Multi-group conversations (4+ devices)

```bash
# Setup 6 devices thành 3 groups
python core1.py --devices \
  192.168.5.74:569924311 \
  192.168.5.82:583563439 \
  192.168.5.90:123456789 \
  192.168.5.91:987654321 \
  192.168.5.92:111222333 \
  192.168.5.93:444555666

# Set devices cho 3 groups
set DEVICES=192.168.5.74:5555,192.168.5.82:5555,192.168.5.90:5555,192.168.5.91:5555,192.168.5.92:5555,192.168.5.93:5555

# Chạy tool - tự động chia thành 3 groups
python core1.py
```

### Device pairing strategies

```bash
# Strategy 1: Sequential pairing (74-82, 90-91, 92-93)
# Devices được sort theo IP và chia đôi

# Strategy 2: Custom pairing với conversation_data.json
# Tự định nghĩa cặp devices trong file JSON

# Strategy 3: Single device testing
set DEVICE=192.168.5.74:5555
python core1.py
```

### Conversation templates

```bash
# Template 1: Casual chat
cat > casual_chat.json << 'EOF'
{
  "conversation": [
    {"message_id": 1, "device_number": 1, "content": "Chào bạn!"},
    {"message_id": 2, "device_number": 2, "content": "Chào! Khỏe không?"},
    {"message_id": 3, "device_number": 1, "content": "Khỏe, cảm ơn! Hôm nay làm gì?"}
  ]
}
EOF

# Template 2: Business chat
cat > business_chat.json << 'EOF'
{
  "conversation": [
    {"message_id": 1, "device_number": 1, "content": "Chào anh, em là Minh từ công ty ABC"},
    {"message_id": 2, "device_number": 2, "content": "Chào em, anh đang cần tư vấn sản phẩm"},
    {"message_id": 3, "device_number": 1, "content": "Dạ, em sẽ gửi catalog cho anh"}
  ]
}
EOF
```

### Batch operations

```bash
# Batch 1: Setup multiple phone mappings
for ip in 192.168.5.{74..93}; do
  phone=$((569924311 + $(echo $ip | cut -d. -f4) - 74))
  python core1.py --add-device $ip $phone
done

# Batch 2: Generate conversation for multiple groups
for group in {1..5}; do
  # Tạo conversation cho từng group
  echo "Generating conversation for group $group"
done

# Batch 3: Run tool for different device sets
for devices in "192.168.5.74:5555,192.168.5.82:5555" "192.168.5.90:5555,192.168.5.91:5555"; do
  set DEVICES=$devices
  python core1.py
  sleep 10
done
```

---

## 📋 5. CLI COMMANDS CHEAT SHEET

### Quick Reference Table

| Command | Mô tả | Ví dụ |
|---------|-------|-------|
| `--help` | Hiển thị help | `python core1.py --help` |
| `--list-devices` | Liệt kê devices | `python core1.py -ld` |
| `--show-config` | Hiển thị config | `python core1.py --show-config` |
| `--add-device IP PHONE` | Thêm 1 device | `python core1.py -ad 192.168.5.90 123456789` |
| `--devices IP:PHONE ...` | Thêm nhiều devices | `python core1.py --devices 192.168.5.90:123456789 192.168.5.91:987654321` |
| `--device-map "IP:PHONE,IP:PHONE"` | Device mapping string | `python core1.py -dm "192.168.5.90:123456789,192.168.5.91:987654321"` |
| `--interactive` | Interactive mode | `python core1.py -i` |
| `--quick-setup` | Quick setup mode | `python core1.py --quick-setup` |
| `--reset-config` | Reset config file | `python core1.py --reset-config` |

### Common Use Cases

```bash
# 1. First time setup
python core1.py --quick-setup

# 2. Add new device
python core1.py --add-device 192.168.5.100 123456789

# 3. Check current setup
python core1.py --list-devices

# 4. Run with specific devices
set DEVICES=192.168.5.74:5555,192.168.5.82:5555
python core1.py

# 5. Interactive configuration
python core1.py -i

# 6. Batch add devices
python core1.py --devices 192.168.5.90:123456789 192.168.5.91:987654321 192.168.5.92:111222333

# 7. Override existing mapping
python core1.py -dm "192.168.5.74:999888777,192.168.5.82:666555444"

# 8. Reset and start fresh
python core1.py --reset-config
python core1.py --quick-setup

# 9. Check configuration
python core1.py --show-config

# 10. Normal run
python core1.py
```

### Environment Variables

```bash
# Single device
set DEVICE=192.168.5.74:5555

# Multiple devices
set DEVICES=192.168.5.74:5555,192.168.5.82:5555,192.168.5.90:5555

# Clear environment
set DEVICE=
set DEVICES=
```

### File Operations

```bash
# Backup configs
cp phone_mapping.json phone_mapping_backup.json
cp conversation_data.json conversation_data_backup.json

# Restore configs
cp phone_mapping_backup.json phone_mapping.json
cp conversation_data_backup.json conversation_data.json

# Clean temporary files
del sync_group_*.json

# View configs
type phone_mapping.json
type conversation_data.json
```

---

## 🔧 TROUBLESHOOTING COMMANDS

```bash
# 1. Check ADB devices
adb devices

# 2. Check tool configuration
python core1.py --show-config

# 3. Validate JSON files
python -m json.tool phone_mapping.json
python -m json.tool conversation_data.json

# 4. Reset everything
python core1.py --reset-config
del sync_group_*.json
del phone_mapping.json

# 5. Test single device
set DEVICE=192.168.5.74:5555
set DEVICES=
python core1.py

# 6. Debug mode (if available)
python core1.py --debug

# 7. Check Python dependencies
pip list | findstr uiautomator2

# 8. Test device connection
python -c "import uiautomator2 as u2; print(u2.connect('192.168.5.74:5555').info)"
```

---

**💡 Tips:**
- Luôn backup config files trước khi thay đổi
- Sử dụng `--list-devices` để kiểm tra setup
- Dùng `--quick-setup` cho lần đầu cài đặt
- Environment variables có ưu tiên cao hơn CLI args
- Message_id đảm bảo tin nhắn được gửi đúng thứ tự
- Sync files tự động cleanup sau khi hoàn thành