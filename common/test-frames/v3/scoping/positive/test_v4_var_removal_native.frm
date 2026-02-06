@@target python

@@system VarTest {
    interface:
        testVars()
        
    machine:
        $Ready {
            testVars() {
                var x = 10
                var y = "hello"
                var z = x + 5
                
                print("x = " + str(x))
                print("y = " + y)
                print("z = " + str(z))
                
                if z == 15:
                    system.return = "SUCCESS"
                else:
                    system.return = "FAIL"
            }
        }
}

# Native Python test code (not Frame code)
import sys
sys.path.insert(0, '/opt/frame_runtime')
from frame_runtime_py import FrameEvent, FrameCompartment

# Create and test the system
vt = VarTest()
result = vt.testVars()

if result == "SUCCESS":
    print("SUCCESS: var keyword handled correctly")
else:
    print("FAIL: var keyword not working")
    # Force test failure
    failed_tests = []
    index = failed_tests[999]