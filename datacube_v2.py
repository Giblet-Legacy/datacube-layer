"""
datacube_v2.py — P13 DataCube v2, hardened layer over the frozen v1 primitive

Function:
    The layer new code imports instead of datacube.py. It requires
    well-formed claims, gates only claims that are UNKNOWN, fails
    closed on corrupt memory, compares subjects and objects after
    Unicode/case/whitespace normalisation, accepts a pluggable
    contradiction test, requires a strict bool for human validation,
    and adds a write-time gate, a P12 rule adapter, cube merging and
    JSON serialisation (SPEC_V2.md §2). Face storage, setting and
    counting are delegated to v1, so v1's contract is kept.

    datacube.py is not edited (Immutable Rule). This file is the
    "add a layer" half of that rule.

Public API (v1 names and numbering kept, new entries appended):
    1. create_cube        — v1 cube after claim validation
    2. set_face           — v1, re-exported
    3. count_faces        — v1, re-exported
    4. inspection_grade   — v1 grade; human_validated must be bool
    5. keystone_gate      — validated, normalised, pluggable gate
    6. normalise          — NFKC + casefold + collapsed whitespace
    7. find_contradiction — first contradicted claim, or None
    8. write_claim        — gate on write, then append a copy
    9. register_gate_rule — wire the gate into a P12 rules_v2 engine
   10. merge_cubes        — combine two cubes of the same claim
   11. validate_cube      — exact cube shape check
   12. cube_to_json       — canonical JSON text
   13. cube_from_json     — parse and validate JSON text

Internal helpers (not exported):
   14. _require_claim       — non-empty str subject and object
   15. _default_contradicts — same subject, different object (normalised)

Layer:    P13 — DataCube, v2 (hardened)
Depends:  datacube.py (P13 v1.0.0); P12 rules_v2 (duck-typed)
Consumed: P15 HAL, SC-OS, The Cockpit
Spec:     SPEC_V2.md 2.0.0 (over SPEC.md v1.0.0)
Version:  2.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy
import json
import os
import sys
import unicodedata

# Locate v1 from this file, not the working directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import datacube as _v1

FACES = _v1.FACES
set_face = _v1.set_face
count_faces = _v1.count_faces

_GATE_FACES = ("FACT", "COUNTER", "CONTEXT")
_SCHEMA = "p13.cube/2"
_CUBE_KEYS = frozenset(("subject", "object") + FACES)
_CONFLICT_POLICIES = ("raise", "keep_older", "keep_newer")


# ---------------------------------------------------------------------------
# 14. _require_claim
#     Raises ValueError unless claim is a dict with non-empty str
#     subject and object (SPEC_V2 §2.1). `what` names it in the message.
# ---------------------------------------------------------------------------
def _require_claim(claim, what="claim"):
    if not isinstance(claim, dict):
        raise ValueError(f"{what} must be a dict, got {type(claim).__name__}")
    for field in ("subject", "object"):
        value = claim.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{what} {field} must be a non-empty str, got {value!r}")


# ---------------------------------------------------------------------------
# 6. normalise
#    NFKC, casefold, collapse whitespace runs, strip (SPEC_V2 §2.4).
# ---------------------------------------------------------------------------
def normalise(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


# ---------------------------------------------------------------------------
# 15. _default_contradicts
#     Same normalised subject AND different normalised object.
# ---------------------------------------------------------------------------
def _default_contradicts(new_claim, existing_claim):
    return (normalise(new_claim["subject"]) == normalise(existing_claim["subject"])
            and normalise(new_claim["object"]) != normalise(existing_claim["object"]))


# ---------------------------------------------------------------------------
# 1. create_cube
#    Validates the claim (SPEC_V2 §2.1), then builds the v1 cube.
# ---------------------------------------------------------------------------
def create_cube(claim):
    _require_claim(claim)
    return _v1.create_cube(claim)


# ---------------------------------------------------------------------------
# 4. inspection_grade
#    human_validated must be exactly True or False (SPEC_V2 §2.7);
#    otherwise TypeError. Then v1 grading.
# ---------------------------------------------------------------------------
def inspection_grade(cube, human_validated):
    if human_validated is not True and human_validated is not False:
        raise TypeError("human_validated must be a bool (signed attestation present?)")
    return _v1.inspection_grade(cube, human_validated)


# ---------------------------------------------------------------------------
# 7. find_contradiction
#    Validates new_unknown (§2.1, §2.2) and every existing entry (§2.3),
#    then returns the first FACT/COUNTER/CONTEXT claim it contradicts,
#    or None. contradicts must return a bool (§2.5).
# ---------------------------------------------------------------------------
def find_contradiction(new_unknown, existing, contradicts=None):
    _require_claim(new_unknown, "UNKNOWN claim")
    if "face" in new_unknown and new_unknown["face"] != "UNKNOWN":
        raise ValueError(
            f"Keystone Gate only gates UNKNOWN claims, got face {new_unknown['face']!r}")
    test = contradicts if contradicts is not None else _default_contradicts

    for i, claim in enumerate(existing):
        if not isinstance(claim, dict):
            raise ValueError(f"existing[{i}] must be a dict, got {type(claim).__name__}")
        face = claim.get("face")
        if face not in FACES:
            raise ValueError(f"existing[{i}] has unknown face {face!r}; must be one of {FACES}")
        if face not in _GATE_FACES:
            continue
        _require_claim(claim, f"existing[{i}]")
        verdict = test(new_unknown, claim)
        if not isinstance(verdict, bool):
            raise TypeError(f"contradicts must return bool, got {type(verdict).__name__}")
        if verdict:
            return claim
    return None


# ---------------------------------------------------------------------------
# 5. keystone_gate
#    None on pass; ValueError naming the contradicted claim otherwise.
# ---------------------------------------------------------------------------
def keystone_gate(new_unknown, existing, contradicts=None):
    hit = find_contradiction(new_unknown, existing, contradicts)
    if hit is not None:
        raise ValueError(
            f"Keystone Gate: UNKNOWN ({new_unknown['subject']}={new_unknown['object']}) "
            f"contradicts {hit['face']} ({hit['subject']}={hit['object']})"
        )


# ---------------------------------------------------------------------------
# 8. write_claim
#    Face must be one of six. UNKNOWN claims pass the gate against store
#    first; then a deep copy is appended and returned (SPEC_V2 §2.8).
# ---------------------------------------------------------------------------
def write_claim(store, claim, contradicts=None):
    _require_claim(claim)
    face = claim.get("face")
    if face not in FACES:
        raise ValueError(f"claim face {face!r} must be one of {FACES}")
    if face == "UNKNOWN":
        keystone_gate(claim, store, contradicts)
    stored = copy.deepcopy(claim)
    store.append(stored)
    return stored


# ---------------------------------------------------------------------------
# 9. register_gate_rule
#    Registers a rule on a P12 rules_v2 engine (SPEC_V2 §2.9). The
#    predicate matches UNKNOWN capsules that contradict current memory;
#    the action returns on_reject(capsule, contradicted_claim).
# ---------------------------------------------------------------------------
def register_gate_rule(engine, existing, on_reject, name="keystone_gate",
                       priority=100, contradicts=None):
    if not callable(on_reject):
        raise ValueError("on_reject must be callable")
    memory = existing if callable(existing) else (lambda: existing)

    def predicate(capsule):
        if capsule.get("face") != "UNKNOWN":
            return False
        return find_contradiction(capsule, memory(), contradicts) is not None

    def action(capsule):
        return on_reject(capsule, find_contradiction(capsule, memory(), contradicts))

    engine.register(name, predicate, action, priority=priority)


# ---------------------------------------------------------------------------
# 11. validate_cube
#     Exact keys (subject, object, six faces), str subject/object,
#     each face str or None (SPEC_V2 §2.11). Extra keys rejected.
# ---------------------------------------------------------------------------
def validate_cube(cube):
    if not isinstance(cube, dict):
        raise ValueError(f"cube must be a dict, got {type(cube).__name__}")
    keys = set(cube)
    if keys != _CUBE_KEYS:
        extra, missing = sorted(keys - _CUBE_KEYS), sorted(_CUBE_KEYS - keys)
        raise ValueError(f"cube keys wrong: extra={extra} missing={missing}")
    _require_claim(cube, "cube")
    for face in FACES:
        if cube[face] is not None and not isinstance(cube[face], str):
            raise ValueError(f"cube face {face} must be str or None")


# ---------------------------------------------------------------------------
# 10. merge_cubes
#     Same normalised claim required. Fill gaps; resolve differing
#     content by on_conflict. Returns a new cube (SPEC_V2 §2.10).
# ---------------------------------------------------------------------------
def merge_cubes(older, newer, on_conflict="raise"):
    if on_conflict not in _CONFLICT_POLICIES:
        raise ValueError(f"on_conflict must be one of {_CONFLICT_POLICIES}")
    validate_cube(older)
    validate_cube(newer)
    for field in ("subject", "object"):
        if normalise(older[field]) != normalise(newer[field]):
            raise ValueError(
                f"cannot merge different claims: {field} {older[field]!r} != {newer[field]!r}")

    merged = copy.deepcopy(older)
    for face in FACES:
        a, b = older[face], newer[face]
        if b is None or a == b:
            continue
        if a is None or on_conflict == "keep_newer":
            merged[face] = b
        elif on_conflict == "raise":
            raise ValueError(f"merge conflict on {face}: {a!r} vs {b!r}")
        # keep_older: leave a
    return merged


# ---------------------------------------------------------------------------
# 12. cube_to_json
#     Validates, then emits canonical schema-tagged JSON (SPEC_V2 §2.11).
# ---------------------------------------------------------------------------
def cube_to_json(cube):
    validate_cube(cube)
    doc = {
        "schema": _SCHEMA,
        "subject": cube["subject"],
        "object": cube["object"],
        "faces": {face: cube[face] for face in FACES},
    }
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


# ---------------------------------------------------------------------------
# 13. cube_from_json
#     Parses, checks schema and exact structure, returns a validated
#     cube. Every failure is ValueError (SPEC_V2 §2.11).
# ---------------------------------------------------------------------------
def cube_from_json(text):
    try:
        doc = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cube JSON unreadable: {exc}") from None
    if not isinstance(doc, dict) or set(doc) != {"schema", "subject", "object", "faces"}:
        raise ValueError("cube JSON must have exactly schema, subject, object, faces")
    if doc["schema"] != _SCHEMA:
        raise ValueError(f"unsupported cube schema {doc['schema']!r}; expected {_SCHEMA!r}")
    faces = doc["faces"]
    if not isinstance(faces, dict) or set(faces) != set(FACES):
        raise ValueError(f"cube JSON faces must be exactly {FACES}")
    cube = {"subject": doc["subject"], "object": doc["object"]}
    cube.update({face: faces[face] for face in FACES})
    validate_cube(cube)
    return cube
