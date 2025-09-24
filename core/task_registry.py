#!/usr/bin/env python3
"""
Task Registry for Automation Job Management

Quản lý các job automation đang chạy với cancel_event mechanism
Theo task T3 trong task.md
"""

import threading
import time
import uuid
from typing import Dict, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class JobInfo:
    """Thông tin về một job automation"""
    job_id: str
    run_id: str
    pair_id: str
    device_a: str
    device_b: str
    status: str = 'pending'  # pending, running, completed, failed, cancelled
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    cancel_event: threading.Event = field(default_factory=threading.Event)
    thread: Optional[threading.Thread] = None
    progress: int = 0
    message: str = ''
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.now()

class TaskRegistry:
    """Registry để quản lý tất cả automation jobs"""
    
    def __init__(self):
        self._jobs: Dict[str, JobInfo] = {}
        self._pair_jobs: Dict[str, str] = {}  # pair_id -> job_id mapping
        self._lock = threading.RLock()
        self._cleanup_interval = 300  # 5 minutes
        self._cleanup_thread = None
        self._shutdown_event = threading.Event()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while not self._shutdown_event.wait(self._cleanup_interval):
                try:
                    self._cleanup_completed_jobs()
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
        
        self._cleanup_thread = threading.Thread(
            target=cleanup_worker,
            name="TaskRegistry-Cleanup",
            daemon=True
        )
        self._cleanup_thread.start()
        logger.info("Task registry cleanup thread started")
    
    def create_job(self, run_id: str, pair_id: str, device_a: str, device_b: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Tạo job mới
        
        Args:
            run_id: ID của run session
            pair_id: ID của device pair
            device_a: Device A identifier
            device_b: Device B identifier
            metadata: Additional metadata
            
        Returns:
            job_id: ID của job được tạo
            
        Raises:
            ValueError: Nếu pair_id đã có job đang chạy
        """
        with self._lock:
            # Check if pair is already running
            if pair_id in self._pair_jobs:
                existing_job_id = self._pair_jobs[pair_id]
                existing_job = self._jobs.get(existing_job_id)
                if existing_job and existing_job.status in ['pending', 'running']:
                    raise ValueError(f"Pair {pair_id} is already running (job: {existing_job_id})")
            
            # Create new job
            job_id = str(uuid.uuid4())
            job_info = JobInfo(
                job_id=job_id,
                run_id=run_id,
                pair_id=pair_id,
                device_a=device_a,
                device_b=device_b,
                metadata=metadata or {}
            )
            
            self._jobs[job_id] = job_info
            self._pair_jobs[pair_id] = job_id
            
            logger.info(f"Created job {job_id} for pair {pair_id}")
            return job_id
    
    def start_job(self, job_id: str, target_func: Callable, *args, **kwargs) -> bool:
        """Bắt đầu job với target function
        
        Args:
            job_id: ID của job
            target_func: Function để chạy
            *args, **kwargs: Arguments cho target function
            
        Returns:
            bool: True nếu start thành công
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            if job.status != 'pending':
                logger.error(f"Job {job_id} is not in pending status: {job.status}")
                return False
            
            # Wrapper function để update job status
            def job_wrapper():
                try:
                    job.status = 'running'
                    job.started_at = datetime.now()
                    logger.info(f"Job {job_id} started")
                    
                    # Call target function với cancel_event
                    result = target_func(job.cancel_event, *args, **kwargs)
                    
                    if job.cancel_event.is_set():
                        job.status = 'cancelled'
                        job.message = 'Cancelled by user'
                        logger.info(f"Job {job_id} cancelled")
                    else:
                        job.status = 'completed'
                        job.message = 'Completed successfully'
                        logger.info(f"Job {job_id} completed")
                    
                    return result
                    
                except Exception as e:
                    job.status = 'failed'
                    job.message = f'Failed: {str(e)}'
                    logger.error(f"Job {job_id} failed: {e}")
                    raise
                finally:
                    job.stopped_at = datetime.now()
            
            # Start thread
            thread = threading.Thread(
                target=job_wrapper,
                name=f"Job-{job_id[:8]}",
                daemon=False
            )
            job.thread = thread
            thread.start()
            
            logger.info(f"Job {job_id} thread started")
            return True
    
    def cancel_job(self, job_id: str, timeout: float = 5.0) -> bool:
        """Cancel job
        
        Args:
            job_id: ID của job
            timeout: Timeout để đợi job dừng
            
        Returns:
            bool: True nếu cancel thành công
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False
            
            if job.status not in ['pending', 'running']:
                logger.info(f"Job {job_id} is not running: {job.status}")
                return True
            
            logger.info(f"Cancelling job {job_id}")
            
            # Set cancel event
            job.cancel_event.set()
            
            # Wait for thread to finish
            if job.thread and job.thread.is_alive():
                job.thread.join(timeout=timeout)
                
                if job.thread.is_alive():
                    logger.warning(f"Job {job_id} thread did not stop within {timeout}s")
                    return False
            
            job.status = 'cancelled'
            job.stopped_at = datetime.now()
            logger.info(f"Job {job_id} cancelled successfully")
            return True
    
    def cancel_pair(self, pair_id: str, timeout: float = 5.0) -> bool:
        """Cancel job cho specific pair
        
        Args:
            pair_id: ID của pair
            timeout: Timeout để đợi job dừng
            
        Returns:
            bool: True nếu cancel thành công
        """
        with self._lock:
            job_id = self._pair_jobs.get(pair_id)
            if not job_id:
                logger.info(f"No running job found for pair {pair_id}")
                return True
            
            return self.cancel_job(job_id, timeout)
    
    def cancel_all_jobs(self, timeout: float = 10.0) -> Dict[str, bool]:
        """Cancel tất cả jobs đang chạy
        
        Args:
            timeout: Total timeout để đợi tất cả jobs dừng
            
        Returns:
            Dict[str, bool]: job_id -> success mapping
        """
        with self._lock:
            running_jobs = [
                job_id for job_id, job in self._jobs.items()
                if job.status in ['pending', 'running']
            ]
            
            if not running_jobs:
                logger.info("No running jobs to cancel")
                return {}
            
            logger.info(f"Cancelling {len(running_jobs)} running jobs")
            
            # Set cancel events for all jobs
            for job_id in running_jobs:
                job = self._jobs[job_id]
                job.cancel_event.set()
            
            # Wait for all threads to finish
            results = {}
            per_job_timeout = timeout / len(running_jobs) if running_jobs else timeout
            
            for job_id in running_jobs:
                job = self._jobs[job_id]
                if job.thread and job.thread.is_alive():
                    job.thread.join(timeout=per_job_timeout)
                    
                    if job.thread.is_alive():
                        logger.warning(f"Job {job_id} did not stop within timeout")
                        results[job_id] = False
                    else:
                        job.status = 'cancelled'
                        job.stopped_at = datetime.now()
                        results[job_id] = True
                        logger.info(f"Job {job_id} cancelled")
                else:
                    job.status = 'cancelled'
                    job.stopped_at = datetime.now()
                    results[job_id] = True
            
            return results
    
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        """Lấy thông tin job"""
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_pair_job(self, pair_id: str) -> Optional[JobInfo]:
        """Lấy job đang chạy cho pair"""
        with self._lock:
            job_id = self._pair_jobs.get(pair_id)
            if job_id:
                return self._jobs.get(job_id)
            return None
    
    def get_running_jobs(self) -> Dict[str, JobInfo]:
        """Lấy tất cả jobs đang chạy"""
        with self._lock:
            return {
                job_id: job for job_id, job in self._jobs.items()
                if job.status in ['pending', 'running']
            }
    
    def get_all_jobs(self) -> Dict[str, JobInfo]:
        """Lấy tất cả jobs"""
        with self._lock:
            return self._jobs.copy()
    
    def update_job_progress(self, job_id: str, progress: int, message: str = '') -> bool:
        """Update progress của job
        
        Args:
            job_id: ID của job
            progress: Progress percentage (0-100)
            message: Progress message
            
        Returns:
            bool: True nếu update thành công
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return False
            
            job.progress = max(0, min(100, progress))
            if message:
                job.message = message
            
            return True
    
    def is_pair_running(self, pair_id: str) -> bool:
        """Kiểm tra xem pair có đang chạy không"""
        with self._lock:
            job_id = self._pair_jobs.get(pair_id)
            if job_id:
                job = self._jobs.get(job_id)
                return job and job.status in ['pending', 'running']
            return False
    
    def _cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Cleanup các jobs đã hoàn thành lâu
        
        Args:
            max_age_hours: Tuổi tối đa của job (hours)
        """
        with self._lock:
            current_time = datetime.now()
            jobs_to_remove = []
            
            for job_id, job in self._jobs.items():
                if job.status in ['completed', 'failed', 'cancelled']:
                    if job.stopped_at:
                        age_hours = (current_time - job.stopped_at).total_seconds() / 3600
                        if age_hours > max_age_hours:
                            jobs_to_remove.append(job_id)
            
            # Remove old jobs
            for job_id in jobs_to_remove:
                job = self._jobs.pop(job_id, None)
                if job:
                    # Remove from pair mapping
                    if job.pair_id in self._pair_jobs and self._pair_jobs[job.pair_id] == job_id:
                        del self._pair_jobs[job.pair_id]
                    
                    logger.debug(f"Cleaned up old job {job_id}")
            
            if jobs_to_remove:
                logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")
    
    def shutdown(self, timeout: float = 30.0):
        """Shutdown task registry
        
        Args:
            timeout: Timeout để đợi tất cả jobs dừng
        """
        logger.info("Shutting down task registry")
        
        # Cancel all running jobs
        self.cancel_all_jobs(timeout=timeout * 0.8)
        
        # Stop cleanup thread
        self._shutdown_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5.0)
        
        logger.info("Task registry shutdown complete")
    
    def __del__(self):
        """Destructor"""
        try:
            self.shutdown(timeout=5.0)
        except:
            pass

# Global task registry instance
_task_registry: Optional[TaskRegistry] = None
_registry_lock = threading.Lock()

def get_task_registry() -> TaskRegistry:
    """Get global task registry instance (singleton)"""
    global _task_registry
    
    if _task_registry is None:
        with _registry_lock:
            if _task_registry is None:
                _task_registry = TaskRegistry()
                logger.info("Global task registry created")
    
    return _task_registry

def shutdown_task_registry():
    """Shutdown global task registry"""
    global _task_registry
    
    if _task_registry is not None:
        with _registry_lock:
            if _task_registry is not None:
                _task_registry.shutdown()
                _task_registry = None
                logger.info("Global task registry shutdown")

if __name__ == "__main__":
    # Test script
    import sys
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    def test_job(cancel_event, duration=5):
        """Test job function"""
        for i in range(duration):
            if cancel_event.is_set():
                print(f"Job cancelled at step {i}")
                return False
            print(f"Job step {i+1}/{duration}")
            time.sleep(1)
        print("Job completed")
        return True
    
    # Test task registry
    registry = get_task_registry()
    
    try:
        # Create and start job
        job_id = registry.create_job(
            run_id="test_run",
            pair_id="test_pair",
            device_a="device1",
            device_b="device2"
        )
        
        print(f"Created job: {job_id}")
        
        # Start job
        registry.start_job(job_id, test_job, duration=10)
        
        # Wait a bit then cancel
        time.sleep(3)
        print("Cancelling job...")
        registry.cancel_job(job_id)
        
        # Check final status
        job = registry.get_job(job_id)
        print(f"Final job status: {job.status if job else 'Not found'}")
        
    finally:
        shutdown_task_registry()