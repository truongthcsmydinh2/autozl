from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid
import json

class MessageRole(Enum):
    """Message role enumeration."""
    ASSISTANT = "assistant"  # Messages sent by automation
    USER = "user"           # Messages received from user
    SYSTEM = "system"       # System messages

class MessageStatus(Enum):
    """Message status enumeration."""
    PENDING = "pending"     # Message queued for sending
    SENDING = "sending"     # Message being sent
    SENT = "sent"           # Message successfully sent
    DELIVERED = "delivered" # Message delivered to recipient
    SEEN = "seen"           # Message seen by recipient
    FAILED = "failed"       # Message failed to send
    RECEIVED = "received"   # Message received from user

class ConversationStatus(Enum):
    """Conversation status enumeration."""
    PENDING = "pending"     # Conversation not started
    ACTIVE = "active"       # Conversation in progress
    PAUSED = "paused"       # Conversation paused
    COMPLETED = "completed" # Conversation finished
    FAILED = "failed"       # Conversation failed
    CANCELLED = "cancelled" # Conversation cancelled

@dataclass
class Message:
    """Represents a single message in a conversation."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = MessageRole.ASSISTANT
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    status: MessageStatus = MessageStatus.PENDING
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing information
    sent_at: Optional[float] = None
    delivered_at: Optional[float] = None
    seen_at: Optional[float] = None
    
    # Response handling
    wait_for_response: bool = False
    response_timeout: float = 30.0
    expected_response_pattern: Optional[str] = None
    
    def mark_sent(self) -> None:
        """Mark message as sent."""
        self.status = MessageStatus.SENT
        self.sent_at = time.time()
    
    def mark_delivered(self) -> None:
        """Mark message as delivered."""
        self.status = MessageStatus.DELIVERED
        self.delivered_at = time.time()
    
    def mark_seen(self) -> None:
        """Mark message as seen."""
        self.status = MessageStatus.SEEN
        self.seen_at = time.time()
    
    def mark_failed(self, error: str = "") -> None:
        """Mark message as failed."""
        self.status = MessageStatus.FAILED
        if error:
            self.metadata["error"] = error
    
    def get_delivery_time(self) -> Optional[float]:
        """Get time taken for delivery."""
        if self.sent_at and self.delivered_at:
            return self.delivered_at - self.sent_at
        return None
    
    def is_expired(self) -> bool:
        """Check if message response timeout has expired."""
        if not self.wait_for_response or not self.sent_at:
            return False
        return (time.time() - self.sent_at) > self.response_timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message_id": self.message_id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "metadata": self.metadata,
            "sent_at": self.sent_at,
            "delivered_at": self.delivered_at,
            "seen_at": self.seen_at,
            "wait_for_response": self.wait_for_response,
            "response_timeout": self.response_timeout,
            "expected_response_pattern": self.expected_response_pattern
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create Message from dictionary."""
        return cls(
            message_id=data["message_id"],
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=data["timestamp"],
            status=MessageStatus(data["status"]),
            metadata=data.get("metadata", {}),
            sent_at=data.get("sent_at"),
            delivered_at=data.get("delivered_at"),
            seen_at=data.get("seen_at"),
            wait_for_response=data.get("wait_for_response", False),
            response_timeout=data.get("response_timeout", 30.0),
            expected_response_pattern=data.get("expected_response_pattern")
        )

