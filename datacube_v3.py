"""
datacube_v3.py — P13 DataCube v3, the polarity-aware Keystone Gate

Function:
    The layer new code imports instead of datacube_v2.py. Re-exports
    every v2 function unchanged and changes one thing (SPEC_V3.md): the
    Keystone Gate's default contradiction rule. Under v3 an UNKNOWN
    contradicts a known FACT, COUNTER or CONTEXT only when subject and
    object are the same and the polarity is opposite, so one subject
    can hold many claims. v2's rule stays available as contradicts_v2.

    datacube.py and datacube_v2.py are not edited (Immutable Rule).

Public API:
    (re-exported from v2: create_cube, set_face, count_faces,
     inspection_grade, normalise, merge_cubes, validate_cube,
     cube_to_json, cube_from_json; contradicts_v2 = v2's default rule)
    1. polarity_of        — "affirm" or "negate"
    2. core_object        — normalised object without a leading "not "
    3. contradicts_v3     — same subject and object, opposite polarity
    4. find_contradiction — v2's, defaulting to contradicts_v3
    5. keystone_gate      — v2's, defaulting to contradicts_v3
    6. write_claim        — v2's, defaulting to contradicts_v3
    7. register_gate_rule — v2's, defaulting to contradicts_v3

Layer:    P13 — DataCube, v3
Depends:  datacube_v2.py (P13 v2.0.0)
Consumed: The Cockpit (v1.3), The Echo, HAL, SC-OS
Spec:     SPEC_V3.md 3.0.0
Version:  3.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import datacube_v2 as _v2  # noqa: E402

create_cube = _v2.create_cube
set_face = _v2.set_face
count_faces = _v2.count_faces
inspection_grade = _v2.inspection_grade
normalise = _v2.normalise
merge_cubes = _v2.merge_cubes
validate_cube = _v2.validate_cube
cube_to_json = _v2.cube_to_json
cube_from_json = _v2.cube_from_json
contradicts_v2 = _v2._default_contradicts

_POLARITIES = ("affirm", "negate")


# ---------------------------------------------------------------------------
# 1. polarity_of
#    SPEC_V3 §2.1: the `polarity` key if present, else a leading "not ".
# ---------------------------------------------------------------------------
def polarity_of(claim):
    if "polarity" in claim:
        if claim["polarity"] not in _POLARITIES:
            raise ValueError(f"polarity must be 'affirm' or 'negate', got {claim['polarity']!r}")
        return claim["polarity"]
    return "negate" if normalise(claim["object"]).startswith("not ") else "affirm"


# ---------------------------------------------------------------------------
# 2. core_object
#    SPEC_V3 §2.2.
# ---------------------------------------------------------------------------
def core_object(claim):
    obj = normalise(claim["object"])
    return obj[4:] if obj.startswith("not ") else obj


# ---------------------------------------------------------------------------
# 3. contradicts_v3
#    SPEC_V3 §2.3. Both polarities are read first, so a bad one in
#    memory raises (the gate fails closed) whatever the subject.
# ---------------------------------------------------------------------------
def contradicts_v3(new_unknown, existing):
    new_pol, old_pol = polarity_of(new_unknown), polarity_of(existing)
    return (normalise(new_unknown["subject"]) == normalise(existing["subject"])
            and core_object(new_unknown) == core_object(existing)
            and new_pol != old_pol)


# ---------------------------------------------------------------------------
# 4. find_contradiction
# ---------------------------------------------------------------------------
def find_contradiction(new_unknown, existing, contradicts=None):
    return _v2.find_contradiction(new_unknown, existing, contradicts or contradicts_v3)


# ---------------------------------------------------------------------------
# 5. keystone_gate
# ---------------------------------------------------------------------------
def keystone_gate(new_unknown, existing, contradicts=None):
    return _v2.keystone_gate(new_unknown, existing, contradicts or contradicts_v3)


# ---------------------------------------------------------------------------
# 6. write_claim
# ---------------------------------------------------------------------------
def write_claim(store, claim, contradicts=None):
    return _v2.write_claim(store, claim, contradicts or contradicts_v3)


# ---------------------------------------------------------------------------
# 7. register_gate_rule
# ---------------------------------------------------------------------------
def register_gate_rule(engine, existing, on_reject, name="keystone_gate", priority=100, contradicts=None):
    return _v2.register_gate_rule(engine, existing, on_reject, name=name, priority=priority,
                                  contradicts=contradicts or contradicts_v3)
