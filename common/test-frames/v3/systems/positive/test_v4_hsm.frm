@@target python

@@system HierarchicalStateMachine {
    interface:
        start()
        pause()
        resume()
        stop()
        getState(): str
        
    machine:
        $Stopped {
            start() {
                -> $Running.$Active()
            }
            
            getState(): str {
                system.return = "Stopped"
            }
        }
        
        $Running {
            stop() {
                -> $Stopped()
            }
            
            getState(): str {
                system.return = "Running"
            }
            
            $Active => $Running {
                pause() {
                    -> $Paused()
                }
                
                getState(): str {
                    system.return = "Active"
                }
            }
            
            $Paused => $Running {
                resume() {
                    -> $Active()
                }
                
                getState(): str {
                    system.return = "Paused"
                }
            }
        }
}

# Test HSM functionality
import sys
sys.path.insert(0, '/opt/frame_runtime')

def test_hsm():
    hsm = HierarchicalStateMachine()
    
    # Initial state should be Stopped
    assert hsm.getState() == "Stopped", f"Expected Stopped, got {hsm.getState()}"
    print("SUCCESS: Initial state is Stopped")
    
    # Start -> Running.Active
    hsm.start()
    state = hsm.getState()
    assert state == "Active", f"Expected Active, got {state}"
    print("SUCCESS: Transitioned to Running.Active")
    
    # Pause -> Running.Paused
    hsm.pause()
    state = hsm.getState()
    assert state == "Paused", f"Expected Paused, got {state}"
    print("SUCCESS: Transitioned to Running.Paused")
    
    # Resume -> Running.Active
    hsm.resume()
    state = hsm.getState()
    assert state == "Active", f"Expected Active, got {state}"
    print("SUCCESS: Resumed to Running.Active")
    
    # Stop from child state should transition to parent handler
    # This tests event forwarding in HSM
    hsm.stop()
    state = hsm.getState()
    assert state == "Stopped", f"Expected Stopped, got {state}"
    print("SUCCESS: Stopped from child state (forwarded to parent)")
    
    print("\nAll HSM tests passed!")

test_hsm()