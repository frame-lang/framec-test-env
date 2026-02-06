@@target typescript
@@visitor-map-golden: origins=frame; min=1

@@system S {
    machine:
        $A {
            e() {
                let x = 1;
                -> $B()
            }
        }
        $B {
            e() { }
        }
}
