"""
test_datacube.py — P13 DataCube test suite

Function:
    Executable expression of SPEC.md. Written before datacube.py per
    build discipline.

Layer:    P13 — DataCube
Spec:     SPEC.md v1.0.0
Licence:  MSL-1.0
"""

import pytest

import datacube

def _claim(subject, obj):
    return {"subject": subject, "object": obj}

# ── create_cube ──────────────────────────────────────────────────────────
def test_create_cube_has_six_faces():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"):
        assert face in cube

def test_create_cube_all_faces_initially_none():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"):
        assert cube[face] is None

def test_create_cube_preserves_subject_object():
    cube = datacube.create_cube(_claim("sky", "blue"))
    assert cube["subject"] == "sky"
    assert cube["object"] == "blue"

# ── set_face ─────────────────────────────────────────────────────────────
def test_set_face_updates():
    cube = datacube.create_cube(_claim("sky", "blue"))
    datacube.set_face(cube, "FACT", "Observed blue at noon.")
    assert cube["FACT"] == "Observed blue at noon."

def test_set_face_rejects_unknown_face():
    cube = datacube.create_cube(_claim("sky", "blue"))
    with pytest.raises(ValueError):
        datacube.set_face(cube, "MAGIC", "nope")

def test_set_face_rejects_non_string():
    cube = datacube.create_cube(_claim("sky", "blue"))
    with pytest.raises(ValueError):
        datacube.set_face(cube, "FACT", 42)

# ── count_faces ──────────────────────────────────────────────────────────
def test_count_faces_empty():
    cube = datacube.create_cube(_claim("sky", "blue"))
    assert datacube.count_faces(cube) == 0

def test_count_faces_partial():
    cube = datacube.create_cube(_claim("sky", "blue"))
    datacube.set_face(cube, "FACT", "x")
    datacube.set_face(cube, "COUNTER", "y")
    assert datacube.count_faces(cube) == 2

def test_count_faces_all():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"):
        datacube.set_face(cube, face, "x")
    assert datacube.count_faces(cube) == 6

# ── inspection_grade ─────────────────────────────────────────────────────
def test_grade_sparse_0():
    cube = datacube.create_cube(_claim("sky", "blue"))
    assert datacube.inspection_grade(cube, human_validated=False) == "SPARSE"

def test_grade_sparse_1():
    cube = datacube.create_cube(_claim("sky", "blue"))
    datacube.set_face(cube, "FACT", "x")
    assert datacube.inspection_grade(cube, human_validated=False) == "SPARSE"

def test_grade_forming_2():
    cube = datacube.create_cube(_claim("sky", "blue"))
    datacube.set_face(cube, "FACT", "x")
    datacube.set_face(cube, "COUNTER", "y")
    assert datacube.inspection_grade(cube, human_validated=False) == "FORMING"

def test_grade_forming_4():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION"):
        datacube.set_face(cube, face, "x")
    assert datacube.inspection_grade(cube, human_validated=False) == "FORMING"

def test_grade_forming_5_without_validation():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT"):
        datacube.set_face(cube, face, "x")
    assert datacube.inspection_grade(cube, human_validated=False) == "FORMING"

def test_grade_coherent_5_with_validation():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT"):
        datacube.set_face(cube, face, "x")
    assert datacube.inspection_grade(cube, human_validated=True) == "COHERENT"

def test_grade_crystalline_6_with_validation():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"):
        datacube.set_face(cube, face, "x")
    assert datacube.inspection_grade(cube, human_validated=True) == "CRYSTALLINE"

def test_grade_6_without_validation_is_forming():
    cube = datacube.create_cube(_claim("sky", "blue"))
    for face in ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN"):
        datacube.set_face(cube, face, "x")
    assert datacube.inspection_grade(cube, human_validated=False) == "FORMING"

# ── keystone_gate ────────────────────────────────────────────────────────
def test_gate_passes_when_no_existing_claims():
    new = _claim("moon", "cheese")
    datacube.keystone_gate(new, existing=[])

def test_gate_passes_when_subject_differs():
    new = _claim("moon", "cheese")
    existing = [dict(_claim("sky", "blue"), face="FACT")]
    datacube.keystone_gate(new, existing)

def test_gate_passes_when_object_agrees():
    new = _claim("sky", "blue")
    existing = [dict(_claim("sky", "blue"), face="FACT")]
    datacube.keystone_gate(new, existing)

def test_gate_rejects_contradiction_with_fact():
    new = _claim("sky", "green")
    existing = [dict(_claim("sky", "blue"), face="FACT")]
    with pytest.raises(ValueError):
        datacube.keystone_gate(new, existing)

def test_gate_rejects_contradiction_with_counter():
    new = _claim("sky", "green")
    existing = [dict(_claim("sky", "blue"), face="COUNTER")]
    with pytest.raises(ValueError):
        datacube.keystone_gate(new, existing)

def test_gate_rejects_contradiction_with_context():
    new = _claim("sky", "green")
    existing = [dict(_claim("sky", "blue"), face="CONTEXT")]
    with pytest.raises(ValueError):
        datacube.keystone_gate(new, existing)

def test_gate_ignores_opinion_face():
    new = _claim("sky", "green")
    existing = [dict(_claim("sky", "blue"), face="OPINION")]
    datacube.keystone_gate(new, existing)

def test_gate_ignores_fiction_face():
    new = _claim("sky", "green")
    existing = [dict(_claim("sky", "blue"), face="FICTION")]
    datacube.keystone_gate(new, existing)
