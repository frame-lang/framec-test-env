// Single-JVM test dispatcher for the Java backend.
//
// Mirrors TestRunner.kt: reads a TSV manifest built by java_batch.sh
// and reflectively invokes each test's `Main.main()` in the same JVM,
// so the cost of JVM startup is paid once instead of once per test.
// TAP pass/fail rules match runner.sh.

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileReader;
import java.io.PrintStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CancellationException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class TestRunner {

    static final long TIMEOUT_SEC = parseLong(System.getenv("JAVA_TEST_TIMEOUT"), 30L);
    static final PrintStream TAP_OUT = System.out;

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("usage: java TestRunner <manifest.tsv>");
            System.exit(2);
        }
        File manifest = new File(args[0]);
        if (!manifest.exists()) {
            System.err.println("manifest not found: " + manifest.getPath());
            System.exit(2);
        }

        ExecutorService exec = Executors.newCachedThreadPool(r -> {
            Thread t = new Thread(r);
            t.setDaemon(true);
            t.setName("java-test-worker");
            return t;
        });

        int pass = 0, fail = 0, skip = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(manifest))) {
            String raw;
            while ((raw = br.readLine()) != null) {
                if (raw.isBlank()) continue;
                String[] parts = raw.split("\t", -1);
                if (parts.length < 3) continue;
                String testNum = parts[0];
                String status = parts[1];
                String testName = parts[2];
                String mainClass = parts.length > 3 ? parts[3] : "";
                String extra = parts.length > 4 ? parts[4] : "";

                switch (status) {
                    case "SKIP":
                        TAP_OUT.println("ok " + testNum + " - " + testName + " # SKIP");
                        skip++;
                        break;
                    case "TRANSPILE_ERROR_OK":
                        TAP_OUT.println("ok " + testNum + " - " + testName + " # correctly rejected by transpiler");
                        pass++;
                        break;
                    case "TRANSPILE_FAIL":
                        TAP_OUT.println("not ok " + testNum + " - " + testName + " # transpile failed");
                        if (!extra.isEmpty()) {
                            for (String line : extra.split("\\\\n", 5)) {
                                TAP_OUT.println("  # " + line);
                            }
                        }
                        fail++;
                        break;
                    case "NO_OUTPUT":
                        TAP_OUT.println("not ok " + testNum + " - " + testName + " # no output file");
                        fail++;
                        break;
                    case "NO_DRIVER":
                        TAP_OUT.println("not ok " + testNum + " - " + testName + " # multi-source case missing Main.java");
                        fail++;
                        break;
                    case "COMPILE_ONLY":
                        TAP_OUT.println("ok " + testNum + " - " + testName + " # transpiled");
                        pass++;
                        break;
                    case "COMPILE_FAIL":
                        TAP_OUT.println("not ok " + testNum + " - " + testName + " # javac failed");
                        fail++;
                        break;
                    case "RUN":
                        TestResult result = runOne(mainClass, exec);
                        if (reportResult(testNum, testName, result)) pass++;
                        else fail++;
                        break;
                    default:
                        TAP_OUT.println("not ok " + testNum + " - " + testName + " # unknown status " + status);
                        fail++;
                }
                TAP_OUT.flush();
            }
        }

        TAP_OUT.println();
        TAP_OUT.println("# java: " + pass + " passed, " + fail + " failed, " + skip + " skipped");
        TAP_OUT.flush();
        exec.shutdownNow();
        System.exit(fail == 0 ? 0 : 1);
    }

    static final class TestResult {
        final int exitCode;
        final String output;
        final boolean timedOut;

        TestResult(int exitCode, String output, boolean timedOut) {
            this.exitCode = exitCode;
            this.output = output;
            this.timedOut = timedOut;
        }
    }

    static TestResult runOne(String mainClass, ExecutorService exec) {
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream(buf, true, StandardCharsets.UTF_8);

        Future<Integer> task = exec.submit(() -> {
            PrintStream savedOut = System.out;
            PrintStream savedErr = System.err;
            System.setOut(ps);
            System.setErr(ps);
            try {
                Class<?> cls = Class.forName(mainClass);
                Method m = cls.getMethod("main", String[].class);
                // Framec emits Main as a package-private class. The method
                // is public static but the enclosing class is not, so
                // reflection needs setAccessible(true) to bypass the
                // class-level access check.
                m.setAccessible(true);
                m.invoke(null, (Object) new String[0]);
                return 0;
            } catch (InvocationTargetException e) {
                Throwable cause = e.getTargetException();
                cause.printStackTrace(ps);
                return 1;
            } catch (Throwable e) {
                e.printStackTrace(ps);
                return 1;
            } finally {
                ps.flush();
                System.setOut(savedOut);
                System.setErr(savedErr);
            }
        });

        try {
            int code = task.get(TIMEOUT_SEC, TimeUnit.SECONDS);
            return new TestResult(code, buf.toString(StandardCharsets.UTF_8), false);
        } catch (TimeoutException e) {
            task.cancel(true);
            return new TestResult(124, buf.toString(StandardCharsets.UTF_8), true);
        } catch (ExecutionException e) {
            return new TestResult(1, buf.toString(StandardCharsets.UTF_8) + "\n" + e.getCause(), false);
        } catch (CancellationException e) {
            return new TestResult(1, buf.toString(StandardCharsets.UTF_8), false);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return new TestResult(1, buf.toString(StandardCharsets.UTF_8), false);
        }
    }

    static boolean reportResult(String testNum, String testName, TestResult r) {
        String output = r.output == null ? "" : r.output;
        if (r.timedOut) {
            TAP_OUT.println("not ok " + testNum + " - " + testName + " # TIMEOUT");
            return false;
        }
        if (r.exitCode != 0) {
            TAP_OUT.println("not ok " + testNum + " - " + testName + " # runtime error (exit " + r.exitCode + ")");
            emitLines(output, 5);
            return false;
        }
        for (String line : output.split("\n", -1)) {
            if (line.startsWith("not ok ")) {
                TAP_OUT.println("not ok " + testNum + " - " + testName);
                return false;
            }
        }
        for (String line : output.split("\n", -1)) {
            if (line.startsWith("ok ") || line.contains("PASS")) {
                TAP_OUT.println("ok " + testNum + " - " + testName);
                return true;
            }
        }
        if (output.isBlank()) {
            TAP_OUT.println("ok " + testNum + " - " + testName + " # clean exit");
            return true;
        }
        TAP_OUT.println("not ok " + testNum + " - " + testName + " # unrecognized output");
        emitLines(output, 3);
        return false;
    }

    static void emitLines(String s, int max) {
        int count = 0;
        for (String line : s.split("\n", -1)) {
            if (count >= max) break;
            TAP_OUT.println("  # " + line);
            count++;
        }
    }

    static long parseLong(String s, long def) {
        if (s == null) return def;
        try { return Long.parseLong(s); } catch (NumberFormatException e) { return def; }
    }
}
