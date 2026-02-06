@@target python_3

@@system TestInvalidReturn {
    interface:
        test(): int
        
    machine:
        $Start {
            test(): int {
                # This should cause a Python syntax error
                ^(42)
            }
        }
}