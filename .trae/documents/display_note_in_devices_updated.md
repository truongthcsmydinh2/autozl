
# Hướng Dẫn Hiển Thị Cột Note Trong Phần Chọn Devices Ở Tab Nuôi Zalo

## 1. Mục Tiêu
- Trong tab **Phone Manage**, hiện tại có một cột **Note** để lưu thông tin ghi chú cho từng thiết bị.
- Khi sang tab **Nuôi Zalo**, danh sách thiết bị đang chỉ hiển thị theo dạng:
  ```
  192.168.4.156:5555 (928903551)
  ```
- Yêu cầu mới: **hiển thị cả phần Note với tiền tố "Máy:"**, ví dụ:
  ```
  192.168.4.156:5555 (928903551 - Máy: 33)
  ```

Điều này sẽ giúp người dùng dễ dàng nhận diện từng máy cùng với ghi chú đi kèm.

---

## 2. Kiến Trúc Dữ Liệu
- Hiện tại danh sách Devices đang lấy từ **API hoặc database** với các trường:
  ```json
  {
      "ip": "192.168.4.156:5555",
      "phone_number": "928903551",
      "note": "33"
  }
  ```
- Cần đảm bảo API trả về đầy đủ trường `note`.

---

## 3. Cập Nhật Backend
- Nếu backend hiện chưa trả về trường `note`, cần cập nhật code trả về đầy đủ dữ liệu:
  ```python
  return jsonify({
      "devices": [
          {"ip": "192.168.4.156:5555", "phone_number": "928903551", "note": "33"},
          {"ip": "192.168.5.74:5555", "phone_number": "569924311", "note": "4"}
      ]
  })
  ```

---

## 4. Cập Nhật Frontend (Nuôi Zalo Tab)
### 4.1. Vị trí code cần chỉnh
- Trong file render danh sách devices của tab **Nuôi Zalo**, hiện tại label đang được build như sau:
  ```javascript
  label = `${device.ip} (${device.phone_number})`
  ```

### 4.2. Thêm Note vào label với tiền tố "Máy:"
- Sửa lại thành:
  ```javascript
  label = `${device.ip} (${device.phone_number} - Máy: ${device.note || "Không có"})`
  ```

Kết quả:
```
192.168.4.156:5555 (928903551 - Máy: 33)
192.168.5.74:5555 (569924311 - Máy: 4)
```

---

## 5. Kiểm Tra UI
- Sau khi sửa, trong giao diện **Nuôi Zalo**, phần danh sách devices sẽ hiển thị như ảnh minh họa:
  - **Trước khi chỉnh sửa:**
    ```
    192.168.4.156:5555 (928903551)
    ```
  - **Sau khi chỉnh sửa:**
    ```
    192.168.4.156:5555 (928903551 - Máy: 33)
    ```

---

## 6. Lợi Ích
- Giúp người vận hành phân biệt nhanh các thiết bị dựa trên **Note** mà không phải quay lại tab Phone Manage.
- Đảm bảo luồng thao tác liền mạch và giảm nhầm lẫn.

---

## 7. Tổng Kết
| Thành phần | Việc cần làm |
|------------|--------------|
| **Backend** | Cập nhật API trả về trường `note`. |
| **Frontend - Label** | Ghép thêm `note` vào label thiết bị với định dạng: **(phone_number - Máy: note)**. |
| **Kiểm tra** | Đảm bảo danh sách hiển thị đúng cả **IP**, **Số điện thoại**, **Máy**. |

Kết quả cuối cùng sẽ giúp hiển thị rõ ràng thông tin thiết bị như yêu cầu.
