
# Phân Biệt Và Xử Lý Hai Trường Hợp Kết Bạn Zalo Trong Auto Tool

## 1. Trường Hợp Chưa Kết Bạn (Case 2)
**Ảnh minh hoạ:** Màn hình profile khi chưa kết bạn

- Sau khi click `com.zing.zalo:id/btn_search_result`, **không vào chat ngay**, mà hiện ra màn hình profile.
- Đặc điểm nhận dạng:
  - Có nút **Chat**: `com.zing.zalo:id/btn_send_message`
  - Có nút **Kết bạn**: `com.zing.zalo:id/btn_send_friend_request`
  - Có dòng thông báo: *"You can't view Nhung's timeline posts since you're not friends"* với `resource-id="com.zing.zalo:id/description"`
  - **Không có** `EditText` chat (`com.zing.zalo:id/chatinput_text`)

### Flow xử lý:
1. Click vào `btn_send_friend_request`
2. Đợi popup hiện lên → Confirm gửi lời mời
3. Sau khi gửi thành công, quay lại hoặc refresh
4. Khi nào trở thành bạn bè mới chuyển sang bước chat

---

## 2. Trường Hợp Đã Kết Bạn (Case 1)
**Ảnh minh hoạ:** Cửa sổ chat khi đã kết bạn

- Sau khi click `com.zing.zalo:id/btn_search_result`, **vào thẳng cửa sổ chat**.
- Đặc điểm nhận dạng:
  - Có ô nhập tin nhắn: `com.zing.zalo:id/chatinput_text`
  - Có danh sách tin nhắn (RecyclerView) hiển thị
  - **Không có** nút `btn_send_friend_request`

### Flow xử lý:
- Nếu detect được `chatinput_text` → tiếp tục logic gửi tin nhắn tự động ngay lập tức.

---

## 3. Logic Phân Biệt Trong Code
Cập nhật hàm kiểm tra trạng thái bạn bè như sau:

```python
def check_friend_status(dev):
    # Ưu tiên kiểm tra đã kết bạn trước
    if dev.element_exists(resourceId="com.zing.zalo:id/chatinput_text", timeout=2):
        return "ALREADY_FRIENDS"
    
    # Nếu chưa có chat input, kiểm tra nút kết bạn
    elif dev.element_exists(resourceId="com.zing.zalo:id/btn_send_friend_request", timeout=2):
        return "NEED_FRIEND_REQUEST"
    
    # Không xác định được trạng thái
    else:
        return "UNSURE"
```

---

## 4. Quy Tắc Flow Tổng Quan
| Trường hợp | Màn hình hiển thị | Resource-ID nhận diện | Action |
|------------|-------------------|-----------------------|--------|
| **Case 1 - Đã kết bạn** | Chat window | `com.zing.zalo:id/chatinput_text` | Gửi tin nhắn ngay |
| **Case 2 - Chưa kết bạn** | Profile | `com.zing.zalo:id/btn_send_friend_request` | Gửi lời mời kết bạn → sau đó quay lại chat |

---

## 5. Nguyên Nhân Log Sai Trước Đây
- Code hiện tại **mặc định trả về `NEED_FRIEND_REQUEST`** nếu không tìm thấy nút nào.
- Khi ở Case 1 (đã kết bạn), tool **không kiểm tra `chatinput_text` trước**, dẫn đến sai luồng xử lý.

---

## 6. Đề Xuất Fix
1. Luôn kiểm tra `chatinput_text` trước tiên.
2. Nếu không có, mới kiểm tra `btn_send_friend_request`.
3. Nếu cả hai đều không tìm thấy → trả về `UNSURE` và log để debug.
4. Khi click gửi lời mời, thêm bước xác nhận popup và trạng thái nút đã thay đổi.
