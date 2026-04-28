// Multi-source port of demos/28_auth_flow.fjava.

public class Main {
    public static void main(String[] args) {
        App app = new App();
        int failures = 0;

        if (!app.app_status().equals("unauthenticated")) {
            System.out.println("FAIL: initial app_status expected unauthenticated");
            failures++;
        }

        String r1 = app.authenticate("user", "wrong");
        if (!r1.equals("denied")) {
            System.out.println("FAIL: bad login expected denied");
            failures++;
        }

        if (!app.app_status().equals("unauthenticated")) {
            System.out.println("FAIL: still unauthenticated after bad login");
            failures++;
        }

        String r2 = app.authenticate("admin", "secret");
        if (!r2.equals("ok")) {
            System.out.println("FAIL: good login expected ok");
            failures++;
        }

        if (!app.app_status().equals("authenticated")) {
            System.out.println("FAIL: should be authenticated after good login");
            failures++;
        }

        if (failures > 0) {
            System.out.println("FAIL: auth_flow (" + failures + " failures)");
            System.exit(1);
        }
        System.out.println("PASS: auth_flow");
    }
}
