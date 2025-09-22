# Tài Liệu Flow Chi Tiết - Core1.py

## 📋 Tổng Quan Kiến Trúc

### Thông Tin Dự Án
- **File chính**: `y:\tool auto\core1.py` (4707 dòng)
- **Mục đích**: Hệ thống automation Zalo multi-device với đồng bộ hóa group chat
- **Công nghệ**: UIAutomator2, Threading, File-based synchronization
- **Kiến trúc**: Device wrapper + Flow management + Barrier synchronization

### Cấu Trúc Thư Mục
```
y:\tool auto\
├── core1.py                    # File chính (4707 dòng)
├── main_gui.py                 # GUI interface
├── phone_mapping.json          # Mapping IP ↔ Phone number
├── conversations/              # Thư mục chứa conversation data
├── sync_files/                 # Thư mục đồng bộ barrier
├── ui/                         # UI components
└── core/                       # Core modules
```

## 🏗️ Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────┐
│                        CORE1.PY ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│  Entry Points                                                   │
│  ├── main()                    # CLI entry point               │
│  ├── run_automation_from_gui() # GUI entry point               │
│  └── get_available_devices_for_gui() # Device discovery        │
├─────────────────────────────────────────────────────────────────┤
│  Device Management Layer                                        │
│  ├── Device class              # UIAutomator2 wrapper          │
│  ├── get_all_connected_devices() # ADB device discovery        │
│  └── Phone mapping (IP ↔ Phone) # Device pairing logic        │
├─────────────────────────────────────────────────────────────────┤
│  Flow Management Layer                                          │
│  ├── flow()                    # Main automation logic         │
│  ├── run_conversation()        # Group chat automation         │
│  └── run_device_automation()   # Device wrapper with threading │
├─────────────────────────────────────────────────────────────────┤
│  Synchronization Layer                                          │
│  ├── Barrier Sync             # Multi-device coordination      │
│  ├── Message ID Sync          # Conversation turn management   │
│  └── Status Management        # Real-time status updates       │
├─────────────────────────────────────────────────────────────────┤
│  UI Automation Layer                                            │
│  ├── Zalo UI Helpers          # App-specific automation        │
│  ├── Search & Navigation      # UI interaction functions       │
│  └── Friend Request Flow      # Social features automation     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Flow Chính

### 1. Main Flow (Entry Point)

**Function**: `main()`
**Vị trí**: Dòng 1521-1720
**Mục đích**: Entry point chính từ CLI

```
┌─────────────────┐
│   main()        │
│                 │
├─ Parse CLI args │
├─ Load phone map │
├─ Setup mode?    │
├─ Device select  │
├─ Single/Multi?  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Single Device   │ ──────┐
│ main_single_    │       │
│ device()        │       │
└─────────────────┘       │
         │                │
         ▼                ▼
┌─────────────────┐   ┌─────────────────┐
│ Multi Device    │   │    flow()       │
│ main_multi_     │   │                 │
│ device()        │   │ Main automation │
└─────────────────┘   │ logic           │
         │             └─────────────────┘
         ▼
┌─────────────────┐
│ Threading &     │
│ Coordination    │
└─────────────────┘
```

**Các bước chính**:
1. Parse command line arguments
2. Load phone mapping từ file
3. Xử lý setup mode (interactive/quick)
4. Validate và update device mapping
5. Discover connected devices
6. Chọn single/multi device mode
7. Khởi chạy automation

### 2. Zalo Automation Flow (GUI Integration)

**Function**: `run_automation_from_gui()`
**Vị trí**: Dòng 4540-4600
**Mục đích**: Entry point từ GUI

```
┌─────────────────┐
│ GUI Request     │
│ - Selected devs │
│ - Conversation  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Device Connect  │
│ - Validate IPs  │
│ - Test connect  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Run Automation  │
│ - Call flow()   │
│ - Collect result│
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Cleanup &       │
│ Return Results  │
└─────────────────┘
```

### 3. Main Automation Flow

**Function**: `flow()`
**Vị trí**: Dòng 4083-4540
**Mục đích**: Logic automation chính

```
┌─────────────────┐
│ 1. Initialize   │
│ - Device info   │
│ - Status update │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 2. Group Sync   │
│ - Determine grp │
│ - Barrier sync  │
│ - Enhanced sync │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 3. Clear Apps   │
│ - Pre-clear sync│
│ - Clear recent  │
│ - Home screen   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 4. Open Zalo    │
│ - Pre-open sync │
│ - App launch    │
│ - Retry logic   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 5. Login Check  │
│ - Auth status   │
│ - Error handle  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 6. Partner Find │
│ - Phone mapping │
│ - Search UI     │
│ - Target select │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 7. Friend Flow  │
│ - Check status  │
│ - Send request  │
│ - Accept friend │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ 8. Conversation │
│ - run_convers() │
│ - Message sync  │
│ - Smart timing  │
└─────────────────┘
```

