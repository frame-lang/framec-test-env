fn main() {
    var sm = TestProtocolVerification()
    sm.start()
    sm.increment()
    sm.increment()
    var value = sm.getValue()
    print(f"Final value: {value}")
}

@@system TestProtocolVerification {
    interface:
        start()
        increment()
        getValue()

    machine:
        $Start {
            start() {
                print("Starting protocol verification test")
                -> $Running
            }
        }

        $Running {
            $>() {
                print("Entered Running state")
            }
            
            increment() {
                self.counter += 1
                print(f"Counter incremented to: {self.counter}")
            }
            
            getValue() {
                return self.counter
            }
        }

    actions:
        print

    domain:
        var counter = 0
}