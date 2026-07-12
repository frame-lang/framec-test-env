# Intentional skip — segmenter coverage target-uniform

The segmenter's tokenization / brace-handling / comment-tracking logic is target-uniform within each comment-syntax family. The matrix corpus has fixtures in the `//` C-family (c, cpp, dart, js, swift, ts — 6 fixtures), the `#` family (gd, py, rb, lua — 4), and the `%` family (erl — 1). Adding this backend's fixture would duplicate coverage that already exists in its comment-syntax family.

See `docs/partial-coverage-audit.md`.
