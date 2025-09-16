
# Phân Tích Lỗi Timeout Khi Gửi Tin Nhắn Và Hướng Xử Lý

## 1. Mô Tả Hiện Tượng
Trong log xuất hiện tình huống **gửi tin nhắn thành công nhưng vẫn bị timeout**, đồng thời CLI vẫn tiếp tục chạy.

### Log minh họa:
```
✅ Gửi tin nhắn message_id 6 thành công
⏳ Nhóm 1 - Smart delay 48.7s cho message_id 7...
⚠️ Timeout waiting for threads after 300s
📥 Nhóm 1 - Đợi Máy 1 gửi message_id 7: Nghe review ổn lắm, view đẹp nữa
⚠️ Thread Device-192.168.5.74:5555 vẫn đang chạy sau timeout
⚠️ Thread Device-192.168.5.88:5555 vẫn đang chạy sau timeout
📤 Nhóm 1 - Máy 1 gửi message_id 7: Nghe review ổn lắm, view đẹp nữa
```
➡ **Tin nhắn đã xuất hiện trên chat**, nhưng hệ thống vẫn báo timeout và threads không được giải phóng.

---

## 2. Nguyên Nhân Chính
### A. Timeout chỉ ở lớp quản lý threads
- Log timeout xuất hiện từ **Thread Manager**, không phải logic gửi tin.
- Nghĩa là **thread chưa báo "hoàn thành"** trong 300 giây → bị coi là treo.

### B. Worker không gửi tín hiệu "done"
- Sau khi hoàn thành nhiệm vụ, thread phải **set trạng thái done** hoặc `join()` với main thread.
- Nếu không, `thread.is_alive()` luôn `True` → báo timeout dù thread vẫn chạy.

### C. Đồng bộ message_id bị kẹt
- Máy 2 đang **đợi máy 1 gửi message** nhưng không nhận được broadcast signal.
- Máy 2 ở trạng thái blocking, không thoát ra được → thread không kết thúc.

---

## 3. Hậu Quả
| Hiện tượng | Ảnh hưởng |
|------------|-----------|
| Gửi tin thành công nhưng timeout | Người dùng thấy kết quả mâu thuẫn, khó debug |
| Threads không được giải phóng | Lần chạy sau dễ bị treo tiếp |
| Đồng bộ message_id sai | Các máy trong nhóm không sync được luồng hội thoại |

---

## 4. Hướng Xử Lý

### A. Bổ sung tín hiệu hoàn thành cho threads
- Sau khi gửi xong, worker phải báo về main thread bằng **Event hoặc Queue**.

**Ví dụ:**
```python
def worker_task(...):
    try:
        do_send_message()
    finally:
        done_event.set()  # báo đã xong
```

### B. Broadcast message_id khi gửi xong
- Máy 1 gửi thành công **phải broadcast** để các máy khác biết đã xong:
```python
broadcast_state(group_id, current_message_id + 1)
```

Nếu không có broadcast → các máy khác cứ "đợi vô hạn".

### C. Thêm timeout nhỏ cho vòng chờ sync
- Máy 2 khi chờ sync message cần có timeout nhỏ (5–10s), nếu hết hạn → auto skip.

### D. Logging chi tiết để debug
- Thêm log trước/sau `join()`:
```python
logger.debug(f"Joining thread {t.name} ... alive={t.is_alive()}")
```
- Khi timeout, log thêm **stacktrace** bằng `threading.enumerate()` để tìm vị trí kẹt.

### E. Force cleanup khi vượt 300s
- Nếu thread vẫn chạy sau timeout, đặt flag `force_stop=True` để thoát vòng lặp và reset trạng thái nhóm.

---

## 5. Flow Xử Lý Đề Xuất
| Bước | Hiện tại | Fix đề xuất |
|------|----------|-------------|
| Máy 1 gửi message | Gửi thành công nhưng không báo | Broadcast signal + set done event |
| Máy 2 đợi message sync | Đợi vô hạn → treo thread | Poll với timeout nhỏ, auto skip nếu hết hạn |
| Thread Manager join() | Thread chưa báo done → báo timeout | Join với done event, nếu quá 300s thì cleanup và reset |

---

## 6. Kết Luận
- Lỗi timeout xuất phát từ **thread chưa được giải phóng**, không phải do lỗi gửi tin nhắn.
- Tin nhắn vẫn gửi OK → logic ADB và thao tác UI không có vấn đề.
- Fix trọng tâm:
  1. Đồng bộ message_id giữa các thiết bị.
  2. Bắt buộc thread báo trạng thái hoàn thành.
  3. Thêm logging chi tiết để dễ debug và cleanup threads kịp thời.
