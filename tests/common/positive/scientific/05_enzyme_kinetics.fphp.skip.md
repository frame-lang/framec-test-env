# Intentional skip — Python-seeded RNG inside FSM handlers

This recipe calls Python's `random.random()` inside Frame handler
bodies and asserts deterministic numeric signatures keyed off
`random.seed(N)`:

```python
random.seed(7)
...
check("seed=7 signature", results, [281, 871, 1996])
```

These signatures don't port across languages because each target
has a different PRNG algorithm. Identical seeds produce different
streams in Java/Go/.NET/Rust/etc. than in Python.

To port, the recipe needs one of:

1. **Frame-side LCG**: replace `random.random()` with a deterministic
   LCG (multiplier/seed/state in the domain).
2. **Driver-decoupled RNG**: have `tick(rand: float)` accept the
   random value, move the RNG to the per-language driver.
3. **Relax assertions**: drop deterministic signatures, keep only
   monotonic / structural invariants.

Cross-ref: framec `_scratch/FRAMEC_BUGS.md` Issue #11.
