@@target python

@@system StackTest {
    interface:
        pushState()
        popState()
        getState(): str
        
    machine:
        $StateA {
            pushState() {
                print("Pushing StateA, going to StateB")
                $$[+]
                -> $StateB()
            }
            
            getState(): str {
                system.return = "StateA"
            }
        }
        
        $StateB {
            pushState() {
                print("Pushing StateB, going to StateC")
                $$[+]
                -> $StateC()
            }
            
            popState() {
                print("Popping from StateB")
                $$[-]
            }
            
            getState(): str {
                system.return = "StateB"
            }
        }
        
        $StateC {
            popState() {
                print("Popping from StateC")
                $$[-]
            }
            
            getState(): str {
                system.return = "StateC"
            }
        }
}

# Test stack operations
var st = StackTest()

# Initial state
var s1 = st.getState()
if s1 == "StateA":
    print("SUCCESS: Initial state is StateA")
else:
    print("FAIL: Expected StateA, got " + s1)

# Push to StateB
st.pushState()
var s2 = st.getState()
if s2 == "StateB":
    print("SUCCESS: Pushed to StateB")
else:
    print("FAIL: Expected StateB, got " + s2)

# Push to StateC
st.pushState()
var s3 = st.getState()
if s3 == "StateC":
    print("SUCCESS: Pushed to StateC")
else:
    print("FAIL: Expected StateC, got " + s3)

# Pop back to StateB
st.popState()
var s4 = st.getState()
if s4 == "StateB":
    print("SUCCESS: Popped back to StateB")
else:
    print("FAIL: Expected StateB after pop, got " + s4)

# Pop back to StateA
st.popState()
var s5 = st.getState()
if s5 == "StateA":
    print("SUCCESS: Popped back to StateA")
else:
    print("FAIL: Expected StateA after second pop, got " + s5)

print("Stack operations test completed")