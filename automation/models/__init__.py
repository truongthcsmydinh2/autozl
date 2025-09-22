"""Data models for the automation system

Provides data structures for device management, conversations, and reporting.
"""

from .device_pair import DevicePair, DeviceInfo, DeviceStatus, PairStatus
from .conversation import Conversation, Message, MessageRole, MessageStatus, ConversationStatus
from .summary import Summary, PerformanceMetrics, SummaryType, SummaryStatus

__all__ = [
    "DevicePair",
    "DeviceInfo",
    "DeviceStatus",
    "PairStatus",
    "Conversation",
    "Message",
    "MessageRole",
    "MessageStatus",
    "ConversationStatus",
    "Summary",
    "PerformanceMetrics",
    "SummaryType",
    "SummaryStatus",
]