@@target typescript
// @frame-map-golden: origins=frame
// @visitor-map-golden: origins=frame; min=1

@@system S {
    machine:
        $A {
            e() {
                native()
                -> $B()
            }
        }
        $B { }
}
