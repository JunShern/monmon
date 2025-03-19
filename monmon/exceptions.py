class MonitorException(Exception):
    """Base exception for all monitor-related issues."""
    pass

class TerminationConditionMet(MonitorException):
    """Raised when a termination condition is detected."""
    def __init__(self, condition, details=None):
        self.condition = condition
        self.details = details
        message = f"Termination condition met: {condition}"
        if details:
            message += f" - {details}"
        super().__init__(message)

class PermissionRequiredException(MonitorException):
    """
    This exception is raised internally when permission is needed.
    Users of the library typically won't encounter this as it's handled 
    within the monitoring system.
    """
    def __init__(self, condition, details=None):
        self.condition = condition
        self.details = details
        message = f"Permission required for: {condition}"
        if details:
            message += f" - {details}"
        super().__init__(message) 