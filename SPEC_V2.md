# SPEC V2 — datacube-layer (P13 DataCube, hardened layer)

SPEC_V2.md — specification for datacube_v2.py, the layer above P13 v1.0.0.

Function:
    Specifies datacube_v2.py, a layer over the frozen P13 v1.0.0
    primitive (datacube.py). It closes divergences D1–D5 recorded in
    NOTES.md and adds the v2 options chosen in NOTES.md (normalised
    and pluggable contradiction, write-time gate, P12 rule
    integration, cube merging, JSON serialisation) without editing
    datacube.py (Immutable Rule).

    SPEC.md v1.0.0 remains authoritative for everything this document
    does not change. Where this document is silent, SPEC.md v1.0.0
    applies unchanged.

Layer:     P13 — DataCube, v2 (hardened)
Depends:   datacube.py (P13 v1.0.0); P12 rules_v2 (duck-typed, only
           for register_gate_rule)
Consumed:  P15 HAL, SC-OS, The Cockpit — new code imports
           datacube_v2, not datacube
Version:   SPEC V2 2.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Compatibility guarantee

- `FACES`, `set_face` and `count_faces` are v1's, re-exported.
- For well-formed inputs (non-empty str subject/object, bool
  `human_validated`, exact face labels, objects that differ by more
  than case/whitespace) every v1 function returns or raises as v1.
- v2 narrows v1 by rejecting malformed claims, non-bool validation
  flags and unknown face labels, and by normalising before comparing
  (§2.4). That narrowing is why the major version is 2.

## 2. Changes from SPEC.md v1.0.0

### 2.1 Claims must be well formed (closes D2)
A claim is a dict whose `subject` and `object` are non-empty `str`.
`create_cube` and `keystone_gate` raise `ValueError` otherwise.

### 2.2 The gated claim must be UNKNOWN (closes D1)
`keystone_gate(new_unknown, ...)`: if `new_unknown` has a `face` key
its value must be exactly `"UNKNOWN"`, else `ValueError`. A claim with
no `face` key is treated as UNKNOWN (v1 behaviour).

### 2.3 Existing claims fail closed (closes D4)
Every entry of `existing` must be a dict whose `face` is one of the
six exact labels, else `ValueError`. FACT/COUNTER/CONTEXT entries
must also be well formed (§2.1). A corrupt memory rejects the write;
it is never silently skipped.

### 2.4 Normalised comparison (closes D5)
`normalise(s)`: Unicode NFKC, `casefold()`, whitespace runs collapsed
to one space, stripped. The default contradiction is: same
normalised `subject` AND different normalised `object`.

### 2.5 Pluggable contradiction
`keystone_gate(new_unknown, existing, contradicts=None)`.
`contradicts(new_claim, existing_claim) -> bool` replaces the default
test and is called for every FACT/COUNTER/CONTEXT entry. A non-bool
return raises `TypeError` (fail closed). This is the hook for semantic
detection; v2 ships no semantic model.

### 2.6 find_contradiction
`find_contradiction(new_unknown, existing, contradicts=None)` returns
the first contradicted existing claim (a dict) or `None`. Same
validation as the gate. `keystone_gate` raises `ValueError` naming
that claim.

### 2.7 Strict human validation (closes D3)
`inspection_grade(cube, human_validated)` raises `TypeError` unless
`human_validated` is exactly `True` or `False`.

### 2.8 Write-time gate
`write_claim(store, claim, contradicts=None) -> dict`.
- `claim["face"]` must be one of the six labels, else `ValueError`.
- If the face is UNKNOWN the gate runs against `store` first; on
  contradiction `ValueError` is raised and `store` is unchanged.
- Otherwise a deep copy of the claim is appended to `store` (a list)
  and returned. Non-UNKNOWN faces are not gated (SPEC §3).

### 2.9 P12 integration
`register_gate_rule(engine, existing, on_reject, name="keystone_gate",
priority=100)` registers one rule on a P12 `rules_v2` engine (only
`engine.register` is used).
- `existing` is a list or a zero-argument callable returning one
  (read at each evaluation, so the rule sees current memory).
- Predicate: capsule `face == "UNKNOWN"` and `find_contradiction`
  returns a claim. Capsules of any other face never match.
- Action: returns `on_reject(capsule, contradicted_claim)`.
- Malformed claims raise in the predicate; `evaluate(safe=True)`
  records them as errors (P12 SPEC_V2 §2.6).

### 2.10 Cube merging
`merge_cubes(older, newer, on_conflict="raise") -> dict`.
- Both must be valid cubes (§2.11) with equal normalised subject and
  object, else `ValueError`. The result keeps `older`'s spelling.
- Per face: None + x → x; x + x → x; x + y conflict resolved by
  `on_conflict`: `"raise"` (ValueError), `"keep_older"`,
  `"keep_newer"`. Any other value → `ValueError`.
- Inputs are not mutated; a new cube is returned.

### 2.11 Cube validation and JSON
`validate_cube(cube)` raises `ValueError` unless the cube's keys are
exactly `subject`, `object` and the six faces, subject/object are
non-empty str, and each face is `str` or `None`. Extra keys (e.g. a
`human_validated` field) are rejected: validation is never a face.

`cube_to_json(cube) -> str`: validates, then emits
`{"schema": "p13.cube/2", "subject", "object", "faces": {...}}` with
sorted keys, compact separators, UTF-8 (not ASCII-escaped).

`cube_from_json(text) -> dict`: parses, requires exactly those top
keys, `schema == "p13.cube/2"`, `faces` with exactly the six labels;
returns a validated cube. Any failure (including bad JSON) raises
`ValueError`. Round trip is exact.

### 2.12 Header discipline
Every function in datacube_v2.py carries a numbered header.

## 3. Not in v2 (decided, see NOTES.md)

- Semantic contradiction model — hook only (§2.5).
- Trust weighting (λ) in the gate — needs P14 trust input; deferred.
- Persistence — P9's job; JSON is a format, not storage.
