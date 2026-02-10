@@target python_3

@@system WithTransition {
    interface:
        next()

    machine:
        $First {
            next() {
                -> $Second
            }
        }

        $Second {
            next() {
                -> $First
            }
        }
}
