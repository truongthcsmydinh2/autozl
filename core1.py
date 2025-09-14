# -*- coding: utf-8 -*-
# Single-file automation với uiautomator2: modern Android automation
# Usage:
#   pip install uiautomator2
#   set DEVICE=R58M123ABC & python core_uiautomator2.py
#   (hoặc) set DEVICE=192.168.5.151:5555 & python core_uiautomator2.py
# Sửa vùng "=== FLOW START/END ===" bên dưới rồi Ctrl+S -> tool tự chạy lại flow trên máy test.

import os, sys, time, subprocess, threading, re, traceback, argparse, json
import uiautomator2 as u2

ENC = "utf-8"
SELF_PATH = os.path.abspath(__file__)
DEVICE = os.environ.get("DEVICE", "192.168.5.74:5555")   # IP:port để test
DEVICES = os.environ.get("DEVICES", "192.168.5.74:5555, 192.168.5.82:5555")  # Danh sách devices cách nhau bởi dấu phẩy
PHONE_CONFIG_FILE = "phone_mapping.json"  # File lưu mapping IP -> số điện thoại

# ---------------- UIAutomator2 Device Wrapper ----------------
class Device:
    """Modern Device API sử dụng uiautomator2"""
    
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.d = None
        self.screen_info = None
        
    def connect(self):
        """Kết nối tới device qua uiautomator2"""
        try:
            # Kết nối device
            if ":" in self.device_id:
                # Network device
                self.d = u2.connect(self.device_id)
            else:
                # USB device
                self.d = u2.connect_usb(self.device_id)
            
            # Lấy thông tin device
            info = self.d.info
            self.screen_info = {
                'width': info['displayWidth'],
                'height': info['displayHeight'],
                'density': info.get('displaySizeDpX', 411)
            }
            
            print(f"📱 Connected: {info['productName']} ({self.screen_info['width']}x{self.screen_info['height']})")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi kết nối device {self.device_id}: {e}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.d:
            try:
                # UIAutomator2 tự động cleanup
                pass
            except:
                pass
    
    # ---------------- Basic Actions ----------------
    def tap(self, x: int, y: int):
        """Tap tại tọa độ x, y"""
        try:
            self.d.click(x, y)
            return f"[OK] Tapped ({x}, {y})"
        except Exception as e:
            return f"[ERR] Tap failed: {e}"
    
    def swipe(self, x1, y1, x2, y2, duration=0.3):
        """Swipe từ (x1,y1) đến (x2,y2)"""
        try:
            self.d.swipe(x1, y1, x2, y2, duration)
            return f"[OK] Swiped ({x1},{y1}) -> ({x2},{y2})"
        except Exception as e:
            return f"[ERR] Swipe failed: {e}"
    
    def text(self, text: str):
        """Nhập text"""
        try:
            self.d.send_keys(text)
            return f"[OK] Text input: {text}"
        except Exception as e:
            return f"[ERR] Text input failed: {e}"
    
    def key(self, keycode: int):
        """Nhấn phím theo keycode"""
        try:
            # Map common keycodes
            key_map = {
                3: "home",
                4: "back", 
                66: "enter",
                84: "search",
                187: "recent"
            }
            
            if keycode in key_map:
                getattr(self.d, key_map[keycode])()
            else:
                self.d.press(keycode)
            return f"[OK] Key pressed: {keycode}"
        except Exception as e:
            return f"[ERR] Key press failed: {e}"
    
    def home(self):
        """Về home screen"""
        return self.d.press("home")
    
    def back(self):
        """Nhấn back"""
        return self.d.press("back")
    
    def recents(self):
        """Mở recent apps"""
        return self.d.press("recent")
    
    def app(self, pkg: str):
        """Mở app theo package name"""
        try:
            self.d.app_start(pkg)
            time.sleep(2)  # Đợi app load
            return f"[OK] Started app: {pkg}"
        except Exception as e:
            return f"[ERR] App start failed: {e}"
    
    def screencap(self, out_path="screen.png"):
        """Chụp screenshot"""
        try:
            self.d.screenshot(out_path)
            return f"[OK] Screenshot saved: {out_path}"
        except Exception as e:
            return f"[ERR] Screenshot failed: {e}"
    
    # ---------------- Modern UI Automation ----------------
    def dump_ui(self):
        """Dump UI hierarchy (for compatibility)"""
        try:
            # UIAutomator2 có thể dump XML
            xml = self.d.dump_hierarchy()
            return xml
        except Exception as e:
            return f"[ERR] UI dump failed: {e}"
    
    def click_by_text(self, text: str, timeout=10, debug=False):
        """Click element bằng text - Modern UIAutomator2 way"""
        try:
            if debug:
                print(f"[DEBUG] Searching for text: {text}")
            
            # Sử dụng UIAutomator2 selector
            element = self.d(text=text)
            
            if element.wait(timeout=timeout):
                element.click()
                if debug:
                    print(f"[DEBUG] ✅ Clicked text: {text}")
                return True
            else:
                if debug:
                    print(f"[DEBUG] ❌ Text not found: {text}")
                return False
                
        except Exception as e:
            if debug:
                print(f"[DEBUG] ❌ Error clicking text: {e}")
            return False
    
    def click_by_resource_id(self, resource_id: str, timeout=10, debug=False):
        """Click element bằng resource-id - Modern UIAutomator2 way"""
        try:
            if debug:
                print(f"[DEBUG] Searching for resource-id: {resource_id}")
            
            # Sử dụng UIAutomator2 selector
            element = self.d(resourceId=resource_id)
            
            if element.wait(timeout=timeout):
                element.click()
                if debug:
                    print(f"[DEBUG] ✅ Clicked resource-id: {resource_id}")
                return True
            else:
                if debug:
                    print(f"[DEBUG] ❌ Resource-id not found: {resource_id}")
                return False
                
        except Exception as e:
            if debug:
                print(f"[DEBUG] ❌ Error clicking resource-id: {e}")
            return False
    
    def click_by_xpath(self, xpath: str, timeout=10, debug=False):
        """Click element bằng XPath - UIAutomator2 way"""
        try:
            if debug:
                print(f"[DEBUG] Searching for xpath: {xpath}")
            
            # UIAutomator2 hỗ trợ XPath
            element = self.d.xpath(xpath)
            
            if element.wait(timeout=timeout):
                element.click()
                if debug:
                    print(f"[DEBUG] ✅ Clicked xpath: {xpath}")
                return True
            else:
                if debug:
                    print(f"[DEBUG] ❌ XPath not found: {xpath}")
                return False
                
        except Exception as e:
            if debug:
                print(f"[DEBUG] ❌ Error clicking xpath: {e}")
            return False
    
    def click_by_description(self, desc: str, timeout=10, debug=False):
        """Click element bằng content description"""
        try:
            if debug:
                print(f"[DEBUG] Searching for description: {desc}")
            
            element = self.d(description=desc)
            
            if element.wait(timeout=timeout):
                element.click()
                if debug:
                    print(f"[DEBUG] ✅ Clicked description: {desc}")
                return True
            else:
                if debug:
                    print(f"[DEBUG] ❌ Description not found: {desc}")
                return False
                
        except Exception as e:
            if debug:
                print(f"[DEBUG] ❌ Error clicking description: {e}")
            return False
    
    def wait_for_element(self, **kwargs):
        """Đợi element xuất hiện"""
        try:
            return self.d(**kwargs).wait(timeout=10)
        except:
            return False
    
    def element_exists(self, **kwargs):
        """Kiểm tra element có tồn tại không"""
        try:
            return self.d(**kwargs).exists
        except:
            return False
    
    def get_element_info(self, **kwargs):
        """Lấy thông tin element"""
        try:
            element = self.d(**kwargs)
            if element.exists:
                return element.info
            return None
        except:
            return None
    
    def set_text(self, text: str, **kwargs):
        """Set text vào input field"""
        try:
            element = self.d(**kwargs)
            if element.wait(timeout=5):
                element.set_text(text)
                return True
            return False
        except:
            return False
    
    def clear_text(self, **kwargs):
        """Clear text trong input field"""
        try:
            element = self.d(**kwargs)
            if element.wait(timeout=5):
                element.clear_text()
                return True
            return False
        except:
            return False
    
    def scroll_to(self, **kwargs):
        """Scroll đến element"""
        try:
            return self.d(**kwargs).scroll.to()
        except:
            return False
    
    def long_click(self, **kwargs):
        """Long click element"""
        try:
            element = self.d(**kwargs)
            if element.wait(timeout=5):
                element.long_click()
                return True
            return False
        except:
            return False
    
    # ---------------- Adaptive Coordinates Support ----------------
    def get_adaptive_coordinates(self, base_x, base_y, base_width=1080, base_height=2220):
        """Convert coordinates từ base resolution sang current resolution"""
        if not self.screen_info:
            return base_x, base_y
            
        scale_x = self.screen_info['width'] / base_width
        scale_y = self.screen_info['height'] / base_height
        
        new_x = int(base_x * scale_x)
        new_y = int(base_y * scale_y)
        
        return new_x, new_y
    
    def tap_adaptive(self, base_x, base_y, base_width=1080, base_height=2220):
        """Tap với adaptive coordinates"""
        x, y = self.get_adaptive_coordinates(base_x, base_y, base_width, base_height)
        return self.tap(x, y)

# ---------------- Device Management Functions ----------------
def get_all_connected_devices():
    """Lấy danh sách tất cả devices kết nối với ADB"""
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
        devices_output = result.stdout
        
        # Parse danh sách devices
        lines = devices_output.strip().split('\n')[1:]  # Bỏ dòng header
        available_devices = []
        for line in lines:
            if line.strip() and '\t' in line:
                device_id = line.split('\t')[0]
                status = line.split('\t')[1]
                if status == 'device':  # Chỉ lấy devices đã sẵn sàng
                    available_devices.append(device_id)
        
        return available_devices
    except Exception as e:
        print(f"❌ Lỗi kiểm tra ADB devices: {e}")
        return []

def select_devices_interactive(available_devices):
    """Tạo menu chọn devices tương tác"""
    if not available_devices:
        return []
    
    if len(available_devices) == 1:
        print(f"✅ Chỉ có 1 device: {available_devices[0]}")
        return available_devices
    
    print("\n📱 Phát hiện nhiều devices:")
    for i, device in enumerate(available_devices, 1):
        print(f"  {i}. {device}")
    print(f"  {len(available_devices) + 1}. Tất cả devices")
    print("  0. Thoát")
    
    while True:
        try:
            choice = input("\n🔢 Chọn device (số): ").strip()
            if choice == '0':
                return []
            elif choice == str(len(available_devices) + 1):
                print(f"✅ Chọn tất cả {len(available_devices)} devices")
                return available_devices
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(available_devices):
                    selected = available_devices[idx]
                    print(f"✅ Chọn device: {selected}")
                    return [selected]
            print("❌ Lựa chọn không hợp lệ, vui lòng thử lại.")
        except KeyboardInterrupt:
            print("\n❌ Đã hủy.")
            return []
        except Exception:
            print("❌ Lỗi nhập liệu, vui lòng thử lại.")

def parse_devices_from_env():
    """Parse danh sách devices từ biến môi trường DEVICES"""
    if not DEVICES:
        return []
    
    devices = [d.strip() for d in DEVICES.split(',') if d.strip()]
    print(f"📋 Sử dụng devices từ biến môi trường: {devices}")
    return devices

# ---------------- Hot-reload FLOW: đọc chính file này, exec vùng flow ----------------
FLOW_PATTERN = re.compile(r"#\s*===\s*FLOW START\s*===\s*(.*?)#\s*===\s*FLOW END\s*===", re.S)

def load_flow_from_self():
    with open(SELF_PATH, "r", encoding="utf-8") as f:
        src = f.read()
    m = FLOW_PATTERN.search(src)
    if not m:
        raise RuntimeError("Không tìm thấy vùng FLOW trong file (markers).")
    code = m.group(1)
    ns = {}
    # Chúng ta cung cấp Device và time trong ns để code flow dùng
    ns.update({"Device": Device, "time": time, "u2": u2})
    exec(code, ns, ns)
    if "flow" not in ns or not callable(ns["flow"]):
        raise RuntimeError("Trong vùng FLOW phải định nghĩa hàm flow(dev).")
    return ns["flow"]

