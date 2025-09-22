import asyncio
from typing import List, Dict, Any, Optional, Callable
from .base_step import BaseStep


class StepManager:
    """Quản lý việc thực thi flow của các automation steps.
    
    StepManager chịu trách nhiệm:
    - Quản lý danh sách các steps
    - Thực thi tuần tự các steps
    - Xử lý lỗi và rollback
    - Theo dõi tiến trình
    """
    
    def __init__(self):
        """Initialize StepManager."""
        self.steps: List[BaseStep] = []
        self.current_step_index = 0
        self.is_running = False
        self.is_paused = False
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
    
    def add_step(self, step: BaseStep) -> None:
        """Thêm step vào flow.
        
        Args:
            step: BaseStep instance để thêm vào flow
        """
        if not isinstance(step, BaseStep):
            raise TypeError("Step phải là instance của BaseStep")
        
        self.steps.append(step)
    
    def add_steps(self, steps: List[BaseStep]) -> None:
        """Thêm nhiều steps vào flow.
        
        Args:
            steps: Danh sách các BaseStep instances
        """
        for step in steps:
            self.add_step(step)
    
    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """Đặt callback để theo dõi tiến trình.
        
        Args:
            callback: Function nhận (current_step, total_steps, step_name)
        """
        self.progress_callback = callback
    
    def reset(self) -> None:
        """Reset tất cả steps về trạng thái ban đầu."""
        for step in self.steps:
            step.reset()
        self.current_step_index = 0
        self.is_running = False
        self.is_paused = False
    
    def pause(self) -> None:
        """Tạm dừng execution."""
        self.is_paused = True
    
    def resume(self) -> None:
        """Tiếp tục execution sau khi pause."""
        self.is_paused = False
    
    def stop(self) -> None:
        """Dừng execution hoàn toàn."""
        self.is_running = False
        self.is_paused = False
    
    async def execute_flow(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi toàn bộ flow của các steps.
        
        Args:
            initial_context: Context ban đầu để bắt đầu flow
            
        Returns:
            Dict[str, Any]: Context cuối cùng sau khi thực thi tất cả steps
            
        Raises:
            Exception: Nếu có lỗi trong quá trình thực thi
        """
        if not self.steps:
            raise ValueError("Không có steps nào để thực thi")
        
        self.is_running = True
        context = initial_context.copy()
        
        try:
            for i, step in enumerate(self.steps):
                # Kiểm tra nếu bị dừng
                if not self.is_running:
                    break
                
                # Kiểm tra nếu bị pause
                while self.is_paused and self.is_running:
                    await asyncio.sleep(0.1)
                
                if not self.is_running:
                    break
                
                self.current_step_index = i
                
                # Gọi progress callback nếu có
                if self.progress_callback:
                    self.progress_callback(i + 1, len(self.steps), step.name)
                
                # Validate trước khi thực thi
                try:
                    is_valid = await step.validate(context)
                    if not is_valid:
                        error_msg = f"Validation failed for step: {step.name}"
                        step.mark_failed(error_msg)
                        raise ValueError(error_msg)
                except Exception as e:
                    error_msg = f"Validation error in step {step.name}: {str(e)}"
                    step.mark_failed(error_msg)
                    raise
                
                # Thực thi step
                try:
                    context = await step.execute(context)
                    step.mark_completed()
                except Exception as e:
                    error_msg = f"Execution error in step {step.name}: {str(e)}"
                    step.mark_failed(error_msg)
                    raise
            
            return context
            
        finally:
            self.is_running = False
    
    async def execute_step_by_index(self, index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Thực thi một step cụ thể theo index.
        
        Args:
            index: Index của step cần thực thi
            context: Context hiện tại
            
        Returns:
            Dict[str, Any]: Context sau khi thực thi step
            
        Raises:
            IndexError: Nếu index không hợp lệ
            Exception: Nếu có lỗi trong quá trình thực thi
        """
        if index < 0 or index >= len(self.steps):
            raise IndexError(f"Step index {index} không hợp lệ")
        
        step = self.steps[index]
        
        # Validate
        is_valid = await step.validate(context)
        if not is_valid:
            error_msg = f"Validation failed for step: {step.name}"
            step.mark_failed(error_msg)
            raise ValueError(error_msg)
        
        # Execute
        try:
            context = await step.execute(context)
            step.mark_completed()
            return context
        except Exception as e:
            error_msg = f"Execution error in step {step.name}: {str(e)}"
            step.mark_failed(error_msg)
            raise
    
    def get_step_status(self) -> List[Dict[str, Any]]:
        """Lấy trạng thái của tất cả steps.
        
        Returns:
            List[Dict[str, Any]]: Danh sách trạng thái của các steps
        """
        return [
            {
                'index': i,
                'name': step.name,
                'status': step.status,
                'error_message': step.error_message,
                'is_completed': step.is_completed
            }
            for i, step in enumerate(self.steps)
        ]
    
    def get_failed_steps(self) -> List[BaseStep]:
        """Lấy danh sách các steps bị lỗi.
        
        Returns:
            List[BaseStep]: Danh sách các steps có lỗi
        """
        return [step for step in self.steps if step.error_message]
    
    def get_completed_steps(self) -> List[BaseStep]:
        """Lấy danh sách các steps đã hoàn thành.
        
        Returns:
            List[BaseStep]: Danh sách các steps đã hoàn thành
        """
        return [step for step in self.steps if step.is_completed]
    
    @property
    def total_steps(self) -> int:
        """Tổng số steps trong flow."""
        return len(self.steps)
    
    @property
    def current_step(self) -> Optional[BaseStep]:
        """Step hiện tại đang được thực thi."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    @property
    def progress_percentage(self) -> float:
        """Phần trăm tiến trình hoàn thành."""
        if not self.steps:
            return 0.0
        
        completed_count = len(self.get_completed_steps())
        return (completed_count / len(self.steps)) * 100.0
    
    def __str__(self) -> str:
        """String representation của StepManager."""
        return f"StepManager({len(self.steps)} steps, {self.progress_percentage:.1f}% completed)"
    
    def __repr__(self) -> str:
        """Detailed string representation của StepManager."""
        return f"StepManager(steps={len(self.steps)}, current_index={self.current_step_index}, running={self.is_running})"