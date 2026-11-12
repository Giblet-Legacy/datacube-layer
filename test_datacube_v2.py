"""
test_datacube_v2.py — P13 DataCube v2 test suite

Function:
    Executable expression of SPEC_V2.md. Written before datacube_v2.py
    per build discipline. Covers v1 compatibility, the closed
    divergences D1–D5, pluggable contradiction, the write-time gate,
    P12 rule integration, cube merging and JSON serialisation.

Layer:    P13 — DataCube, v2
Spec:     SPEC_V2.md 2.0.0
Licence:  MSL-1.0
"""

import json

import pytest

import datacube
import datacube_v2 as dc

FACES = ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN")


def _claim(subject, obj, face=None):
    c = {"subject": subject, "object": obj}
    if face is not None:
        c["face"] = face
    return c


def _full_cube(subject="sky", obj="blue", fill=FACES):
    cube = dc.create_cube(_claim(subject, obj))
    for f in fill:
        dc.set_face(cube, f, f.lower())
    return cube


# 1. Compatibility with v1 (SPEC_V2 §1) -------------------------------------

def test_reexports_v1():
    assert dc.FACES == datacube.FACES
    assert dc.set_face is datacube.set_face
    assert dc.count_faces is datacube.count_faces


def test_create_cube_matches_v1():
    c = _claim("sky", "blue")
    assert dc.create_cube(c) == datacube.create_cube(c)


@pytest.mark.parametrize("n", range(7))
@pytest.mark.parametrize("hv", [True, False])
def test_grade_matches_v1(n, hv):
    cube = _full_cube(fill=FACES[:n])
    assert dc.inspection_grade(cube, hv) == datacube.inspection_grade(cube, hv)


@pytest.mark.parametrize("face", ["FACT", "COUNTER", "CONTEXT"])
def test_gate_rejects_like_v1(face):
    with pytest.raises(ValueError):
        dc.keystone_gate(_claim("sky", "green"), [_claim("sky", "blue", face)])


@pytest.mark.parametrize("face", ["OPINION", "FICTION", "UNKNOWN"])
def test_gate_ignores_non_gate_faces(face):
    dc.keystone_gate(_claim("sky", "green"), [_claim("sky", "blue", face)])


# 2. Well-formed claims (SPEC_V2 §2.1, D2) ----------------------------------

@pytest.mark.parametrize("bad", [{}, {"subject": "sky"}, {"object": "blue"},
                                 _claim("", "blue"), _claim("sky", 3), "sky"])
def test_create_cube_rejects_malformed(bad):
    with pytest.raises(ValueError):
        dc.create_cube(bad)


def test_gate_none_subjects_no_longer_collide():
    with pytest.raises(ValueError, match="subject"):
        dc.keystone_gate({}, [{"face": "FACT", "object": "x"}])


# 3. Gated claim must be UNKNOWN (SPEC_V2 §2.2, D1) -------------------------

@pytest.mark.parametrize("face", ["FACT", "COUNTER", "OPINION", "unknown"])
def test_gate_rejects_non_unknown_new_claim(face):
    with pytest.raises(ValueError, match="UNKNOWN"):
        dc.keystone_gate(_claim("moon", "cheese", face), [])


def test_gate_accepts_explicit_unknown():
    dc.keystone_gate(_claim("moon", "cheese", "UNKNOWN"), [])


# 4. Existing claims fail closed (SPEC_V2 §2.3, D4) -------------------------

@pytest.mark.parametrize("entry", ["junk", _claim("sky", "blue"),
                                   _claim("sky", "blue", "fact"),
                                   _claim("sky", "blue", "MAGIC")])
def test_gate_rejects_corrupt_existing(entry):
    with pytest.raises(ValueError):
        dc.keystone_gate(_claim("moon", "cheese"), [entry])


def test_gate_rejects_malformed_gate_face_entry():
    with pytest.raises(ValueError):
        dc.keystone_gate(_claim("moon", "cheese"), [{"face": "FACT", "subject": "sky"}])


# 5. Normalisation (SPEC_V2 §2.4, D5) ---------------------------------------

def test_normalise():
    assert dc.normalise("  Blue\t Sky\n") == "blue sky"
    assert dc.normalise("ＢＬＵＥ") == "blue"  # NFKC full-width


