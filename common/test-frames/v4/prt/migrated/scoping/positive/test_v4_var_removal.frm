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

# Test var keyword removal
var vt = VarTest()
var result = vt.testVars()

if result == "SUCCESS":
    print("SUCCESS: var keyword handled correctly")
else:
    print("FAIL: var keyword not working")