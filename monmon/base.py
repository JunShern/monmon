import threading
import time
import yaml
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from monmon.types import LogEntry
from monmon.exceptions import TerminationConditionMet

class BaseMonitor(ABC):
    """
    Abstract base class for all monitors.
    Handles threading, synchronization, and lifecycle management.
    """
    def __init__(self, config_path="monmon.yaml"):
        # Synchronization primitives
        self._termination_flag = threading.Event()
        self._pause_flag = threading.Event()
        self._resume_flag = threading.Event()
        self._permission_granted = None
        
        # Threading
        self._monitoring_thread = None
        self._main_thread_id = threading.main_thread().ident
        
        # State
        self._logs: List[LogEntry] = []
        self._current_permission_condition = None
        
        # Load configuration
        self._config_path = config_path
        self._conditions = self._load_conditions()
    
    def _load_conditions(self) -> Dict[str, list]:
        """Load monitoring conditions from YAML file."""
        if not os.path.exists(self._config_path):
            return {"terminate_if": [], "ask_permission_if": []}
        
        with open(self._config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def __enter__(self):
        """Context manager entry point."""
        # Clear any previous state
        self._pause_flag.clear()
        self._resume_flag.clear()
        self._termination_flag.clear()
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(target=self._monitor_loop)
        self._monitoring_thread.daemon = True
        self._monitoring_thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - ensures cleanup."""
        # Signal thread to terminate and wait for it
        self._termination_flag.set()
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=1.0)
        
        # Don't suppress exceptions
        return False
    
    def log(self, role: str, content: Any):
        """
        Log an event for monitoring.
        This method will pause execution if a permission condition is triggered.
        
        Args:
            role: The role of the entity generating the content (e.g., "assistant", "user")
            content: The content being logged (can be any type)
        """
        # Add to logs
        log_entry: LogEntry = {
            "role": role, 
            "content": content, 
            "timestamp": time.time()
        }
        self._logs.append(log_entry)
        
        # Check if we're currently paused - if so, wait for resume
        if self._pause_flag.is_set():
            print(f"Agent paused: Waiting for permission...")
            self._resume_flag.wait()  # Block until resumed
            
            # If permission was denied, raise termination
            if not self._permission_granted:
                raise TerminationConditionMet(
                    f"Permission denied for: {self._current_permission_condition}"
                )
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in background thread."""
        while not self._termination_flag.is_set():
            # First check termination conditions
            self._check_termination_conditions()
            
            # Then check permission conditions if not already paused
            if not self._pause_flag.is_set():
                self._check_permission_conditions()
            
            # Sleep to avoid CPU spinning
            time.sleep(0.1)
    
    @abstractmethod
    def _check_termination_conditions(self):
        """
        Check if any termination conditions are met.
        To be implemented by concrete monitor strategies.
        """
        pass
    
    @abstractmethod
    def _check_permission_conditions(self):
        """
        Check if any permission conditions are met.
        To be implemented by concrete monitor strategies.
        """
        pass
    
    def terminate(self, condition: str, details: Optional[str] = None):
        """
        Terminate the agent by raising an exception.
        
        Args:
            condition: The condition that triggered termination
            details: Optional additional details about the termination
        """
        # Set the termination flag to stop the monitoring thread
        self._termination_flag.set()
        
        # Raise exception
        raise TerminationConditionMet(condition, details)
    
    def request_permission(self, condition: str):
        """
        Pause the main thread and request permission.
        This is called by concrete implementations when a condition is detected.
        
        Args:
            condition: The condition that triggered the permission request
        """
        self._current_permission_condition = condition
        self._pause_flag.set()
        self._resume_flag.clear()
        
        # Notify listeners (UI, etc) that permission is needed
        self._notify_permission_needed(condition)
    
    def grant_permission(self, granted: bool = True):
        """
        Called when user responds to permission request.
        
        Args:
            granted: Whether permission was granted (True) or denied (False)
        """
        self._permission_granted = granted
        self._resume_flag.set()  # Signal main thread to continue
        self._pause_flag.clear()  # Clear the pause flag
    
    def _notify_permission_needed(self, condition: str):
        """
        Notify listeners that permission is needed. Override for UI integration.
        
        Args:
            condition: The condition that triggered the permission request
        """
        print(f"Permission required: {condition}")
        # In a real implementation, this might send a signal to a UI 