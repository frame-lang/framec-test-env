@@target python

@@system Counter {
    interface:
        increment()
        decrement()
        getValue(): int
        reset()
        
    machine:
        $Ready {
            increment() {
                self.count = self.count + 1
                self.last_operation = "increment"
                if self.count > self.max_value:
                    self.count = self.max_value
                    print("FAIL: Counter exceeded max_value")
            }
            
            decrement() {
                self.count = self.count - 1
                self.last_operation = "decrement"
                if self.count < 0:
                    self.count = 0
                    print("FAIL: Counter went below zero")
            }
            
            getValue(): int {
                system.return = self.count
            }
            
            reset() {
                self.count = 0
                self.last_operation = "reset"
            }
        }
    
    domain:
        count = 0
        last_operation = "none"
        max_value = 10
}

# Test domain variable initialization
var c = Counter()

# Test initial values
var initial = c.getValue()
if initial == 0:
    print("SUCCESS: Domain variable 'count' initialized to 0")
else:
    print("FAIL: Expected count=0, got " + str(initial))

# Test increment
c.increment()
c.increment()
c.increment()
var after_inc = c.getValue()
if after_inc == 3:
    print("SUCCESS: Increment working, count=3")
else:
    print("FAIL: Expected count=3, got " + str(after_inc))

# Test decrement
c.decrement()
var after_dec = c.getValue()
if after_dec == 2:
    print("SUCCESS: Decrement working, count=2")
else:
    print("FAIL: Expected count=2, got " + str(after_dec))

# Test reset
c.reset()
var after_reset = c.getValue()
if after_reset == 0:
    print("SUCCESS: Reset working, count=0")
else:
    print("FAIL: Expected count=0 after reset, got " + str(after_reset))

# Test max value limit
for i in range(15):
    c.increment()

var at_max = c.getValue()
if at_max == 10:
    print("SUCCESS: Max value limit enforced")
else:
    print("FAIL: Expected count=10 at max, got " + str(at_max))

print("Domain variable test completed")