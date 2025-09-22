"""Zalo Automation System

A comprehensive automation framework for managing Zalo messaging across multiple devices.
Provides step-based execution flow with device management and conversation tracking.
"""

from .core.base_step import BaseStep, StepStatus
from .core.step_manager import StepManager, FlowStatus
from .steps.login_checker import LoginChecker
from .steps.friend_checker import FriendChecker
from .steps.chat_window_checker import ChatWindowChecker
from .steps.messaging_handler import MessagingHandler
from .models.device_pair import DevicePair, DeviceInfo, DeviceStatus, PairStatus
from .models.conversation import Conversation, Message, MessageRole, MessageStatus, ConversationStatus
from .models.summary import Summary, PerformanceMetrics, SummaryType, SummaryStatus
from .utils.device_utils import DeviceUtils, DeviceConnectionStatus

__version__ = "1.0.0"
__author__ = "Zalo Automation Team"

__all__ = [
    # Core classes
    "BaseStep",
    "StepStatus", 
    "StepManager",
    "FlowStatus",
    
    # Step implementations
    "LoginChecker",
    "FriendChecker", 
    "ChatWindowChecker",
    "MessagingHandler",
    
    # Models
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
    
    # Utilities
    "DeviceUtils",
    "DeviceConnectionStatus",
]