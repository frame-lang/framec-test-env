// Multi-source port of demos/39_tagged_instantiation.fjava.
// The original .fjava had two @@system blocks in one file, which
// framec rejects on Java with E430. Each system now lives in its
// own .fjava → public class file in this dir; Main.java is the
// driver.

public class Main {
    public static void main(String[] args) {
        System.out.println("=== Test 39: Tagged System Instantiation ===");

        Calculator calc = new Calculator();
        Counter counter = new Counter();

        // Test Calculator
        int result = (int) calc.add(3, 4);
        if (result != 7) {
            System.out.println("FAIL: Expected 7, got " + result);
            System.exit(1);
        }
        System.out.println("Calculator.add(3, 4) = " + result);

        result = (int) calc.get_result();
        if (result != 7) {
            System.out.println("FAIL: Expected 7, got " + result);
            System.exit(1);
        }
        System.out.println("Calculator.get_result() = " + result);

        // Test Counter
        counter.increment();
        counter.increment();
        counter.increment();
        int count = (int) counter.get_count();
        if (count != 3) {
            System.out.println("FAIL: Expected 3, got " + count);
            System.exit(1);
        }
        System.out.println("Counter after 3 increments: " + count);

        System.out.println("PASS");
    }
}