@dataclass
class Conversation:
    """Represents a conversation between automation and user."""
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_pair_id: str = ""
    contact_name: str = ""
    contact_phone: Optional[str] = None
    
    # Conversation metadata
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Status and timing
    status: ConversationStatus = ConversationStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    last_activity: Optional[float] = None
    
    # Messages
    messages: List[Message] = field(default_factory=list)
    
    # Configuration
    auto_response_enabled: bool = True
    response_delay_min: float = 1.0
    response_delay_max: float = 3.0
    max_retries: int = 3
    
    # Statistics
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default statistics."""
        if not self.statistics:
            self.statistics = {
                "total_messages": 0,
                "messages_sent": 0,
                "messages_received": 0,
                "messages_failed": 0,
                "average_response_time": 0.0,
                "success_rate": 0.0
            }
    
    def start_conversation(self) -> None:
        """Start the conversation."""
        self.status = ConversationStatus.ACTIVE
        self.started_at = time.time()
        self.last_activity = self.started_at
    
    def complete_conversation(self) -> None:
        """Complete the conversation."""
        self.status = ConversationStatus.COMPLETED
        self.completed_at = time.time()
        self._update_statistics()
    
    def pause_conversation(self) -> None:
        """Pause the conversation."""
        self.status = ConversationStatus.PAUSED
    
    def resume_conversation(self) -> None:
        """Resume the conversation."""
        self.status = ConversationStatus.ACTIVE
        self.last_activity = time.time()
    
    def fail_conversation(self, error: str = "") -> None:
        """Mark conversation as failed."""
        self.status = ConversationStatus.FAILED
        if error:
            self.statistics["error"] = error
    
    def add_message(self, message_data: Dict[str, Any]) -> Message:
        """Add a new message to the conversation."""
        # Create message from data
        if isinstance(message_data, dict):
            message = Message(
                role=MessageRole(message_data.get("role", MessageRole.ASSISTANT.value)),
                content=message_data["content"],
                wait_for_response=message_data.get("wait_for_response", False),
                response_timeout=message_data.get("response_timeout", 30.0),
                expected_response_pattern=message_data.get("expected_response_pattern")
            )
        else:
            message = message_data
        
        self.messages.append(message)
        self.last_activity = time.time()
        self._update_message_statistics()
        
        return message
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID."""
        for message in self.messages:
            if message.message_id == message_id:
                return message
        return None
    
    def get_pending_messages(self) -> List[Message]:
        """Get all pending messages."""
        return [msg for msg in self.messages if msg.status == MessageStatus.PENDING]
    
    def get_failed_messages(self) -> List[Message]:
        """Get all failed messages."""
        return [msg for msg in self.messages if msg.status == MessageStatus.FAILED]
    
    def get_last_user_message(self) -> Optional[Message]:
        """Get the last message from user."""
        for message in reversed(self.messages):
            if message.role == MessageRole.USER:
                return message
        return None
    
    def get_conversation_duration(self) -> Optional[float]:
        """Get conversation duration in seconds."""
        if not self.started_at:
            return None
        
        end_time = self.completed_at or time.time()
        return end_time - self.started_at
    
    def is_waiting_for_response(self) -> bool:
        """Check if conversation is waiting for user response."""
        if not self.messages:
            return False
        
        last_message = self.messages[-1]
        return (last_message.role == MessageRole.ASSISTANT and 
                last_message.wait_for_response and 
                last_message.status in [MessageStatus.SENT, MessageStatus.DELIVERED, MessageStatus.SEEN] and
                not last_message.is_expired())
    
    def _update_message_statistics(self) -> None:
        """Update message statistics."""
        self.statistics["total_messages"] = len(self.messages)
        self.statistics["messages_sent"] = sum(1 for msg in self.messages 
                                             if msg.role == MessageRole.ASSISTANT and 
                                             msg.status in [MessageStatus.SENT, MessageStatus.DELIVERED, MessageStatus.SEEN])
        self.statistics["messages_received"] = sum(1 for msg in self.messages 
                                                 if msg.role == MessageRole.USER)
        self.statistics["messages_failed"] = sum(1 for msg in self.messages 
                                                if msg.status == MessageStatus.FAILED)
    
    def _update_statistics(self) -> None:
        """Update conversation statistics."""
        self._update_message_statistics()
        
        # Calculate success rate
        total_sent_attempts = self.statistics["messages_sent"] + self.statistics["messages_failed"]
        if total_sent_attempts > 0:
            self.statistics["success_rate"] = self.statistics["messages_sent"] / total_sent_attempts
        
        # Calculate average response time
        response_times = []
        for message in self.messages:
            if message.role == MessageRole.ASSISTANT and message.get_delivery_time():
                response_times.append(message.get_delivery_time())
        
        if response_times:
            self.statistics["average_response_time"] = sum(response_times) / len(response_times)
    
    def export_messages(self, format: str = "json") -> str:
        """Export messages in specified format."""
        if format == "json":
            return json.dumps([msg.to_dict() for msg in self.messages], indent=2)
        elif format == "text":
            lines = []
            for msg in self.messages:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg.timestamp))
                role = msg.role.value.upper()
                lines.append(f"[{timestamp}] {role}: {msg.content}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "conversation_id": self.conversation_id,
            "device_pair_id": self.device_pair_id,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "last_activity": self.last_activity,
            "messages": [msg.to_dict() for msg in self.messages],
            "auto_response_enabled": self.auto_response_enabled,
            "response_delay_min": self.response_delay_min,
            "response_delay_max": self.response_delay_max,
            "max_retries": self.max_retries,
            "statistics": self.statistics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create Conversation from dictionary."""
        conversation = cls(
            conversation_id=data["conversation_id"],
            device_pair_id=data["device_pair_id"],
            contact_name=data["contact_name"],
            contact_phone=data.get("contact_phone"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            status=ConversationStatus(data["status"]),
            created_at=data["created_at"],
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            last_activity=data.get("last_activity"),
            auto_response_enabled=data.get("auto_response_enabled", True),
            response_delay_min=data.get("response_delay_min", 1.0),
            response_delay_max=data.get("response_delay_max", 3.0),
            max_retries=data.get("max_retries", 3),
            statistics=data.get("statistics", {})
        )
        
        # Load messages
        for msg_data in data.get("messages", []):
            conversation.messages.append(Message.from_dict(msg_data))
        
        return conversation
    
    def __str__(self) -> str:
        """String representation of the conversation."""
        duration = self.get_conversation_duration()
        duration_str = f"{duration:.1f}s" if duration else "N/A"
        return f"Conversation({self.conversation_id[:8]}): {self.contact_name} [{self.status.value}] ({len(self.messages)} msgs, {duration_str})"
    
    def __repr__(self) -> str:
        """Detailed representation of the conversation."""
        return (f"Conversation(conversation_id='{self.conversation_id}', "
                f"contact='{self.contact_name}', "
                f"status={self.status.value}, "
                f"messages={len(self.messages)})")