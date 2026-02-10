@@target python_3

@@system StackOps {
    interface:
        push_state()
        pop_state()
        do_work()

    machine:
        $Main {
            push_state() {
                $$[+]
                -> $Sub
            }

            do_work() {
            }
        }

        $Sub {
            pop_state() {
                $$[-]
            }

            do_work() {
            }
        }
}
