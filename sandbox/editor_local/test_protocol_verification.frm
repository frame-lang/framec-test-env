system TestProtocolVerification {
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

def main():
    test_system = TestProtocolVerification()
    test_system.start()
    test_system.increment()
    test_system.increment()
    value = test_system.getValue()
    print(f"Final value: {value}")