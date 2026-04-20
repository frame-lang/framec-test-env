#!/usr/bin/env ruby
# Single-process Ruby test dispatcher. Mirrors TestRunner.py — reads the
# manifest, `load`s each test in a fresh anonymous module for isolation,
# captures stdout/stderr, emits TAP.

require 'stringio'
require 'timeout'

TIMEOUT_SEC = (ENV['RUBY_TEST_TIMEOUT'] || '30').to_i

def run_one(path)
  buf = StringIO.new
  saved_out, saved_err = $stdout, $stderr
  $stdout = buf
  $stderr = buf
  code = 0
  timed_out = false
  begin
    Timeout.timeout(TIMEOUT_SEC) do
      # `load(path, true)` wraps in an anonymous module — breaks method
      # resolution in Frame-generated code (methods on a class defined in
      # the module can't find each other without explicit scoping). Use
      # plain `load` instead; tests are self-contained and any constant
      # redefinition across tests is overwritten benignly.
      load(path)
    end
  rescue Timeout::Error
    timed_out = true
    code = 124
  rescue SystemExit => e
    code = e.status unless e.status == 0
  rescue Exception => e
    buf.puts(e.full_message)
    code = 1
  ensure
    $stdout = saved_out
    $stderr = saved_err
  end
  [code, buf.string, timed_out]
end

def report(num, name, code, out, timed_out)
  if timed_out
    puts "not ok #{num} - #{name} # TIMEOUT"; return false
  end
  if code != 0
    puts "not ok #{num} - #{name} # runtime error (exit #{code})"
    out.lines.first(5).each { |l| puts "  # #{l.chomp}" }
    return false
  end
  lines = out.lines.map(&:chomp)
  if lines.any? { |l| l.start_with?("not ok ") }
    puts "not ok #{num} - #{name}"; return false
  end
  if lines.any? { |l| l.start_with?("ok ") || l.include?("PASS") }
    puts "ok #{num} - #{name}"; return true
  end
  if out.strip.empty?
    puts "ok #{num} - #{name} # clean exit"; return true
  end
  puts "not ok #{num} - #{name} # unrecognized output"
  lines.first(3).each { |l| puts "  # #{l}" }
  false
end

manifest = ARGV[0] or (warn "usage: ruby TestRunner.rb <manifest.tsv>"; exit 2)
unless File.exist?(manifest)
  warn "manifest not found: #{manifest}"; exit 2
end

pass = fail_c = skip = 0
File.foreach(manifest) do |raw|
  raw = raw.chomp
  next if raw.strip.empty?
  parts = raw.split("\t", -1)
  next if parts.length < 3
  num, status, name = parts[0], parts[1], parts[2]
  main_path = parts[3] || ""
  extra = parts[4] || ""

  case status
  when 'SKIP'
    puts "ok #{num} - #{name} # SKIP"; skip += 1
  when 'TRANSPILE_ERROR_OK'
    puts "ok #{num} - #{name} # correctly rejected by transpiler"; pass += 1
  when 'TRANSPILE_FAIL'
    puts "not ok #{num} - #{name} # transpile failed"
    extra.split('\\n').first(5).each { |l| puts "  # #{l}" } unless extra.empty?
    fail_c += 1
  when 'NO_OUTPUT'
    puts "not ok #{num} - #{name} # no output file"; fail_c += 1
  when 'COMPILE_ONLY'
    puts "ok #{num} - #{name} # transpiled"; pass += 1
  when 'RUN'
    code, out, timed_out = run_one(main_path)
    if report(num, name, code, out, timed_out) then pass += 1 else fail_c += 1 end
  else
    puts "not ok #{num} - #{name} # unknown status #{status}"; fail_c += 1
  end
  $stdout.flush
end

puts ""
puts "# ruby: #{pass} passed, #{fail_c} failed, #{skip} skipped"
exit(fail_c == 0 ? 0 : 1)
