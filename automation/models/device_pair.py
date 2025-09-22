from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

class DeviceStatus(Enum):
    """Device status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class PairStatus(Enum):
    """Device pair status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCING = "syncing"
    ERROR = "error"

@dataclass
class DeviceInfo:
    """Information about a single device."""
    device_id: str
    device_name: str
    device_type: str  # "android", "ios", etc.
    os_version: str
    app_version: str
    status: DeviceStatus = DeviceStatus.INACTIVE
    last_seen: float = field(default_factory=time.time)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_last_seen(self) -> None:
        """Update the last seen timestamp."""
        self.last_seen = time.time()
    
    def is_online(self, timeout: float = 300.0) -> bool:
        """Check if device is considered online based on last seen time."""
        return (time.time() - self.last_seen) < timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type,
            "os_version": self.os_version,
            "app_version": self.app_version,
            "status": self.status.value,
            "last_seen": self.last_seen,
            "capabilities": self.capabilities,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceInfo':
        """Create DeviceInfo from dictionary."""
        return cls(
            device_id=data["device_id"],
            device_name=data["device_name"],
            device_type=data["device_type"],
            os_version=data["os_version"],
            app_version=data["app_version"],
            status=DeviceStatus(data.get("status", DeviceStatus.INACTIVE.value)),
            last_seen=data.get("last_seen", time.time()),
            capabilities=data.get("capabilities", {}),
            metadata=data.get("metadata", {})
        )

@dataclass
class DevicePair:
    """Represents a pair of devices for automation."""
    pair_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_device: Optional[DeviceInfo] = None
    receiver_device: Optional[DeviceInfo] = None
    status: PairStatus = PairStatus.DISCONNECTED
    created_at: float = field(default_factory=time.time)
    last_sync: Optional[float] = None
    sync_interval: float = 60.0  # seconds
    configuration: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default statistics."""
        if not self.statistics:
            self.statistics = {
                "total_messages_sent": 0,
                "total_messages_received": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "last_operation_time": None,
                "uptime_seconds": 0
            }
    
    def set_sender_device(self, device: DeviceInfo) -> None:
        """Set the sender device."""
        self.sender_device = device
        self._update_pair_status()
    
    def set_receiver_device(self, device: DeviceInfo) -> None:
        """Set the receiver device."""
        self.receiver_device = device
        self._update_pair_status()
    
    def _update_pair_status(self) -> None:
        """Update pair status based on device states."""
        if not self.sender_device or not self.receiver_device:
            self.status = PairStatus.DISCONNECTED
            return
        
        if (self.sender_device.status == DeviceStatus.ACTIVE and 
            self.receiver_device.status == DeviceStatus.ACTIVE):
            if self.status != PairStatus.CONNECTED:
                self.status = PairStatus.CONNECTED
                self.last_sync = time.time()
        else:
            self.status = PairStatus.DISCONNECTED
    
    def is_ready_for_automation(self) -> bool:
        """Check if pair is ready for automation tasks."""
        return (
            self.status == PairStatus.CONNECTED and
            self.sender_device is not None and
            self.receiver_device is not None and
            self.sender_device.is_online() and
            self.receiver_device.is_online()
        )
    
    def needs_sync(self) -> bool:
        """Check if devices need synchronization."""
        if not self.last_sync:
            return True
        return (time.time() - self.last_sync) > self.sync_interval
    
    def update_sync(self) -> None:
        """Update last sync timestamp."""
        self.last_sync = time.time()
        if self.sender_device:
            self.sender_device.update_last_seen()
        if self.receiver_device:
            self.receiver_device.update_last_seen()
    
    def record_operation(self, success: bool, operation_type: str = "message") -> None:
        """Record an automation operation result."""
        self.statistics["last_operation_time"] = time.time()
        
        if success:
            self.statistics["successful_operations"] += 1
            if operation_type == "message_sent":
                self.statistics["total_messages_sent"] += 1
            elif operation_type == "message_received":
                self.statistics["total_messages_received"] += 1
        else:
            self.statistics["failed_operations"] += 1
    
    def get_success_rate(self) -> float:
        """Calculate operation success rate."""
        total_ops = self.statistics["successful_operations"] + self.statistics["failed_operations"]
        if total_ops == 0:
            return 0.0
        return self.statistics["successful_operations"] / total_ops
    
    def get_uptime(self) -> float:
        """Get pair uptime in seconds."""
        if self.status == PairStatus.CONNECTED and self.last_sync:
            return time.time() - self.created_at
        return self.statistics.get("uptime_seconds", 0)
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update pair configuration."""
        self.configuration.update(config)
        
        # Update sync interval if provided
        if "sync_interval" in config:
            self.sync_interval = config["sync_interval"]
    
    def get_device_by_id(self, device_id: str) -> Optional[DeviceInfo]:
        """Get device by ID."""
        if self.sender_device and self.sender_device.device_id == device_id:
            return self.sender_device
        if self.receiver_device and self.receiver_device.device_id == device_id:
            return self.receiver_device
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pair_id": self.pair_id,
            "sender_device": self.sender_device.to_dict() if self.sender_device else None,
            "receiver_device": self.receiver_device.to_dict() if self.receiver_device else None,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_sync": self.last_sync,
            "sync_interval": self.sync_interval,
            "configuration": self.configuration,
            "statistics": self.statistics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevicePair':
        """Create DevicePair from dictionary."""
        pair = cls(
            pair_id=data["pair_id"],
            status=PairStatus(data.get("status", PairStatus.DISCONNECTED.value)),
            created_at=data.get("created_at", time.time()),
            last_sync=data.get("last_sync"),
            sync_interval=data.get("sync_interval", 60.0),
            configuration=data.get("configuration", {}),
            statistics=data.get("statistics", {})
        )
        
        if data.get("sender_device"):
            pair.sender_device = DeviceInfo.from_dict(data["sender_device"])
        
        if data.get("receiver_device"):
            pair.receiver_device = DeviceInfo.from_dict(data["receiver_device"])
        
        return pair
    
    def __str__(self) -> str:
        """String representation of the device pair."""
        sender_name = self.sender_device.device_name if self.sender_device else "None"
        receiver_name = self.receiver_device.device_name if self.receiver_device else "None"
        return f"DevicePair({self.pair_id[:8]}): {sender_name} -> {receiver_name} [{self.status.value}]"
    
    def __repr__(self) -> str:
        """Detailed representation of the device pair."""
        return (f"DevicePair(pair_id='{self.pair_id}', "
                f"status={self.status.value}, "
                f"sender={self.sender_device.device_id if self.sender_device else None}, "
                f"receiver={self.receiver_device.device_id if self.receiver_device else None})")