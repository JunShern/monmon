from typing import Any, TypedDict

class LogEntry(TypedDict):
    """Type definition for log entries."""
    role: str
    content: Any
    timestamp: float 