def test_gate_case_and_space_not_contradiction():
    dc.keystone_gate(_claim("Sky", " BLUE "), [_claim("sky", "blue", "FACT")])


def test_gate_catches_case_variant_subject():
    with pytest.raises(ValueError):
        dc.keystone_gate(_claim("SKY", "green"), [_claim("sky", "blue", "FACT")])


# 6. Pluggable contradiction (SPEC_V2 §2.5, §2.6) ---------------------------

def test_custom_contradicts_used():
    synonyms = {"azure": "blue"}

    def semantic(new, old):
        a = synonyms.get(dc.normalise(new["object"]), dc.normalise(new["object"]))
        return dc.normalise(new["subject"]) == dc.normalise(old["subject"]) and a != dc.normalise(old["object"])

    existing = [_claim("sky", "blue", "FACT")]
    dc.keystone_gate(_claim("sky", "azure"), existing, contradicts=semantic)
    with pytest.raises(ValueError):
        dc.keystone_gate(_claim("sky", "red"), existing, contradicts=semantic)


def test_custom_contradicts_non_bool_raises():
    with pytest.raises(TypeError):
        dc.keystone_gate(_claim("sky", "x"), [_claim("sky", "blue", "FACT")],
                         contradicts=lambda a, b: "yes")


def test_find_contradiction_returns_claim_or_none():
    hit = _claim("sky", "blue", "CONTEXT")
    existing = [_claim("sea", "wet", "FACT"), hit]
    assert dc.find_contradiction(_claim("sky", "green"), existing) is hit
    assert dc.find_contradiction(_claim("sky", "blue"), existing) is None


# 7. Strict human validation (SPEC_V2 §2.7, D3) -----------------------------

@pytest.mark.parametrize("hv", ["no", 1, 0, None, "True"])
def test_grade_rejects_non_bool_validation(hv):
    with pytest.raises(TypeError):
        dc.inspection_grade(_full_cube(), hv)


# 8. Write-time gate (SPEC_V2 §2.8) -----------------------------------------

def test_write_claim_appends_copy():
    store = []
    c = _claim("sky", "blue", "FACT")
    stored = dc.write_claim(store, c)
    assert store == [c] and stored is store[0] and stored is not c


def test_write_claim_rejects_contradicting_unknown_and_leaves_store():
    store = []
    dc.write_claim(store, _claim("sky", "blue", "FACT"))
    with pytest.raises(ValueError):
        dc.write_claim(store, _claim("sky", "green", "UNKNOWN"))
    assert len(store) == 1


def test_write_claim_accepts_consistent_unknown():
    store = [_claim("sky", "blue", "FACT")]
    dc.write_claim(store, _claim("moon", "cheese", "UNKNOWN"))
    assert len(store) == 2


@pytest.mark.parametrize("face", [None, "fact", "SEVENTH"])
def test_write_claim_requires_valid_face(face):
    with pytest.raises(ValueError):
        dc.write_claim([], _claim("sky", "blue", face))


# 9. P12 integration (SPEC_V2 §2.9) -----------------------------------------

@pytest.fixture
def p12():
    rules_v2 = pytest.importorskip("rules_v2")
    sign = pytest.importorskip("sign")
    ed = pytest.importorskip("cryptography.hazmat.primitives.asymmetric.ed25519")
    key = ed.Ed25519PrivateKey.generate()
    return rules_v2.create_engine(), sign, key


def test_gate_rule_fires_on_contradiction(p12):
    engine, sign, key = p12
    memory = [_claim("sky", "blue", "FACT")]
    dc.register_gate_rule(engine, memory, lambda cap, hit: ("rejected", hit["face"]))
    cap = sign.sign_capsule(_claim("sky", "green", "UNKNOWN"), key)
    assert engine.evaluate(cap, key.public_key()) == [
        {"name": "keystone_gate", "result": ("rejected", "FACT")}]
    assert engine.get_priority("keystone_gate") == 100