# ---------------- Multi-Device Threading Support ----------------
class DeviceWorker:
    """Worker class để chạy flow trên một device trong thread riêng"""
    
    def __init__(self, device_id: str, device_name: str = None):
        self.device_id = device_id
        self.device_name = device_name or device_id
        self.device = None
        self.stop_event = threading.Event()
        self.thread = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log với prefix device name"""
        prefix = f"[{self.device_name}]"
        if level == "ERROR":
            print(f"\033[91m{prefix} {message}\033[0m")  # Red
        elif level == "SUCCESS":
            print(f"\033[92m{prefix} {message}\033[0m")  # Green
        elif level == "WARNING":
            print(f"\033[93m{prefix} {message}\033[0m")  # Yellow
        else:
            print(f"\033[94m{prefix} {message}\033[0m")  # Blue
    
    def initialize_device(self):
        """Khởi tạo device"""
        try:
            # Đảm bảo device_id có format IP:5555 cho network devices
            device_id = self.device_id
            if ':' not in device_id and '.' in device_id:  # IP address without port
                device_id = f"{device_id}:5555"
            
            self.device = Device(device_id)
            if self.device.connect():
                return True
            else:
                self.log("❌ Không thể kết nối device", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Lỗi khởi tạo device: {e}", "ERROR")
            return False
    
    def run_flow_once(self, flow_fn, all_devices=None):
        """Chạy flow một lần trên device này với group support"""
        try:
            if all_devices:
                result = flow_fn(self.device, all_devices)
            else:
                result = flow_fn(self.device)
            if result == "LOGIN_REQUIRED":
                return False
            elif result == "SUCCESS":
                return True
        except Exception as e:
            self.log(f"❌ Flow crashed: {e}", "ERROR")
            traceback.print_exc()
        return True
    
    def worker_loop(self, all_devices=None):
        """Main loop cho worker thread - chỉ chạy một lần với group support"""
        if not self.initialize_device():
            return
        
        # Chạy flow một lần duy nhất
        try:
            flow_fn = load_flow_from_self()
            result = self.run_flow_once(flow_fn, all_devices)
            if not result:
                # Nếu cần đăng nhập, thoát ngay
                sys.exit(0)
        except Exception as e:
            sys.exit(1)
        
        # Cleanup
        self.cleanup()
    
    def start(self, all_devices=None):
        """Bắt đầu worker thread với group support"""
        self.thread = threading.Thread(target=self.worker_loop, args=(all_devices,), daemon=True)
        self.thread.start()
    
    def stop(self):
        """Dừng worker thread"""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.device:
            self.device.disconnect()

# ---------------- Main Functions ----------------
def run_flow_once(flow_fn, dev: Device, all_devices=None):
    try:
        if all_devices:
            result = flow_fn(dev, all_devices)
        else:
            result = flow_fn(dev)
        # Nếu flow trả về "LOGIN_REQUIRED", thoát tool ngay lập tức
        if result == "LOGIN_REQUIRED":
            print("\n🛑 Tool thoát. Vui lòng đăng nhập Zalo và chạy lại tool.")
            sys.exit(0)  # Thoát tool hoàn toàn
    except Exception:
        print("[ERR] Flow crashed:")
        traceback.print_exc()

def main_single_device(device_id, all_devices=None):
    """Single device mode - chỉ chạy một lần với group support"""
    # Đảm bảo device_id có format IP:5555 cho network devices
    if ':' not in device_id and '.' in device_id:  # IP address without port
        device_id = f"{device_id}:5555"
    
    device = Device(device_id)
    
    if not device.connect():
        print(f"❌ Không thể kết nối device: {device_id}")
        sys.exit(1)
    
    # Chạy flow một lần duy nhất
    try:
        flow_fn = load_flow_from_self()
        run_flow_once(flow_fn, device, all_devices)
    except Exception:
        print("[ERR] Flow failed")
        sys.exit(1)
    finally:
        device.disconnect()

def main_multi_device(selected_devices):
    """Multi-device mode - chạy group-based conversation trên tất cả devices"""
    workers = []
    
    # Extract IPs từ device IDs để tạo all_devices list
    all_device_ips = []
    for device_id in selected_devices:
        ip = device_id.split(":")[0] if ":" in device_id else device_id
        all_device_ips.append(ip)
    
    print(f"🔗 Group-based execution với {len(selected_devices)} devices")
    print(f"📋 Device IPs: {all_device_ips}")
    
    # Tạo workers cho từng device
    for i, device_id in enumerate(selected_devices):
        device_name = f"Device-{i+1}({device_id})"
        worker = DeviceWorker(device_id, device_name)
        workers.append(worker)
    
    # Khởi động tất cả workers với all_devices parameter
    for worker in workers:
        worker.start(all_device_ips)
        time.sleep(0.5)  # Delay nhỏ giữa các worker
    
    # Chờ tất cả workers hoàn thành
    for worker in workers:
        if worker.thread:
            worker.thread.join()
    
    # Cleanup
    for worker in workers:
        worker.cleanup()

# Default PHONE_MAP - sẽ được override bởi CLI args hoặc config file
DEFAULT_PHONE_MAP = {
    "192.168.5.74": "569924311",
    "192.168.5.82": "583563439",
}

# Global PHONE_MAP sẽ được load từ các nguồn khác nhau
PHONE_MAP = {}

def load_phone_map_from_file():
    """Load phone mapping từ file config"""
    try:
        if os.path.exists(PHONE_CONFIG_FILE):
            with open(PHONE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('phone_mapping', {})
    except Exception as e:
        print(f"⚠️ Lỗi đọc file config: {e}")
    return {}

def save_phone_map_to_file(phone_map):
    """Lưu phone mapping vào file config"""
    try:
        data = {
            'phone_mapping': phone_map,
            'timestamp': time.time(),
            'created_by': 'core1.py CLI'
        }
        with open(PHONE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Đã lưu phone mapping vào {PHONE_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu file config: {e}")
        return False

def parse_device_map_string(device_map_str):
    """Parse device map string từ CLI argument"""
    phone_map = {}
    try:
        # Format: "IP1:phone1,IP2:phone2"
        pairs = device_map_str.split(',')
        for pair in pairs:
            if ':' in pair:
                ip, phone = pair.strip().split(':', 1)
                phone_map[ip.strip()] = phone.strip()
        return phone_map
    except Exception as e:
        print(f"❌ Lỗi parse device map: {e}")
        return {}

def list_devices_and_mapping():
    """Hiển thị danh sách devices và phone mapping"""
    print("\n📱 DANH SÁCH DEVICES VÀ PHONE MAPPING")
    print("=" * 45)
    
    # Lấy devices từ ADB
    available_devices = get_all_connected_devices()
    env_devices = parse_devices_from_env()
    
    print(f"📋 Devices từ ADB ({len(available_devices)}):")
    if available_devices:
        for device in available_devices:
            ip = device.split(':')[0] if ':' in device else device
            phone = PHONE_MAP.get(ip, "chưa có số")
            status = "🟢 có số" if phone != "chưa có số" else "🔴 chưa có số"
            print(f"  {device} -> {phone} {status}")
    else:
        print("  Không có device nào kết nối")
    
    print(f"\n📋 Devices từ biến môi trường ({len(env_devices)}):")
    if env_devices:
        for device in env_devices:
            ip = device.split(':')[0] if ':' in device else device
            phone = PHONE_MAP.get(ip, "chưa có số")
            status = "🟢 có số" if phone != "chưa có số" else "🔴 chưa có số"
            print(f"  {device} -> {phone} {status}")
    else:
        print("  Không có device nào trong biến môi trường")
    
    print(f"\n📞 Phone mapping hiện tại ({len(PHONE_MAP)}):")
    if PHONE_MAP:
        for ip, phone in PHONE_MAP.items():
            print(f"  {ip} -> {phone}")
    else:
        print("  Chưa có phone mapping nào")

def quick_setup_mode():
    """Quick setup mode - tự động detect devices và nhập số điện thoại"""
    print("\n🚀 QUICK SETUP MODE")
    print("=" * 25)
    
    # Lấy devices từ ADB
    available_devices = get_all_connected_devices()
    
    if not available_devices:
        print("❌ Không tìm thấy device nào từ ADB")
        print("💡 Hãy đảm bảo devices đã kết nối và ADB hoạt động")
        return {}
    
    print(f"📱 Phát hiện {len(available_devices)} device(s) từ ADB:")
    
    phone_map = {}
    for i, device in enumerate(available_devices, 1):
        ip = device.split(':')[0] if ':' in device else device
        current_phone = PHONE_MAP.get(ip, "")
        
        print(f"\n📱 Device {i}/{len(available_devices)}: {device}")
        if current_phone:
            print(f"📞 Số hiện tại: {current_phone}")
        
        while True:
            try:
                if current_phone:
                    phone = input(f"📞 Nhập số điện thoại (Enter để giữ '{current_phone}'): ").strip()
                    if not phone:
                        phone = current_phone
                        break
                else:
                    phone = input("📞 Nhập số điện thoại: ").strip()
                
                if phone:
                    if validate_phone_number(phone):
                        phone_map[ip] = phone
                        print(f"  ✅ {ip} -> {phone}")
                        break
                    else:
                        print("  ❌ Số điện thoại không hợp lệ (9-15 chữ số, có thể có +)")
                else:
                    print("  ⚠️ Bỏ qua device này")
                    break
            except KeyboardInterrupt:
                print("\n❌ Đã hủy")
                return {}
    
    if phone_map:
        print(f"\n📋 Phone mapping mới:")
        for ip, phone in phone_map.items():
            print(f"  {ip} -> {phone}")
        
        save_choice = input("\n💾 Lưu vào file config? (Y/n): ").strip().lower()
        if save_choice not in ['n', 'no']:
            save_phone_map_to_file(phone_map)
    
    return phone_map

def interactive_phone_mapping():
    """Interactive mode để nhập phone mapping với cải thiện"""
    print("\n📱 INTERACTIVE PHONE MAPPING MODE")
    print("=" * 40)
    
    # Lấy danh sách devices hiện có
    available_devices = get_all_connected_devices()
    env_devices = parse_devices_from_env()
    
    all_devices = list(set(available_devices + env_devices))
    
    if not all_devices:
        print("❌ Không tìm thấy devices nào")
        print("💡 Hãy đảm bảo devices đã kết nối hoặc thiết lập biến môi trường DEVICES")
        return {}
    
    print(f"📋 Phát hiện {len(all_devices)} devices:")
    for i, device in enumerate(all_devices, 1):
        ip = device.split(':')[0] if ':' in device else device
        current_phone = PHONE_MAP.get(ip, "chưa có")
        status = "🟢" if current_phone != "chưa có" else "🔴"
        print(f"  {i}. {device} -> {current_phone} {status}")
    
    phone_map = {}
    print("\n💡 Nhập số điện thoại cho từng device:")
    print("   - Enter để bỏ qua")
    print("   - Format: IP:PHONE để nhập nhanh")
    print("   - Ctrl+C để thoát")
    
    for device in all_devices:
        ip = device.split(':')[0] if ':' in device else device
        current_phone = PHONE_MAP.get(ip, "")
        
        prompt = f"\n📞 {device}"
        if current_phone:
            prompt += f" (hiện tại: {current_phone})"
        prompt += ": "
        
        try:
            user_input = input(prompt).strip()
            
            if not user_input:
                if current_phone:
                    phone_map[ip] = current_phone
                    print(f"  📋 Giữ nguyên: {ip} -> {current_phone}")
                continue
            
            # Kiểm tra format IP:PHONE
            if ':' in user_input and len(user_input.split(':')) == 2:
                input_ip, input_phone = user_input.split(':', 1)
                if validate_ip_address(input_ip.strip()) and validate_phone_number(input_phone.strip()):
                    phone_map[input_ip.strip()] = input_phone.strip()
                    print(f"  ✅ {input_ip.strip()} -> {input_phone.strip()}")
                    continue
                else:
                    print("  ❌ Format IP:PHONE không hợp lệ")
                    continue
            
            # Kiểm tra chỉ số điện thoại
            if validate_phone_number(user_input):
                phone_map[ip] = user_input
                print(f"  ✅ {ip} -> {user_input}")
            else:
                print("  ❌ Số điện thoại không hợp lệ (9-15 chữ số, có thể có +)")
                
        except KeyboardInterrupt:
            print("\n❌ Đã hủy")
            return {}
    
    if phone_map:
        print(f"\n📋 Phone mapping mới:")
        for ip, phone in phone_map.items():
            print(f"  {ip} -> {phone}")
        
        save_choice = input("\n💾 Lưu vào file config? (Y/n): ").strip().lower()
        if save_choice not in ['n', 'no']:
            save_phone_map_to_file(phone_map)
    
    return phone_map

def validate_phone_number(phone):
    """Validate số điện thoại"""
    import re
    # Cho phép số điện thoại 9-15 chữ số, có thể có dấu + ở đầu
    pattern = r'^\+?[0-9]{9,15}$'
    return bool(re.match(pattern, phone.strip()))

def validate_ip_address(ip):
    """Validate IP address"""
    import re
    # Cho phép IP hoặc IP:port
    ip_part = ip.split(':')[0] if ':' in ip else ip
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip_part))

def interactive_setup_mode():
    """Interactive setup mode - chọn devices, pairing, phone mapping và conversation"""
    print("\n" + "=" * 50)
    print("🚀 ZALO AUTOMATION SETUP")
    print("=" * 50)
    
    # Step 1: Device Selection và Pairing
    device_pairs = select_device_pairs()
    if not device_pairs:
        print("❌ Không có device pairs nào được chọn")
        return None
    
    # Step 2: Phone Mapping
    phone_mapping = setup_phone_mapping_for_pairs(device_pairs)
    if not phone_mapping:
        print("❌ Không có phone mapping nào được cấu hình")
        return None
    
    # Step 3: Conversation Input
    conversations = setup_conversations_for_pairs(device_pairs)
    if not conversations:
        print("❌ Không có conversation nào được nhập")
        return None
    
    # Step 4: Preview và Confirm
    if not preview_and_confirm_setup(device_pairs, phone_mapping, conversations):
        print("❌ Setup bị hủy")
        return None
    
    # Step 5: Save configs
    save_setup_configs(phone_mapping, conversations)
    print("\n✅ Setup hoàn thành! Sẵn sàng chạy automation...")
    return (device_pairs, phone_mapping, conversations)

def select_device_pairs():
    """Chọn devices và tạo cặp"""
    print("\n📱 BƯỚC 1: CHỌN DEVICES VÀ TẠO CẶP")
    print("-" * 35)
    
    # Lấy available devices
    available_devices = get_all_connected_devices()
    if not available_devices:
        print("❌ Không tìm thấy device nào từ ADB")
        print("💡 Hãy đảm bảo devices đã kết nối và ADB hoạt động")
        return []
    
    print(f"📋 Phát hiện {len(available_devices)} device(s):")
    for i, device in enumerate(available_devices, 1):
        print(f"  {i}. {device}")
    
    # Chọn số cặp
    while True:
        try:
            num_pairs = int(input(f"\n🔢 Nhập số cặp muốn tạo (1-{len(available_devices)//2}): "))
            if 1 <= num_pairs <= len(available_devices)//2:
                break
            else:
                print(f"❌ Số cặp phải từ 1 đến {len(available_devices)//2}")
        except (ValueError, KeyboardInterrupt):
            print("❌ Đã hủy hoặc input không hợp lệ")
            return []
    
    # Chọn devices cho từng cặp
    device_pairs = []
    selected_devices = set()
    
    for pair_num in range(1, num_pairs + 1):
        print(f"\n👥 CẶP {pair_num}:")
        
        # Hiển thị devices còn lại
        remaining_devices = [d for d in available_devices if d not in selected_devices]
        if len(remaining_devices) < 2:
            print("❌ Không đủ devices để tạo cặp")
            return []
        
        print("📋 Devices còn lại:")
        for i, device in enumerate(remaining_devices, 1):
            print(f"  {i}. {device}")
        
        # Chọn device 1
        while True:
            try:
                choice1 = int(input(f"🔹 Chọn device 1 cho cặp {pair_num}: ")) - 1
                if 0 <= choice1 < len(remaining_devices):
                    device1 = remaining_devices[choice1]
                    break
                else:
                    print("❌ Lựa chọn không hợp lệ")
            except (ValueError, KeyboardInterrupt):
                print("❌ Đã hủy")
                return []
        
        # Chọn device 2
        remaining_after_first = [d for d in remaining_devices if d != device1]
        print("📋 Devices còn lại sau khi chọn device 1:")
        for i, device in enumerate(remaining_after_first, 1):
            print(f"  {i}. {device}")
        
        while True:
            try:
                choice2 = int(input(f"🔸 Chọn device 2 cho cặp {pair_num}: ")) - 1
                if 0 <= choice2 < len(remaining_after_first):
                    device2 = remaining_after_first[choice2]
                    break
                else:
                    print("❌ Lựa chọn không hợp lệ")
            except (ValueError, KeyboardInterrupt):
                print("❌ Đã hủy")
                return []
        
        # Thêm cặp và mark devices đã chọn
        device_pairs.append((device1, device2))
        selected_devices.add(device1)
        selected_devices.add(device2)
        print(f"  ✅ Cặp {pair_num}: {device1} ↔ {device2}")
    
    # Hiển thị tổng kết
    print(f"\n📋 TỔNG KẾT: {len(device_pairs)} cặp được tạo")
    for i, (dev1, dev2) in enumerate(device_pairs, 1):
        print(f"  👥 Cặp {i}: {dev1} ↔ {dev2}")
    
    confirm = input("\n✅ Xác nhận device pairing? (Y/n): ").strip().lower()
    if confirm in ['n', 'no']:
        return []
    
    return device_pairs

def setup_phone_mapping_for_pairs(device_pairs):
    """Setup phone mapping cho các devices trong pairs"""
    print("\n📞 BƯỚC 2: CẤU HÌNH PHONE MAPPING")
    print("-" * 35)
    
    phone_mapping = {}
    all_devices = []
    for dev1, dev2 in device_pairs:
        all_devices.extend([dev1, dev2])
    
    for i, device in enumerate(all_devices, 1):
        ip = device.split(':')[0] if ':' in device else device
        # Try both formats: with and without port
        current_phone = PHONE_MAP.get(device, "") or PHONE_MAP.get(ip, "")
        
        print(f"\n📱 Device {i}/{len(all_devices)}: {device}")
        if current_phone:
            print(f"📞 Số hiện tại: {current_phone}")
        
        while True:
            try:
                if current_phone:
                    phone = input(f"📞 Nhập số điện thoại (Enter để giữ '{current_phone}'): ").strip()
                    if not phone:
                        phone = current_phone
                        # Lưu số hiện tại vào mapping
                        phone_mapping[device] = phone
                        print(f"  📋 Giữ nguyên: {device} -> {phone}")
                        break
                else:
                    phone = input("📞 Nhập số điện thoại: ").strip()
                
                if phone:
                    if validate_phone_number(phone):
                        phone_mapping[device] = phone
                        print(f"  ✅ {device} -> {phone}")
                        break
                    else:
                        print("  ❌ Số điện thoại không hợp lệ (9-15 chữ số, có thể có +)")
                else:
                    print("  ⚠️ Bỏ qua device này")
                    break
            except KeyboardInterrupt:
                print("\n❌ Đã hủy")
                return {}
    
    print(f"\n📞 PHONE MAPPING HOÀN THÀNH ({len(phone_mapping)} devices):")
    for device, phone in phone_mapping.items():
        print(f"  {device} -> {phone}")
    
    return phone_mapping

def setup_conversations_for_pairs(device_pairs):
    """Setup conversations cho từng pair"""
    print("\n💬 BƯỚC 3: NHẬP CONVERSATION CHO TỪNG NHÓM")
    print("-" * 45)
    
    conversations = {}
    
    for pair_num, (dev1, dev2) in enumerate(device_pairs, 1):
        print(f"\n👥 NHÓM {pair_num}: {dev1} ↔ {dev2}")
        print("📝 Nhập conversation (format: '1: message' hoặc '2: message')")
        print("💡 Tips:")
        print("   - '1:' cho device đầu tiên, '2:' cho device thứ hai")
        print("   - Nhập 'done' để kết thúc")
        print("   - Nhập 'preview' để xem conversation hiện tại")
        print("   - Nhập 'clear' để xóa và bắt đầu lại")
        
        conversation = []
        message_id = 1
        
        while True:
            try:
                line = input(f"📝 Message {message_id}: ").strip()
                
                if line.lower() == 'done':
                    break
                elif line.lower() == 'preview':
                    print("\n📋 CONVERSATION PREVIEW:")
                    for msg in conversation:
                        device_name = dev1 if msg['device_number'] == 1 else dev2
                        print(f"  {msg['message_id']}. {device_name}: {msg['content']}")
                    continue
                elif line.lower() == 'clear':
                    conversation = []
                    message_id = 1
                    print("🗑️ Đã xóa conversation")
                    continue
                elif not line:
                    continue
                
                # Parse message format
                if ':' in line and len(line.split(':', 1)) == 2:
                    device_num_str, message = line.split(':', 1)
                    device_num_str = device_num_str.strip()
                    message = message.strip()
                    
                    if device_num_str in ['1', '2'] and message:
                        device_num = int(device_num_str)
                        conversation.append({
                            'message_id': message_id,
                            'device_number': device_num,
                            'content': message
                        })
                        device_name = dev1 if device_num == 1 else dev2
                        print(f"  ✅ {device_name}: {message}")
                        message_id += 1
                    else:
                        print("❌ Format không đúng. Sử dụng '1: message' hoặc '2: message'")
                else:
                    print("❌ Format không đúng. Sử dụng '1: message' hoặc '2: message'")
                    
            except KeyboardInterrupt:
                print("\n❌ Đã hủy")
                return {}
        
        if conversation:
            conversations[f"pair_{pair_num}"] = {
                'devices': [dev1, dev2],
                'conversation': conversation
            }
            print(f"✅ Nhóm {pair_num}: {len(conversation)} tin nhắn")
        else:
            print(f"⚠️ Nhóm {pair_num}: Không có conversation nào")
    
    return conversations

def preview_and_confirm_setup(device_pairs, phone_mapping, conversations):
    """Preview và confirm toàn bộ setup"""
    print("\n📋 BƯỚC 4: PREVIEW VÀ CONFIRM SETUP")
    print("-" * 35)
    
    # Preview device pairs
    print(f"\n👥 DEVICE PAIRS ({len(device_pairs)} cặp):")
    for i, (dev1, dev2) in enumerate(device_pairs, 1):
        print(f"  {i}. {dev1} ↔ {dev2}")
    
    # Preview phone mapping
    print(f"\n📞 PHONE MAPPING ({len(phone_mapping)} devices):")
    for ip, phone in phone_mapping.items():
        print(f"  {ip} -> {phone}")
    
    # Preview conversations
    print(f"\n💬 CONVERSATIONS ({len(conversations)} nhóm):")
    for pair_key, data in conversations.items():
        pair_num = pair_key.split('_')[1]
        conv_count = len(data['conversation'])
        print(f"  Nhóm {pair_num}: {conv_count} tin nhắn")
        
        # Show first few messages
        for msg in data['conversation'][:3]:
            device_name = data['devices'][0] if msg['device_number'] == 1 else data['devices'][1]
            print(f"    {msg['message_id']}. {device_name}: {msg['content']}")
        
        if conv_count > 3:
            print(f"    ... và {conv_count - 3} tin nhắn khác")
    
    # Confirm
    print("\n" + "=" * 50)
    confirm = input("✅ Xác nhận setup và bắt đầu automation? (Y/n): ").strip().lower()
    return confirm not in ['n', 'no']

def save_setup_configs(phone_mapping, conversations):
    """Save phone mapping và conversations vào files"""
    # Save phone mapping
    if phone_mapping:
        save_phone_map_to_file(phone_mapping)
    
    # Save conversations
    if conversations:
        conversation_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_pairs': len(conversations),
            'conversations': conversations
        }
        
        try:
            with open('conversation_data.json', 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Đã lưu conversations vào conversation_data.json")
        except Exception as e:
            print(f"❌ Lỗi lưu conversations: {e}")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='UIAutomator2 Zalo Automation Tool với CLI phone mapping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ví dụ sử dụng:
  python core1.py                                    # Interactive setup mode
  python core1.py -s                                 # Force setup mode
  python core1.py -i                                 # Interactive phone mapping
  python core1.py -dm "192.168.5.74:569924311,192.168.5.82:583563439"  # CLI phone mapping
  python core1.py -ad 192.168.5.74 569924311         # Thêm một device
  python core1.py --devices 192.168.5.74:569924311 192.168.5.82:583563439  # Thêm nhiều devices
  python core1.py -ld                                # Liệt kê devices
  python core1.py --quick-setup                      # Quick setup mode
  python core1.py --show-config                      # Hiển thị config hiện tại
        """
    )
    
    parser.add_argument(
        '-dm', '--device-map',
        type=str,
        help='Phone mapping theo format "IP1:phone1,IP2:phone2"'
    )
    
    parser.add_argument(
        '-ad', '--add-device',
        nargs=2,
        metavar=('IP', 'PHONE'),
        help='Thêm một device với IP và số điện thoại'
    )
    
    parser.add_argument(
        '--devices',
        nargs='+',
        metavar='IP:PHONE',
        help='Nhập nhiều devices theo format IP:PHONE'
    )
    
    parser.add_argument(
        '-ld', '--list-devices',
        action='store_true',
        help='Hiển thị danh sách devices hiện có và phone mapping'
    )
    
    parser.add_argument(
        '-s', '--setup',
        action='store_true',
        help='Force interactive setup mode - chọn devices, pairing và conversation'
    )
    
    parser.add_argument(
        '--quick-setup',
        action='store_true',
        help='Quick setup mode - tự động detect devices và nhập số điện thoại'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Chế độ interactive để nhập phone mapping'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Hiển thị phone mapping hiện tại và thoát'
    )
    
    parser.add_argument(
        '--reset-config',
        action='store_true',
        help='Reset phone mapping về default và thoát'
    )
    
    return parser.parse_args()

