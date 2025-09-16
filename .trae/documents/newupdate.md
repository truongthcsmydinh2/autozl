Phân tích hiện trạng

Từ log + code trong repo, mình rút ra những điểm sau:

Đã có phần test cho friend status fix
— Bản test (test_zalo_friend_status_fix.py) kiểm tra các trường hợp: ALREADY_FRIEND, NEED_FRIEND_REQUEST, UNKNOWN, v.v. Có tests pass được. (✅ Friend status scenario tests passed) trong log. 
GitHub

Có module ui_friend_status_fix.py
— Thực hiện việc phân tích UI dump để xác định resource-id / text để ra trạng thái friend. 
GitHub

Trong core1.py và main_gui.py có flow chính để khi biết trạng thái thì làm hành động tiếp theo
— Nhưng từ log bạn gửi, sau khi NEED_FRIEND_REQUEST được phát hiện, hệ thống vẫn tiếp tục chạy flow hội thoại mà không chuyển sang bước gửi lời mời kết bạn.

Có cấu hình fallback / unknown status
— Nếu không tìm thấy chatinput_text hoặc btn_send_friend_request hay text chỉ ra profile bị giới hạn, thì trả về UNKNOWN. 
GitHub

Vấn đề chính

Logic phát hiện NEED_FRIEND_REQUEST hoạt động nhưng flow xử lý sau đó không thực thi đúng chức năng gửi lời mời kết bạn.

Có lẽ trong code, sau khi status được xác nhận là NEED_FRIEND_REQUEST, hàm gửi lời mời (check_and_add_friend()) chưa được gọi, hoặc được gọi nhưng không thực hiện đúng, hoặc bị luồng hội thoại tự động override.

Đề xuất giải pháp

Dưới đây là các bước sửa + kiểm tra để đảm bảo NEED_FRIEND_REQUEST dẫn tới flow add friend trước khi bắt đầu hội thoại:

# Fix Friend Flow for NEED_FRIEND_REQUEST

## 1. Kiểm tra hàm xác định trạng thái friend

- Trong `ui_friend_status_fix.py`, xác nhận rằng khi resource-id / text phát hiện `btn_send_friend_request`, hàm trả về đúng `NEED_FRIEND_REQUEST`.
- Thêm log rõ ràng khi status này được phát hiện (nếu chưa có):
  ```python
  logger.debug(f"[STATUS] Detected NEED_FRIEND_REQUEST for device {device_id}")

2. Gắn flow xử lý NEED_FRIEND_REQUEST

Trong core1.py (hoặc nơi flow chính được điều phối), tìm phần:

status = ui_friend_status_fix.check_status(...)
if status == ALREADY_FRIEND:
    start_conversation(...)
else:
    start_conversation(...)  # <- sai nếu bao gồm NEED_FRIEND_REQUEST


Thay bằng cấu trúc phân nhánh rõ ràng:

if status == ALREADY_FRIEND:
    start_conversation(...)
elif status == NEED_FRIEND_REQUEST:
    check_and_add_friend(...)
    # có thể đợi một khoảng nếu cần xác nhận UI thay đổi / nút biến mất
    start_conversation(...)
else:
    # UNKNOWN hoặc Limited Profile
    handle_unknown_status(...)

3. Cập nhật hàm check_and_add_friend(...)

Đảm bảo hàm này thực hiện các bước:

Click btn_send_friend_request

Kiểm tra có màn hình xác nhận hay popup hay không

Chờ state UI thay đổi — nút btn_send_friend_request bị ẩn hoặc thay đổi thành “đã gửi” hoặc thành “chatinput_text” tùy UI của Zalo

Nếu có lỗi, log rõ

Thêm log trước và sau mỗi bước để xác minh là đã thực thi:

logger.debug("Clicking send friend request button")
...
logger.debug("Friend request sent or button disappeared / state changed")

4. Sửa test để cover flow add friend

Hiện tại test chỉ kiểm tra logic phân loại trạng thái UI dump. Cần thêm test giả lập UI dump có btn_send_friend_request và test rằng sau khi status đó, hàm check_and_add_friend được gọi / mock được gọi / nút được click.

Có thể dùng mocking để đảm bảo check_and_add_friend được trigger khi status NEED_FRIEND_REQUEST.

5. Xử lý fallback & sync với flow hội thoại

Đảm bảo rằng flow hội thoại (start_conversation) chỉ được gọi sau khi add friend thành công hoặc khi status là ALREADY_FRIEND.

Nếu chưa add friend, start_conversation không nên được gọi — hoặc gọi với một thông báo lỗi / delay để chờ add friend.

6. Kiểm thử thực tế (manual / automation)

Kiểm thử trên thiết bị thật, giả lập profile chưa kết bạn để xem hệ thống có gửi lời mời kết bạn hay không, sau đó mới bắt đầu gửi tin nhắn.

Kiểm thử độ trễ / trường hợp UI không tải nhanh, để tránh race condition (chạy flow hội thoại trước khi add friend hoàn tất).

Gợi ý structure file sửa

Bạn có thể tạo file tên là FRIEND_FLOW_FIX_NEW.md với các nội dung sau:

# FRIEND_FLOW_FIX_NEW

## Mục đích
Đảm bảo khi phát hiện trạng thái `NEED_FRIEND_REQUEST`, hệ thống chuyển sang flow gửi lời mời kết bạn trước khi bắt đầu hội thoại.

## Các thay đổi cần thực hiện
- Thêm phân nhánh `elif status == NEED_FRIEND_REQUEST` trong core flow
- Cập nhật `check_and_add_friend` để thực sự thao tác UI gửi request
- Thêm log rõ ràng cho bước gửi lời mời
- Cập nhật test để kiểm tra nút gửi lời mời được nhấn khi status phù hợp
- Chặn flow hội thoại nếu chưa kết bạn

## Kiểm thử
1. UI dump có nút `btn_send_friend_request` → test status = NEED_FRIEND_REQUEST  
2. Mở automation với profile chưa kết bạn → hệ thống gửi lời mời  
3. Sau add friend thành công → flow conversation  
4. Nếu không thể add friend (UI lỗi) → log error và skip hoặc retry


Kết luận

Vấn đề là logic xử lý sau khi phát hiện NEED_FRIEND_REQUEST chưa thực thi đúng hoặc bị override.

Bằng cách tách rõ phân nhánh, đảm bảo hàm gửi lời mời thực sự được gọi, và thêm kiểm thử & log rõ ràng, sẽ khắc phục được tình trạng “NEED_FRIEND_REQUEST được phát hiện nhưng vẫn tiếp tục flow hội thoại”.