from typing import Dict, Any, Optional, List
import asyncio
import logging
from ..core.base_step import BaseStep
from ..models.conversation import Conversation
from ..models.summary import Summary

logger = logging.getLogger(__name__)

class MessagingHandler(BaseStep):
    """Handles message sending and conversation management."""
    
    def __init__(self, device_pair_id: str, conversation: Conversation):
        super().__init__()
        self.device_pair_id = device_pair_id
        self.conversation = conversation
        self.current_message_index = 0
        
        # Element IDs for messaging interface
        self.MESSAGE_INPUT_ID = "com.zing.zalo:id/message_input"
        self.SEND_BUTTON_ID = "com.zing.zalo:id/send_button"
        self.MESSAGE_LIST_ID = "com.zing.zalo:id/message_list"
        self.TYPING_INDICATOR_ID = "com.zing.zalo:id/typing_indicator"
        
        # Text patterns
        self.DELIVERED_TEXT = "Đã gửi"
        self.SEEN_TEXT = "Đã xem"
        self.TYPING_TEXT = "đang nhập..."
        
    async def validate(self) -> bool:
        """Validate that messaging interface is ready."""
        try:
            # Check if chat window is open
            if not await self._is_chat_window_open():
                logger.error("Chat window is not open")
                return False
                
            # Check if message input is available
            if not await self._is_message_input_available():
                logger.error("Message input field is not available")
                return False
                
            # Check if there are messages to send
            if not self.conversation.messages or self.current_message_index >= len(self.conversation.messages):
                logger.warning("No more messages to send")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
    
    async def execute(self) -> Dict[str, Any]:
        """Execute message sending process."""
        try:
            result = {
                "success": False,
                "messages_sent": 0,
                "current_index": self.current_message_index,
                "conversation_completed": False,
                "error": None
            }
            
            # Get current message to send
            current_message = self.conversation.messages[self.current_message_index]
            
            # Send the message
            send_success = await self._send_message(current_message["content"])
            if not send_success:
                result["error"] = "Failed to send message"
                return result
                
            # Wait for delivery confirmation
            await self._wait_for_delivery()
            
            # Update message status
            self.conversation.messages[self.current_message_index]["status"] = "sent"
            self.conversation.messages[self.current_message_index]["sent_at"] = asyncio.get_event_loop().time()
            
            # Check if we should wait for response
            if current_message.get("wait_for_response", False):
                response = await self._wait_for_response()
                if response:
                    # Add response to conversation
                    self.conversation.add_message({
                        "role": "user",
                        "content": response,
                        "timestamp": asyncio.get_event_loop().time(),
                        "status": "received"
                    })
            
            # Move to next message
            self.current_message_index += 1
            result["messages_sent"] = 1
            result["current_index"] = self.current_message_index
            
            # Check if conversation is completed
            if self.current_message_index >= len(self.conversation.messages):
                result["conversation_completed"] = True
                await self._finalize_conversation()
            
            result["success"] = True
            self.context.update(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Message sending failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages_sent": 0,
                "current_index": self.current_message_index
            }
    
    async def _is_chat_window_open(self) -> bool:
        """Check if chat window is currently open."""
        try:
            # Implementation would use device automation to check UI elements
            # This is a placeholder for the actual device interaction
            await asyncio.sleep(0.1)
            return True
        except Exception:
            return False
    
    async def _is_message_input_available(self) -> bool:
        """Check if message input field is available and enabled."""
        try:
            # Implementation would check for message input element
            await asyncio.sleep(0.1)
            return True
        except Exception:
            return False
    
    async def _send_message(self, message_content: str) -> bool:
        """Send a message through the chat interface."""
        try:
            logger.info(f"Sending message: {message_content[:50]}...")
            
            # Clear input field
            await self._clear_message_input()
            
            # Type message
            await self._type_message(message_content)
            
            # Send message
            await self._click_send_button()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def _clear_message_input(self) -> None:
        """Clear the message input field."""
        # Implementation would interact with device to clear input
        await asyncio.sleep(0.1)
    
    async def _type_message(self, content: str) -> None:
        """Type message content into input field."""
        # Implementation would use device automation to type text
        await asyncio.sleep(0.5)  # Simulate typing time
    
    async def _click_send_button(self) -> None:
        """Click the send button."""
        # Implementation would click send button
        await asyncio.sleep(0.2)
    
    async def _wait_for_delivery(self, timeout: float = 10.0) -> bool:
        """Wait for message delivery confirmation."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                # Check for delivery indicators
                if await self._check_delivery_status():
                    return True
                await asyncio.sleep(0.5)
            
            logger.warning("Message delivery timeout")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for delivery: {e}")
            return False
    
    async def _check_delivery_status(self) -> bool:
        """Check if message has been delivered."""
        # Implementation would check for delivery indicators in UI
        return True
    
    async def _wait_for_response(self, timeout: float = 30.0) -> Optional[str]:
        """Wait for user response to the message."""
        try:
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                # Check for typing indicator
                if await self._is_user_typing():
                    # Wait a bit more for complete response
                    await asyncio.sleep(2.0)
                
                # Check for new messages
                new_message = await self._get_latest_user_message()
                if new_message:
                    return new_message
                
                await asyncio.sleep(1.0)
            
            logger.info("No response received within timeout")
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for response: {e}")
            return None
    
    async def _is_user_typing(self) -> bool:
        """Check if user is currently typing."""
        # Implementation would check for typing indicator
        return False
    
    async def _get_latest_user_message(self) -> Optional[str]:
        """Get the latest message from user."""
        # Implementation would extract latest message from chat
        return None
    
    async def _finalize_conversation(self) -> None:
        """Finalize the conversation and create summary."""
        try:
            # Mark conversation as completed
            self.conversation.status = "completed"
            self.conversation.completed_at = asyncio.get_event_loop().time()
            
            # Create conversation summary
            summary = Summary(
                device_pair_id=self.device_pair_id,
                conversation_id=self.conversation.id,
                total_messages=len(self.conversation.messages),
                duration=self.conversation.completed_at - self.conversation.started_at,
                success_rate=self._calculate_success_rate(),
                notes=self._generate_summary_notes()
            )
            
            # Save summary (implementation would save to database)
            logger.info(f"Conversation completed. Summary: {summary.notes}")
            
        except Exception as e:
            logger.error(f"Error finalizing conversation: {e}")
    
    def _calculate_success_rate(self) -> float:
        """Calculate message success rate."""
        if not self.conversation.messages:
            return 0.0
        
        sent_messages = sum(1 for msg in self.conversation.messages 
                          if msg.get("status") == "sent")
        return sent_messages / len(self.conversation.messages)
    
    def _generate_summary_notes(self) -> str:
        """Generate summary notes for the conversation."""
        total_messages = len(self.conversation.messages)
        success_rate = self._calculate_success_rate()
        
        return f"Conversation completed with {total_messages} messages. Success rate: {success_rate:.1%}"
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        total_messages = len(self.conversation.messages)
        progress_percentage = (self.current_message_index / total_messages) * 100 if total_messages > 0 else 0
        
        return {
            "current_message": self.current_message_index,
            "total_messages": total_messages,
            "progress_percentage": progress_percentage,
            "conversation_id": self.conversation.id,
            "status": self.status
        }