def test_gate_rule_silent_when_consistent_or_not_unknown(p12):
    engine, sign, key = p12
    dc.register_gate_rule(engine, [_claim("sky", "blue", "FACT")], lambda c, h: "x")
    for claim in (_claim("sky", "blue", "UNKNOWN"), _claim("sky", "green", "OPINION")):
        assert engine.evaluate(sign.sign_capsule(claim, key), key.public_key()) == []


def test_gate_rule_reads_live_memory(p12):
    engine, sign, key = p12
    memory = []
    dc.register_gate_rule(engine, lambda: memory, lambda c, h: "x", name="gate")
    cap = sign.sign_capsule(_claim("sky", "green", "UNKNOWN"), key)
    assert engine.evaluate(cap, key.public_key()) == []
    memory.append(_claim("sky", "blue", "FACT"))
    assert engine.evaluate(cap, key.public_key()) == [{"name": "gate", "result": "x"}]


def test_gate_rule_malformed_is_error_in_safe_mode(p12):
    engine, sign, key = p12
    dc.register_gate_rule(engine, [], lambda c, h: "x")
    cap = sign.sign_capsule({"face": "UNKNOWN", "subject": "sky"}, key)
    out = engine.evaluate(cap, key.public_key(), safe=True)
    assert out[0]["name"] == "keystone_gate" and out[0]["error"].startswith("ValueError")


# 10. Cube merging (SPEC_V2 §2.10) ------------------------------------------

def test_merge_fills_gaps_and_keeps_inputs():
    a = _full_cube(fill=("FACT",))
    b = _full_cube(subject="SKY", fill=("COUNTER",))
    a0, b0 = json.dumps(a), json.dumps(b)
    m = dc.merge_cubes(a, b)
    assert m["FACT"] == "fact" and m["COUNTER"] == "counter" and m["subject"] == "sky"
    assert dc.count_faces(m) == 2
    assert json.dumps(a) == a0 and json.dumps(b) == b0


def test_merge_conflict_policies():
    a = _full_cube(fill=("FACT",))
    b = _full_cube(fill=())
    dc.set_face(b, "FACT", "newer fact")
    with pytest.raises(ValueError):
        dc.merge_cubes(a, b)
    assert dc.merge_cubes(a, b, on_conflict="keep_older")["FACT"] == "fact"
    assert dc.merge_cubes(a, b, on_conflict="keep_newer")["FACT"] == "newer fact"
    with pytest.raises(ValueError):
        dc.merge_cubes(a, b, on_conflict="average")


def test_merge_identical_content_not_conflict():
    assert dc.merge_cubes(_full_cube(), _full_cube()) == _full_cube()


def test_merge_rejects_different_claim():
    with pytest.raises(ValueError):
        dc.merge_cubes(_full_cube(obj="blue"), _full_cube(obj="green"))


# 11. Validation and JSON (SPEC_V2 §2.11) -----------------------------------

def test_validate_rejects_seventh_face():
    cube = _full_cube()
    cube["human_validated"] = True
    with pytest.raises(ValueError):
        dc.validate_cube(cube)


def test_validate_rejects_non_str_face():
    cube = _full_cube()
    cube["FACT"] = 42
    with pytest.raises(ValueError):
        dc.validate_cube(cube)


def test_json_roundtrip_exact():
    cube = _full_cube(subject="café", fill=("FACT", "UNKNOWN"))
    text = dc.cube_to_json(cube)
    assert "café" in text and json.loads(text)["schema"] == "p13.cube/2"
    assert dc.cube_from_json(text) == cube


def test_json_preserves_none_vs_empty():
    cube = _full_cube(fill=())
    dc.set_face(cube, "COUNTER", "")
    back = dc.cube_from_json(dc.cube_to_json(cube))
    assert back["COUNTER"] == "" and back["FACT"] is None


@pytest.mark.parametrize("text", [
    "not json",
    "[]",
    '{"schema": "p13.cube/1", "subject": "s", "object": "o", "faces": {}}',
    json.dumps({"schema": "p13.cube/2", "subject": "s", "object": "o",
                "faces": {f: None for f in FACES[:5]}}),
    json.dumps({"schema": "p13.cube/2", "subject": "s", "object": "o",
                "faces": {f: None for f in FACES}, "extra": 1}),
])
def test_json_rejects_bad_input(text):
    with pytest.raises(ValueError):
        dc.cube_from_json(text)