### 4. Conversation Flow (Group Chat Automation)

**Function**: `run_conversation()`
**Vị trí**: Dòng 3050-3200
**Mục đích**: Quản lý cuộc hội thoại đồng bộ

```
┌─────────────────┐
│ Load Convers.   │
│ - From file     │
│ - Format conv   │
│ - Message IDs   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Group Setup     │
│ - Determine grp │
│ - Role in group │
│ - Init sync     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Message Loop    │
│ ┌─────────────┐ │
│ │ For each    │ │
│ │ message:    │ │
│ │             │ │
│ │ Wait turn   │ │
│ │ Smart delay │ │
│ │ Send msg    │ │
│ │ Update sync │ │
│ └─────────────┘ │
└─────────────────┘
```

**Message Synchronization Flow**:
```
Device 1                    Device 2
   │                           │
   ├─ Wait message_id=1        │
   ├─ Send message 1           │
   ├─ Update sync file        │
   │                           ├─ Wait message_id=2
   │                           ├─ Send message 2
   │                           ├─ Update sync file
   ├─ Wait message_id=3        │
   ├─ Send message 3           │
   │                           ├─ Wait message_id=4
   │                           ├─ Send message 4
   ▼                           ▼
```

### 5. Device Management Flow

**Class**: `Device`
**Vị trí**: Dòng 200-500
**Mục đích**: Wrapper cho UIAutomator2

```
┌─────────────────┐
│ Device Init     │
│ - IP address    │
│ - Port config   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Connection      │
│ - ADB connect   │
│ - UI2 init      │
│ - Health check  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ UI Operations   │
│ - tap()         │
│ - swipe()       │
│ - input_text()  │
│ - element_*()   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ App Management  │
│ - app()         │
│ - app_stop()    │
│ - key()         │
└─────────────────┘
```

### 6. Barrier Synchronization Flow

**Functions**: `signal_ready_at_barrier()`, `wait_for_group_barrier()`
**Mục đích**: Đồng bộ hóa multi-device

```
Barrier Sync Points:

1. Pre-Clear Apps Barrier
   ├─ All devices ready to clear apps
   └─ Simultaneous app clearing

2. Pre-Open App Barrier  
   ├─ All devices ready to open Zalo
   └─ Simultaneous app opening

3. App Opened Barrier
   ├─ All devices opened Zalo successfully
   └─ Proceed to login check

4. Message Turn Barriers
   ├─ Wait for specific message_id
   └─ Synchronized conversation flow
```

**Barrier Implementation**:
```
┌─────────────────┐
│ Device A        │
│ signal_ready()  │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Sync File       │◄──►│ Device B        │
│ barrier_X.json  │    │ signal_ready()  │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ wait_for_group_ │    │ wait_for_group_ │
│ barrier()       │    │ barrier()       │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 ▼
         ┌─────────────────┐
         │ All Ready!      │
         │ Continue...     │
         └─────────────────┘
```

### 7. Status Management Flow

**Function**: `update_shared_status()`
**Mục đích**: Real-time status tracking

```
Status Lifecycle:

starting (0%) → syncing (10%) → clearing_apps (23%) → 
opening_app (25%) → checking_login (35%) → 
ready_for_conversation (80%) → running (50%) → 
completed (100%)

Error States:
error, stopped, connection_failed, login_required
```

## 📚 Chi Tiết Function Quan Trọng

### 1. `main()` - Entry Point Chính
```python
def main():
    # Parse CLI arguments
    # Load phone mapping
    # Handle special options (list, config, reset)
    # Setup mode handling
    # Device validation and selection
    # Single vs Multi device routing
```

### 2. `flow()` - Main Automation Logic
```python
def flow(dev, all_devices=None, stop_event=None, status_callback=None):
    # Device initialization and status update
    # Enhanced barrier synchronization
    # Clear apps with sync
    # Open Zalo with retry logic
    # Login status check
    # Partner phone mapping
    # Search and friend request flow
    # Conversation automation
```

### 3. `run_conversation()` - Chat Automation
```python
def run_conversation(dev, device_role, debug=False, all_devices=None, stop_event=None, status_callback=None):
    # Load conversation data
    # Group and role determination
    # Message ID synchronization
    # Smart timing and delays
    # Turn-based message sending
```

### 4. `Device` Class - UIAutomator2 Wrapper
```python
class Device:
    def __init__(self, device_id)
    def connect()
    def disconnect()
    def tap(x, y)
    def swipe(x1, y1, x2, y2)
    def input_text(text)
    def element_exists()
    def app(package)
    def app_stop(package)
```

