@@target python_3

@@system NativeCode {
    interface:
        process()

    machine:
        $Active {
            process() {
                -> $Active
            }
        }
}
