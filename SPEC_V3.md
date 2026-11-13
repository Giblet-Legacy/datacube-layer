# SPEC V3 — datacube-layer (P13 DataCube, polarity-aware Keystone Gate)

SPEC_V3.md — specification for datacube_v3.py, the layer above P13 v2.0.0.

Function:
    Changes what the Keystone Gate counts as a contradiction, so that
    one subject can hold many claims (James: "a repo is a subject with
    its own cluster of claims"). SPEC_V2.md remains authoritative for
    everything this document does not change; every v2 function is
    re-exported unchanged. datacube.py and datacube_v2.py are not edited.

Layer:     P13 — DataCube, v3
Depends:   datacube_v2.py (P13 v2.0.0)
Consumed:  The Cockpit (v1.3), The Echo, HAL, SC-OS
Version:   SPEC V3 3.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Why v3

v2's default rule (SPEC_V2 §2.4): an UNKNOWN contradicts a known
FACT, COUNTER or CONTEXT when the **subject is the same and the object
differs**. That reads the object as the subject's single value
("sky = blue", so "sky = green" contradicts it). It also means a subject
can hold only one known claim before every UNKNOWN about it is refused:
"envelope-layer = design" contradicts "envelope-layer = status".

Signing the repos as subjects with several claims each hit this on 49
of 72 claims (2026-11-13). The v2 CHANGELOG already records the
limitation: contradiction is subject and object only; polarity is not
compared.

## 2. The v3 rule

### 2.1 polarity_of(claim) -> "affirm" | "negate"
- If the claim has a `polarity` key, it must be "affirm" or "negate"
  (else ValueError) and is returned.
- Otherwise "negate" if the normalised object starts with "not ",
  else "affirm". (This matches the Cockpit v1.2 parse, so claims
  written before v1.2, which have no polarity key, still read right.)

### 2.2 core_object(claim) -> str
The normalised object (SPEC_V2 §2.4: NFKC, casefold, collapsed
whitespace), with one leading "not " removed.

### 2.3 contradicts_v3(new_unknown, existing) -> bool
True exactly when the normalised subjects are equal, the core objects
are equal, and the polarities differ. "sky = not blue" contradicts
"sky = blue"; "envelope-layer = design" does not contradict
"envelope-layer = status".

### 2.4 Trade-off (deliberate)
A different object is now a different claim, not a contradiction, so
"sky = green" no longer contradicts "sky = blue". A caller that wants
the single-value reading passes `contradicts=contradicts_v2` (v2's rule,
re-exported) to any gate function.

## 3. Gate functions

`find_contradiction`, `keystone_gate`, `write_claim` and
`register_gate_rule` keep v2's signatures, validation and errors; the
only change is the default `contradicts`, which is `contradicts_v3`.
They call v2's functions with that default, so v2's validation (face
checks, fail-closed memory, bool verdicts) is unchanged. Memory entries
may carry `polarity`; an invalid one makes the gate raise ValueError
(it fails closed).

## 4. Public API

v2 re-exported unchanged: create_cube, set_face, count_faces,
inspection_grade, normalise, merge_cubes, validate_cube, cube_to_json,
cube_from_json. New: polarity_of, core_object, contradicts_v3,
contradicts_v2 (v2's default rule). v3 defaults: find_contradiction,
keystone_gate, write_claim, register_gate_rule.

## 5. Tests (test_datacube_v3.py)

- v2 names are v2's objects; contradicts_v2 is v2's default rule.
- polarity_of: explicit key, "not " prefix, default affirm, bad value.
- core_object strips one "not " and normalises.
- contradicts_v3: opposite polarity on the same subject and object;
  not for a different object; not for the same polarity; normalised.
- keystone_gate: many claims on one subject pass; an opposite-polarity
  UNKNOWN is refused with v2's message; only FACT, COUNTER and CONTEXT
  gate; contradicts_v2 restores the old rule; a bad memory polarity
  fails closed.
- write_claim and register_gate_rule use the v3 rule.

---

## Document control

- **SPEC V3 3.0.0** — 2026-11-13, by the VS Code AI on James's
  delegation ("fix properly"), after the Keystone Gate refused 49 of
  72 repo claims under v2's rule.
