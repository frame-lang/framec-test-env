@@target python_3

@@system WithInterface {
    interface:
        greet()

    machine:
        $Ready {
            greet() {
            }
        }
}
