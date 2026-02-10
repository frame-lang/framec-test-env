@@target python_3

@@system EnterExit {
    interface:
        toggle()

    machine:
        $Off {
            $>() {
            }

            $<() {
            }

            toggle() {
                -> $On
            }
        }

        $On {
            $>() {
            }

            $<() {
            }

            toggle() {
                -> $Off
            }
        }
}
