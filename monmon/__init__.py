"""
monmon: A Monitoring System for AI Agents

monmon provides a flexible framework for monitoring and controlling AI agents,
with support for rule-based termination, permission requirements, and extensible
monitoring strategies.
"""

from monmon.base import BaseMonitor
from monmon.exceptions import MonitorException, TerminationConditionMet, PermissionRequiredException
from monmon.types import LogEntry
from monmon.monitors import LocalMonitor

__version__ = "0.1.0"

__all__ = [
    "BaseMonitor",
    "LocalMonitor", 
    "TerminationConditionMet",
    "PermissionRequiredException",
    "MonitorException",
    "LogEntry"
] 