Prompt chi tiết:

Mục tiêu: Viết thêm một luồng phụ (sub-flow) để:

Kiểm tra xem đã kết bạn chưa sau khi vào trang profile từ kết quả tìm kiếm.

Nếu chưa kết bạn → gửi lời mời kết bạn (case 1).

Nếu bên kia đã gửi lời mời → hiện popup xác nhận kết bạn (case 2).

Sau khi kết bạn xong → quay lại flow chính, tiếp tục như bình thường.

Logic chi tiết
def check_and_add_friend(dev):
    """
    Flow phụ: kiểm tra kết bạn và xử lý gửi / chấp nhận lời mời.
    """
    RID_ADD_FRIEND = "com.zing.zalo:id/btn_send_friend_request"  # nút "Kết bạn"
    RID_CONFIRM_POPUP = "com.zing.zalo:id/button1"               # nút popup "ACCEPT"
    RID_ACCEPT = "com.zing.zalo:id/btnAccept"                     # nút "Đồng ý"
    RID_FUNCTION = "com.zing.zalo:id/btn_function"                # nút chức năng cuối
    RID_SEND_INVITE = "com.zing.zalo:id/btnSendInvitation"        # nút "Gửi lời mời"
    RID_SEND_MSG = "com.zing.zalo:id/btn_send_message"            # nút "Nhắn tin"

    # Kiểm tra có nút kết bạn không
    if dev.element_exists(resourceId=RID_ADD_FRIEND):
        print("[DEBUG] Có nút Kết bạn → kiểm tra flow")
        dev.click_by_resource_id(RID_ADD_FRIEND, timeout=5)  # Ấn vào nút "Kết bạn"
        time.sleep(3)  # đợi popup hoặc màn hình load

        # --- CASE 2: Popup confirm hiện ra ---
        if dev.element_exists(resourceId=RID_CONFIRM_POPUP):
            print("[DEBUG] Popup confirm hiện → xác nhận kết bạn")
            dev.click_by_resource_id(RID_CONFIRM_POPUP, timeout=5)
            time.sleep(1)
            dev.click_by_resource_id(RID_ACCEPT, timeout=5)
            time.sleep(1)
            dev.click_by_resource_id(RID_FUNCTION, timeout=5)
            print("[DEBUG] Đã hoàn tất chấp nhận kết bạn (case 2)")

        # --- CASE 1: Không có popup → gửi lời mời bình thường ---
        elif dev.element_exists(resourceId=RID_SEND_INVITE):
            print("[DEBUG] Gửi lời mời kết bạn (case 1)")
            dev.click_by_resource_id(RID_SEND_INVITE, timeout=5)
            time.sleep(2)
            # Sau khi gửi xong, quay lại màn hình chính → bấm nút "Nhắn tin"
            if dev.element_exists(resourceId=RID_SEND_MSG):
                dev.click_by_resource_id(RID_SEND_MSG, timeout=5)
                print("[DEBUG] Nhấn 'Nhắn tin' để quay lại flow chính")

    else:
        print("[DEBUG] Không có nút Kết bạn → tiếp tục flow chính")

Cách tích hợp vào flow chính

Trong flow hiện tại, sau bước:

dev.click_by_resource_id("com.zing.zalo:id/btn_search_result", timeout=5)


Bạn thêm đoạn này ngay sau đó:

# Sau khi vào profile từ kết quả tìm kiếm → kiểm tra kết bạn
check_and_add_friend(dev)

Tóm tắt hoạt động

Nếu chưa kết bạn:

Hiện nút btn_send_friend_request.

Bấm → hiện nút btnSendInvitation → gửi lời mời → quay về flow chính bằng btn_send_message.

Nếu bên kia đã gửi lời mời:

Bấm vào btn_send_friend_request → hiện popup có button1.

Bấm button1 → btnAccept → btn_function → quay về flow chính.

Nếu đã là bạn bè:

Không có nút btn_send_friend_request → bỏ qua sub-flow này.

Lưu ý

Dùng time.sleep(2-3s) để đảm bảo màn hình kịp load popup hoặc button.

Toàn bộ sub-flow nằm gọn trong hàm check_and_add_friend để dễ bảo trì.

Khi quay lại flow chính, sẽ tiếp tục thao tác như trước đây, không bị gián đoạn.