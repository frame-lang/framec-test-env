<?php
// Single-process PHP test dispatcher. Each test is included into a fresh
// anonymous scope via an include-inside-a-function trick; stdout/stderr
// captured via ob_start. One PHP interpreter covers all tests.

declare(strict_types=1);

$timeout = (int)(getenv('PHP_TEST_TIMEOUT') ?: '30');

function run_one(string $path, int $timeout): array {
    // Capture stdout into an ob buffer. PHP has no hard per-call timeout
    // below signal-based or pcntl_alarm — acceptable since tests are
    // expected to be short. A soft deadline is enforced after the fact.
    ob_start();
    $start = microtime(true);
    $code = 0;
    $timed_out = false;
    try {
        (function($__p) { require $__p; })($path);
    } catch (\Throwable $e) {
        echo "\n", (string)$e, "\n";
        $code = 1;
    }
    $output = ob_get_clean();
    $elapsed = microtime(true) - $start;
    if ($elapsed > $timeout) {
        $timed_out = true;
        $code = 124;
    }
    return [$code, $output, $timed_out];
}

function emit_lines(string $s, int $max): void {
    $n = 0;
    foreach (preg_split('/\r?\n/', $s) as $line) {
        if ($n >= $max) break;
        echo "  # ", $line, "\n";
        $n++;
    }
}

function report(string $num, string $name, int $code, string $out, bool $timed_out): bool {
    if ($timed_out) { echo "not ok $num - $name # TIMEOUT\n"; return false; }
    if ($code !== 0) {
        echo "not ok $num - $name # runtime error (exit $code)\n";
        emit_lines($out, 5);
        return false;
    }
    $lines = preg_split('/\r?\n/', $out);
    foreach ($lines as $l) {
        if (str_starts_with($l, 'not ok ')) { echo "not ok $num - $name\n"; return false; }
    }
    foreach ($lines as $l) {
        if (str_starts_with($l, 'ok ') || str_contains($l, 'PASS')) {
            echo "ok $num - $name\n"; return true;
        }
    }
    if (trim($out) === '') { echo "ok $num - $name # clean exit\n"; return true; }
    echo "not ok $num - $name # unrecognized output\n";
    emit_lines($out, 3);
    return false;
}

$argvv = $_SERVER['argv'];
if (count($argvv) < 2) { fwrite(STDERR, "usage: php TestRunner.php <manifest.tsv>\n"); exit(2); }
$manifest = $argvv[1];
if (!is_file($manifest)) { fwrite(STDERR, "manifest not found: $manifest\n"); exit(2); }

$pass = 0; $fail = 0; $skip = 0;
$fh = fopen($manifest, 'r');
while (($raw = fgets($fh)) !== false) {
    $raw = rtrim($raw, "\n");
    if (trim($raw) === '') continue;
    $parts = explode("\t", $raw);
    if (count($parts) < 3) continue;
    [$num, $status, $name] = array_slice($parts, 0, 3);
    $path = $parts[3] ?? '';
    $extra = $parts[4] ?? '';

    switch ($status) {
        case 'SKIP':
            echo "ok $num - $name # SKIP\n"; $skip++; break;
        case 'TRANSPILE_ERROR_OK':
            echo "ok $num - $name # correctly rejected by transpiler\n"; $pass++; break;
        case 'TRANSPILE_FAIL':
            echo "not ok $num - $name # transpile failed\n";
            if ($extra !== '') foreach (array_slice(explode('\\n', $extra), 0, 5) as $l) echo "  # $l\n";
            $fail++; break;
        case 'NO_OUTPUT':
            echo "not ok $num - $name # no output file\n"; $fail++; break;
        case 'COMPILE_ONLY':
            echo "ok $num - $name # transpiled\n"; $pass++; break;
        case 'RUN':
            [$code, $out, $to] = run_one($path, $timeout);
            if (report($num, $name, $code, $out, $to)) $pass++;
            else $fail++;
            break;
        default:
            echo "not ok $num - $name # unknown status $status\n"; $fail++;
    }
    @ob_flush();
}
fclose($fh);

echo "\n";
echo "# php: $pass passed, $fail failed, $skip skipped\n";
exit($fail === 0 ? 0 : 1);