### 5. UI Automation Helpers

#### `ensure_on_messages_tab()`
- Đảm bảo đang ở tab Tin nhắn
- Retry logic với multiple attempts
- Resource ID validation

#### `open_search_strong()`
- Mở ô tìm kiếm với enhanced logic
- Multiple click strategies
- Verification after opening

#### `enter_query_and_submit()`
- Nhập query và submit
- Text input validation
- Search execution

#### `click_first_search_result()`
- Click kết quả tìm kiếm đầu tiên
- Friend request flow integration
- Preferred text matching

## 🔄 Luồng Dữ Liệu và Dependencies

### Data Flow
```
CLI Args/GUI Input
        │
        ▼
Phone Mapping (JSON)
        │
        ▼
Device Discovery (ADB)
        │
        ▼
Device Pairing Logic
        │
        ▼
Conversation Data (JSON)
        │
        ▼
Barrier Sync Files
        │
        ▼
Status Updates
        │
        ▼
Automation Results
```

### File Dependencies
```
phone_mapping.json          # IP ↔ Phone mapping
conversations/group_X.json  # Conversation data
sync_files/barrier_X.json   # Barrier synchronization
sync_files/message_X.json   # Message turn sync
status_X.json              # Device status tracking
```

### External Dependencies
```
uiautomator2               # Android UI automation
subprocess                 # ADB command execution
threading                  # Multi-device coordination
json                       # Data serialization
time                       # Timing and delays
random                     # Smart delay patterns
os                         # File system operations
```

## 🛠️ Error Handling và Debugging

### Error Handling Strategies

1. **Retry Logic**
   - App opening: 5 attempts với progressive delay
   - UI operations: 3 attempts với exponential backoff
   - Barrier sync: 3 attempts với cleanup

2. **Timeout Management**
   - Barrier sync: 90-150s adaptive timeout
   - UI operations: 5-10s per operation
   - Message turns: 600s conversation timeout

3. **Fallback Mechanisms**
   - Barrier failure → Independent execution
   - UI element not found → Alternative strategies
   - Connection loss → Reconnection attempts

### Debugging Features

1. **UI Dump Analysis**
   ```python
   def dump_ui_and_log(dev, context="", debug=False)
   def check_btn_send_friend_request_in_dump()
   ```

2. **Status Tracking**
   ```python
   def update_shared_status(device_ip, status, message, progress)
   ```

3. **Debug Logging**
   - Extensive debug prints với [DEBUG] prefix
   - Function entry/exit logging
   - Parameter và result logging

## ⚙️ Configuration Management

### Configuration Files

1. **phone_mapping.json**
   ```json
   {
     "phone_mapping": {
       "192.168.1.100:5555": "0123456789",
       "192.168.1.101:5555": "0987654321"
     }
   }
   ```

2. **conversations/group_X.json**
   ```json
   [
     {"message_id": 1, "device_number": 1, "content": "Hello"},
     {"message_id": 2, "device_number": 2, "content": "Hi there"}
   ]
   ```

3. **Resource IDs (Constants)**
   ```python
   RID_TAB_MESSAGE = "com.zing.zalo:id/tab_message"
   RID_SEARCH_BUTTON = "com.zing.zalo:id/search_button"
   RID_MSG_LIST = "com.zing.zalo:id/message_list"
   ```

### Environment Variables
```bash
DEVICES="192.168.1.100,192.168.1.101"  # Device list
DEBUG="1"                               # Debug mode
```

## 🚀 Cách Sử Dụng

### CLI Usage
```bash
# Single device
python core1.py --devices 192.168.1.100:0123456789

# Multiple devices
python core1.py --devices 192.168.1.100:0123456789 192.168.1.101:0987654321

# Interactive setup
python core1.py --interactive

# Quick setup
python core1.py --quick-setup
```

### GUI Integration
```python
# Get available devices
devices = get_available_devices_for_gui()

# Run automation
results = run_automation_from_gui(
    selected_devices=["192.168.1.100", "192.168.1.101"],
    conversation_text="Hello\nHi there"
)
```

## 📊 Performance và Optimization

### Timing Optimizations
- Smart delay patterns (70% fast, 30% slow messages)
- Adaptive timeouts based on retry attempts
- Staggered device startup để tránh conflicts

### Resource Management
- Device connection pooling
- File-based synchronization thay vì network
- Cleanup automatic cho temp files

### Scalability
- Group-based device pairing (2 devices per group)
- Parallel execution với threading
- Modular conversation loading

---

**Tài liệu này mô tả chi tiết flow và kiến trúc của core1.py - hệ thống automation Zalo multi-device với đồng bộ hóa group chat.**

*Cập nhật lần cuối: 2024*