@@target python

# Native Python imports and code
import sys
sys.path.insert(0, '/opt/frame_runtime')

# Native Python class
class Logger:
    def __init__(self):
        self.messages = []
    
    def log(self, msg):
        self.messages.append(msg)
        print(f"[LOG] {msg}")

# Global logger
logger = Logger()

@@system StateMachine {
    interface:
        process(data: str)
        getState(): str
        
    machine:
        $Idle {
            process(data: str) {
                # No 'var' keyword - this is native Python
                msg = f"Processing {data} in Idle state"
                logger.log(msg)
                
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
                    $$[+]
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
                    $$[-]
                else:
                    system.return = "paused"
            }
            
            getState(): str {
                system.return = "paused"
            }
        }
}

# Native Python test code
def test_native_integration():
    print("=== Frame v4 Native Integration Test ===")
    
    # Create Frame system instance (native Python instantiation)
    sm = StateMachine()
    
    # Test initial state
    state = sm.getState()
    if state == "idle":
        print("SUCCESS: Initial state is idle")
    else:
        print(f"FAIL: Expected idle, got {state}")
        raise AssertionError()
    
    # Test transitions
    sm.process("start")
    if sm.getState() == "active":
        print("SUCCESS: Transitioned to active")
    else:
        print("FAIL: Should be active")
        raise AssertionError()
    
    # Test stack operations
    sm.process("pause")
    if sm.getState() == "paused":
        print("SUCCESS: Pushed to paused")
    else:
        print("FAIL: Should be paused")
        raise AssertionError()
    
    sm.process("resume")
    if sm.getState() == "active":
        print("SUCCESS: Popped back to active")
    else:
        print("FAIL: Should be active after resume")
        raise AssertionError()
    
    print("\nKey observations:")
    print("- No 'var' keyword needed in native Python code")
    print("- Frame systems are classes in the native language")
    print("- Test code is pure native Python")
    print("- Frame only processes @@system blocks")

# Run the test
test_native_integration()