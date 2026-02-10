@@target python_3

@@system DomainVars {
    interface:
        increment()

    machine:
        $Counting {
            increment() {
            }
        }

    domain:
        var count = 0
}
