# CHANGELOG — datacube-layer (P13 DataCube)

CHANGELOG.md — build history for P13 DataCube, latest entry at top.

## [v2.0.0] — 2026-11-12

### Good
- Laptop audit against SPEC.md: v1 tests 25/25, seven divergences
  found (NOTES D1–D7; D1–D5 closed in v2). `datacube.py` left untouched (Immutable Rule).
- `datacube_v2.py`: hardened layer specified in `SPEC_V2.md` before
  code, tests in `test_datacube_v2.py` (73) written before the
  implementation.
- Gate now only accepts UNKNOWN claims, requires non-empty str
  subject/object, and fails closed on corrupt memory entries.
- `inspection_grade` requires a real bool: `"no"` no longer grades
  CRYSTALLINE.
- Normalised comparison (NFKC, casefold, whitespace) plus a pluggable
  `contradicts` hook for semantic detection.
- Added `write_claim` (gate fires on write), `register_gate_rule`
  (P12 rules_v2 integration), `merge_cubes`, JSON serialisation.
- `conftest.py`: `pytest` passes from any working directory.
- Docs fixed: README status, CHANGELOG scaffold heading.
- 98/98 tests pass (v1 25, v2 73).

### Bad
- v1 `datacube.py` keeps D1–D5 by design; new code must import
  `datacube_v2`.
- No semantic model ships: only the hook. Trust weighting deferred.

### Ugly
- v1 `inspection_grade` carries a redundant SPARSE condition (D6).
  Harmless; left frozen.

## [v1.0.0] — 2026-11-12

### Good
- `datacube.py` implemented to SPEC v1.0.0.
- 25/25 pytest tests pass.
- Six faces: FACT, COUNTER, OPINION, FICTION, CONTEXT, UNKNOWN.
- Inspection grades: CRYSTALLINE, COHERENT, FORMING, SPARSE.
- Keystone Gate rejects UNKNOWN claims that contradict FACT/COUNTER/CONTEXT.

### Bad
- (none)

### Ugly
- (none)

## [v0.0.0] — scaffold

### Good
- Repository scaffolded: `Giblet-Legacy/datacube-layer` created for P13.
- Depends on P12 Rules v1.0.0 and P14 Leighton Engine v1.0.0.

### Bad
- (none)

### Ugly
- (none)
