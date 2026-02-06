#!/usr/bin/env python3
"""
test_v4_native_integration.py - Demonstrates Frame v4's "going native" approach
This is a native Python file with embedded Frame systems.
"""

# Native Python imports
import sys
import json
from typing import List, Dict, Optional

# Add Frame runtime to path (for testing environment)
sys.path.insert(0, '/opt/frame_runtime')

# Native Python classes
class Logger:
    """Native Python class - not touched by Frame"""
    def __init__(self):
        self.messages: List[str] = []
    
    def log(self, msg: str) -> None:
        self.messages.append(msg)
        print(f"[LOG] {msg}")

# Global logger instance
logger = Logger()

# Frame system embedded in native Python file
@@system StateMachine {
    interface:
        process(data: str)
        getState(): str
        
    machine:
        $Idle {
            process(data: str) {
                # Using native Python variable (no 'var' keyword)
                logger.log(f"Processing {data} in Idle state")
                
                if data == "start":
                    -> $Active()
                else:
                    system.return = "ignored"
            }
            
            getState(): str {
                system.return = "idle"
            }
        }
        
        $Active {
            process(data: str) {
                logger.log(f"Processing {data} in Active state")
                
                if data == "stop":
                    -> $Idle()
                elif data == "pause":
                    $$[+]  # Push state to stack
                    -> $Paused()
                else:
                    system.return = "processed"
            }
            
            getState(): str {
                system.return = "active"
            }
        }
        
        $Paused {
            process(data: str) {
                if data == "resume":
                    $$[-]  # Pop back to previous state
                else:
                    system.return = "paused"
            }
            
            getState(): str {
                system.return = "paused"
            }
        }
}

# Another Frame system showing composition
@@system Controller {
    interface:
        execute(command: str): str
        
    machine:
        $Ready {
            execute(command: str): str {
                # Using the native logger
                logger.log(f"Executing command: {command}")
                
                # Native Python string operations
                parts = command.split(":")
                if len(parts) == 2:
                    action = parts[0]
                    data = parts[1]
                    
                    # Create and use another Frame system
                    sm = StateMachine()
                    sm.process("start")
                    result = sm.process(data)
                    
                    system.return = f"Result: {result}"
                else:
                    system.return = "Invalid command format"
            }
        }
}

# Native Python test code - NOT processed by Frame
def test_state_machine():
    """Test the embedded Frame state machine"""
    sm = StateMachine()
    
    # Test initial state
    assert sm.getState() == "idle", f"Expected idle, got {sm.getState()}"
    print("SUCCESS: Initial state is idle")
    
    # Test transition to active
    sm.process("start")
    assert sm.getState() == "active", f"Expected active, got {sm.getState()}"
    print("SUCCESS: Transitioned to active")
    
    # Test stack push to paused
    sm.process("pause")
    assert sm.getState() == "paused", f"Expected paused, got {sm.getState()}"
    print("SUCCESS: Pushed to paused state")
    
    # Test stack pop back to active
    sm.process("resume")
    assert sm.getState() == "active", f"Expected active after resume, got {sm.getState()}"
    print("SUCCESS: Popped back to active")
    
    # Test transition back to idle
    sm.process("stop")
    assert sm.getState() == "idle", f"Expected idle, got {sm.getState()}"
    print("SUCCESS: Transitioned back to idle")

def test_controller():
    """Test the controller with composition"""
    ctrl = Controller()
    
    result = ctrl.execute("process:test_data")
    print(f"Controller result: {result}")
    
    # Check that logger captured messages
    assert len(logger.messages) > 0, "Logger should have messages"
    print(f"SUCCESS: Logger captured {len(logger.messages)} messages")

def main():
    """Main test runner - pure native Python"""
    print("=== Frame v4 Native Integration Test ===")
    print("This demonstrates Frame systems embedded in native Python code")
    print()
    
    try:
        test_state_machine()
        print()
        test_controller()
        print()
        print("ALL TESTS PASSED")
    except AssertionError as e:
        print(f"FAIL: {e}")
        # Force test failure for test infrastructure
        sys.exit(1)

# Native Python module execution
if __name__ == "__main__":
    main()