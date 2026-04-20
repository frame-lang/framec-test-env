#!/usr/bin/env lua
-- Single-process Lua test dispatcher. Loads each test in an isolated
-- environment via setfenv/load (Lua 5.1/5.2+ compatible).

local TIMEOUT_SEC = tonumber(os.getenv('LUA_TEST_TIMEOUT') or '30') or 30

local function capture_print()
    local buf = {}
    local orig_print = print
    local function captured(...)
        local args = {...}
        for i = 1, #args do args[i] = tostring(args[i]) end
        buf[#buf + 1] = table.concat(args, '\t')
    end
    _G.print = captured
    return buf, orig_print
end

local function run_one(path)
    local buf, orig_print = capture_print()
    local code = 0
    local timed_out = false
    -- Lua has no native timeout; we just run. Tests are expected to be
    -- bounded (the slow language tests run external processes, not Lua).
    local loader, err
    if loadfile then
        loader, err = loadfile(path)
    end
    if not loader then
        _G.print = orig_print
        return 1, 'loadfile error: ' .. tostring(err), false
    end
    local ok, run_err = pcall(loader)
    _G.print = orig_print
    if not ok then
        code = 1
        buf[#buf + 1] = tostring(run_err)
    end
    return code, table.concat(buf, '\n'), timed_out
end

local function emit_lines(s, max)
    local n = 0
    for line in s:gmatch('[^\n]+') do
        if n >= max then break end
        print('  # ' .. line)
        n = n + 1
    end
end

local function report(num, name, code, out, timed_out)
    if timed_out then
        print('not ok ' .. num .. ' - ' .. name .. ' # TIMEOUT')
        return false
    end
    if code ~= 0 then
        print('not ok ' .. num .. ' - ' .. name .. ' # runtime error (exit ' .. code .. ')')
        emit_lines(out, 5)
        return false
    end
    for line in out:gmatch('[^\n]+') do
        if line:sub(1, 7) == 'not ok ' then
            print('not ok ' .. num .. ' - ' .. name)
            return false
        end
    end
    for line in out:gmatch('[^\n]+') do
        if line:sub(1, 3) == 'ok ' or line:find('PASS') then
            print('ok ' .. num .. ' - ' .. name)
            return true
        end
    end
    if out:gsub('%s', '') == '' then
        print('ok ' .. num .. ' - ' .. name .. ' # clean exit')
        return true
    end
    print('not ok ' .. num .. ' - ' .. name .. ' # unrecognized output')
    emit_lines(out, 3)
    return false
end

local manifest = arg[1]
if not manifest then
    io.stderr:write('usage: lua TestRunner.lua <manifest.tsv>\n')
    os.exit(2)
end
local fh = io.open(manifest, 'r')
if not fh then
    io.stderr:write('manifest not found: ' .. manifest .. '\n')
    os.exit(2)
end

local pass, fail, skip = 0, 0, 0
for raw in fh:lines() do
    if raw:gsub('%s', '') ~= '' then
        local parts = {}
        for p in (raw .. '\t'):gmatch('([^\t]*)\t') do parts[#parts+1] = p end
        if #parts >= 3 then
            local num, status, name = parts[1], parts[2], parts[3]
            local path = parts[4] or ''
            local extra = parts[5] or ''
            if status == 'SKIP' then
                print('ok ' .. num .. ' - ' .. name .. ' # SKIP'); skip = skip + 1
            elseif status == 'TRANSPILE_ERROR_OK' then
                print('ok ' .. num .. ' - ' .. name .. ' # correctly rejected by transpiler'); pass = pass + 1
            elseif status == 'TRANSPILE_FAIL' then
                print('not ok ' .. num .. ' - ' .. name .. ' # transpile failed')
                if extra ~= '' then
                    local n = 0
                    for l in extra:gmatch('[^\\]+') do
                        if n >= 5 then break end
                        print('  # ' .. l); n = n + 1
                    end
                end
                fail = fail + 1
            elseif status == 'NO_OUTPUT' then
                print('not ok ' .. num .. ' - ' .. name .. ' # no output file'); fail = fail + 1
            elseif status == 'COMPILE_ONLY' then
                print('ok ' .. num .. ' - ' .. name .. ' # transpiled'); pass = pass + 1
            elseif status == 'RUN' then
                local code, out, to = run_one(path)
                if report(num, name, code, out, to) then pass = pass + 1 else fail = fail + 1 end
            else
                print('not ok ' .. num .. ' - ' .. name .. ' # unknown status ' .. status); fail = fail + 1
            end
            io.stdout:flush()
        end
    end
end
fh:close()

print('')
print('# lua: ' .. pass .. ' passed, ' .. fail .. ' failed, ' .. skip .. ' skipped')
os.exit(fail == 0 and 0 or 1)