def show_current_config():
    """Hiển thị phone mapping hiện tại"""
    print("\n📋 PHONE MAPPING HIỆN TẠI")
    print("=" * 30)
    
    if os.path.exists(PHONE_CONFIG_FILE):
        print(f"📁 File config: {PHONE_CONFIG_FILE}")
        file_map = load_phone_map_from_file()
        if file_map:
            print("📞 Từ file config:")
            for ip, phone in file_map.items():
                print(f"  {ip} -> {phone}")
        else:
            print("📞 File config trống")
    else:
        print(f"📁 File config: {PHONE_CONFIG_FILE} (chưa tồn tại)")
    
    print("\n📞 Default mapping:")
    for ip, phone in DEFAULT_PHONE_MAP.items():
        print(f"  {ip} -> {phone}")
    
    print("\n📞 Mapping hiện tại (merged):")
    # Sử dụng PHONE_MAP hiện tại thay vì load lại
    for ip, phone in PHONE_MAP.items():
        print(f"  {ip} -> {phone}")

def load_phone_map():
    """Load phone mapping từ các nguồn theo thứ tự ưu tiên"""
    global PHONE_MAP
    
    # 1. Từ file config
    file_map = load_phone_map_from_file()
    
    # 2. Merge với default
    PHONE_MAP = DEFAULT_PHONE_MAP.copy()
    PHONE_MAP.update(file_map)
    
    return PHONE_MAP

