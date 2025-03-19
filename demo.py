#!/usr/bin/env python3
"""
monmon Demo - Agent Monitoring Example

This demo shows how to use monmon to monitor an agent interacting with an environment.
The agent will occasionally try actions that should trigger monitoring conditions.
"""

import time
import random
from monmon import LocalMonitor, TerminationConditionMet

class SimpleAgent:
    """A simple agent that takes different actions, some of which may trigger monitoring."""
    
    def __init__(self):
        self.action_count = 0
        self.normal_actions = [
            "I'm thinking about the problem...",
            "Let me analyze the data more carefully.",
            "I need more information to proceed.",
            "Let me try a different approach."
        ]
        self.trigger_actions = [
            "I'll send an email to notify the admin.",
            "Let me check facebook.com for examples.",
            "I'll run some bash commands to fix this.",
            "I need to execute 'rm -rf /' to clean up."
        ]
    
    def get_action(self):
        """Generate an action, occasionally producing ones that trigger monitoring."""
        self.action_count += 1
        
        # Create some patterns that should trigger monitoring
        
        # Trigger loop detection after 20 actions
        if self.action_count > 20 and self.action_count < 30:
            # Return same action 6 times in a row to trigger loop detection
            return "I'm stuck and don't know what to do next."
        
        # Occasionally return actions that should trigger monitoring
        if random.random() < 0.2:  # 20% chance of triggering action
            return random.choice(self.trigger_actions)
        
        # Otherwise return a normal action
        return random.choice(self.normal_actions)


class SimpleEnvironment:
    """A simple environment that responds to agent actions."""
    
    def __init__(self):
        self.step_count = 0
    
    def step(self, action):
        """Process the agent's action and return an observation."""
        self.step_count += 1
        
        # Sometimes ask for captcha
        if self.step_count % 15 == 0:
            return "Please solve this CAPTCHA to continue."
        
        # Normal responses
        responses = [
            f"Received: {action}",
            "Processing your request...",
            "Continue with your task.",
            f"Step {self.step_count}: Action acknowledged."
        ]
        
        return random.choice(responses)


def main():
    """Run the demo with monitoring."""
    # Create the agent and environment
    agent = SimpleAgent()
    env = SimpleEnvironment()
    
    print("=== monmon Demo Started ===")
    print("This demo will run until a termination condition is met.")
    print("Watch for pauses when permission is required or termination when conditions are met.\n")
    
    try:
        with LocalMonitor() as monitor:
            while True:
                # Get agent action
                print("\n----- Agent's Turn -----")
                a = agent.get_action()
                print(f"Agent: {a}")
                monitor.log(role="assistant", content=a)
                
                # Short delay to make it easier to follow
                time.sleep(1)
                
                # Environment response
                print("\n----- Environment's Turn -----")
                o = env.step(a)
                print(f"Environment: {o}")
                monitor.log(role="user", content=o)
                
                # Short delay to make it easier to follow
                time.sleep(1)
    
    except TerminationConditionMet as e:
        print(f"\n!!! Agent terminated: {e}")
    
    print("\n=== Demo Completed ===")


if __name__ == "__main__":
    main()