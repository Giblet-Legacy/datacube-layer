# P13 DataCube — Laptop Audit Prompt

P13 datacube-layer is frozen at v1.0.0 on the phone with 25/25 tests passing.

## Your Task

1. Pull `Giblet-Legacy/datacube-layer`.
2. Audit against SPEC.md and CHANGELOG.md.
3. Run `pytest -q` — expect 25 passed.
4. If you find gaps, create `datacube_v2.py` (do NOT edit v1).
5. Suggested V2 hardening: semantic contradiction detection (beyond string equality), integrate the gate with P12 rules engine so a match fires an action, support cube merging (multiple cubes for the same subject over time), add JSON serialisation for cubes.
6. Push when green so the phone can verify.
