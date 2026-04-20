// Single-JVM test dispatcher for Kotlin backend tests.
//
// Reads a TSV manifest built by kotlin_batch.sh (one row per test), then
// reflectively invokes each test's generated `MainKt.main()` in the same
// JVM — so the cost of JVM + Kotlin stdlib startup is paid once instead
// of once per test. Mirrors runner.sh's TAP pass/fail rules so output is
// drop-in compatible with the rest of the framework.

import java.io.BufferedReader
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileReader
import java.io.PrintStream
import java.lang.reflect.InvocationTargetException
import java.util.concurrent.CancellationException
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

private data class TestResult(val exitCode: Int, val output: String, val timedOut: Boolean)

fun main(args: Array<String>) {
    if (args.isEmpty()) {
        System.err.println("usage: TestRunnerKt <manifest.tsv>")
        kotlin.system.exitProcess(2)
    }
    val manifest = File(args[0])
    if (!manifest.exists()) {
        System.err.println("manifest not found: ${manifest.path}")
        kotlin.system.exitProcess(2)
    }

    val originalOut = System.out
    val timeoutSec = System.getenv("KOTLIN_TEST_TIMEOUT")?.toLongOrNull() ?: 30L

    val executor = Executors.newCachedThreadPool { r ->
        Thread(r).apply { isDaemon = true; name = "kotlin-test-worker" }
    }

    var pass = 0
    var fail = 0
    var skip = 0

    BufferedReader(FileReader(manifest)).useLines { lines ->
        for (raw in lines) {
            if (raw.isBlank()) continue
            val parts = raw.split("\t")
            if (parts.size < 3) continue
            val testNum = parts[0]
            val status = parts[1]
            val testName = parts[2]
            val mainClass = parts.getOrNull(3).orEmpty()
            val extra = parts.getOrNull(4).orEmpty()

            when (status) {
                "SKIP" -> {
                    originalOut.println("ok $testNum - $testName # SKIP")
                    skip++
                }
                "TRANSPILE_ERROR_OK" -> {
                    originalOut.println("ok $testNum - $testName # correctly rejected by transpiler")
                    pass++
                }
                "TRANSPILE_FAIL" -> {
                    originalOut.println("not ok $testNum - $testName # transpile failed")
                    if (extra.isNotEmpty()) {
                        extra.split("\\n").take(5).forEach { originalOut.println("  # $it") }
                    }
                    fail++
                }
                "NO_OUTPUT" -> {
                    originalOut.println("not ok $testNum - $testName # no output file")
                    fail++
                }
                "COMPILE_ONLY" -> {
                    originalOut.println("ok $testNum - $testName # transpiled")
                    pass++
                }
                "COMPILE_FAIL" -> {
                    originalOut.println("not ok $testNum - $testName # kotlinc failed")
                    fail++
                }
                "RUN" -> {
                    val result = runOne(mainClass, timeoutSec, executor)
                    val passed = reportResult(testNum, testName, result, originalOut)
                    if (passed) pass++ else fail++
                }
                else -> {
                    originalOut.println("not ok $testNum - $testName # unknown status $status")
                    fail++
                }
            }
            originalOut.flush()
        }
    }

    originalOut.println()
    originalOut.println("# kotlin: $pass passed, $fail failed, $skip skipped")
    originalOut.flush()

    executor.shutdownNow()
    kotlin.system.exitProcess(if (fail == 0) 0 else 1)
}

private fun runOne(mainClass: String, timeoutSec: Long, executor: java.util.concurrent.ExecutorService): TestResult {
    val capture = ByteArrayOutputStream()
    val ps = PrintStream(capture, true, Charsets.UTF_8)

    val task: Future<Int> = executor.submit<Int> {
        val savedOut = System.out
        val savedErr = System.err
        System.setOut(ps)
        System.setErr(ps)
        try {
            val cls = Class.forName(mainClass)
            val m = cls.getMethod("main", Array<String>::class.java)
            m.invoke(null, emptyArray<String>())
            0
        } catch (e: InvocationTargetException) {
            e.targetException.printStackTrace(ps)
            1
        } catch (e: Throwable) {
            e.printStackTrace(ps)
            1
        } finally {
            ps.flush()
            System.setOut(savedOut)
            System.setErr(savedErr)
        }
    }

    return try {
        val code = task.get(timeoutSec, TimeUnit.SECONDS)
        TestResult(code, capture.toString(Charsets.UTF_8), false)
    } catch (_: TimeoutException) {
        task.cancel(true)
        TestResult(124, capture.toString(Charsets.UTF_8), true)
    } catch (e: ExecutionException) {
        TestResult(1, capture.toString(Charsets.UTF_8) + "\n" + e.cause, false)
    } catch (_: CancellationException) {
        TestResult(1, capture.toString(Charsets.UTF_8), false)
    }
}

private fun reportResult(testNum: String, testName: String, r: TestResult, out: PrintStream): Boolean {
    val output = r.output
    return when {
        r.timedOut -> {
            out.println("not ok $testNum - $testName # TIMEOUT")
            false
        }
        r.exitCode != 0 -> {
            out.println("not ok $testNum - $testName # runtime error (exit ${r.exitCode})")
            output.lineSequence().take(5).forEach { out.println("  # $it") }
            false
        }
        output.lineSequence().any { it.startsWith("not ok ") } -> {
            out.println("not ok $testNum - $testName")
            false
        }
        output.lineSequence().any { it.startsWith("ok ") || it.contains("PASS") } -> {
            out.println("ok $testNum - $testName")
            true
        }
        output.isBlank() -> {
            out.println("ok $testNum - $testName # clean exit")
            true
        }
        else -> {
            out.println("not ok $testNum - $testName # unrecognized output")
            output.lineSequence().take(3).forEach { out.println("  # $it") }
            false
        }
    }
}
