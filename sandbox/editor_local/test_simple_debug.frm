# Simple debug test
@@system DebugTestSystem {
    interface: {
        start()
    }
    
    machine: {
        $Start {
            start() {
                print("Hello from Frame!")
                -> $Running
            }
        }
        
        $Running {
            $>() {
                print("Debug test complete")
            }
        }
    }
}

# Create and run the system
fn main() {
    var system = DebugTestSystem()
    system.start()
}