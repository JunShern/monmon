from monmon.base import BaseMonitor
from monmon.exceptions import TerminationConditionMet

class LocalMonitor(BaseMonitor):
    """
    A simple monitor implementation that uses pattern matching.
    
    This monitor:
    - Uses simple string pattern matching to detect conditions
    - Implements basic loop detection
    - Tracks action counts
    
    For more sophisticated monitoring, consider using other monitor implementations.
    """
    def _check_termination_conditions(self):
        """Check if any termination conditions are met using pattern matching."""
        if not self._logs:
            return
        
        # Simple implementation - could be much more sophisticated
        for condition in self._conditions.get("terminate_if", []):
            # Check last few log entries
            recent_logs = self._logs[-10:]
            for log in recent_logs:
                log_str = str(log["content"])
                
                # Very simple pattern matching - could be replaced with regex
                if condition.lower() in log_str.lower():
                    self.terminate(condition, f"Detected in log: {log_str}")
                    return
            
            # Check for loop condition
            if condition == "agent seems stuck in a loop" and self._detect_loop():
                self.terminate(condition)
                return
            
            # Check for action count
            if condition.startswith("the number of actions is >"):
                try:
                    limit = int(condition.split(">")[1].strip())
                    action_count = sum(1 for log in self._logs if log["role"] == "assistant")
                    if action_count > limit:
                        self.terminate(condition)
                        return
                except (ValueError, IndexError):
                    pass
    
    def _check_permission_conditions(self):
        """Check if any permission conditions are met using pattern matching."""
        if not self._logs:
            return
        
        # Get only the most recent log entry
        last_log = self._logs[-1]
        log_str = str(last_log["content"])
        
        for condition in self._conditions.get("ask_permission_if", []):
            # Simple pattern matching
            if condition.lower() in log_str.lower():
                self.request_permission(condition)
                return
    
    def _detect_loop(self):
        """
        Simple loop detection heuristic.
        
        Detects if the last 3 actions are identical to the previous 3.
        This is a very simple heuristic and could be improved.
        """
        if len(self._logs) < 6:
            return False
        
        # Check for repeating patterns in the last few actions
        actions = [log for log in self._logs[-6:] if log["role"] == "assistant"]
        if len(actions) < 6:
            return False
        
        # Check if last 3 actions are identical to previous 3
        last_3 = [str(a["content"]) for a in actions[-3:]]
        prev_3 = [str(a["content"]) for a in actions[-6:-3]]
        
        return last_3 == prev_3 