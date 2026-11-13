"""
test_datacube_v3.py — P13 DataCube v3 (polarity-aware Keystone Gate) test suite

Function:
    Executable expression of SPEC_V3.md. Written before datacube_v3.py
    and run red first.

Functions in this file (pytest-collected):
    1. test_v2_reexports
    2. test_polarity_of
    3. test_core_object
    4. test_contradicts_v3
    5. test_keystone_gate
    6. test_write_claim_and_rule_use_v3

Helpers:
    7. _c — a claim dict

Layer:    P13 — DataCube, v3
Spec:     SPEC_V3.md 3.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import pytest

import datacube_v2
import datacube_v3 as dc


# 7. _c
def _c(subject, obj, face=None, polarity=None):
    out = {"subject": subject, "object": obj}
    if face:
        out["face"] = face
    if polarity:
        out["polarity"] = polarity
    return out


# 1. test_v2_reexports
def test_v2_reexports():
    for name in ("create_cube", "set_face", "count_faces", "inspection_grade", "normalise",
                 "merge_cubes", "validate_cube", "cube_to_json", "cube_from_json"):
        assert getattr(dc, name) is getattr(datacube_v2, name)
    assert dc.contradicts_v2 is datacube_v2._default_contradicts


# 2. test_polarity_of
def test_polarity_of():
    assert dc.polarity_of(_c("sky", "blue", polarity="negate")) == "negate"
    assert dc.polarity_of(_c("sky", "blue")) == "affirm"
    assert dc.polarity_of(_c("sky", "  NOT  blue")) == "negate"
    assert dc.polarity_of(_c("sky", "nothing")) == "affirm"  # "not" must be a word
    with pytest.raises(ValueError):
        dc.polarity_of(_c("sky", "blue", polarity="maybe"))


# 3. test_core_object
def test_core_object():
    assert dc.core_object(_c("sky", "Not  Blue ")) == "blue"
    assert dc.core_object(_c("sky", "not not blue")) == "not blue"
    assert dc.core_object(_c("sky", "Blue")) == "blue"


# 4. test_contradicts_v3
def test_contradicts_v3():
    known = _c("Sky", "blue", "FACT", "affirm")
    assert dc.contradicts_v3(_c("sky", "not blue"), known)
    assert dc.contradicts_v3(_c(" SKY ", "blue", polarity="negate"), known)
    assert not dc.contradicts_v3(_c("sky", "blue"), known)  # same polarity
    assert not dc.contradicts_v3(_c("sky", "green"), known)  # different object: a different claim
    assert not dc.contradicts_v3(_c("sea", "not blue"), known)
    assert dc.contradicts_v3(_c("sky", "blue"), _c("sky", "not blue", "FACT"))  # pre-1.2 memory


# 5. test_keystone_gate
def test_keystone_gate():
    memory = [_c("envelope-layer", "status", "FACT", "affirm"), _c("envelope-layer", "P1 Envelope", "CONTEXT"),
              _c("sky", "blue", "FACT", "affirm"), _c("sky", "not grey", "OPINION")]
    dc.keystone_gate(_c("envelope-layer", "design"), memory)  # many claims on one subject
    dc.keystone_gate(_c("sky", "grey"), memory)  # OPINION does not gate
    with pytest.raises(ValueError, match="Keystone Gate: UNKNOWN"):
        dc.keystone_gate(_c("sky", "not blue", "UNKNOWN"), memory)
    with pytest.raises(ValueError, match="Keystone Gate"):
        dc.keystone_gate(_c("envelope-layer", "design"), memory, contradicts=dc.contradicts_v2)
    with pytest.raises(ValueError):
        dc.keystone_gate(_c("sky", "blue"), [_c("sky", "blue", "FACT", "sideways")])  # fails closed
    with pytest.raises(ValueError):
        dc.keystone_gate(_c("sky", "not blue", "FACT"), memory)  # v2: only UNKNOWN is gated
    assert dc.find_contradiction(_c("sky", "not blue"), memory) is memory[2]
    assert dc.find_contradiction(_c("sky", "green"), memory) is None


# 6. test_write_claim_and_rule_use_v3
def test_write_claim_and_rule_use_v3():
    store = [_c("sky", "blue", "FACT", "affirm")]
    dc.write_claim(store, _c("sky", "green", "UNKNOWN"))
    assert len(store) == 2
    with pytest.raises(ValueError):
        dc.write_claim(store, _c("sky", "not blue", "UNKNOWN"))
    assert len(store) == 2

    class Engine:
        def __init__(self):
            self.rules = {}

        def register(self, name, predicate, action, priority=0):
            self.rules[name] = (predicate, action)

    eng = Engine()
    dc.register_gate_rule(eng, store, lambda cap, hit: hit)
    predicate, action = eng.rules["keystone_gate"]
    assert predicate(_c("sky", "not blue", "UNKNOWN"))
    assert not predicate(_c("sky", "violet", "UNKNOWN"))
    assert action(_c("sky", "not blue", "UNKNOWN")) is store[0]
