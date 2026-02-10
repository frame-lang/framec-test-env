@@target python_3

@@system WithParams {
    interface:
        start(initial)
        add(value)

    machine:
        $Idle {
            start(initial) {
                -> $Running
            }
        }

        $Running {
            add(value) {
            }
        }
}