def should_run_setup_mode(args):
    """Kiểm tra có nên chạy setup mode không"""
    # Force setup nếu có --setup
    if args.setup:
        return True
    
    # Auto setup nếu không có config cơ bản
    if not os.path.exists('conversation_data.json') or not os.path.exists(PHONE_CONFIG_FILE):
        print("\n💡 Chưa có config cơ bản, chuyển sang setup mode...")
        return True
    
    # Không có arguments đặc biệt nào, hỏi user
    if not any([args.device_map, args.add_device, args.devices, args.quick_setup, 
                args.interactive, args.list_devices, args.show_config, args.reset_config]):
        choice = input("\n🚀 Chạy setup mode? (Y/n): ").strip().lower()
        return choice not in ['n', 'no']
    
    return False

def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Load phone mapping trước
    load_phone_map()
    
    # Xử lý các options đặc biệt trước
    if args.list_devices:
        list_devices_and_mapping()
        return
    
    if args.show_config:
        show_current_config()
        return
    
    if args.reset_config:
        if os.path.exists(PHONE_CONFIG_FILE):
            os.remove(PHONE_CONFIG_FILE)
            print(f"✅ Đã reset config file: {PHONE_CONFIG_FILE}")
        else:
            print(f"📁 Config file không tồn tại: {PHONE_CONFIG_FILE}")
        return
    
    # Kiểm tra có nên chạy setup mode không
    if should_run_setup_mode(args):
        setup_result = interactive_setup_mode()
        if setup_result:
            device_pairs, phone_mapping, conversations = setup_result
            # Extract all devices từ pairs
            all_devices = []
            for dev1, dev2 in device_pairs:
                all_devices.extend([dev1, dev2])
            
            # Update global phone mapping
            PHONE_MAP.update(phone_mapping)
            
            print(f"🚀 Bắt đầu automation với {len(all_devices)} devices từ setup: {all_devices}")
            
            # Chạy automation ngay với devices đã setup
            if len(all_devices) == 1:
                main_single_device(all_devices[0])
            else:
                main_multi_device(all_devices)
            return
        else:
            print("❌ Setup không thành công")
            return
    
    # Xử lý phone mapping từ CLI arguments
    updated_mapping = False
    
    # --add-device IP PHONE
    if args.add_device:
        ip, phone = args.add_device
        if validate_ip_address(ip) and validate_phone_number(phone):
            PHONE_MAP[ip] = phone
            print(f"📞 Đã thêm device: {ip} -> {phone}")
            updated_mapping = True
        else:
            print(f"❌ IP hoặc số điện thoại không hợp lệ: {ip}, {phone}")
            return
    
    # --devices IP:PHONE IP:PHONE ...
    if args.devices:
        devices_map = {}
        for device_str in args.devices:
            if ':' in device_str:
                ip, phone = device_str.split(':', 1)
                if validate_ip_address(ip.strip()) and validate_phone_number(phone.strip()):
                    devices_map[ip.strip()] = phone.strip()
                else:
                    print(f"❌ Device không hợp lệ: {device_str}")
                    return
            else:
                print(f"❌ Format device không đúng (cần IP:PHONE): {device_str}")
                return
        
        if devices_map:
            PHONE_MAP.update(devices_map)
            print(f"📞 Đã thêm {len(devices_map)} device(s): {devices_map}")
            updated_mapping = True
    
    # --device-map "IP1:phone1,IP2:phone2"
    if args.device_map:
        cli_map = parse_device_map_string(args.device_map)
        if cli_map:
            # Validate tất cả trước khi update
            for ip, phone in cli_map.items():
                if not validate_ip_address(ip) or not validate_phone_number(phone):
                    print(f"❌ Device mapping không hợp lệ: {ip} -> {phone}")
                    return
            
            PHONE_MAP.update(cli_map)
            print(f"📞 Đã cập nhật phone mapping từ CLI: {cli_map}")
            updated_mapping = True
        else:
            print("❌ Lỗi parse device map từ CLI")
            return
    
    # Quick setup mode
    if args.quick_setup:
        quick_map = quick_setup_mode()
        if quick_map:
            PHONE_MAP.update(quick_map)
            print(f"📞 Đã cập nhật phone mapping từ quick setup: {quick_map}")
            updated_mapping = True
        return
    
    # Interactive mode
    if args.interactive:
        interactive_map = interactive_phone_mapping()
        if interactive_map:
            PHONE_MAP.update(interactive_map)
            print(f"📞 Đã cập nhật phone mapping từ interactive: {interactive_map}")
            updated_mapping = True
        return
    
    # Nếu có update mapping từ CLI, lưu vào file
    if updated_mapping:
        save_choice = input("\n💾 Lưu phone mapping vào file config? (Y/n): ").strip().lower()
        if save_choice not in ['n', 'no']:
            save_phone_map_to_file(PHONE_MAP)
    
    # Kiểm tra uiautomator2 đã cài đặt chưa
    try:
        import uiautomator2 as u2
        try:
            version = getattr(u2, '__version__', 'unknown')
            print(f"✅ UIAutomator2 loaded (version: {version})")
        except:
            print("✅ UIAutomator2 loaded successfully")
    except ImportError:
        print("❌ UIAutomator2 chưa được cài đặt. Chạy: pip install uiautomator2")
        sys.exit(1)
    
    # Hiển thị phone mapping hiện tại
    if PHONE_MAP:
        print(f"📞 Phone mapping hiện tại: {PHONE_MAP}")
    
    # Lấy danh sách devices từ biến môi trường hoặc từ ADB
    env_devices = parse_devices_from_env()
    available_devices = get_all_connected_devices()
    
    if env_devices:
        # Sử dụng devices từ biến môi trường, kiểm tra có kết nối không
        valid_devices = [d for d in env_devices if d in available_devices]
        if not valid_devices:
            print(f"❌ Không có device nào từ DEVICES kết nối: {env_devices}")
            print(f"📱 Devices hiện có: {available_devices}")
            return
    else:
        # Không có biến môi trường, chọn tương tác
        if not available_devices:
            print("❌ Không có device nào kết nối")
            return
        valid_devices = select_devices_interactive(available_devices)
        if not valid_devices:
            return
    
    print(f"🚀 Chạy trên {len(valid_devices)} device(s): {valid_devices}")
    
    if len(valid_devices) == 1:
        # Single device mode - không cần group logic
        main_single_device(valid_devices[0])
    else:
        # Multi-device mode - sử dụng group-based conversation
        main_multi_device(valid_devices)

