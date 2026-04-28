// Multi-source port of demos/20_multi_system_composition.fjava.

public class Main {
    public static void main(String[] args) {
        App app = new App();
        app.start();
        app.stop();
        System.out.println("PASS: multi_system_composition");
    }
}
