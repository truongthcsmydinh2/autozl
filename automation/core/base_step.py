from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseStep(ABC):
    """Base abstract class cho tất cả automation steps.
    
    Mỗi step phải implement execute() và validate() methods.
    """
    
    def __init__(self, name: str):
        """Initialize step với tên.
        
        Args:
            name: Tên của step
        """
        self.name = name
        self.is_completed = False
        self.error_message: Optional[str] = None
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi step và trả về context được cập nhật.
        
        Args:
            context: Dictionary chứa dữ liệu context hiện tại
            
        Returns:
            Dict[str, Any]: Context được cập nhật sau khi thực thi step
            
        Raises:
            Exception: Nếu có lỗi trong quá trình thực thi
        """
        pass
    
    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Kiểm tra điều kiện trước khi thực thi step.
        
        Args:
            context: Dictionary chứa dữ liệu context hiện tại
            
        Returns:
            bool: True nếu điều kiện hợp lệ, False nếu không
        """
        pass
    
    def mark_completed(self) -> None:
        """Đánh dấu step đã hoàn thành thành công."""
        self.is_completed = True
        self.error_message = None
    
    def mark_failed(self, error: str) -> None:
        """Đánh dấu step thất bại với thông báo lỗi.
        
        Args:
            error: Thông báo lỗi
        """
        self.is_completed = False
        self.error_message = error
    
    def reset(self) -> None:
        """Reset trạng thái của step về ban đầu."""
        self.is_completed = False
        self.error_message = None
    
    @property
    def status(self) -> str:
        """Trả về trạng thái hiện tại của step.
        
        Returns:
            str: 'completed', 'failed', hoặc 'pending'
        """
        if self.is_completed:
            return 'completed'
        elif self.error_message:
            return 'failed'
        else:
            return 'pending'
    
    def __str__(self) -> str:
        """String representation của step."""
        return f"Step({self.name}) - Status: {self.status}"
    
    def __repr__(self) -> str:
        """Detailed string representation của step."""
        return f"BaseStep(name='{self.name}', status='{self.status}', error='{self.error_message}')"