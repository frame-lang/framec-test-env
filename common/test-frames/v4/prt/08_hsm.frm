@@target python_3

@@system HSMForward {
    interface:
        event_a()
        event_b()

    machine:
        $Parent {
            event_a() {
            }

            event_b() {
            }
        }

        $Child => $Parent {
            event_a() {
            }

            event_b() {
                => $^
            }
        }
}