def run_zalo_automation(device_pairs, conversations, phone_mapping, progress_callback=None, stop_event=None, status_callback=None):
    """
    Hàm chính để chạy automation từ GUI Zalo
    
    Args:
        device_pairs: List[Tuple[dict, dict]] - Danh sách cặp thiết bị
        conversations: List[str] - Danh sách hội thoại
        phone_mapping: Dict[str, str] - Mapping IP -> số điện thoại
        progress_callback: callable - Callback để báo cáo tiến trình
    
    Returns:
        dict: Kết quả automation với format {"pair_1": {"status": "completed"}, ...}
    """
    global PHONE_MAP
    try:
        if progress_callback:
            progress_callback("🚀 Bắt đầu automation từ Zalo GUI...")
        
        print(f"\n🚀 Bắt đầu Zalo automation với {len(device_pairs)} cặp thiết bị")
        print(f"💬 Có {len(conversations)} hội thoại")
        print(f"📞 Có {len(phone_mapping)} mapping số điện thoại")
        
        # Debug logs chi tiết
        print("\n[DEBUG] ===== AUTOMATION DEBUG INFO =====")
        print(f"[DEBUG] Device pairs received: {len(device_pairs)}")
        for i, (d1, d2) in enumerate(device_pairs):
            print(f"[DEBUG] Pair {i+1}: {d1['ip']} ↔ {d2['ip']}")
        
        print(f"[DEBUG] Conversations: {conversations}")
        print(f"[DEBUG] Phone mapping: {phone_mapping}")
        print(f"[DEBUG] Progress callback: {'Available' if progress_callback else 'None'}")
        print(f"[DEBUG] Current global PHONE_MAP: {PHONE_MAP}")
        print("[DEBUG] =====================================\n")
        
        # Cập nhật global PHONE_MAP với mapping từ GUI
        PHONE_MAP.update(phone_mapping)
        
        # Lưu phone mapping vào file để đồng bộ
        if phone_mapping:
            save_phone_map_to_file(phone_mapping)
            if progress_callback:
                progress_callback(f"📞 Đã tải {len(phone_mapping)} mapping số điện thoại.")
        
        results = {}
        
        # Xử lý từng cặp thiết bị
        for pair_index, (device1, device2) in enumerate(device_pairs, 1):
            # Check stop signal before processing each pair
            if stop_event and stop_event.is_set():
                if progress_callback:
                    progress_callback("⏹️ Automation đã được dừng.")
                break
                
            pair_name = f"pair_{pair_index}"
            
            if progress_callback:
                progress_callback(f"🔄 Xử lý cặp {pair_index}/{len(device_pairs)}: {device1['ip']} ↔ {device2['ip']}")
            
            print(f"\n📱 Cặp {pair_index}: {device1['ip']} ↔ {device2['ip']}")
            
            # Chuẩn bị danh sách devices cho cặp này với format IP:5555
            device_ips = []
            for device_info in [device1, device2]:
                device_ip = device_info['ip']
                if ':' not in device_ip:
                    device_ip = f"{device_ip}:5555"
                device_ips.append(device_ip)
            
            # Kết nối devices
            connected_devices = []
            connection_results = {}
            
            for device_info in [device1, device2]:
                # Đảm bảo device_ip có format IP:5555
                device_ip = device_info['ip']
                if ':' not in device_ip:
                    device_ip = f"{device_ip}:5555"
                
                try:
                    if progress_callback:
                        progress_callback(f"🔌 Kết nối {device_ip}...")
                    
                    print(f"🔌 Kết nối device: {device_ip}")
                    dev = Device(device_ip)
                    if dev.connect():
                        connected_devices.append(dev)
                        connection_results[device_ip] = {"status": "connected", "result": None}
                        print(f"✅ Kết nối thành công: {device_ip}")
                    else:
                        connection_results[device_ip] = {"status": "connection_failed", "result": None}
                        print(f"❌ Kết nối thất bại: {device_ip}")
                except Exception as e:
                    connection_results[device_ip] = {"status": "error", "result": str(e)}
                    print(f"❌ Lỗi kết nối {device_ip}: {e}")
            
            if len(connected_devices) < 2:
                error_msg = f"Chỉ kết nối được {len(connected_devices)}/2 devices trong cặp {pair_index}"
                print(f"❌ {error_msg}")
                results[pair_name] = {"status": "connection_failed", "error": error_msg}
                
                # Cleanup devices đã kết nối
                for dev in connected_devices:
                    try:
                        dev.disconnect()
                    except:
                        pass
                continue
            
            # Chạy automation trên cặp devices
            try:
                if progress_callback:
                    progress_callback(f"🎯 Bắt đầu automation cặp {pair_index}...")
                
                print(f"🎯 Bắt đầu automation cặp {pair_index} với {len(connected_devices)} devices")
                
                # Chạy automation trên từng device trong cặp với parallel processing
                import threading
                import queue
                
                pair_results = {}
                result_queue = queue.Queue()
                threads = []
                
                def run_device_automation(dev, device_index, delay_before_start=0):
                    """Chạy automation trên một device với delay trước khi bắt đầu"""
                    device_ip = dev.device_id
                    
                    try:
                        # Emit device status update
                        if status_callback:
                            status_callback('device_status', device_ip, 'Đang chuẩn bị', '')
                        
                        # Check stop signal before starting
                        if stop_event and stop_event.is_set():
                            if status_callback:
                                status_callback('device_status', device_ip, 'Đã dừng', '')
                            result_queue.put((device_ip, {"status": "stopped", "result": "Automation stopped"}))
                            return
                            
                        # Delay trước khi bắt đầu để stagger start times
                        if delay_before_start > 0:
                            print(f"⏸️ Device {device_ip} delay {delay_before_start}s trước khi bắt đầu...")
                            if progress_callback:
                                progress_callback(f"⏸️ Device {device_ip} delay {delay_before_start}s...")
                            
                            if status_callback:
                                status_callback('device_status', device_ip, f'Đang delay {delay_before_start}s', '')
                            
                            # Check stop signal during delay
                            for i in range(delay_before_start):
                                if stop_event and stop_event.is_set():
                                    if status_callback:
                                        status_callback('device_status', device_ip, 'Đã dừng', '')
                                    result_queue.put((device_ip, {"status": "stopped", "result": "Automation stopped during delay"}))
                                    return
                                time.sleep(1)
                        
                        print(f"📱 Chạy automation trên {device_ip} (device {device_index+1}/{len(connected_devices)})")
                        if progress_callback:
                            progress_callback(f"📱 Bắt đầu automation trên {device_ip}...")
                        
                        if status_callback:
                            status_callback('device_status', device_ip, 'Đang chạy automation', '')
                        
                        # Check stop signal before running flow
                        if stop_event and stop_event.is_set():
                            if status_callback:
                                status_callback('device_status', device_ip, 'Đã dừng', '')
                            result_queue.put((device_ip, {"status": "stopped", "result": "Automation stopped before flow"}))
                            return
                            
                        result = flow(dev, all_devices=device_ips, stop_event=stop_event, status_callback=status_callback)
                        
                        # Check stop signal after flow
                        if stop_event and stop_event.is_set():
                            if status_callback:
                                status_callback('device_status', device_ip, 'Đã dừng', '')
                            result_queue.put((device_ip, {"status": "stopped", "result": "Automation stopped after flow"}))
                        else:
                            if status_callback:
                                status_callback('device_status', device_ip, 'Hoàn thành', str(result))
                            result_queue.put((device_ip, {"status": "completed", "result": result}))
                            print(f"✅ Hoàn thành automation trên {device_ip}: {result}")
                            
                            if progress_callback:
                                progress_callback(f"✅ Hoàn thành {device_ip}: {result}")
                            
                    except Exception as e:
                        if status_callback:
                            status_callback('device_status', device_ip, 'Lỗi', str(e))
                        result_queue.put((device_ip, {"status": "error", "result": str(e)}))
                        print(f"❌ Lỗi automation trên {device_ip}: {e}")
                        
                        if progress_callback:
                            progress_callback(f"❌ Lỗi {device_ip}: {str(e)}")
                
                # Tạo và start threads với staggered delays
                for i, dev in enumerate(connected_devices):
                    # Tăng delay giữa các devices từ 5+i*2 lên 8+i*3
                    delay_before_start = 8 + (i * 3) if i > 0 else 0  # 0s, 11s, 14s...
                    
                    thread = threading.Thread(
                        target=run_device_automation,
                        args=(dev, i, delay_before_start),
                        name=f"Device-{dev.device_id}"
                    )
                    threads.append(thread)
                    thread.start()
                    
                    # Nhỏ delay giữa việc start các threads để tránh race condition
                    time.sleep(0.5)
                
                # Đợi tất cả threads hoàn thành hoặc stop signal
                print(f"⏳ Đợi tất cả {len(threads)} devices hoàn thành automation...")
                if progress_callback:
                    progress_callback(f"⏳ Đợi {len(threads)} devices hoàn thành...")
                
                for thread in threads:
                    if stop_event and stop_event.is_set():
                        break
                    thread.join(timeout=1.0)  # Check every second for stop signal
                
                # Thu thập kết quả từ queue
                while not result_queue.empty():
                    device_ip, result = result_queue.get()
                    pair_results[device_ip] = result
                
                # Kiểm tra xem có device nào failed to open app không
                app_open_failures = []
                for device_ip, result in pair_results.items():
                    if result.get("result") == "APP_OPEN_FAILED":
                        app_open_failures.append(device_ip)
                
                if app_open_failures:
                    print(f"⚠️ Một số devices không mở được Zalo app: {app_open_failures}")
                    if progress_callback:
                        progress_callback(f"⚠️ Devices không mở được app: {', '.join(app_open_failures)}")
                
                # Tổng hợp kết quả cặp
                success_count = sum(1 for r in pair_results.values() if r["status"] == "completed" and r.get("result") not in ["APP_OPEN_FAILED", "LOGIN_REQUIRED"])
                if success_count == len(connected_devices):
                    results[pair_name] = {"status": "completed", "devices": pair_results}
                    if progress_callback:
                        progress_callback(f"✅ Hoàn thành cặp {pair_index}: {success_count}/{len(connected_devices)} thành công")
                else:
                    results[pair_name] = {"status": "partial_success", "devices": pair_results}
                    if progress_callback:
                        progress_callback(f"⚠️ Cặp {pair_index} hoàn thành một phần: {success_count}/{len(connected_devices)} thành công")
                
            except Exception as e:
                error_msg = f"Lỗi automation cặp {pair_index}: {str(e)}"
                print(f"❌ {error_msg}")
                results[pair_name] = {"status": "error", "error": error_msg}
                if progress_callback:
                    progress_callback(f"❌ {error_msg}")
            
            # Cleanup devices
            for dev in connected_devices:
                try:
                    dev.disconnect()
                except:
                    pass
            
            # Delay giữa các cặp
            if pair_index < len(device_pairs):
                print(f"⏸️ Nghỉ 2 giây trước cặp tiếp theo...")
                time.sleep(2)
        
        # Tổng hợp kết quả cuối cùng
        total_pairs = len(device_pairs)
        success_pairs = sum(1 for r in results.values() if r["status"] == "completed")
        
        final_message = f"Hoàn thành: {success_pairs}/{total_pairs} thành công."
        print(f"\n🏁 {final_message}")
        
        if progress_callback:
            progress_callback(f"🏁 {final_message}")
        
        return results
        
    except Exception as e:
        error_msg = f"Lỗi chung trong automation: {str(e)}"
        print(f"❌ {error_msg}")
        if progress_callback:
            progress_callback(f"❌ {error_msg}")
        return {"error": error_msg}

if __name__ == "__main__":
    main()

# ===================== EDIT PHÍA DƯỚI NÀY =====================
# === FLOW START ===
import re, time

PKG = "com.zing.zalo"
RID_SEARCH_BTN   = "com.zing.zalo:id/action_bar_search_btn"
RID_ACTION_BAR   = "com.zing.zalo:id/zalo_action_bar"
RID_MSG_LIST     = "com.zing.zalo:id/recycler_view_msgList"
RID_TAB_MESSAGE  = "com.zing.zalo:id/maintab_message"
TEXT_SEARCH_PLACEHOLDER = "Tìm kiếm"

def is_login_required(dev, debug=False):
    """Kiểm tra có cần đăng nhập không - UIAutomator2 way"""
    try:
        # Kiểm tra login buttons
        if dev.element_exists(resourceId="com.zing.zalo:id/btnLogin"):
            if debug: print("[DEBUG] Login button found")
            return True
        
        if dev.element_exists(text="btnRegisterUsingPhoneNumber"):
            if debug: print("[DEBUG] Register button found")
            return True
        
        # Kiểm tra main layout
        if dev.element_exists(resourceId="com.zing.zalo:id/maintab_root_layout"):
            return False
        
        if dev.element_exists(resourceId=RID_MSG_LIST):
            return False
            
        return False
    except Exception as e:
        if debug: print(f"[DEBUG] Error checking login: {e}")
        return False

def ensure_on_messages_tab(dev, debug=False):
    """Ép về tab 'Tin nhắn' để có action bar & search đúng ngữ cảnh - UIAutomator2 way"""
    try:
        # Nếu list tin nhắn đã có thì coi như đang ở tab message
        if dev.element_exists(resourceId=RID_MSG_LIST):
            return True
        
        # Click vào tab message
        if dev.click_by_resource_id(RID_TAB_MESSAGE, timeout=3, debug=debug):
            time.sleep(0.6)
            return dev.element_exists(resourceId=RID_MSG_LIST)
        
        # Fallback: click by text
        if dev.click_by_text("Tin nhắn", timeout=3, debug=debug):
            time.sleep(0.6)
            return dev.element_exists(resourceId=RID_MSG_LIST)
        
        return True  # không tìm thấy thì vẫn tiếp tục (tránh block)
    except Exception as e:
        if debug: print(f"[DEBUG] Error ensuring messages tab: {e}")
        return True

def verify_search_opened(dev, timeout=3, debug=False):
    """Verify search interface opened - UIAutomator2 way"""
    try:
        # Kiểm tra search input field
        search_selectors = [
            {"resourceId": "android:id/search_src_text"},
            {"resourceId": "com.zing.zalo:id/search_src_text"},
            {"resourceId": "com.zing.zalo:id/search_edit"},
            {"className": "android.widget.EditText"},
            {"className": "androidx.appcompat.widget.SearchView$SearchAutoComplete"}
        ]
        
        for selector in search_selectors:
            if dev.d(**selector).wait(timeout=timeout):
                if debug: print(f"[DEBUG] Search opened - found: {selector}")
                return True
        
        # Kiểm tra IME (keyboard) hiển thị
        try:
            ime_info = dev.d.info.get('inputMethodShown', False)
            if ime_info:
                if debug: print("[DEBUG] Search opened - IME shown")
                return True
        except:
            pass
        
        return False
    except Exception as e:
        if debug: print(f"[DEBUG] Error verifying search: {e}")
        return False

def open_search_strong(dev, debug=False):
    """Mở search interface - UIAutomator2 optimized"""
    
    # Method 1: Click search button by resource-id (most reliable)
    if dev.click_by_resource_id(RID_SEARCH_BTN, timeout=5, debug=False):
        if verify_search_opened(dev, debug=False):
            if debug: print("[DEBUG] ✅ Search opened successfully")
            return True
    
    # Method 2: Quick fallback methods
    fallback_methods = [
        ("text", "Search"),
        ("text", "Tìm kiếm"),
        ("xpath", '//*[@text="Search"]'),
        ("description", "Search")
    ]
    
    for method_type, selector in fallback_methods:
        try:
            if method_type == "text":
                success = dev.click_by_text(selector, timeout=2, debug=False)
            elif method_type == "xpath":
                success = dev.click_by_xpath(selector, timeout=2, debug=False)
            elif method_type == "description":
                success = dev.click_by_description(selector, timeout=2, debug=False)
            
            if success and verify_search_opened(dev, debug=False):
                if debug: print(f"[DEBUG] ✅ Search opened via {method_type}: {selector}")
                return True
        except:
            continue
    
    # Method 3: Adaptive coordinates (last resort)
    search_positions = [(76, 126), (495, 126), (540, 126)]
    for base_x, base_y in search_positions:
        dev.tap_adaptive(base_x, base_y)
        time.sleep(0.5)
        if verify_search_opened(dev, debug=False):
            if debug: print(f"[DEBUG] ✅ Search opened via coordinates: ({base_x}, {base_y})")
            return True
    
    # Method 4: Search key fallback
    dev.key(84)  # SEARCH key
    if verify_search_opened(dev, debug=False):
        if debug: print("[DEBUG] ✅ Search opened via search key")
        return True
    
    if debug: print("[DEBUG] ❌ Could not open search")
    return False

