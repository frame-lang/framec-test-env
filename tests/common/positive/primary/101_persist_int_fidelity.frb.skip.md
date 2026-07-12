# Intentional skip — dynamic int/float fidelity only

Probes the int-vs-float representation ambiguity that only arises on dynamically-typed backends: after a persist round-trip, does an integer domain field deserialize back as an int (not a float)? GDScript and Lua are the two dynamic backends where the JSON number path can silently promote `42` to `42.0`. On statically-typed backends the field's declared type pins the representation, so there is nothing to probe.

See `docs/partial-coverage-audit.md`.
