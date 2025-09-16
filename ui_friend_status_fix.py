import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

DUMP_DIR = Path("debug_dumps")

# Các khóa nhận diện trong resource-id/text
RID_CHAT_INPUT_KEY = "chatinput_text"            # Đã là bạn
RID_ADD_FRIEND_KEY = "btn_send_friend_request"   # Chưa là bạn
LIMITED_TEXT_KEYS = [
    "Bạn chưa thể xem nhật ký",                   # Tiếng Việt
    "You can't view",                             # Tiếng Anh
]

def _to_pattern(device_serial: str) -> str:
    if ":" in device_serial:
        ip, port = device_serial.split(":", 1)
        return f"ui_dump_{ip.replace('.', '_')}_{port}_*.xml"
    else:
        return f"ui_dump_{device_serial.replace('.', '_')}_*.xml"

def _latest_dump_file(device_serial: str) -> Optional[Path]:
    """Tìm file UI dump mới nhất cho thiết bị."""
    pattern = _to_pattern(device_serial)
    candidates = sorted(DUMP_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None

def _parse_xml(path: Path):
    try:
        tree = ET.parse(path)
        return tree.getroot()
    except Exception as e:
        print(f"[ERROR] Không parse được XML: {path} -> {e}")
        return None

def _has_resource_id(root, resource_id: str) -> bool:
    """Kiểm tra XML tree có resource-id cụ thể - sử dụng 'in' comparison."""
    if root is None:
        return False
    for node in root.iter("node"):
        element_resource_id = node.attrib.get('resource-id', '')
        if resource_id in element_resource_id:
            bounds = node.attrib.get('bounds', '')
            print(f"[DEBUG] ✅ Found resource-id contains '{resource_id}' at {bounds}")
            return True
    return False

def _has_text_contains(root, keywords) -> bool:
    if root is None:
        return False
    if isinstance(keywords, str):
        keywords = [keywords]
    for node in root.iter("node"):
        text = (node.attrib.get("text") or "").strip()
        if not text:
            continue
        for kw in keywords:
            if kw in text:
                print(f"[DEBUG] ✅ Found text contains '{kw}' -> '{text}'")
                return True
    return False

def check_friend_status_from_dump(device_serial: str, wait_for_dump_sec: float = 1.5) -> str:
    """
    Trả về:
      - 'ALREADY_FRIEND'
      - 'NEED_FRIEND_REQUEST' 
      - 'UNKNOWN' (khi không thể xác định được)
    """
    # Validation device_serial
    if not device_serial or not isinstance(device_serial, str):
        print(f"[ERROR] Invalid device_serial: {device_serial}")
        return "UNKNOWN"
    
    print(f"[DEBUG] 🔍 Checking friend status for device: {device_serial}")
    
    # 1) Lấy file UI dump mới nhất
    try:
        dump_path = _latest_dump_file(device_serial)
    except Exception as e:
        print(f"[ERROR] Lỗi khi tìm dump file cho {device_serial}: {e}")
        return "UNKNOWN"

    # 2) Nếu chưa có file, chờ ngắn rồi tìm lại
    if not dump_path:
        time.sleep(wait_for_dump_sec)
        dump_path = _latest_dump_file(device_serial)

    if not dump_path or not dump_path.exists() or dump_path.stat().st_size < 60:
        print(f"[DEBUG] ❗ Chưa có UI dump phù hợp cho {device_serial} -> fallback UNKNOWN")
        return "UNKNOWN"

    print(f"[DEBUG] 🔎 Phân tích UI dump: {dump_path.name}")

    # 3) Parse và phân tích
    try:
        root = _parse_xml(dump_path)
        if root is None:
            print(f"[ERROR] ❌ Không thể parse XML dump: {dump_path}")
            return "UNKNOWN"
    except Exception as e:
        print(f"[ERROR] ❌ Lỗi khi parse XML dump {dump_path}: {e}")
        return "UNKNOWN"

    # Đã là bạn
    if _has_resource_id(root, RID_CHAT_INPUT_KEY):
        return "ALREADY_FRIEND"

    # Chưa là bạn
    if _has_resource_id(root, RID_ADD_FRIEND_KEY):
        return "NEED_FRIEND_REQUEST"

    # Hồ sơ bị giới hạn (không có nút kết bạn)
    if _has_text_contains(root, LIMITED_TEXT_KEYS):
        return "NEED_FRIEND_REQUEST"

    # Smart fallback: trả về UNKNOWN để debug
    print("[DEBUG] ⚠️ Không match resource-id/text nào -> Fallback UNKNOWN")
    return "UNKNOWN"