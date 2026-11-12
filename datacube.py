"""
datacube.py — P13 DataCube primitive layer

Function:
    Implements the six-face structure of a claim, the inspection
    grades, and the Keystone Gate. The Keystone Gate enforces the
    rule that an UNKNOWN hypothesis cannot contradict FACT, COUNTER,
    or CONTEXT.

Public API:
    1. create_cube      — Create an empty six-face cube.
    2. set_face         — Set content on a single face.
    3. count_faces      — Count non-None faces.
    4. inspection_grade — CRYSTALLINE / COHERENT / FORMING / SPARSE.
    5. keystone_gate    — Reject UNKNOWN claims that contradict facts.

Layer:    P13 — DataCube
Depends:  P12 Rules, P14 Leighton Engine
Consumed: P15 HAL, SC-OS, The Cockpit
Version:  1.0.0 (on freeze; 0.0.0-dev until then)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

FACES = ("FACT", "COUNTER", "OPINION", "FICTION", "CONTEXT", "UNKNOWN")
_GATE_FACES = ("FACT", "COUNTER", "CONTEXT")

# ---------------------------------------------------------------------------
# 1. create_cube
#    Builds a cube dict from a claim. All six faces initialised to None.
# ---------------------------------------------------------------------------
def create_cube(claim):
    cube = {
        "subject": claim.get("subject"),
        "object": claim.get("object"),
    }
    for face in FACES:
        cube[face] = None
    return cube

# ---------------------------------------------------------------------------
# 2. set_face
#    Sets a single face. Rejects unknown faces and non-string content.
# ---------------------------------------------------------------------------
def set_face(cube, face, content):
    if face not in FACES:
        raise ValueError(f"unknown face: {face!r}; must be one of {FACES}")
    if not isinstance(content, str):
        raise ValueError("face content must be a string")
    cube[face] = content
    return cube

# ---------------------------------------------------------------------------
# 3. count_faces
#    Returns the number of faces that have been set (non-None).
# ---------------------------------------------------------------------------
def count_faces(cube):
    return sum(1 for face in FACES if cube.get(face) is not None)

# ---------------------------------------------------------------------------
# 4. inspection_grade
#    Returns one of CRYSTALLINE, COHERENT, FORMING, SPARSE.
#    Human validation is a boolean flag, NEVER a seventh face.
# ---------------------------------------------------------------------------
def inspection_grade(cube, human_validated):
    count = count_faces(cube)
    if count == 6 and human_validated:
        return "CRYSTALLINE"
    if count == 5 and human_validated:
        return "COHERENT"
    if 2 <= count <= 4:
        return "FORMING"
    if count <= 1 and not (count == 5 or count == 6):
        return "SPARSE"
    # count is 5 or 6 without human validation
    return "FORMING"

# ---------------------------------------------------------------------------
# 5. keystone_gate
#    Rejects an UNKNOWN claim if it contradicts any existing FACT,
#    COUNTER, or CONTEXT. Contradiction = same subject, different object.
#    Raises ValueError on contradiction. Silent pass otherwise.
# ---------------------------------------------------------------------------
def keystone_gate(new_unknown, existing):
    new_subject = new_unknown.get("subject")
    new_object = new_unknown.get("object")

    for claim in existing:
        face = claim.get("face")
        if face not in _GATE_FACES:
            continue
        if claim.get("subject") != new_subject:
            continue
        if claim.get("object") != new_object:
            raise ValueError(
                f"Keystone Gate: UNKNOWN ({new_subject}={new_object}) "
                f"contradicts {face} ({claim.get('subject')}={claim.get('object')})"
            )
