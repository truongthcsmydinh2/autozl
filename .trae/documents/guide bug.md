AutoZL – Phân Tích Lỗi & Hướng Dẫn Khắc Phục

Dự án: autozl

Tài liệu này mô tả các vấn đề đang gặp phải trong hệ thống, nguyên nhân tiềm ẩn và gợi ý hướng xử lý.

1. Lỗi đồng bộ thời gian mở Zalo giữa các máy
Mô tả:

Trong cùng một nhóm, có máy mở Zalo rất sớm, trong khi máy khác mở rất chậm.

Dẫn đến trạng thái không đồng bộ giữa các máy khi bắt đầu chạy luồng tự động.

Nguyên nhân khả thi:

Thiếu cơ chế đồng bộ thời gian giữa các máy trong cùng nhóm.

File core/flow_manager.py và core1.py chưa sử dụng lock hoặc barrier trước khi gọi luồng khởi tạo Zalo.

Network delay hoặc thời gian ADB phản hồi khác nhau giữa các máy.

Chưa có trạng thái chờ (wait_until_all_ready) trước khi chuyển sang bước tiếp theo.

Hướng khắc phục:

Sử dụng thread barrier hoặc asyncio gather để đồng bộ:

# Ví dụ đơn giản trong Python
from threading import Barrier

start_barrier = Barrier(total_devices)  # total_devices = số lượng máy trong nhóm

def open_zalo(device):
    print(f"[{device}] Đang chuẩn bị mở Zalo...")
    start_barrier.wait()  # Chờ tất cả máy sẵn sàng
    print(f"[{device}] Mở Zalo đồng thời!")



Trong code của bạn, thêm một step đồng bộ trước khi gọi ADB mở Zalo.

Log để kiểm tra thời gian từng máy bắt đầu:

logger.info(f"[{device_name}] Start time: {datetime.now()}")

2. CLI vẫn chạy nhưng GUI báo hoàn thành sớm
Mô tả:

Trên CLI terminal / cmd, tiến trình vẫn chạy bình thường.

Trong GUI, phần status báo "đã hoàn thành", dù thực tế CLI chưa kết thúc.

Bảng chia tin nhắn tự động không hiển thị trạng thái từng máy.

Nguyên nhân khả thi:

GUI không liên kết đúng với thread hoặc process đang chạy trong CLI.

Hàm update GUI (ui/device_management.py hoặc ui/execution_control.py) chỉ kiểm tra trạng thái ban đầu mà không subscribe sự kiện real-time.

Thread chính có thể kết thúc sớm hơn các worker thread, dẫn đến GUI hiểu là "xong".

Hướng khắc phục:

Đồng bộ dữ liệu CLI ↔ GUI bằng multiprocessing Manager hoặc WebSocket.

Đảm bảo GUI đọc trạng thái từ source thực tế, ví dụ một shared status.json:

{
  "group_1": {
    "device_a52sxqxx": "running",
    "device_ginkgo": "waiting",
    "device_bluejay": "done"
  }
}


Trong GUI, cập nhật real-time bằng QTimer hoặc thread-safe signal:

from PyQt6.QtCore import QTimer

def update_status_table():
    data = load_status_from_file("status.json")
    refresh_gui_table(data)

timer = QTimer()
timer.timeout.connect(update_status_table)
timer.start(2000)  # refresh mỗi 2 giây

3. Lỗi UiObjectNotFoundException khi gửi tin nhắn
Log lỗi:
[DEBUG] ❌ Error sending message: (-32001, 'androidx.test.uiautomator.UiObjectNotFoundException', ({'mask': 16, 'childOrSibling': [], 'childOrSiblingSelector': [], 'className': 'android.widget.EditText'}, 'Chuẩn, toàn nhắn t'))
❌ Nhóm 1 - Không thể gửi message_id 12: Chuẩn, toàn nhắn tin thôi chán ghê
✅ Nhóm 1 - Hoàn thành cuộc hội thoại
🧹 Nhóm 1 - Đã cleanup sync file

Nguyên nhân khả thi:

Không tìm thấy element EditText trên màn hình Zalo:

Zalo update giao diện → UI selector không còn khớp.

ADB đang thao tác sai context, ví dụ chưa focus đúng khung chat.

Cửa sổ chat chưa load xong nhưng script đã gửi lệnh.

Kiểm tra và xác nhận:

Chạy thủ công lệnh:

adb shell uiautomator dump
adb pull /sdcard/window_dump.xml


Mở file window_dump.xml để xem cây UI, kiểm tra xem có android.widget.EditText hay không.

Giải pháp:

Thêm bước chờ trước khi gửi tin nhắn:

from adbutils import adb
import time

def wait_for_edit_text(device, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        xml = device.dump_hierarchy()
        if "android.widget.EditText" in xml:
            return True
        time.sleep(0.5)
    raise Exception("Không tìm thấy EditText trong giới hạn thời gian!")


Cập nhật selector trong core1.py:

selector = {
    "className": "android.widget.EditText",
    "clickable": True
}


Đảm bảo cleanup file sync chỉ chạy sau khi confirm message đã gửi thành công.

Checklist kiểm tra nhanh
Hạng mục	Đã kiểm tra?
Đồng bộ thời gian giữa các máy (Barrier hoặc asyncio.gather)	⬜
GUI đọc trạng thái từ file / queue real-time	⬜
Kiểm tra uiautomator dump và cập nhật selector mới	⬜
Thêm bước chờ trước khi gửi message	⬜
Log đầy đủ trạng thái từng thiết bị	⬜
Kết luận

Các vấn đề chính liên quan đến:

Thiếu đồng bộ giữa các thiết bị trong nhóm.

Mất kết nối CLI ↔ GUI khiến trạng thái hiển thị sai.

Thay đổi UI Zalo dẫn đến UiObjectNotFoundException.

Khắc phục theo các bước trên sẽ giúp hệ thống chạy ổn định, dễ kiểm soát và debug hơn.
4. Giải pháp khắc phục
4.1. Thêm kiểm tra trạng thái trước khi gửi

Thay vì gửi tin nhắn ngay, hãy đảm bảo chắc chắn UI ở đúng trạng thái chat:

def ensure_chat_ready(device, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        xml = device.dump_hierarchy()
        if "android.widget.EditText" in xml:
            return True
        time.sleep(0.3)
    raise Exception("Không tìm thấy khung chat, UI không đúng trạng thái!")

4.2. Chống chạy quá nhanh giữa các tin nhắn

Nếu mạng hoặc UI bị lag, script có thể chạy nhanh hơn tốc độ load UI.

# Sau khi gửi tin nhắn xong, delay ngắn để Zalo ổn định
time.sleep(random.uniform(0.8, 1.5))

4.3. Bắt UI bất thường

Khi xảy ra lỗi, log thêm ảnh màn hình hoặc UI dump để dễ debug:

def capture_error_state(device, group_id, message_id):
    timestamp = int(time.time())
    device.screenshot(f"error_{group_id}_{message_id}_{timestamp}.png")
    device.shell("uiautomator dump /sdcard/error_dump.xml")
    device.pull("/sdcard/error_dump.xml", f"error_{group_id}_{message_id}.xml")
