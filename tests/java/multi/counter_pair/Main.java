// Multi-source driver for tests/java/multi/counter_pair.
//
// Java requires one public class per file, so Counter and DriverSys
// each live in their own .fjava → public class. The runner places
// every generated .java alongside this Main.java in the same
// frametest.<sanitized> package, so we can call them without
// qualification.

public class Main {
    public static void main(String[] args) {
        DriverSys driver = new DriverSys();

        // Three bumps on the embedded counter via the driver.
        driver.bump_inner();
        driver.bump_inner();
        driver.bump_inner();

        // Read back the embedded counter's value.
        Object countObj = driver.inner_count();
        int count = (int) countObj;

        if (count == 3) {
            System.out.println("PASS");
        } else {
            throw new RuntimeException("expected 3, got " + count);
        }
    }
}
