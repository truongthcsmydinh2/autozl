from typing import Dict, Any, List, Optional
from ..core.base_step import BaseStep


class ChatWindowChecker(BaseStep):
    """Step kiểm tra và mở cửa sổ chat với contact trên Zalo.
    
    ChatWindowChecker sẽ:
    - Mở cửa sổ chat với contact cụ thể
    - Kiểm tra trạng thái cửa sổ chat
    - Xác minh đã vào đúng cuộc trò chuyện
    - Cập nhật context với thông tin chat window
    """
    
    def __init__(self):
        """Initialize ChatWindowChecker step."""
        super().__init__("Chat Window Checker")
        
        # Các element IDs cho cửa sổ chat
        self.chat_window_elements = [
            "com.zing.zalo:id/chat_input",
            "com.zing.zalo:id/message_input",
            "com.zing.zalo:id/et_message",
            "com.zing.zalo:id/edit_text_message",
            "com.zing.zalo:id/input_text",
            "com.zing.zalo:id/chat_edit_text"
        ]
        
        # Các element IDs cho nút gửi tin nhắn
        self.send_button_elements = [
            "com.zing.zalo:id/send_button",
            "com.zing.zalo:id/btn_send",
            "com.zing.zalo:id/send_message",
            "com.zing.zalo:id/iv_send",
            "com.zing.zalo:id/button_send"
        ]
        
        # Các element IDs cho danh sách tin nhắn
        self.message_list_elements = [
            "com.zing.zalo:id/message_list",
            "com.zing.zalo:id/chat_list",
            "com.zing.zalo:id/recycler_view_message",
            "com.zing.zalo:id/list_message",
            "com.zing.zalo:id/conversation_list"
        ]
        
        # Các element IDs cho header chat (tên người chat)
        self.chat_header_elements = [
            "com.zing.zalo:id/chat_title",
            "com.zing.zalo:id/contact_name",
            "com.zing.zalo:id/tv_name",
            "com.zing.zalo:id/title_text",
            "com.zing.zalo:id/toolbar_title"
        ]
        
        # Các element IDs cho nút back
        self.back_button_elements = [
            "com.zing.zalo:id/back_button",
            "com.zing.zalo:id/btn_back",
            "com.zing.zalo:id/iv_back",
            "com.zing.zalo:id/navigation_back"
        ]
        
        # Các text patterns cho cửa sổ chat
        self.chat_text_patterns = [
            "Nhập tin nhắn",
            "Type a message",
            "Gửi",
            "Send",
            "Đang soạn",
            "Typing"
        ]
    
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Kiểm tra điều kiện trước khi thực thi.
        
        Args:
            context: Context chứa thông tin thiết bị và contact
            
        Returns:
            bool: True nếu có thiết bị và target contact
        """
        device = context.get("device")
        is_logged_in = context.get("is_logged_in", False)
        target_contact = context.get("target_contact")
        
        if device is None or not is_logged_in or not target_contact:
            return False
        
        # Kiểm tra xem device có phương thức cần thiết không
        required_methods = ['exists', 'click', 'send_keys', 'scroll']
        for method in required_methods:
            if not hasattr(device, method):
                return False
        
        return True
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi mở cửa sổ chat.
        
        Args:
            context: Context hiện tại
            
        Returns:
            Dict[str, Any]: Context được cập nhật với thông tin chat window
        """
        device = context["device"]
        target_contact = context["target_contact"]
        
        try:
            # Mở cửa sổ chat với contact
            open_result = await self._open_chat_window(device, target_contact)
            if not open_result["success"]:
                raise Exception(f"Không thể mở cửa sổ chat: {open_result['error']}")
            
            # Xác minh đã vào đúng cửa sổ chat
            verification_result = await self._verify_chat_window(device, target_contact)
            
            # Lấy thông tin chi tiết về cửa sổ chat
            chat_info = await self._get_chat_window_info(device)
            
            # Cập nhật context
            context["in_chat_window"] = verification_result["verified"]
            context["chat_window_info"] = chat_info
            context["chat_open_result"] = open_result
            context["chat_verification"] = verification_result
            context["current_chat_contact"] = target_contact
            
            # Log thông tin
            if verification_result["verified"]:
                print(f"✓ Đã mở cửa sổ chat với: {target_contact}")
                print(f"  Method: {open_result['method']}")
                if chat_info["has_input"]:
                    print(f"  ✓ Tìm thấy input box")
                if chat_info["has_send_button"]:
                    print(f"  ✓ Tìm thấy nút gửi")
                if chat_info["message_count"] > 0:
                    print(f"  ✓ Có {chat_info['message_count']} tin nhắn trong lịch sử")
            else:
                print(f"✗ Không thể xác minh cửa sổ chat với: {target_contact}")
                print(f"  Error: {verification_result['error']}")
            
            return context
            
        except Exception as e:
            error_msg = f"Lỗi khi mở cửa sổ chat: {str(e)}"
            print(f"✗ {error_msg}")
            
            # Cập nhật context với thông tin lỗi
            context["in_chat_window"] = False
            context["chat_window_error"] = error_msg
            
            raise Exception(error_msg)
    
    async def _open_chat_window(self, device, contact_name: str) -> Dict[str, Any]:
        """Mở cửa sổ chat với contact.
        
        Args:
            device: Device instance
            contact_name: Tên contact
            
        Returns:
            Dict[str, Any]: Kết quả mở cửa sổ chat
        """
        result = {
            "success": False,
            "method": "",
            "error": "",
            "attempts": []
        }
        
        try:
            # Các phương pháp mở chat khác nhau
            open_methods = [
                "click_contact_from_search",
                "click_contact_from_list",
                "navigate_to_chat_tab"
            ]
            
            for method in open_methods:
                attempt_result = {"method": method, "success": False, "error": ""}
                
                try:
                    if method == "click_contact_from_search":
                        # Nếu đang ở kết quả tìm kiếm, click vào contact
                        if device.exists(textContains=contact_name):
                            device.click(textContains=contact_name)
                            import asyncio
                            await asyncio.sleep(3)  # Đợi load chat window
                            
                            if await self._is_in_chat_window(device):
                                attempt_result["success"] = True
                                result["success"] = True
                                result["method"] = method
                    
                    elif method == "click_contact_from_list":
                        # Tìm contact trong danh sách và click
                        if device.exists(text=contact_name):
                            device.click(text=contact_name)
                            import asyncio
                            await asyncio.sleep(3)
                            
                            if await self._is_in_chat_window(device):
                                attempt_result["success"] = True
                                result["success"] = True
                                result["method"] = method
                    
                    elif method == "navigate_to_chat_tab":
                        # Điều hướng đến tab chat và tìm conversation
                        chat_nav_result = await self._navigate_to_chat_tab(device)
                        if chat_nav_result["success"]:
                            # Tìm conversation với contact
                            conv_result = await self._find_conversation(device, contact_name)
                            if conv_result["found"]:
                                attempt_result["success"] = True
                                result["success"] = True
                                result["method"] = method
                
                except Exception as e:
                    attempt_result["error"] = str(e)
                
                result["attempts"].append(attempt_result)
                
                if result["success"]:
                    break
            
            if not result["success"]:
                result["error"] = "Không thể mở cửa sổ chat bằng bất kỳ phương pháp nào"
            
            return result
            
        except Exception as e:
            result["error"] = f"Lỗi khi mở chat: {str(e)}"
            return result
    
    async def _navigate_to_chat_tab(self, device) -> Dict[str, Any]:
        """Điều hướng đến tab chat.
        
        Args:
            device: Device instance
            
        Returns:
            Dict[str, Any]: Kết quả điều hướng
        """
        result = {"success": False, "error": ""}
        
        try:
            # Các element IDs cho tab chat
            chat_tab_elements = [
                "com.zing.zalo:id/tab_chat",
                "com.zing.zalo:id/navigation_chat",
                "com.zing.zalo:id/bottom_navigation_chat"
            ]
            
            for element_id in chat_tab_elements:
                if device.exists(resourceId=element_id):
                    device.click(resourceId=element_id)
                    import asyncio
                    await asyncio.sleep(2)
                    result["success"] = True
                    break
            
            if not result["success"]:
                # Thử bằng text
                if device.exists(text="Chat") or device.exists(text="Tin nhắn"):
                    text_element = "Chat" if device.exists(text="Chat") else "Tin nhắn"
                    device.click(text=text_element)
                    import asyncio
                    await asyncio.sleep(2)
                    result["success"] = True
            
            if not result["success"]:
                result["error"] = "Không tìm thấy tab chat"
            
            return result
            
        except Exception as e:
            result["error"] = f"Lỗi khi điều hướng đến tab chat: {str(e)}"
            return result
    
    async def _find_conversation(self, device, contact_name: str) -> Dict[str, Any]:
        """Tìm conversation với contact trong danh sách chat.
        
        Args:
            device: Device instance
            contact_name: Tên contact
            
        Returns:
            Dict[str, Any]: Kết quả tìm conversation
        """
        result = {"found": False, "error": ""}
        
        try:
            # Tìm conversation trong danh sách
            if device.exists(textContains=contact_name):
                device.click(textContains=contact_name)
                import asyncio
                await asyncio.sleep(3)
                
                if await self._is_in_chat_window(device):
                    result["found"] = True
                else:
                    result["error"] = "Click vào conversation nhưng không vào được chat window"
            else:
                result["error"] = f"Không tìm thấy conversation với {contact_name}"
            
            return result
            
        except Exception as e:
            result["error"] = f"Lỗi khi tìm conversation: {str(e)}"
            return result
    
    async def _is_in_chat_window(self, device) -> bool:
        """Kiểm tra xem có đang ở trong cửa sổ chat không.
        
        Args:
            device: Device instance
            
        Returns:
            bool: True nếu đang ở trong cửa sổ chat
        """
        try:
            # Kiểm tra các elements đặc trưng của chat window
            chat_indicators = [
                *self.chat_window_elements,
                *self.send_button_elements,
                *self.message_list_elements
            ]
            
            for element_id in chat_indicators:
                if device.exists(resourceId=element_id):
                    return True
            
            # Kiểm tra text patterns
            for text_pattern in self.chat_text_patterns:
                if device.exists(textContains=text_pattern):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _verify_chat_window(self, device, contact_name: str) -> Dict[str, Any]:
        """Xác minh đã vào đúng cửa sổ chat.
        
        Args:
            device: Device instance
            contact_name: Tên contact cần xác minh
            
        Returns:
            Dict[str, Any]: Kết quả xác minh
        """
        result = {
            "verified": False,
            "contact_match": False,
            "has_chat_elements": False,
            "error": ""
        }
        
        try:
            # Kiểm tra có elements chat không
            result["has_chat_elements"] = await self._is_in_chat_window(device)
            
            # Kiểm tra tên contact trong header
            contact_match = False
            for element_id in self.chat_header_elements:
                if device.exists(resourceId=element_id):
                    try:
                        header_element = device(resourceId=element_id)
                        header_text = header_element.get_text() if hasattr(header_element, 'get_text') else ""
                        if contact_name.lower() in header_text.lower():
                            contact_match = True
                            break
                    except Exception:
                        continue
            
            # Nếu không tìm thấy trong header, kiểm tra bằng cách khác
            if not contact_match:
                if device.exists(textContains=contact_name):
                    contact_match = True
            
            result["contact_match"] = contact_match
            result["verified"] = result["has_chat_elements"] and result["contact_match"]
            
            if not result["verified"]:
                if not result["has_chat_elements"]:
                    result["error"] = "Không tìm thấy elements chat window"
                elif not result["contact_match"]:
                    result["error"] = f"Không xác minh được đang chat với {contact_name}"
            
            return result
            
        except Exception as e:
            result["error"] = f"Lỗi khi xác minh chat window: {str(e)}"
            return result
    
    async def _get_chat_window_info(self, device) -> Dict[str, Any]:
        """Lấy thông tin chi tiết về cửa sổ chat.
        
        Args:
            device: Device instance
            
        Returns:
            Dict[str, Any]: Thông tin chi tiết chat window
        """
        info = {
            "has_input": False,
            "has_send_button": False,
            "has_message_list": False,
            "message_count": 0,
            "input_element_id": "",
            "send_button_id": "",
            "can_send_message": False
        }
        
        try:
            # Kiểm tra input box
            for element_id in self.chat_window_elements:
                if device.exists(resourceId=element_id):
                    info["has_input"] = True
                    info["input_element_id"] = element_id
                    break
            
            # Kiểm tra send button
            for element_id in self.send_button_elements:
                if device.exists(resourceId=element_id):
                    info["has_send_button"] = True
                    info["send_button_id"] = element_id
                    break
            
            # Kiểm tra message list
            for element_id in self.message_list_elements:
                if device.exists(resourceId=element_id):
                    info["has_message_list"] = True
                    break
            
            # Ước lượng số tin nhắn (đơn giản)
            try:
                if info["has_message_list"]:
                    # Đếm số elements có thể là tin nhắn
                    hierarchy = device.dump_hierarchy()
                    message_indicators = ['message', 'text', 'bubble']
                    lines = hierarchy.split('\n')
                    message_count = 0
                    for line in lines:
                        if any(indicator in line.lower() for indicator in message_indicators):
                            if 'text=' in line and len(line.strip()) > 30:
                                message_count += 1
                    info["message_count"] = min(message_count, 50)  # Giới hạn 50
            except Exception:
                pass
            
            # Xác định có thể gửi tin nhắn không
            info["can_send_message"] = info["has_input"] and info["has_send_button"]
            
            return info
            
        except Exception:
            return info
    
    async def close_chat_window(self, device) -> bool:
        """Đóng cửa sổ chat hiện tại.
        
        Args:
            device: Device instance
            
        Returns:
            bool: True nếu đóng thành công
        """
        try:
            # Tìm nút back
            for element_id in self.back_button_elements:
                if device.exists(resourceId=element_id):
                    device.click(resourceId=element_id)
                    import asyncio
                    await asyncio.sleep(2)
                    return True
            
            # Thử bấm back bằng key
            device.press("back")
            import asyncio
            await asyncio.sleep(2)
            return True
            
        except Exception:
            return False
    
    def get_chat_elements(self) -> List[str]:
        """Lấy danh sách các element IDs cho chat window.
        
        Returns:
            List[str]: Danh sách element IDs
        """
        return self.chat_window_elements.copy()
    
    def get_send_button_elements(self) -> List[str]:
        """Lấy danh sách các element IDs cho nút gửi.
        
        Returns:
            List[str]: Danh sách element IDs
        """
        return self.send_button_elements.copy()
    
    def add_chat_element(self, element_id: str) -> None:
        """Thêm element ID cho chat window.
        
        Args:
            element_id: Element ID cần thêm
        """
        if element_id not in self.chat_window_elements:
            self.chat_window_elements.append(element_id)
    
    def add_send_button_element(self, element_id: str) -> None:
        """Thêm element ID cho nút gửi.
        
        Args:
            element_id: Element ID cần thêm
        """
        if element_id not in self.send_button_elements:
            self.send_button_elements.append(element_id)