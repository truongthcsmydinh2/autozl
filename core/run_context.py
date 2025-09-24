from typing import Optional, Dict, Any
import threading
import logging
import uuid
from datetime import datetime

class RunContext:
    """Context cho mỗi automation run, chứa thông tin và state cần thiết"""
    
    def __init__(self, pair_id: str, run_id: Optional[str] = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.pair_id = pair_id
        self.cancel_event = threading.Event()
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "running"  # running, completed, cancelled, error
        self.error_message: Optional[str] = None
        
        # Logger riêng cho run này
        self.logger = logging.getLogger(f"automation.{self.run_id}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.run_id[:8]}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Metadata bổ sung
        self.metadata: Dict[str, Any] = {}
        
    def is_cancelled(self) -> bool:
        """Kiểm tra xem run có bị cancel không"""
        return self.cancel_event.is_set()
    
    def cancel(self, reason: str = "User cancelled"):
        """Cancel run này"""
        self.cancel_event.set()
        self.status = "cancelled"
        self.end_time = datetime.now()
        self.logger.info(f"Run cancelled: {reason}")
    
    def complete(self, success: bool = True, error_message: Optional[str] = None):
        """Đánh dấu run hoàn thành"""
        self.end_time = datetime.now()
        if success:
            self.status = "completed"
            self.logger.info("Run completed successfully")
        else:
            self.status = "error"
            self.error_message = error_message
            self.logger.error(f"Run failed: {error_message}")
    
    def log_info(self, message: str, **kwargs):
        """Log info với context"""
        self.logger.info(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error với context"""
        self.logger.error(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning với context"""
        self.logger.warning(message, extra=kwargs)
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata cho run"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata của run"""
        return self.metadata.get(key, default)
    
    def get_duration(self) -> Optional[float]:
        """Lấy thời gian chạy (seconds)"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        else:
            return (datetime.now() - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context thành dict để serialize"""
        return {
            "run_id": self.run_id,
            "pair_id": self.pair_id,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.get_duration(),
            "error_message": self.error_message,
            "metadata": self.metadata,
            "is_cancelled": self.is_cancelled()
        }
    
    def __str__(self) -> str:
        return f"RunContext(run_id={self.run_id[:8]}, pair_id={self.pair_id}, status={self.status})"
    
    def __repr__(self) -> str:
        return self.__str__()

# Context manager để tự động cleanup
class AutoRunContext(RunContext):
    """RunContext với auto cleanup khi exit"""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Có exception xảy ra
            self.complete(success=False, error_message=str(exc_val))
        elif not self.is_cancelled() and self.status == "running":
            # Hoàn thành bình thường
            self.complete(success=True)
        
        # Cleanup logger handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()