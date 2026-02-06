@@target python

@@system SimpleHSM {
    interface:
        processChild()
        processParent()
        getState(): str
        
    machine:
        $Child => $Parent {
            processChild() {
                print("Child handling processChild")
                system.return = "child"
            }
            
            getState(): str {
                system.return = "Child"
            }
        }
        
        $Parent {
            processChild() {
                print("Parent handling processChild (forwarded from child)")
                system.return = "parent_forwarded"
            }
            
            processParent() {
                print("Parent handling processParent")
                -> $Child()
            }
            
            getState(): str {
                system.return = "Parent"
            }
        }
}

# Test basic HSM parent-child relationship
import sys
sys.path.insert(0, '/opt/frame_runtime')

hsm = SimpleHSM()

# Should start in Child state (first declared)
state = hsm.getState()
if state == "Child":
    print("SUCCESS: Initial state is Child")
else:
    print(f"FAIL: Expected Child, got {state}")
    raise AssertionError()

# Call child handler
result = hsm.processChild()
if result == "child":
    print("SUCCESS: Child handled its own event")
else:
    print(f"FAIL: Expected 'child', got {result}")
    raise AssertionError()

# Transition to parent
hsm.processParent()
state = hsm.getState()
if state == "Child":
    print("SUCCESS: Transitioned from Parent back to Child")
else:
    print(f"FAIL: Expected Child after parent transition, got {state}")
    raise AssertionError()

print("\nBasic HSM test passed!")