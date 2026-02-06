@@target python

# Basic persistence test
@@persist @@system PersistentCounter {
    interface:
        increment()
        decrement()
        getValue(): int
        save(): str
        restore(data: str)
        
    machine:
        $Idle {
            increment() {
                self.count = self.count + 1
                -> $Active()
            }
            
            getValue(): int {
                system.return = self.count
            }
        }
        
        $Active {
            increment() {
                self.count = self.count + 1
            }
            
            decrement() {
                self.count = self.count - 1
                if self.count <= 0:
                    self.count = 0
                    -> $Idle()
            }
            
            getValue(): int {
                system.return = self.count
            }
        }
    
    domain:
        count = 0
        lastOperation = "none"
}

# Test persistence
import sys
import json
sys.path.insert(0, '/opt/frame_runtime')

def test_persistence():
    # Create and modify a counter
    counter1 = PersistentCounter()
    
    # Initial state
    assert counter1.getValue() == 0, "Should start at 0"
    print("SUCCESS: Initial count is 0")
    
    # Increment several times
    counter1.increment()  # Goes to Active
    counter1.increment()
    counter1.increment()
    assert counter1.getValue() == 3, "Should be 3 after increments"
    print("SUCCESS: Count is 3 after increments")
    
    # Save the state
    snapshot = counter1.save()
    print(f"Saved snapshot: {snapshot}")
    
    # Modify further
    counter1.increment()
    counter1.increment()
    assert counter1.getValue() == 5, "Should be 5"
    
    # Restore to saved state
    counter1.restore(snapshot)
    restored_value = counter1.getValue()
    assert restored_value == 3, f"Should restore to 3, got {restored_value}"
    print("SUCCESS: Restored to saved state (count=3)")
    
    # Create a new instance and restore
    counter2 = PersistentCounter()
    assert counter2.getValue() == 0, "New instance should start at 0"
    
    counter2.restore(snapshot)
    assert counter2.getValue() == 3, "Should restore to 3 in new instance"
    print("SUCCESS: New instance restored from snapshot")
    
    print("\nAll persistence tests passed!")

test_persistence()