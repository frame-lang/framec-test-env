// Single-process .NET test dispatcher for the C# backend.
//
// Reads a TSV manifest produced by csharp_batch.sh, then reflectively
// invokes each test's `frametest.<sanitized>.Program.Main()` inside the
// same runtime — so the ~1-2s dotnet cold start is paid once instead of
// once per test. TAP pass/fail rules match runner.sh.

using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public static class TestRunner {

    static readonly int TIMEOUT_SEC =
        int.TryParse(Environment.GetEnvironmentVariable("CSHARP_TEST_TIMEOUT"), out var v) ? v : 30;

    public static int Main(string[] args) {
        if (args.Length == 0) {
            Console.Error.WriteLine("usage: TestRunner <manifest.tsv>");
            return 2;
        }
        if (!File.Exists(args[0])) {
            Console.Error.WriteLine($"manifest not found: {args[0]}");
            return 2;
        }

        var originalOut = Console.Out;
        var asm = Assembly.GetExecutingAssembly();

        int pass = 0, fail = 0, skip = 0;
        foreach (var raw in File.ReadAllLines(args[0])) {
            if (string.IsNullOrWhiteSpace(raw)) continue;
            var parts = raw.Split('\t');
            if (parts.Length < 3) continue;
            var testNum = parts[0];
            var status = parts[1];
            var testName = parts[2];
            var mainClass = parts.Length > 3 ? parts[3] : "";
            var extra = parts.Length > 4 ? parts[4] : "";

            switch (status) {
                case "SKIP":
                    originalOut.WriteLine($"ok {testNum} - {testName} # SKIP");
                    skip++;
                    break;
                case "TRANSPILE_ERROR_OK":
                    originalOut.WriteLine($"ok {testNum} - {testName} # correctly rejected by transpiler");
                    pass++;
                    break;
                case "TRANSPILE_FAIL":
                    originalOut.WriteLine($"not ok {testNum} - {testName} # transpile failed");
                    if (extra.Length > 0) {
                        foreach (var line in extra.Split("\\n").Take(5)) {
                            originalOut.WriteLine("  # " + line);
                        }
                    }
                    fail++;
                    break;
                case "NO_OUTPUT":
                    originalOut.WriteLine($"not ok {testNum} - {testName} # no output file");
                    fail++;
                    break;
                case "COMPILE_ONLY":
                    originalOut.WriteLine($"ok {testNum} - {testName} # transpiled");
                    pass++;
                    break;
                case "COMPILE_FAIL":
                    originalOut.WriteLine($"not ok {testNum} - {testName} # dotnet build failed");
                    fail++;
                    break;
                case "RUN":
                    var r = RunOne(asm, mainClass);
                    if (ReportResult(originalOut, testNum, testName, r)) pass++; else fail++;
                    break;
                default:
                    originalOut.WriteLine($"not ok {testNum} - {testName} # unknown status {status}");
                    fail++;
                    break;
            }
            originalOut.Flush();
        }

        originalOut.WriteLine();
        originalOut.WriteLine($"# csharp: {pass} passed, {fail} failed, {skip} skipped");
        originalOut.Flush();
        return fail == 0 ? 0 : 1;
    }

    record TestResult(int ExitCode, string Output, bool TimedOut);

    static TestResult RunOne(Assembly asm, string mainClass) {
        var buf = new StringBuilder();
        var writer = new StringWriter(buf);
        var savedOut = Console.Out;
        var savedErr = Console.Error;

        int code = 0;
        bool timedOut = false;

        // Redirect BEFORE queuing the task. Task.Run schedules on the
        // thread pool, but the test body may begin executing before the
        // main thread reaches SetOut — causing early Console.WriteLine
        // calls to leak to the real stdout (showing up as phantom TAP
        // lines like "ok 1 - mealy_machine" in the outer TAP stream and
        // breaking the integrity check).
        Console.SetOut(writer);
        Console.SetError(writer);
        try {
            var task = Task.Run(() => {
                try {
                    var type = asm.GetType(mainClass);
                    if (type == null) {
                        writer.WriteLine($"type not found: {mainClass}");
                        code = 1;
                        return;
                    }
                    var mi = type.GetMethod("Main", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static);
                    if (mi == null) {
                        writer.WriteLine($"Main method not found on {mainClass}");
                        code = 1;
                        return;
                    }
                    var pars = mi.GetParameters();
                    object?[] invokeArgs =
                        pars.Length == 0 ? Array.Empty<object?>()
                        : new object?[] { Array.Empty<string>() };
                    var result = mi.Invoke(null, invokeArgs);
                    if (result is int ic) code = ic;
                } catch (TargetInvocationException e) {
                    writer.WriteLine(e.InnerException?.ToString() ?? e.ToString());
                    code = 1;
                } catch (Exception e) {
                    writer.WriteLine(e.ToString());
                    code = 1;
                }
            });

            if (!task.Wait(TimeSpan.FromSeconds(TIMEOUT_SEC))) {
                timedOut = true;
                code = 124;
            }
        } finally {
            Console.Out.Flush();
            Console.SetOut(savedOut);
            Console.SetError(savedErr);
        }
        return new TestResult(code, buf.ToString(), timedOut);
    }

    static bool ReportResult(TextWriter tap, string num, string name, TestResult r) {
        var output = r.Output ?? "";
        if (r.TimedOut) {
            tap.WriteLine($"not ok {num} - {name} # TIMEOUT");
            return false;
        }
        if (r.ExitCode != 0) {
            tap.WriteLine($"not ok {num} - {name} # runtime error (exit {r.ExitCode})");
            EmitLines(tap, output, 5);
            return false;
        }
        var lines = output.Split('\n');
        if (lines.Any(l => l.StartsWith("not ok "))) {
            tap.WriteLine($"not ok {num} - {name}");
            return false;
        }
        if (lines.Any(l => l.StartsWith("ok ") || l.Contains("PASS"))) {
            tap.WriteLine($"ok {num} - {name}");
            return true;
        }
        if (string.IsNullOrWhiteSpace(output)) {
            tap.WriteLine($"ok {num} - {name} # clean exit");
            return true;
        }
        tap.WriteLine($"not ok {num} - {name} # unrecognized output");
        EmitLines(tap, output, 3);
        return false;
    }

    static void EmitLines(TextWriter w, string s, int max) {
        var n = 0;
        foreach (var line in s.Split('\n')) {
            if (n >= max) break;
            w.WriteLine("  # " + line);
            n++;
        }
    }
}
