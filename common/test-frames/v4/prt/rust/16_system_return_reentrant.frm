@@target rust

@@system SystemReturnReentrantTest {
    interface:
        outer_call(): i32 = 0
        inner_call(): i32 = 0
        nested_call(): i32 = 0
        get_call_count(): i32

    machine:
        $Start {
            $.call_count: i32 = 0

            outer_call(): i32 {
                $.call_count = $.call_count + 1;
                // Call inner - creates nested return context
                let inner_result = self.inner_call();
                // Our return should be independent of inner's
                ^ 100 + inner_result
            }

            inner_call(): i32 {
                $.call_count = $.call_count + 1;
                ^ 10
            }

            nested_call(): i32 {
                $.call_count = $.call_count + 1;
                // Two levels of nesting
                let r1 = self.inner_call();
                let r2 = self.outer_call();
                ^ 1000 + r1 + r2
            }

            get_call_count(): i32 {
                ^ $.call_count
            }
        }
}

fn main() {
    println!("=== Test 16: System Return Reentrant (Rust) ===");

    // Test 1: Simple inner call
    let mut s1 = SystemReturnReentrantTest::new();
    let result = s1.inner_call();
    assert_eq!(result, 10, "Expected 10, got {}", result);
    println!("1. inner_call() = {}", result);

    // Test 2: Outer calls inner - contexts should be separate
    let mut s2 = SystemReturnReentrantTest::new();
    let result = s2.outer_call();
    // outer returns 100 + inner's 10 = 110
    assert_eq!(result, 110, "Expected 110, got {}", result);
    let count = s2.get_call_count();
    assert_eq!(count, 2, "Expected 2 calls, got {}", count);
    println!("2. outer_call() = {} (call_count = {})", result, count);

    // Test 3: Deeply nested
    let mut s3 = SystemReturnReentrantTest::new();
    let result = s3.nested_call();
    // nested: 1000 + inner(10) + outer(100 + inner(10)) = 1000 + 10 + 110 = 1120
    assert_eq!(result, 1120, "Expected 1120, got {}", result);
    let count = s3.get_call_count();
    assert_eq!(count, 4, "Expected 4 calls, got {}", count);
    println!("3. nested_call() = {} (call_count = {})", result, count);

    println!("PASS: System return reentrant works correctly");
}
