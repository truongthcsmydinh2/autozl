# Hướng dẫn Parallel Execution - Zalo Automation

## Tổng quan

Hệ thống Zalo Automation đã được cập nhật để hỗ trợ **parallel execution** (thực thi đồng thời) cho multiple device pairs, giúp tăng hiệu suất và giảm thời gian thực hiện automation.

## Cách thức hoạt động

### 1. Parallel Execution ở cấp độ Cặp (Pair-level)

- **Trước đây**: Các cặp thiết bị chạy tuần tự (cặp 1 → cặp 2 → cặp 3)
- **Hiện tại**: Tất cả các cặp chạy đồng thời (cặp 1 || cặp 2 || cặp 3)

```
Trước:  [Cặp 1] → [Cặp 2] → [Cặp 3]  (Thời gian: 3x)
Sau:    [Cặp 1] || [Cặp 2] || [Cặp 3]  (Thời gian: 1x)
```

### 2. Parallel Execution trong mỗi Cặp

#### Close App & Open Zalo: Đồng thời
- Cả 2 thiết bị trong cặp đóng app và mở Zalo cùng lúc
- Giảm thời gian chờ đợi

#### Nhắn tin: Tuần tự trong cặp
- Trong mỗi cặp: Device 1 nhắn trước → Device 2 nhắn sau
- Giữa các cặp: Tất cả cặp nhắn tin đồng thời

```
Cặp 1: [Device A nhắn] → [Device B nhắn]
Cặp 2: [Device C nhắn] → [Device D nhắn]  // Đồng thời với Cặp 1
Cặp 3: [Device E nhắn] → [Device F nhắn]  // Đồng thời với Cặp 1,2
```

## Cải tiến về Performance

### Staggered Start
- **Delay giữa các cặp**: 1 giây để tránh overload
- **Delay giữa devices trong cặp**: 8s, 11s, 14s... để tránh race condition

### Thread Management
- Mỗi cặp chạy trong thread riêng biệt
- Mỗi device trong cặp chạy trong sub-thread riêng
- Sử dụng `threading.Event` để đồng bộ hóa completion

## Error Handling

### 1. Connection Failures
- Nếu 1 device trong cặp kết nối thất bại → Cặp đó bị skip
- Các cặp khác tiếp tục chạy bình thường

### 2. App Open Failures
- Retry logic: 5 lần thử với delay tăng dần
- Nếu thất bại → Device đó báo `APP_OPEN_FAILED`
- Cặp vẫn tiếp tục với device còn lại

### 3. Stop Signal Handling
- Stop signal được kiểm tra ở nhiều điểm:
  - Trước khi bắt đầu automation
  - Trong quá trình delay
  - Trước và sau khi chạy flow
- Tất cả threads dừng gracefully khi nhận stop signal

### 4. Timeout Protection
- **Thread timeout**: 300 giây (5 phút)
- **Force cleanup**: Nếu threads không kết thúc đúng hạn
- **Enhanced logging**: Chi tiết trạng thái từng thread

## Progress Tracking

### Progress Callbacks
```python
# Thông báo bắt đầu parallel mode
"🚀 Bắt đầu automation với Parallel Mode cho {n} cặp thiết bị"

# Thông báo khởi tạo cặp
"🔄 Khởi tạo cặp {i}/{total}: {ip1} ↔ {ip2} (Parallel Mode)"

# Thông báo delay
"⏸️ Device {ip} delay {n}s..."

# Thông báo hoàn thành
"✅ Hoàn thành {ip}: {result}"
```

### Status Callbacks
```python
# Trạng thái device
status_callback('device_status', device_ip, 'Đang chuẩn bị', '')
status_callback('device_status', device_ip, 'Đang chạy automation', '')
status_callback('device_status', device_ip, 'Hoàn thành', result)
status_callback('device_status', device_ip, 'Lỗi', error_message)
```

## Monitoring & Debugging

### Thread Status Logging
```
⏳ [THREAD_WAIT] Còn 2/6 events chưa completed (45s/300s)
  Thread 1 (Device-192.168.1.100:5555): ✅ DONE
  Thread 2 (Device-192.168.1.101:5555): 🔄 ALIVE
  Thread 3 (Device-192.168.1.102:5555): ✅ DONE
  Thread 4 (Device-192.168.1.103:5555): 🔄 ALIVE
  Thread 5 (Device-192.168.1.104:5555): ✅ DONE
  Thread 6 (Device-192.168.1.105:5555): ✅ DONE
```

### Force Cleanup Logging
```
⚠️ [FORCE_CLEANUP] Timeout waiting for done_events after 300.0s
🔧 [FORCE_CLEANUP] Bắt đầu force cleanup cho 2 threads...
🔧 [FORCE_CLEANUP] Force joining thread Device-192.168.1.101:5555 (done_event: NOT_SET)
✅ [FORCE_CLEANUP] Thread Device-192.168.1.101:5555 đã join thành công
```

## Lợi ích

1. **Tăng tốc độ**: Giảm thời gian thực hiện từ O(n) xuống O(1) cho n cặp
2. **Tối ưu tài nguyên**: Sử dụng đồng thời nhiều devices
3. **Robust error handling**: Xử lý lỗi không ảnh hưởng đến các cặp khác
4. **Monitoring tốt hơn**: Theo dõi chi tiết trạng thái từng thread
5. **Graceful shutdown**: Dừng an toàn khi cần thiết

## Cấu hình

### Timing Parameters
```python
# Delay giữa các cặp khi start
PAIR_START_DELAY = 1  # giây

# Delay giữa devices trong cặp
DEVICE_START_DELAY = 8 + (device_index * 3)  # 0s, 11s, 14s...

# Thread join timeout
THREAD_JOIN_TIMEOUT = 5.0  # giây

# Max wait time cho threads
MAX_THREAD_WAIT_TIME = 300  # giây (5 phút)
```

### Retry Logic
```python
# App open retry
MAX_APP_OPEN_RETRIES = 5
RETRY_DELAY_BASE = 2  # giây, tăng dần mỗi lần retry
```

## Testing

Sử dụng `test_parallel_pairs.py` để test parallel execution:

```bash
python test_parallel_pairs.py
```

Script này sẽ:
- Tạo mock device pairs
- Test parallel execution
- Đo thời gian thực hiện
- So sánh với thời gian tuần tự
- Báo cáo kết quả chi tiết

## Troubleshooting

### Vấn đề thường gặp

1. **Threads không kết thúc**
   - Kiểm tra log `[THREAD_WAIT]`
   - Xem stacktrace trong `[FORCE_CLEANUP]`
   - Tăng timeout nếu cần

2. **Connection failures**
   - Kiểm tra network connectivity
   - Verify device IPs
   - Check ADB connection

3. **App open failures**
   - Kiểm tra Zalo app đã cài đặt
   - Verify app package name
   - Check device permissions

### Debug Commands

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor thread status
import threading
print(f"Active threads: {threading.active_count()}")
for thread in threading.enumerate():
    print(f"  {thread.name}: {thread.is_alive()}")
```

---

*Tài liệu này được tạo tự động và cập nhật theo phiên bản mới nhất của hệ thống.*