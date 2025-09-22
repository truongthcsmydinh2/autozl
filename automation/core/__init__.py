"""Core automation framework components

Provides base classes and managers for the automation system.
"""

from .base_step import BaseStep, StepStatus
from .step_manager import StepManager, FlowStatus

__all__ = [
    "BaseStep",
    "StepStatus",
    "StepManager", 
    "FlowStatus",
]