def enter_query_and_submit(dev, text, debug=False):
    """Nhập query và submit - UIAutomator2 optimized"""
    try:
        # Tìm search input field
        search_selectors = [
            {"resourceId": "android:id/search_src_text"},
            {"resourceId": "com.zing.zalo:id/search_src_text"},
            {"resourceId": "com.zing.zalo:id/search_edit"},
            {"className": "android.widget.EditText"}
        ]
        
        for selector in search_selectors:
            if dev.d(**selector).exists:
                # Set text và submit
                dev.d(**selector).set_text(text)
                time.sleep(0.3)
                dev.key(66)  # ENTER
                time.sleep(1)
                if debug: print(f"[DEBUG] ✅ Entered text: {text}")
                return True
        
        # Fallback: send keys directly
        dev.text(text)
        time.sleep(0.3)
        dev.key(66)  # ENTER
        time.sleep(1)
        if debug: print(f"[DEBUG] ✅ Entered text (fallback): {text}")
        return True
        
    except Exception as e:
        if debug: print(f"[DEBUG] ❌ Error entering text: {e}")
        return False

def click_first_search_result(dev, preferred_text=None, debug=False):
    """Click first search result - UIAutomator2 optimized với resource-id"""
    try:
        # Method 1: Click by search result button resource-id (most reliable)
        if dev.click_by_resource_id("com.zing.zalo:id/btn_search_result", timeout=3, debug=False):
            if debug: print("[DEBUG] ✅ Clicked search result button")
            return True
        
        # Method 2: Click by preferred text
        if preferred_text and dev.click_by_text(preferred_text, timeout=3, debug=False):
            if debug: print(f"[DEBUG] ✅ Found and clicked: {preferred_text}")
            return True
        
        # Method 3: Click first item in message list
        if dev.element_exists(resourceId=RID_MSG_LIST):
            recyclerview = dev.d(resourceId=RID_MSG_LIST)
            if recyclerview.exists:
                first_child = recyclerview.child(clickable=True)
                if first_child.exists:
                    first_child.click()
                    if debug: print("[DEBUG] ✅ Clicked first search result")
                    return True
        
        # Method 4: Click first clickable item
        clickable_items = dev.d(clickable=True)
        if clickable_items.exists:
            clickable_items.click()
            if debug: print("[DEBUG] ✅ Clicked first available result")
            return True
        
        # Method 5: Fallback coordinates
        dev.tap(540, 960)
        if debug: print("[DEBUG] ✅ Used fallback tap")
        return True
        
    except Exception as e:
        if debug: print(f"[DEBUG] ❌ Error clicking result: {e}")
        return False

def send_message_human_like(dev, message, debug=False):
    """Gửi tin nhắn với human-like typing simulation"""
    import random
    import time as time_module
    
    try:
        # Tìm input field để nhập tin nhắn
        input_selectors = [
            {"resourceId": "com.zing.zalo:id/message_edit_text"},
            {"resourceId": "com.zing.zalo:id/edit_text_message"},
            {"resourceId": "com.zing.zalo:id/input_message"},
            {"className": "android.widget.EditText"}
        ]
        
        for selector in input_selectors:
            if dev.d(**selector).exists:
                # Clear input field
                dev.d(**selector).clear_text()
                time_module.sleep(0.2)
                
                # Human-like typing simulation
                if debug: print(f"[DEBUG] 🎯 Bắt đầu gõ: {message}")
                
                # Gõ từng ký tự với delay ngẫu nhiên
                for i, char in enumerate(message):
                    # Gõ ký tự
                    current_text = message[:i+1]
                    dev.d(**selector).set_text(current_text)
                    
                    # Delay ngẫu nhiên giữa các ký tự (50-200ms)
                    char_delay = random.uniform(0.05, 0.2)
                    time_module.sleep(char_delay)
                    
                    # Thỉnh thoảng dừng lâu hơn (như người suy nghĩ)
                    if random.random() < 0.1:  # 10% chance
                        think_delay = random.uniform(0.3, 1.0)
                        time_module.sleep(think_delay)
                
                # Đợi một chút trước khi gửi (như người đọc lại)
                read_delay = random.uniform(0.5, 2.0)
                time_module.sleep(read_delay)
                
                # Tìm và click send button
                send_selectors = [
                    {"resourceId": "com.zing.zalo:id/new_chat_input_btn_chat_send"},
                    {"resourceId": "com.zing.zalo:id/send_button"},
                    {"resourceId": "com.zing.zalo:id/btn_send"},
                    {"description": "Send"},
                    {"text": "Gửi"}
                ]
                
                for send_selector in send_selectors:
                    if dev.d(**send_selector).exists:
                        dev.d(**send_selector).click()
                        if debug: print(f"[DEBUG] ✅ Sent message (human-like): {message}")
                        return True
                
                # Fallback: nhấn Enter
                dev.key(66)  # ENTER
                if debug: print(f"[DEBUG] ✅ Sent message (Enter): {message}")
                return True
        
        # Fallback: nhập text trực tiếp
        dev.text(message)
        time_module.sleep(0.3)
        dev.key(66)  # ENTER
        if debug: print(f"[DEBUG] ✅ Sent message (fallback): {message}")
        return True
        
    except Exception as e:
        if debug: print(f"[DEBUG] ❌ Error sending message: {e}")
        return False

def send_message(dev, message, debug=False):
    """Wrapper function để maintain compatibility"""
    return send_message_human_like(dev, message, debug)

