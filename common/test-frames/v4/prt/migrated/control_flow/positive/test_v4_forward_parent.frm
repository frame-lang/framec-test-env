@@target python

@@system ForwardTest {
    interface:
        handleEvent()
        
    machine:
        $Child => $Parent {
            handleEvent() {
                print("Child handler")
                # Forward to parent
                => $^
            }
        }
        
        $Parent {
            handleEvent() {
                print("Parent handler")
                system.return = "handled by parent"
            }
        }
}

# Test forward event
var ft = ForwardTest()
var result = ft.handleEvent()

if result == "handled by parent":
    print("SUCCESS: Forward to parent works")
else:
    print("FAIL: Expected 'handled by parent', got " + str(result))