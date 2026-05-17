# 01_statement_disambiguator — skip

Recipe 110 (Statement Disambiguator) relies on Python-only data
abstractions that do not port uniformly across the 16 non-Python backends:

- Heterogeneous `dict` tokens (`{"kind": ..., "value": ...}`) shaped on the fly
- `set` membership for `is_type_name` lookup, defined as a domain field of
  type `set` and mutated from *outside* the system (`d.known_types = {...}`)
- `list`-typed interface argument with mixed element types
- `actions:` section helpers (`peek()`, `is_type_name()`) using these primitives

Porting cleanly would require redesigning the algorithm to use parallel
string arrays + hard-coded type membership. That changes the cookbook
intent (which is the bounded-lookahead **pattern**, not the type plumbing).

Skipped pending recipe rewrite. The Python-only canonical recipe stays
exercised on Python; the 16 other backends are intentionally out of scope.
