from typing import Dict, Any, List
from ..core.base_step import BaseStep


class LoginChecker(BaseStep):
    """Step kiểm tra trạng thái đăng nhập Zalo trên thiết bị.
    
    LoginChecker sẽ:
    - Kiểm tra xem thiết bị đã đăng nhập Zalo chưa
    - Phát hiện các màn hình đăng nhập
    - Cập nhật context với thông tin trạng thái đăng nhập
    """
    
    def __init__(self):
        """Initialize LoginChecker step."""
        super().__init__("Login Checker")
        
        # Các element IDs liên quan đến đăng nhập
        self.login_elements = [
            "com.zing.zalo:id/login_button",
            "com.zing.zalo:id/phone_input",
            "com.zing.zalo:id/password_input",
            "com.zing.zalo:id/btn_login",
            "com.zing.zalo:id/et_phone",
            "com.zing.zalo:id/et_password",
            "com.zing.zalo:id/tv_login",
            "com.zing.zalo:id/btn_register"
        ]
        
        # Các text patterns cho màn hình đăng nhập
        self.login_text_patterns = [
            "Đăng nhập",
            "Số điện thoại",
            "Mật khẩu",
            "Đăng ký",
            "Quên mật khẩu",
            "Login",
            "Phone number",
            "Password"
        ]
        
        # Các element IDs cho màn hình chính (đã đăng nhập)
        self.main_screen_elements = [
            "com.zing.zalo:id/tab_chat",
            "com.zing.zalo:id/tab_contact",
            "com.zing.zalo:id/tab_timeline",
            "com.zing.zalo:id/tab_me",
            "com.zing.zalo:id/bottom_navigation",
            "com.zing.zalo:id/navigation_chat",
            "com.zing.zalo:id/navigation_contact"
        ]
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Kiểm tra điều kiện trước khi thực thi.
        
        Args:
            context: Context chứa thông tin thiết bị
            
        Returns:
            bool: True nếu có thiết bị trong context
        """
        device = context.get("device")
        if device is None:
            return False
        
        # Kiểm tra xem device có phương thức cần thiết không
        required_methods = ['exists', 'dump_hierarchy', 'app_current']
        for method in required_methods:
            if not hasattr(device, method):
                return False
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi kiểm tra trạng thái đăng nhập.
        
        Args:
            context: Context hiện tại
            
        Returns:
            Dict[str, Any]: Context được cập nhật với thông tin đăng nhập
        """
        device = context["device"]
        
        try:
            # Kiểm tra app hiện tại
            current_app = await self._get_current_app(device)
            context["current_app"] = current_app
            
            # Nếu không phải Zalo app, cần mở Zalo
            if not self._is_zalo_app(current_app):
                await self._open_zalo_app(device)
                # Đợi app load
                import asyncio
                await asyncio.sleep(3)
            
            # Kiểm tra trạng thái đăng nhập
            login_status = await self._check_login_status(device)
            
            # Cập nhật context
            context["is_logged_in"] = login_status["is_logged_in"]
            context["login_status"] = login_status["status"]
            context["login_details"] = login_status["details"]
            context["screen_type"] = login_status["screen_type"]
            
            # Log thông tin
            if login_status["is_logged_in"]:
                print(f"✓ Thiết bị đã đăng nhập Zalo - Screen: {login_status['screen_type']}")
            else:
                print(f"✗ Thiết bị chưa đăng nhập Zalo - Screen: {login_status['screen_type']}")
                print(f"  Details: {login_status['details']}")
            
            return context
            
        except Exception as e:
            error_msg = f"Lỗi khi kiểm tra trạng thái đăng nhập: {str(e)}"
            print(f"✗ {error_msg}")
            
            # Cập nhật context với thông tin lỗi
            context["is_logged_in"] = False
            context["login_status"] = "error"
            context["login_details"] = error_msg
            context["screen_type"] = "unknown"
            
            raise Exception(error_msg)
    
    async def _get_current_app(self, device) -> str:
        """Lấy thông tin app hiện tại.
        
        Args:
            device: Device instance
            
        Returns:
            str: Package name của app hiện tại
        """
        try:
            current_app = device.app_current()
            return current_app.get('package', '') if current_app else ''
        except Exception:
            return ''
    
    def _is_zalo_app(self, package_name: str) -> bool:
        """Kiểm tra xem có phải Zalo app không.
        
        Args:
            package_name: Package name của app
            
        Returns:
            bool: True nếu là Zalo app
        """
        zalo_packages = [
            'com.zing.zalo',
            'com.vng.zalo'
        ]
        return package_name in zalo_packages
    
    async def _open_zalo_app(self, device) -> None:
        """Mở Zalo app.
        
        Args:
            device: Device instance
        """
        try:
            # Thử mở Zalo bằng package name
            device.app_start('com.zing.zalo')
        except Exception:
            try:
                # Thử package name khác
                device.app_start('com.vng.zalo')
            except Exception:
                # Thử mở bằng cách khác
                device.shell('am start -n com.zing.zalo/.ui.MainActivity')
    
    async def _check_login_status(self, device) -> Dict[str, Any]:
        """Kiểm tra trạng thái đăng nhập chi tiết.
        
        Args:
            device: Device instance
            
        Returns:
            Dict[str, Any]: Thông tin chi tiết về trạng thái đăng nhập
        """
        result = {
            "is_logged_in": False,
            "status": "unknown",
            "details": "",
            "screen_type": "unknown",
            "found_elements": []
        }
        
        try:
            # Kiểm tra các elements đăng nhập
            login_elements_found = []
            for element_id in self.login_elements:
                if device.exists(resourceId=element_id):
                    login_elements_found.append(element_id)
            
            # Kiểm tra các elements màn hình chính
            main_elements_found = []
            for element_id in self.main_screen_elements:
                if device.exists(resourceId=element_id):
                    main_elements_found.append(element_id)
            
            # Kiểm tra text patterns
            login_texts_found = []
            for text_pattern in self.login_text_patterns:
                if device.exists(text=text_pattern) or device.exists(textContains=text_pattern):
                    login_texts_found.append(text_pattern)
            
            result["found_elements"] = {
                "login_elements": login_elements_found,
                "main_elements": main_elements_found,
                "login_texts": login_texts_found
            }
            
            # Phân tích kết quả
            if main_elements_found:
                # Có elements của màn hình chính -> đã đăng nhập
                result["is_logged_in"] = True
                result["status"] = "logged_in"
                result["screen_type"] = "main_screen"
                result["details"] = f"Tìm thấy {len(main_elements_found)} elements màn hình chính"
                
            elif login_elements_found or login_texts_found:
                # Có elements đăng nhập -> chưa đăng nhập
                result["is_logged_in"] = False
                result["status"] = "need_login"
                result["screen_type"] = "login_screen"
                result["details"] = f"Tìm thấy {len(login_elements_found)} login elements, {len(login_texts_found)} login texts"
                
            else:
                # Không tìm thấy elements nào -> không xác định
                result["is_logged_in"] = False
                result["status"] = "unknown_screen"
                result["screen_type"] = "unknown"
                result["details"] = "Không tìm thấy elements đặc trưng nào"
                
                # Thử dump hierarchy để phân tích thêm
                try:
                    hierarchy = device.dump_hierarchy()
                    if "zalo" in hierarchy.lower():
                        result["details"] += " (Phát hiện Zalo trong hierarchy)"
                except Exception:
                    pass
            
            return result
            
        except Exception as e:
            result["status"] = "error"
            result["details"] = f"Lỗi khi kiểm tra: {str(e)}"
            return result
    
    def get_login_elements(self) -> List[str]:
        """Lấy danh sách các element IDs cho đăng nhập.
        
        Returns:
            List[str]: Danh sách element IDs
        """
        return self.login_elements.copy()
    
    def get_main_screen_elements(self) -> List[str]:
        """Lấy danh sách các element IDs cho màn hình chính.
        
        Returns:
            List[str]: Danh sách element IDs
        """
        return self.main_screen_elements.copy()
    
    def add_login_element(self, element_id: str) -> None:
        """Thêm element ID cho đăng nhập.
        
        Args:
            element_id: Element ID cần thêm
        """
        if element_id not in self.login_elements:
            self.login_elements.append(element_id)
    
    def add_main_screen_element(self, element_id: str) -> None:
        """Thêm element ID cho màn hình chính.
        
        Args:
            element_id: Element ID cần thêm
        """
        if element_id not in self.main_screen_elements:
            self.main_screen_elements.append(element_id)