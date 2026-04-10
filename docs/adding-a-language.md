# Adding a Language to the Test Environment

When a new language backend is added to the framepiler, follow these steps to add test coverage.

## 1. Create the Dockerfile

Create `docker/base/<lang>/Dockerfile`:

```dockerfile
FROM <official-base-image>
RUN <install any extra dependencies> && mkdir -p /tests /output
COPY runners/runner.sh /runner.sh
RUN chmod +x /runner.sh
ENTRYPOINT ["/runner.sh"]
CMD ["<lang-name>"]
```

Choose a Debian/Ubuntu-based image (not Alpine — the framec binary is glibc-linked).

## 2. Add Runner Support

Edit `docker/runners/runner.sh`. Add two entries:

### Language config (near the top):

```bash
    <lang>) target="<framec-target>"; ext="<frame-ext>"; out_ext="<output-ext>" ;;
```

Example: `kotlin) target="kotlin"; ext="fkt"; out_ext="kt" ;;`

### Compile and run (in the case statement):

```bash
        <lang>)
            # Compile step (if needed)
            if <compile-command> "$out_file" 2>&1; then
                run_output=$(<run-command> 2>&1) || run_status=$?
            else
                run_status=1
                run_output="compile failed"
            fi
            ;;
```

For interpreted languages (no compile step):

```bash
        <lang>)
            run_output=$(<interpreter> "$out_file" 2>&1) || run_status=$?
            ;;
```

## 3. Add Compose Service

Edit `docker/docker-compose.yml`:

```yaml
  <lang>:
    build: { context: ., dockerfile: base/<lang>/Dockerfile }
    environment: *env
    volumes: [*framec, *tests, "../output/<lang>:/output"]
```

## 4. Create Test Files

Add per-language test files with the new extension to each test category:

```
tests/common/positive/primary/01_interface_return.f<ext>
tests/common/positive/control_flow/transition_basic.f<ext>
...
```

Each file needs the `@@target <lang>` pragma and a native test harness epilog.

## 5. Build and Verify

```bash
cd docker/
FRAMEC_BIN=/dev/null docker compose build <lang>
FRAMEC_BIN=$(pwd)/framec-linux docker compose run --rm <lang>
```

## Checklist

- [ ] `docker/base/<lang>/Dockerfile` created
- [ ] `docker/runners/runner.sh` — language config + compile/run case added
- [ ] `docker/docker-compose.yml` — service added
- [ ] Test files created with `.<ext>` extension
- [ ] `FRAMEC_BIN=/dev/null docker compose build <lang>` succeeds
- [ ] `FRAMEC_BIN=... docker compose run --rm <lang>` shows all tests passing
