@@target python

@@system NativeCodeReturns {
    interface:
        testNativeFunctions(): str
        testNativeClasses(): int
        testLambdas(): list
        
    machine:
        $Ready {
            testNativeFunctions(): str {
                # Native Python function defined inside handler
                # This is NATIVE CODE - not a Frame construct
                def calculate_sum(a, b):
                    # This return is inside native Python function
                    # Should remain as Python return, not system.return
                    return a + b
                
                def get_message(value):
                    if value > 10:
                        return "high"  # Native Python early return
                    return "low"  # Native Python return
                
                # Use the native functions
                total = calculate_sum(5, 3)
                msg = get_message(total)
                
                # Frame handler return to interface
                return f"Total: {total}, Message: {msg}"
            }
            
            testNativeClasses(): int {
                # Native Python class inside handler
                class Counter:
                    def __init__(self):
                        self.value = 0
                    
                    def increment(self):
                        self.value += 1
                        return self.value  # Native Python method return
                    
                    def get_value(self):
                        return self.value  # Native Python method return
                
                # Use the native class
                counter = Counter()
                counter.increment()
                counter.increment()
                result = counter.get_value()
                
                # Frame handler return to interface
                return result
            }
            
            testLambdas(): list {
                # Native Python lambdas and list comprehensions
                # Lambda returns are native Python
                double = lambda x: x * 2
                is_even = lambda x: x % 2 == 0
                
                numbers = [1, 2, 3, 4, 5]
                
                # List comprehension with native returns
                doubled = [double(n) for n in numbers]
                evens = [n for n in doubled if is_even(n)]
                
                # Generator with native yield/return
                def make_generator():
                    for i in range(3):
                        yield i * 10  # Native Python yield
                
                gen_values = list(make_generator())
                
                # Frame handler return to interface
                result = [doubled, evens, gen_values]
                return result
            }
        }
}

# Native Python test code
import sys
sys.path.insert(0, '/opt/frame_runtime')

def test_native_code_returns():
    ncr = NativeCodeReturns()
    
    # Test 1: Native functions inside handlers
    result1 = ncr.testNativeFunctions()
    assert result1 == "Total: 8, Message: low", f"Expected 'Total: 8, Message: low', got {result1}"
    print("SUCCESS: Native function returns work correctly")
    
    # Test 2: Native classes inside handlers  
    result2 = ncr.testNativeClasses()
    assert result2 == 2, f"Expected 2, got {result2}"
    print("SUCCESS: Native class method returns work correctly")
    
    # Test 3: Lambdas and generators
    result3 = ncr.testLambdas()
    assert result3[0] == [2, 4, 6, 8, 10], f"Expected doubled list, got {result3[0]}"
    assert result3[1] == [2, 4, 6, 8, 10], f"Expected evens list, got {result3[1]}"
    assert result3[2] == [0, 10, 20], f"Expected generator values, got {result3[2]}"
    print("SUCCESS: Lambda and generator returns work correctly")
    
    print("\nAll native code return tests passed!")
    print("Key insight: Native code inside handlers remains native.")
    print("Only Frame-level returns (handler returns) use Frame semantics.")

test_native_code_returns()