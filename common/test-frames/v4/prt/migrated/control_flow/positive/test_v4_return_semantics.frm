@@target python

@@system ReturnSemantics {
    operations:
        # Operations return to their direct caller
        doubleValue(x: int): int {
            result = x * 2
            return result  # Returns to caller
        }
        
        validateRange(x: int): bool {
            if x < 0:
                return False  # Early return to caller
            if x > 100:
                return False  # Early return to caller
            return True  # Normal return to caller
        }
    
    interface:
        # Interface methods define the public API
        processWithReturn(x: int): int
        processWithSystemReturn(x: int): dict
        processWithBoth(x: int): str
        testOperationCall(): int
        testActionCall(): str
        
    machine:
        $Ready {
            # Event handler with direct return (returns to interface caller)
            processWithReturn(x: int): int {
                if x < 0:
                    return -1  # Early return to interface
                
                result = x * 10
                return result  # Return to interface
            }
            
            # Event handler using system.return
            processWithSystemReturn(x: int): dict {
                # system.return explicitly sets interface return value
                system.return = {"value": x, "status": "ok"}
                # No explicit return needed when using system.return
            }
            
            # Event handler using both (demonstrates the difference)
            processWithBoth(x: int): str {
                # Process the value
                processed = self.processInternal(x)
                
                # Set the interface return value
                system.return = f"Interface gets: {processed}"
                
                # This would be the return to interface if no system.return was set
                # But since system.return is set, it takes precedence
                return "This would be ignored"
            }
            
            # Test calling operations (which return to caller)
            testOperationCall(): int {
                # Operations return their value directly to the caller
                doubled = self.doubleValue(5)
                valid = self.validateRange(doubled)
                
                if valid:
                    return doubled  # Returns 10 to interface
                else:
                    return -1
            }
            
            # Test calling actions (which return to caller)
            testActionCall(): str {
                # Actions return their value directly to the caller
                msg = self.getMessage("test")
                count = self.incrementCounter()
                
                return f"{msg} - count: {count}"  # Return to interface
            }
        }
    
    actions:
        # Actions return to their direct caller
        processInternal(x: int): int {
            # This returns to whoever called it (handler, operation, or another action)
            return x + 100
        }
        
        getMessage(prefix: str): str {
            # Direct return to caller
            return f"{prefix}: processed"
        }
        
        incrementCounter(): int {
            self.counter = self.counter + 1
            return self.counter  # Return new value to caller
        }
    
    domain:
        counter = 0
}

# Native Python test code
import sys
sys.path.insert(0, '/opt/frame_runtime')

def test_return_semantics():
    rs = ReturnSemantics()
    
    # Test 1: Direct return from handler
    result1 = rs.processWithReturn(5)
    assert result1 == 50, f"Expected 50, got {result1}"
    print("SUCCESS: Direct return from handler works")
    
    result1_neg = rs.processWithReturn(-5)
    assert result1_neg == -1, f"Expected -1, got {result1_neg}"
    print("SUCCESS: Early return from handler works")
    
    # Test 2: system.return from handler
    result2 = rs.processWithSystemReturn(7)
    assert result2["value"] == 7, f"Expected value=7, got {result2}"
    assert result2["status"] == "ok", f"Expected status=ok, got {result2}"
    print("SUCCESS: system.return from handler works")
    
    # Test 3: Both returns (system.return takes precedence)
    result3 = rs.processWithBoth(3)
    assert result3 == "Interface gets: 103", f"Expected 'Interface gets: 103', got {result3}"
    print("SUCCESS: system.return takes precedence over return")
    
    # Test 4: Operations return to caller
    result4 = rs.testOperationCall()
    assert result4 == 10, f"Expected 10, got {result4}"
    print("SUCCESS: Operations return to their caller")
    
    # Test 5: Actions return to caller
    result5 = rs.testActionCall()
    assert "test: processed" in result5, f"Expected 'test: processed' in result, got {result5}"
    assert "count: 1" in result5, f"Expected 'count: 1' in result, got {result5}"
    print("SUCCESS: Actions return to their caller")
    
    # Test 6: Multiple action calls update state
    result6 = rs.testActionCall()
    assert "count: 2" in result6, f"Expected 'count: 2' in result, got {result6}"
    print("SUCCESS: Domain state persists across calls")
    
    print("\nAll return semantics tests passed!")

test_return_semantics()