def load_conversation_from_file(group_id):
    """Load cuộc hội thoại từ file conversation_data.json như trong main.py"""
    try:
        import json
        import os
        if os.path.exists('conversation_data.json'):
            with open('conversation_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Tìm conversation cho group này
            conversations = data.get('conversations', {})
            pair_key = f"pair_{group_id}"
            
            if pair_key in conversations:
                return conversations[pair_key].get('conversation', [])
                
    except Exception as e:
        print(f"[DEBUG] Lỗi load conversation từ file: {e}")
    
    # Fallback conversation đơn giản nếu không load được
    return [
    {"message_id": 1, "device_number": 1, "content": "Cậu đang làm gì đấy"},
    {"message_id": 2, "device_number": 2, "content": "Đang xem phim nè"},
    {"message_id": 3, "device_number": 1, "content": "Phim gì thế"},
    {"message_id": 4, "device_number": 2, "content": "Phim hài vui lắm"},
    {"message_id": 5, "device_number": 1, "content": "Cho tớ link đi"},
    {"message_id": 6, "device_number": 2, "content": "Xíu gửi nha"},
    {"message_id": 7, "device_number": 1, "content": "Ok luôn"},
    {"message_id": 8, "device_number": 2, "content": "Cậu ăn cơm chưa"},
    {"message_id": 9, "device_number": 1, "content": "Chưa đói nên chưa ăn"},
    {"message_id": 10, "device_number": 2, "content": "Ăn sớm đi kẻo đói"},
    {"message_id": 11, "device_number": 1, "content": "Ừ biết rồi"},
    {"message_id": 12, "device_number": 2, "content": "Chiều nay rảnh không"},
    {"message_id": 13, "device_number": 1, "content": "Cũng rảnh một chút"},
    {"message_id": 14, "device_number": 2, "content": "Đi cà phê không"},
    {"message_id": 15, "device_number": 1, "content": "Đi luôn chứ sao"},
    {"message_id": 16, "device_number": 2, "content": "Ở quán cũ nhé"},
    {"message_id": 17, "device_number": 1, "content": "Ok quán đó yên tĩnh"},
    {"message_id": 18, "device_number": 2, "content": "Có chuyện muốn kể"},
    {"message_id": 19, "device_number": 1, "content": "Chuyện gì thế"},
    {"message_id": 20, "device_number": 2, "content": "Bị người ta nói xấu sau lưng"},
    {"message_id": 21, "device_number": 1, "content": "Ai mà tệ vậy"},
    {"message_id": 22, "device_number": 2, "content": "Người trong nhóm luôn"},
    {"message_id": 23, "device_number": 1, "content": "Nghe mà tức thật"},
    {"message_id": 24, "device_number": 2, "content": "Ừ tớ cũng giận lắm"},
    {"message_id": 25, "device_number": 1, "content": "Thôi chiều ra cà phê tâm sự"},
    {"message_id": 26, "device_number": 2, "content": "Ừ gặp rồi kể rõ hơn"},
    {"message_id": 27, "device_number": 1, "content": "Ok deal luôn"},
    {"message_id": 28, "device_number": 2, "content": "Cậu có muốn nói gì thêm không"},
    {"message_id": 29, "device_number": 1, "content": "Chưa có"},
    {"message_id": 30, "device_number": 2, "content": "Ok"},
    {"message_id": 31, "device_number": 1, "content": "Cậu có muốn nói gì thêm không"},
    {"message_id": 32, "device_number": 2, "content": "Ok"}
    ]

def determine_group_and_role(device_ip, all_devices):
    """Xác định nhóm và role của device dựa trên IP"""
    # Chuẩn hóa device_ip để chỉ lấy phần IP (bỏ port nếu có)
    clean_device_ip = device_ip.split(':')[0] if ':' in device_ip else device_ip
    
    # Chuẩn hóa all_devices để chỉ lấy phần IP (bỏ port nếu có)
    clean_all_devices = [d.split(':')[0] if ':' in d else d for d in all_devices]
    
    # Sắp xếp devices theo IP để đảm bảo consistent grouping
    sorted_devices = sorted(clean_all_devices)
    device_index = sorted_devices.index(clean_device_ip)
    
    # Chia thành các nhóm 2 máy
    group_id = (device_index // 2) + 1
    role_in_group = (device_index % 2) + 1
    
    return group_id, role_in_group

def get_sync_file_path(group_id):
    """Lấy đường dẫn file sync cho nhóm"""
    return f"sync_group_{group_id}.json"

def read_current_message_id(group_id):
    """Đọc current message_id từ file sync"""
    import json
    import os
    sync_file = get_sync_file_path(group_id)
    try:
        if os.path.exists(sync_file):
            with open(sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('current_message_id', 1)
    except Exception:
        pass
    return 1

def update_current_message_id(group_id, message_id):
    """Cập nhật current message_id vào file sync"""
    import json
    sync_file = get_sync_file_path(group_id)
    try:
        data = {'current_message_id': message_id, 'timestamp': time.time()}
        with open(sync_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return True
    except Exception:
        return False

def wait_for_message_turn(group_id, target_message_id, role_in_group, timeout=300):
    """Đợi đến lượt gửi message_id cụ thể với timeout"""
    import time as time_module
    start_time = time_module.time()
    
    while time_module.time() - start_time < timeout:
        current_id = read_current_message_id(group_id)
        if current_id == target_message_id:
            return True
        
        # Delay ngắn trước khi check lại
        time_module.sleep(0.5)
    
    print(f"⚠️ Nhóm {group_id} - Timeout đợi message_id {target_message_id}")
    return False

def calculate_smart_delay(message_length, is_first_message=False):
    """Tính delay thông minh dựa trên độ dài tin nhắn"""
    import random
    
    if is_first_message:
        return random.uniform(1, 3)  # Delay ngắn cho tin nhắn đầu
    
    # Base delay dựa trên độ dài tin nhắn (giả lập thời gian đọc + suy nghĩ)
    base_delay = min(len(message_length) * 0.1, 8)  # Tối đa 8s cho tin nhắn dài
    
    # Thêm random variation (±50%)
    variation = base_delay * 0.5
    final_delay = base_delay + random.uniform(-variation, variation)
    
    # Đảm bảo delay trong khoảng hợp lý (2-15s)
    return max(2, min(15, final_delay))

def run_conversation(dev, device_role, debug=False, all_devices=None, stop_event=None, status_callback=None):
    """Chạy cuộc hội thoại với message_id synchronization và smart timing"""
    import random
    import time as time_module
    
    # Lấy IP của device hiện tại
    device_ip = dev.device_id.split(":")[0] if ":" in dev.device_id else dev.device_id
    
    # Nếu không có all_devices, fallback về logic cũ
    if not all_devices:
        all_devices = [device_ip]
    
    # Xác định nhóm và role trong nhóm
    group_id, role_in_group = determine_group_and_role(device_ip, all_devices)
    
    print(f"💬 Device {device_ip} - Nhóm {group_id}, Role {role_in_group}")
    
    # Load conversation từ file như trong main.py
    conversation_data = load_conversation_from_file(group_id)
    
    # Convert format từ main.py sang format cần thiết với message_id support
    conversation = []
    for msg_data in conversation_data:
        if isinstance(msg_data, dict):
            if 'message_id' in msg_data and 'device_number' in msg_data and 'content' in msg_data:
                # Format mới với message_id: {"message_id": 1, "device_number": 1, "content": "message"}
                conversation.append({
                    "message_id": msg_data['message_id'],
                    "sender": msg_data['device_number'],
                    "message": msg_data['content']
                })
            elif 'device_number' in msg_data and 'content' in msg_data:
                # Format từ main.py: {"device_number": 1, "content": "message"} - tự tạo message_id
                conversation.append({
                    "message_id": len(conversation) + 1,
                    "sender": msg_data['device_number'],
                    "message": msg_data['content']
                })
            elif 'sender' in msg_data and 'message' in msg_data:
                # Format cũ: {"sender": 1, "message": "text"} - tự tạo message_id
                conversation.append({
                    "message_id": len(conversation) + 1,
                    "sender": msg_data['sender'],
                    "message": msg_data['message']
                })
    
    if not conversation:
        print(f"❌ Nhóm {group_id} - Không có cuộc hội thoại")
        return False
    
    print(f"📋 Nhóm {group_id} - Bắt đầu cuộc hội thoại với {len(conversation)} tin nhắn (message_id sync enabled)")
    
    # Khởi tạo sync file nếu là device đầu tiên
    if role_in_group == 1:
        update_current_message_id(group_id, 1)
        print(f"🔄 Nhóm {group_id} - Khởi tạo sync với message_id = 1")
    
    # Duyệt qua conversation của nhóm với message_id synchronization
    for msg in conversation:
        message_id = msg["message_id"]
        
        # Kiểm tra stop signal trước xử lý mỗi message
        if stop_event and stop_event.is_set():
            print(f"[DEBUG] Stop signal received during conversation for {device_ip}")
            return False
        
        # Emit status update cho message hiện tại
        if status_callback:
            status_callback('message_status_updated', {
                'device_ip': device_ip,
                'message_id': message_id,
                'content': msg['message'],
                'status': 'processing',
                'sender': msg['sender'],
                'role_in_group': role_in_group
            })
        
        if msg["sender"] == role_in_group:
            # Đợi đến lượt message_id này
            print(f"⏳ Nhóm {group_id} - Đợi lượt message_id {message_id}...")
            if not wait_for_message_turn(group_id, message_id, role_in_group):
                print(f"❌ Nhóm {group_id} - Timeout đợi message_id {message_id}, bỏ qua")
                continue
            
            # Kiểm tra stop signal sau wait
            if stop_event and stop_event.is_set():
                print(f"[DEBUG] Stop signal received after waiting for message turn for {device_ip}")
                return False
            
            # Tính delay thông minh
            is_first = (message_id == 1)
            smart_delay = calculate_smart_delay(msg['message'], is_first)
            
            if not is_first:
                print(f"⏳ Nhóm {group_id} - Smart delay {smart_delay:.1f}s cho message_id {message_id}...")
                
                # Emit status update cho delay
                if status_callback:
                    status_callback('message_status_updated', {
                        'device_ip': device_ip,
                        'message_id': message_id,
                        'content': msg['message'],
                        'status': 'delaying',
                        'delay_time': smart_delay,
                        'sender': msg['sender'],
                        'role_in_group': role_in_group
                    })
                
                # Kiểm tra stop signal trước smart delay
                if stop_event and stop_event.is_set():
                    print(f"[DEBUG] Stop signal received during smart delay for {device_ip}")
                    return False
                
                time_module.sleep(smart_delay)
            
            print(f"📤 Nhóm {group_id} - Máy {role_in_group} gửi message_id {message_id}: {msg['message']}")
            
            # Emit status update cho việc gửi
            if status_callback:
                status_callback('message_status_updated', {
                    'device_ip': device_ip,
                    'message_id': message_id,
                    'content': msg['message'],
                    'status': 'sending',
                    'sender': msg['sender'],
                    'role_in_group': role_in_group
                })
            
            # Gửi tin nhắn với human-like typing
            if send_message(dev, msg["message"], debug=debug):
                print(f"✅ Nhóm {group_id} - Đã gửi message_id {message_id}: {msg['message']}")
                
                # Emit status update cho việc gửi thành công
                if status_callback:
                    status_callback('message_status_updated', {
                        'device_ip': device_ip,
                        'message_id': message_id,
                        'content': msg['message'],
                        'status': 'sent',
                        'sender': msg['sender'],
                        'role_in_group': role_in_group
                    })
                
                # Cập nhật current_message_id để device khác có thể tiếp tục
                next_message_id = message_id + 1
                update_current_message_id(group_id, next_message_id)
                print(f"🔄 Nhóm {group_id} - Cập nhật current_message_id = {next_message_id}")
                
                # Delay ngắn sau khi gửi (1-3 giây)
                post_send_wait = random.uniform(1, 3)
                print(f"⏸️ Nhóm {group_id} - Nghỉ {post_send_wait:.1f}s sau message_id {message_id}...")
                
                # Kiểm tra stop signal trước post send delay
                if stop_event and stop_event.is_set():
                    print(f"[DEBUG] Stop signal received during post send delay for {device_ip}")
                    return False
                
                time_module.sleep(post_send_wait)
            else:
                print(f"❌ Nhóm {group_id} - Không thể gửi message_id {message_id}: {msg['message']}")
                # Vẫn cập nhật message_id để không block các device khác
                update_current_message_id(group_id, message_id + 1)
                break
        else:
            # Không phải lượt của mình trong nhóm - chỉ log
            print(f"📥 Nhóm {group_id} - Đợi Máy {msg['sender']} gửi message_id {message_id}: {msg['message']}")
    
    print(f"✅ Nhóm {group_id} - Hoàn thành cuộc hội thoại")
    
    # Cleanup sync file khi hoàn thành
    try:
        sync_file = get_sync_file_path(group_id)
        if os.path.exists(sync_file):
            os.remove(sync_file)
            print(f"🧹 Nhóm {group_id} - Đã cleanup sync file")
    except Exception:
        pass
    
    return True

# Default PHONE_MAP - sẽ được override bởi CLI args hoặc config file
DEFAULT_PHONE_MAP = {
    "192.168.5.74": "569924311",
    "192.168.5.82": "583563439",
}

# Global PHONE_MAP sẽ được load từ các nguồn khác nhau
PHONE_MAP = {}

def load_phone_map_from_file():
    """Load phone mapping từ file config"""
    try:
        if os.path.exists(PHONE_CONFIG_FILE):
            with open(PHONE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('phone_mapping', {})
    except Exception as e:
        print(f"⚠️ Lỗi đọc file config: {e}")
    return {}

def save_phone_map_to_file(phone_map):
    """Lưu phone mapping vào file config"""
    try:
        data = {
            'phone_mapping': phone_map,
            'timestamp': time.time(),
            'created_by': 'core1.py CLI'
        }
        with open(PHONE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Đã lưu phone mapping vào {PHONE_CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu file config: {e}")
        return False

def parse_device_map_string(device_map_str):
    """Parse device map string từ CLI argument"""
    phone_map = {}
    try:
        # Format: "IP1:phone1,IP2:phone2"
        pairs = device_map_str.split(',')
        for pair in pairs:
            if ':' in pair:
                ip, phone = pair.strip().split(':', 1)
                phone_map[ip.strip()] = phone.strip()
        return phone_map
    except Exception as e:
        print(f"❌ Lỗi parse device map: {e}")
        return {}

def interactive_phone_mapping():
    """Interactive mode để nhập phone mapping"""
    print("\n📱 INTERACTIVE PHONE MAPPING MODE")
    print("=" * 40)
    
    # Lấy danh sách devices hiện có
    available_devices = get_all_connected_devices()
    env_devices = parse_devices_from_env()
    
    all_devices = list(set(available_devices + env_devices))
    
    if not all_devices:
        print("❌ Không tìm thấy devices nào")
        return {}
    
    print(f"📋 Phát hiện {len(all_devices)} devices:")
    for i, device in enumerate(all_devices, 1):
        ip = device.split(':')[0] if ':' in device else device
        current_phone = PHONE_MAP.get(ip, "chưa có")
        print(f"  {i}. {device} (số hiện tại: {current_phone})")
    
    phone_map = {}
    print("\n💡 Nhập số điện thoại cho từng device (Enter để bỏ qua):")
    
    for device in all_devices:
        ip = device.split(':')[0] if ':' in device else device
        current_phone = PHONE_MAP.get(ip, "")
        
        prompt = f"📞 {device}"
        if current_phone:
            prompt += f" (hiện tại: {current_phone})"
        prompt += ": "
        
        try:
            phone = input(prompt).strip()
            if phone:
                phone_map[ip] = phone
                print(f"  ✅ {ip} -> {phone}")
            elif current_phone:
                phone_map[ip] = current_phone
                print(f"  📋 Giữ nguyên: {ip} -> {current_phone}")
        except KeyboardInterrupt:
            print("\n❌ Đã hủy")
            return {}
    
    if phone_map:
        print(f"\n📋 Phone mapping mới:")
        for ip, phone in phone_map.items():
            print(f"  {ip} -> {phone}")
        
        save_choice = input("\n💾 Lưu vào file config? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            save_phone_map_to_file(phone_map)
    
    return phone_map

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='UIAutomator2 Zalo Automation Tool với CLI phone mapping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ví dụ sử dụng:
  python core1.py                                    # Chế độ bình thường
  python core1.py -i                                 # Interactive phone mapping
  python core1.py -dm "192.168.5.74:569924311,192.168.5.82:583563439"  # CLI phone mapping
  python core1.py --show-config                      # Hiển thị config hiện tại
        """
    )
    
    parser.add_argument(
        '-dm', '--device-map',
        type=str,
        help='Phone mapping theo format "IP1:phone1,IP2:phone2"'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Chế độ interactive để nhập phone mapping'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Hiển thị phone mapping hiện tại và thoát'
    )
    
    parser.add_argument(
        '--reset-config',
        action='store_true',
        help='Reset phone mapping về default và thoát'
    )
    
    return parser.parse_args()

def show_current_config():
    """Hiển thị phone mapping hiện tại"""
    print("\n📋 PHONE MAPPING HIỆN TẠI")
    print("=" * 30)
    
    if os.path.exists(PHONE_CONFIG_FILE):
        print(f"📁 File config: {PHONE_CONFIG_FILE}")
        file_map = load_phone_map_from_file()
        if file_map:
            print("📞 Từ file config:")
            for ip, phone in file_map.items():
                print(f"  {ip} -> {phone}")
        else:
            print("📞 File config trống")
    else:
        print(f"📁 File config: {PHONE_CONFIG_FILE} (chưa tồn tại)")
    
    print("\n📞 Default mapping:")
    for ip, phone in DEFAULT_PHONE_MAP.items():
        print(f"  {ip} -> {phone}")
    
    print("\n📞 Mapping hiện tại (merged):")
    current_map = load_phone_map()
    for ip, phone in current_map.items():
        print(f"  {ip} -> {phone}")

def flow(dev, all_devices=None, stop_event=None, status_callback=None):
    """Main flow function - UIAutomator2 version với group-based conversation automation"""
    
    # DEBUG: Log thông tin device
    device_ip = dev.device_id
    print(f"[DEBUG] Starting flow for device: {device_ip}")
    print(f"[DEBUG] All devices passed to flow: {all_devices}")
    
    # Mở app Zalo với retry logic và delay
    print(f"[DEBUG] Opening Zalo app on {device_ip}...")
    
    # Thêm delay ngẫu nhiên để tránh conflict khi nhiều device cùng mở
    import random
    initial_delay = random.uniform(1, 3)
    print(f"[DEBUG] Initial delay: {initial_delay:.2f}s")
    
    # Kiểm tra stop signal trước delay
    if stop_event and stop_event.is_set():
        print(f"[DEBUG] Stop signal received during initial delay for {device_ip}")
        return "STOPPED"
    
    time.sleep(initial_delay)
    
    # Enhanced retry logic cho việc mở app với better error handling
    max_retries = 5  # Tăng số lần retry
    app_opened_successfully = False
    
    for attempt in range(max_retries):
        try:
            print(f"[DEBUG] Attempt {attempt + 1}/{max_retries} to open Zalo on {device_ip}")
            
            # Thử force stop app trước khi mở lại (trừ lần đầu)
            if attempt > 0:
                try:
                    dev.app_stop(PKG)
                    time.sleep(1)
                    print(f"[DEBUG] Force stopped Zalo app before retry")
                except:
                    pass
            
            # Mở app
            dev.app(PKG)
            
            # Đợi app mở hoàn toàn với progressive delay
            base_delay = 4 + (attempt * 1)  # Tăng delay theo số lần retry
            app_open_delay = base_delay + random.uniform(0, 2)
            print(f"[DEBUG] Waiting {app_open_delay:.2f}s for app to fully load...")
            
            # Kiểm tra stop signal trước delay
            if stop_event and stop_event.is_set():
                print(f"[DEBUG] Stop signal received during app open delay for {device_ip}")
                return "STOPPED"
            
            time.sleep(app_open_delay)
            
            # Kiểm tra app đã mở thành công chưa với multiple checks
            success_indicators = [
                ("maintab_root_layout", "com.zing.zalo:id/maintab_root_layout"),
                ("message_list", RID_MSG_LIST),
                ("login_button", "com.zing.zalo:id/btnLogin"),
                ("action_bar", RID_ACTION_BAR),
                ("tab_message", RID_TAB_MESSAGE)
            ]
            
            found_indicator = None
            for indicator_name, resource_id in success_indicators:
                if dev.element_exists(resourceId=resource_id):
                    found_indicator = indicator_name
                    break
            
            if found_indicator:
                print(f"[DEBUG] Zalo app opened successfully on {device_ip} (found: {found_indicator})")
                app_opened_successfully = True
                break
            else:
                print(f"[DEBUG] App not fully loaded on attempt {attempt + 1}, no success indicators found")
                if attempt < max_retries - 1:
                    retry_delay = 2 + (attempt * 1)  # Progressive retry delay
                    print(f"[DEBUG] Waiting {retry_delay}s before retry...")
                    
                    # Kiểm tra stop signal trước retry delay
                    if stop_event and stop_event.is_set():
                        print(f"[DEBUG] Stop signal received during retry delay for {device_ip}")
                        return "STOPPED"
                    
                    time.sleep(retry_delay)
                    
        except Exception as e:
            print(f"[DEBUG] Error opening app on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                retry_delay = 3 + (attempt * 1)
                print(f"[DEBUG] Exception occurred, waiting {retry_delay}s before retry...")
                
                # Kiểm tra stop signal trước exception retry delay
                if stop_event and stop_event.is_set():
                    print(f"[DEBUG] Stop signal received during exception retry delay for {device_ip}")
                    return "STOPPED"
                
                time.sleep(retry_delay)
    
    if not app_opened_successfully:
        print(f"[ERROR] Failed to open Zalo app after {max_retries} attempts on {device_ip}")
        return "APP_OPEN_FAILED"
    
    print(f"[DEBUG] Zalo app opening process completed on {device_ip}")
    
    # Kiểm tra đăng nhập
    print(f"[DEBUG] Checking login status for {device_ip}...")
    if is_login_required(dev, debug=True):
        ip = dev.device_id.split(":")[0] if ":" in dev.device_id else dev.device_id
        print(f"[DEBUG] Login required for {device_ip}")
        print(f"IP: {ip} - chưa đăng nhập → thoát flow.")
        return "LOGIN_REQUIRED"
    
    ip = dev.device_id.split(":")[0] if ":" in dev.device_id else dev.device_id
    print(f"[DEBUG] Login check passed for {device_ip}")
    print(f"IP: {ip} - đã đăng nhập. Bắt đầu flow…")
    
    # DEBUG: Log thông tin đầu vào
    print(f"[DEBUG] Current IP: {ip}")
    print(f"[DEBUG] All devices: {all_devices}")
    
    # Inline load phone mapping từ file để đảm bảo có mapping mới nhất
    try:
        import json
        import os
        PHONE_CONFIG_FILE = 'phone_mapping.json'
        if os.path.exists(PHONE_CONFIG_FILE):
            with open(PHONE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                file_map = data.get('phone_mapping', {})
                # Update PHONE_MAP với data từ file
                PHONE_MAP.update(file_map)
                print(f"[DEBUG] Loaded phone mapping from file: {file_map}")
        else:
            print(f"[DEBUG] Phone config file not found: {PHONE_CONFIG_FILE}")
    except Exception as e:
        print(f"[DEBUG] Error loading phone mapping: {e}")
    
    print(f"[DEBUG] Current PHONE_MAP after reload: {PHONE_MAP}")
    
    # Xác định nhóm và role trong nhóm
    if all_devices:
        # Chuẩn hóa all_devices để chỉ chứa IP không có port cho việc xác định role
        normalized_devices = []
        for device in all_devices:
            clean_ip = device.split(':')[0] if ':' in device else device
            normalized_devices.append(clean_ip)
        
        group_id, role_in_group = determine_group_and_role(ip, normalized_devices)
        print(f"📱 Device {ip} - Nhóm {group_id}, Role {role_in_group}")
        
        # Tìm partner trong cùng nhóm
        sorted_devices = sorted(normalized_devices)
        print(f"[DEBUG] Sorted devices: {sorted_devices}")
        
        try:
            device_index = sorted_devices.index(ip)
            print(f"[DEBUG] Device index: {device_index}")
        except ValueError:
            print(f"[DEBUG] IP {ip} not found in sorted_devices")
            target_phone = ""
            partner_ip = ""
            device_role = 1
            print(f"[DEBUG] Fallback: target_phone={target_phone}, partner_ip={partner_ip}")
            return "SUCCESS"
        
        if role_in_group == 1:
            partner_index = device_index + 1
        else:
            partner_index = device_index - 1
        
        print(f"[DEBUG] Partner index: {partner_index}")
        
        if 0 <= partner_index < len(sorted_devices):
            partner_ip = sorted_devices[partner_index]
            # Tìm target_phone trong PHONE_MAP với cả 2 format: có port và không có port
            partner_ip_with_port = f"{partner_ip}:5555"
            target_phone = PHONE_MAP.get(partner_ip_with_port, "") or PHONE_MAP.get(partner_ip, "")
            print(f"[DEBUG] Partner IP: {partner_ip}")
            print(f"[DEBUG] Trying PHONE_MAP keys: {partner_ip_with_port}, {partner_ip}")
            print(f"[DEBUG] Target phone from PHONE_MAP: {target_phone}")
            
            if not target_phone:
                print(f"[DEBUG] No phone mapping found for partner {partner_ip}")
                print(f"[DEBUG] Available PHONE_MAP keys: {list(PHONE_MAP.keys())}")
        else:
            target_phone = ""
            partner_ip = ""
            print(f"[DEBUG] Partner index {partner_index} out of range")
    else:
        # Fallback về logic cũ cho 2 máy
        device_role = 1 if ip == "192.168.5.74" else 2
        target_ip = "192.168.5.82" if ip == "192.168.5.74" else "192.168.5.74"
        target_ip_with_port = f"{target_ip}:5555"
        target_phone = PHONE_MAP.get(target_ip_with_port, "") or PHONE_MAP.get(target_ip, "")
        print(f"📱 Device role: Máy {device_role} (fallback mode)")
        print(f"[DEBUG] Fallback target_phone: {target_phone}")
    
    # Kiểm tra stop signal trước chuyển tab
    if stop_event and stop_event.is_set():
        print(f"[DEBUG] Stop signal received before switching to messages tab for {device_ip}")
        return "STOPPED"
    
    # Ép về tab Tin nhắn trước
    ensure_on_messages_tab(dev, debug=True)
    time.sleep(0.4)
    
    # Kiểm tra stop signal trước mở search
    if stop_event and stop_event.is_set():
        print(f"[DEBUG] Stop signal received before opening search for {device_ip}")
        return "STOPPED"
    
    print("• Mở ô tìm kiếm…")
    if not open_search_strong(dev, debug=True):
        print("❌ Không mở được ô tìm kiếm. Thử bấm thêm một lần nữa với key SEARCH…")
        dev.key(84)  # SEARCH key
        time.sleep(0.6)
        if not verify_search_opened(dev, debug=True):
            print("❌ Không mở được ô tìm kiếm. Thoát flow.")
            return "SUCCESS"
    
    # Kiểm tra stop signal trước nhập số
    if stop_event and stop_event.is_set():
        print(f"[DEBUG] Stop signal received before entering phone number for {device_ip}")
        return "STOPPED"
    
    # Nhập số điện thoại của partner để tìm kiếm
    if target_phone:
        print(f"• Nhập số đối tác: {target_phone}")
        enter_query_and_submit(dev, target_phone, debug=True)
    else:
        print("• Không có số trong map, nhập 'gxe'")
        enter_query_and_submit(dev, "gxe", debug=True)
    
    # Kiểm tra stop signal trước click search result
    if stop_event and stop_event.is_set():
        print(f"[DEBUG] Stop signal received before clicking search result for {device_ip}")
        return "STOPPED"
    
    print("• Chọn kết quả đầu tiên…")
    if click_first_search_result(dev, preferred_text=target_phone, debug=True):
        print("✅ Đã vào chat. Đợi 3 giây trước khi bắt đầu cuộc hội thoại...")
        
        # Kiểm tra stop signal trước delay
        if stop_event and stop_event.is_set():
            print(f"[DEBUG] Stop signal received before conversation delay for {device_ip}")
            return "STOPPED"
        
        time.sleep(3)
        
        # Kiểm tra stop signal trước bắt đầu conversation
        if stop_event and stop_event.is_set():
            print(f"[DEBUG] Stop signal received before starting conversation for {device_ip}")
            return "STOPPED"
        
        # Bắt đầu cuộc hội thoại với group support
        print("💬 Bắt đầu cuộc hội thoại tự động...")
        if all_devices:
            run_conversation(dev, role_in_group, debug=True, all_devices=all_devices, stop_event=stop_event, status_callback=status_callback)
        else:
            run_conversation(dev, device_role, debug=True, stop_event=stop_event, status_callback=status_callback)
    else:
        print("❌ Không thể vào chat")
    
    print("✅ Hoàn thành flow.")
    return "SUCCESS"
# === FLOW END ===

def run_automation_from_gui(selected_devices, conversation_text=None):
    """Function để chạy automation từ GUI
    
    Args:
        selected_devices: List các device IPs được chọn từ GUI
        conversation_text: Text hội thoại từ GUI (optional)
    
    Returns:
        dict: Kết quả automation cho từng device
    """
    print(f"\n🚀 Bắt đầu automation từ GUI với {len(selected_devices)} devices")
    print(f"📱 Devices: {selected_devices}")
    
    if conversation_text:
        print(f"💬 Conversation text: {conversation_text[:50]}...")
        # Update global conversation nếu có
        global CONVERSATION
        CONVERSATION = conversation_text.strip().split('\n')
    
    results = {}
    connected_devices = []
    
    # Kết nối tất cả devices
    for device_ip in selected_devices:
        try:
            print(f"\n🔌 Kết nối device: {device_ip}")
            dev = Device(device_ip)
            if dev.connect():
                connected_devices.append(dev)
                results[device_ip] = {"status": "connected", "result": None}
                print(f"✅ Kết nối thành công: {device_ip}")
            else:
                results[device_ip] = {"status": "connection_failed", "result": None}
                print(f"❌ Kết nối thất bại: {device_ip}")
        except Exception as e:
            results[device_ip] = {"status": "error", "result": str(e)}
            print(f"❌ Lỗi kết nối {device_ip}: {e}")
    
    if not connected_devices:
        print("❌ Không có device nào kết nối được")
        return results
    
    # Chạy automation trên tất cả devices đã kết nối
    device_ips = [dev.device_id for dev in connected_devices]
    print(f"\n🎯 Bắt đầu automation với {len(connected_devices)} devices")
    
    for dev in connected_devices:
        device_ip = dev.device_id
        try:
            print(f"\n📱 Chạy automation trên {device_ip}")
            result = flow(dev, all_devices=device_ips)
            results[device_ip]["result"] = result
            results[device_ip]["status"] = "completed"
            print(f"✅ Hoàn thành automation trên {device_ip}: {result}")
        except Exception as e:
            results[device_ip]["result"] = str(e)
            results[device_ip]["status"] = "error"
            print(f"❌ Lỗi automation trên {device_ip}: {e}")
    
    # Ngắt kết nối tất cả devices
    for dev in connected_devices:
        try:
            dev.disconnect()
        except:
            pass
    
    print(f"\n🏁 Hoàn thành automation từ GUI")
    return results

def get_available_devices_for_gui():
    """Function để lấy danh sách devices cho GUI
    
    Returns:
        list: Danh sách device IPs có sẵn
    """
    try:
        devices = get_all_connected_devices()
        device_ips = []
        for device_id in devices:
            # Normalize device ID (remove port if exists)
            ip = device_id.split(':')[0] if ':' in device_id else device_id
            if ip not in device_ips:
                device_ips.append(ip)
        return sorted(device_ips)
    except Exception as e:
        print(f"❌ Lỗi lấy danh sách devices: {e}")
        return []