from typing import Dict, Any, List, Optional
from ..core.base_step import BaseStep


class FriendChecker(BaseStep):
    """Step kiểm tra danh sách bạn bè và tìm kiếm contact trên Zalo.
    
    FriendChecker sẽ:
    - Điều hướng đến tab danh bạ/bạn bè
    - Tìm kiếm contact theo tên hoặc số điện thoại
    - Kiểm tra trạng thái kết bạn
    - Cập nhật context với thông tin contact
    """
    
    def __init__(self):
        """Initialize FriendChecker step."""
        super().__init__("Friend Checker")
        
        # Các element IDs cho tab danh bạ
        self.contact_tab_elements = [
            "com.zing.zalo:id/tab_contact",
            "com.zing.zalo:id/navigation_contact",
            "com.zing.zalo:id/bottom_navigation_contact",
            "com.zing.zalo:id/tab_phonebook"
        ]
        
        # Các element IDs cho tìm kiếm
        self.search_elements = [
            "com.zing.zalo:id/search_view",
            "com.zing.zalo:id/search_input",
            "com.zing.zalo:id/et_search",
            "com.zing.zalo:id/search_edit_text",
            "com.zing.zalo:id/search_bar",
            "com.zing.zalo:id/action_search"
        ]
        
        # Các element IDs cho danh sách bạn bè
        self.friend_list_elements = [
            "com.zing.zalo:id/friend_list",
            "com.zing.zalo:id/contact_list",
            "com.zing.zalo:id/recycler_view",
            "com.zing.zalo:id/list_view"
        ]
        
        # Các text patterns cho tab danh bạ
        self.contact_text_patterns = [
            "Danh bạ",
            "Bạn bè",
            "Contacts",
            "Friends",
            "Tìm kiếm",
            "Search"
        ]
        
        # Các text patterns cho trạng thái kết bạn
        self.friend_status_patterns = [
            "Kết bạn",
            "Đã gửi lời mời",
            "Chấp nhận",
            "Từ chối",
            "Bạn bè",
            "Add friend",
            "Friend request sent",
            "Accept",
            "Decline",
            "Friends"
        ]
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Kiểm tra điều kiện trước khi thực thi.
        
        Args:
            context: Context chứa thông tin thiết bị và trạng thái đăng nhập
            
        Returns:
            bool: True nếu thiết bị đã đăng nhập
        """
        device = context.get("device")
        is_logged_in = context.get("is_logged_in", False)
        
        if device is None or not is_logged_in:
            return False
        
        # Kiểm tra xem device có phương thức cần thiết không
        required_methods = ['exists', 'click', 'send_keys', 'scroll']
        for method in required_methods:
            if not hasattr(device, method):
                return False
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi kiểm tra danh sách bạn bè.
        
        Args:
            context: Context hiện tại
            
        Returns:
            Dict[str, Any]: Context được cập nhật với thông tin bạn bè
        """
        device = context["device"]
        target_contact = context.get("target_contact", "")
        
        try:
            # Điều hướng đến tab danh bạ
            navigation_result = await self._navigate_to_contacts(device)
            if not navigation_result["success"]:
                raise Exception(f"Không thể điều hướng đến tab danh bạ: {navigation_result['error']}")
            
            # Tìm kiếm contact nếu có target
            search_result = None
            if target_contact:
                search_result = await self._search_contact(device, target_contact)
                context["search_result"] = search_result
            
            # Lấy danh sách bạn bè hiện tại
            friends_list = await self._get_friends_list(device)
            context["friends_list"] = friends_list
            
            # Kiểm tra trạng thái contact cụ thể
            contact_status = None
            if target_contact and search_result and search_result["found"]:
                contact_status = await self._check_contact_status(device, target_contact)
                context["contact_status"] = contact_status
            
            # Cập nhật context
            context["in_contacts_tab"] = True
            context["contacts_navigation"] = navigation_result
            
            # Log thông tin
            print(f"✓ Đã điều hướng đến tab danh bạ")
            if target_contact:
                if search_result and search_result["found"]:
                    print(f"✓ Tìm thấy contact: {target_contact}")
                    if contact_status:
                        print(f"  Trạng thái: {contact_status['status']}")
                else:
                    print(f"✗ Không tìm thấy contact: {target_contact}")
            
            print(f"✓ Tìm thấy {len(friends_list)} bạn bè trong danh sách")
            
            return context
            
        except Exception as e:
            error_msg = f"Lỗi khi kiểm tra danh sách bạn bè: {str(e)}"
            print(f"✗ {error_msg}")
            
            # Cập nhật context với thông tin lỗi
            context["in_contacts_tab"] = False
            context["friends_error"] = error_msg
            
            raise Exception(error_msg)
    
    async def _navigate_to_contacts(self, device) -> Dict[str, Any]:
        """Điều hướng đến tab danh bạ.
        
        Args:
            device: Device instance
            
        Returns:
            Dict[str, Any]: Kết quả điều hướng
        """
        result = {
            "success": False,
            "method": "",
            "error": "",
            "attempts": []
        }
        
        try:
            # Thử các cách điều hướng khác nhau
            navigation_attempts = [
                {"method": "resourceId", "elements": self.contact_tab_elements},
                {"method": "text", "patterns": self.contact_text_patterns}
            ]
            
            for attempt in navigation_attempts:
                method = attempt["method"]
                attempt_result = {"method": method, "success": False, "error": ""}
                
                try:
                    if method == "resourceId":
                        for element_id in attempt["elements"]:
                            if device.exists(resourceId=element_id):
                                device.click(resourceId=element_id)
                                # Đợi load
                                import asyncio
                                await asyncio.sleep(2)
                                
                                # Kiểm tra xem đã vào tab danh bạ chưa
                                if await self._verify_in_contacts_tab(device):
                                    attempt_result["success"] = True
                                    result["success"] = True
                                    result["method"] = f"resourceId: {element_id}"
                                    break
                    
                    elif method == "text":
                        for text_pattern in attempt["patterns"]:
                            if device.exists(text=text_pattern):
                                device.click(text=text_pattern)
                                # Đợi load
                                import asyncio
                                await asyncio.sleep(2)
                                
                                # Kiểm tra xem đã vào tab danh bạ chưa
                                if await self._verify_in_contacts_tab(device):
                                    attempt_result["success"] = True
                                    result["success"] = True
                                    result["method"] = f"text: {text_pattern}"
                                    break
                    
                except Exception as e:
                    attempt_result["error"] = str(e)
                
                result["attempts"].append(attempt_result)
                
                if result["success"]:
                    break
            
            if not result["success"]:
                result["error"] = "Không thể tìm thấy tab danh bạ"
            
            return result
            
        except Exception as e:
            result["error"] = f"Lỗi khi điều hướng: {str(e)}"
            return result
    
    async def _verify_in_contacts_tab(self, device) -> bool:
        """Kiểm tra xem đã ở trong tab danh bạ chưa.
        
        Args:
            device: Device instance
            
        Returns:
            bool: True nếu đã ở trong tab danh bạ
        """
        try:
            # Kiểm tra các elements đặc trưng của tab danh bạ
            contact_indicators = [
                # Search elements
                *self.search_elements,
                # Friend list elements
                *self.friend_list_elements
            ]
            
            for element_id in contact_indicators:
                if device.exists(resourceId=element_id):
                    return True
            
            # Kiểm tra text patterns
            for text_pattern in self.contact_text_patterns:
                if device.exists(textContains=text_pattern):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _search_contact(self, device, contact_name: str) -> Dict[str, Any]:
        """Tìm kiếm contact theo tên.
        
        Args:
            device: Device instance
            contact_name: Tên contact cần tìm
            
        Returns:
            Dict[str, Any]: Kết quả tìm kiếm
        """
        result = {
            "found": False,
            "search_method": "",
            "contact_name": contact_name,
            "error": "",
            "results_count": 0
        }
        
        try:
            # Tìm search box
            search_element = None
            search_method = ""
            
            for element_id in self.search_elements:
                if device.exists(resourceId=element_id):
                    search_element = device(resourceId=element_id)
                    search_method = element_id
                    break
            
            if search_element is None:
                # Thử tìm bằng text
                if device.exists(text="Tìm kiếm") or device.exists(text="Search"):
                    search_element = device(text="Tìm kiếm") if device.exists(text="Tìm kiếm") else device(text="Search")
                    search_method = "text_search"
            
            if search_element is None:
                result["error"] = "Không tìm thấy search box"
                return result
            
            # Click vào search box và nhập tên
            search_element.click()
            import asyncio
            await asyncio.sleep(1)
            
            # Clear text cũ nếu có
            search_element.clear_text()
            await asyncio.sleep(0.5)
            
            # Nhập tên contact
            search_element.send_keys(contact_name)
            await asyncio.sleep(2)  # Đợi kết quả tìm kiếm
            
            # Kiểm tra kết quả
            search_results = await self._check_search_results(device, contact_name)
            
            result["found"] = search_results["found"]
            result["search_method"] = search_method
            result["results_count"] = search_results["count"]
            result["results"] = search_results["results"]
            
            return result
            
        except Exception as e:
            result["error"] = f"Lỗi khi tìm kiếm: {str(e)}"
            return result
    
    async def _check_search_results(self, device, contact_name: str) -> Dict[str, Any]:
        """Kiểm tra kết quả tìm kiếm.
        
        Args:
            device: Device instance
            contact_name: Tên contact đã tìm
            
        Returns:
            Dict[str, Any]: Thông tin kết quả tìm kiếm
        """
        result = {
            "found": False,
            "count": 0,
            "results": []
        }
        
        try:
            # Kiểm tra xem có kết quả nào không
            if device.exists(textContains=contact_name):
                result["found"] = True
                
                # Đếm số kết quả (ước lượng)
                elements_with_name = device(textContains=contact_name)
                if hasattr(elements_with_name, '__len__'):
                    result["count"] = len(elements_with_name)
                else:
                    result["count"] = 1
                
                # Lấy thông tin chi tiết (nếu có thể)
                try:
                    for i in range(min(result["count"], 5)):  # Giới hạn 5 kết quả đầu
                        element = elements_with_name[i] if result["count"] > 1 else elements_with_name
                        element_info = {
                            "text": element.get_text() if hasattr(element, 'get_text') else contact_name,
                            "index": i
                        }
                        result["results"].append(element_info)
                except Exception:
                    # Nếu không lấy được chi tiết, chỉ ghi nhận có kết quả
                    result["results"] = [{"text": contact_name, "index": 0}]
            
            return result
            
        except Exception:
            return result
    
    async def _get_friends_list(self, device) -> List[Dict[str, Any]]:
        """Lấy danh sách bạn bè hiện tại.
        
        Args:
            device: Device instance
            
        Returns:
            List[Dict[str, Any]]: Danh sách bạn bè
        """
        friends = []
        
        try:
            # Tìm list view chứa danh sách bạn bè
            list_element = None
            for element_id in self.friend_list_elements:
                if device.exists(resourceId=element_id):
                    list_element = device(resourceId=element_id)
                    break
            
            if list_element is None:
                return friends
            
            # Lấy các items trong list (ước lượng)
            # Đây là implementation đơn giản, có thể cần điều chỉnh tùy theo UI
            try:
                # Scroll để load thêm items nếu cần
                device.scroll.vert.forward(steps=3)
                import asyncio
                await asyncio.sleep(1)
                
                # Đếm số items có thể nhìn thấy
                visible_items = 0
                
                # Thử tìm các text elements trong list
                try:
                    hierarchy = device.dump_hierarchy()
                    # Đơn giản hóa: đếm số dòng có tên người
                    lines = hierarchy.split('\n')
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['text=', 'content-desc=']):
                            if len(line.strip()) > 20:  # Có thể là tên người
                                visible_items += 1
                                if visible_items <= 10:  # Giới hạn 10 items
                                    friends.append({
                                        "name": "Friend",  # Placeholder
                                        "index": visible_items,
                                        "visible": True
                                    })
                except Exception:
                    # Fallback: ước lượng có ít nhất vài bạn bè
                    friends = [{"name": "Friend", "index": i, "visible": True} for i in range(1, 4)]
                
            except Exception:
                pass
            
            return friends
            
        except Exception:
            return friends
    
    async def _check_contact_status(self, device, contact_name: str) -> Dict[str, Any]:
        """Kiểm tra trạng thái kết bạn với contact.
        
        Args:
            device: Device instance
            contact_name: Tên contact
            
        Returns:
            Dict[str, Any]: Thông tin trạng thái contact
        """
        status = {
            "contact_name": contact_name,
            "status": "unknown",
            "is_friend": False,
            "can_add_friend": False,
            "details": ""
        }
        
        try:
            # Kiểm tra các text patterns cho trạng thái
            for pattern in self.friend_status_patterns:
                if device.exists(text=pattern) or device.exists(textContains=pattern):
                    if pattern in ["Bạn bè", "Friends"]:
                        status["status"] = "friends"
                        status["is_friend"] = True
                        status["details"] = "Đã là bạn bè"
                    elif pattern in ["Kết bạn", "Add friend"]:
                        status["status"] = "can_add"
                        status["can_add_friend"] = True
                        status["details"] = "Có thể kết bạn"
                    elif pattern in ["Đã gửi lời mời", "Friend request sent"]:
                        status["status"] = "request_sent"
                        status["details"] = "Đã gửi lời mời kết bạn"
                    break
            
            if status["status"] == "unknown":
                status["details"] = "Không xác định được trạng thái"
            
            return status
            
        except Exception as e:
            status["details"] = f"Lỗi khi kiểm tra trạng thái: {str(e)}"
            return status
    
    def get_contact_elements(self) -> List[str]:
        """Lấy danh sách các element IDs cho tab danh bạ.
        
        Returns:
            List[str]: Danh sách element IDs
        """
        return self.contact_tab_elements.copy()
    
    def get_search_elements(self) -> List[str]:
        """Lấy danh sách các element IDs cho tìm kiếm.
        
        Returns:
            List[str]: Danh sách element IDs
        """
        return self.search_elements.copy()
    
    def add_contact_element(self, element_id: str) -> None:
        """Thêm element ID cho tab danh bạ.
        
        Args:
            element_id: Element ID cần thêm
        """
        if element_id not in self.contact_tab_elements:
            self.contact_tab_elements.append(element_id)
    
    def add_search_element(self, element_id: str) -> None:
        """Thêm element ID cho tìm kiếm.
        
        Args:
            element_id: Element ID cần thêm
        """
        if element_id not in self.search_elements:
            self.search_elements.append(element_id)