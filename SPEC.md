# SPEC — datacube-layer (P13 DataCube)

SPEC.md — the complete layer specification for P13 DataCube.

Function:
    This document is the authoritative specification for primitive
    layer P13 of the Forge Stack. It defines the six-face structure
    of a claim, the inspection grades, and the Keystone Gate.

Layer:     P13 — DataCube
Depends:   P12 Rules, P14 Leighton Engine
Consumed:  P15 HAL, SC-OS, The Cockpit
Version:   SPEC 1.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

## 1. The Six Faces

Every claim is a cube with six faces (bins, not scores):

    FACT     — Verifiable truth
    COUNTER  — Opposing argument or disconfirmation
    OPINION  — Personal perspective
    FICTION  — Speculative take
    CONTEXT  — Historical framing or evidence source
    UNKNOWN  — Open questions, hypotheses (the "Dream Space")

Critical: an empty COUNTER means disconfirmation was not sought.
It does NOT mean none exists. Faces are bins; presence or absence
of content is a signal of what was inspected, not what is true.

## 2. Inspection Grades

Grades are mutually exclusive, determined by how many faces have
content AND whether human validation has been recorded:

    CRYSTALLINE — all 6 faces filled + human validation
    COHERENT    — exactly 5 faces filled + human validation
    FORMING     — 2-4 faces filled
    SPARSE      — 0-1 faces filled

Human validation is a SEPARATE signed attestation. It is NEVER a
seventh face. A cube with 5 faces filled but no human validation
is FORMING, not COHERENT.

## 3. The Keystone Gate

The Keystone Gate enforces logical consistency on the UNKNOWN face.

Rule: An UNKNOWN hypothesis cannot contradict FACT, COUNTER, or
CONTEXT. If it does, the claim is rejected before entering memory.

The gate is content-agnostic in v1.0.0: "contradiction" is defined
as the UNKNOWN claim's `subject` matching a FACT/COUNTER/CONTEXT
claim's `subject` AND having a different `object`. This is a
deliberately simple heuristic — semantic contradiction detection
is a P13 v2 concern, not v1.

If contradiction is detected, the gate raises ValueError with a
descriptive message. The gate fires on write, so a rejected claim
never reaches the substrate (P9).

## 4. Function Contracts

### 4.1 create_cube(claim: dict) -> dict
- Input: a claim dict with a `subject` and `object` at minimum.
- Output: cube dict with six faces, each None if not inspected.
- Empty faces are None, not empty strings.

### 4.2 set_face(cube: dict, face: str, content: str) -> dict
- Sets a face to content.
- Raises ValueError if `face` is not one of the six known faces.
- Raises ValueError if content is not a string.

### 4.3 count_faces(cube: dict) -> int
- Returns the count of non-None faces (0-6).

### 4.4 inspection_grade(cube: dict, human_validated: bool) -> str
- Returns CRYSTALLINE, COHERENT, FORMING, or SPARSE.
- human_validated must be True for CRYSTALLINE or COHERENT.

### 4.5 keystone_gate(new_unknown: dict, existing: list[dict]) -> None
- Input:
  - new_unknown: the new UNKNOWN claim (must be classified as UNKNOWN).
  - existing: list of previously stored claims (any face).
- Output: None on pass, raises ValueError on contradiction.
- Contradiction: any existing FACT/COUNTER/CONTEXT claim with the
  same `subject` and different `object`.

## 5. Known Limitations (P13 v1.0.0)

- Contradiction detection is string-equality based. Semantic
  contradiction detection is a v2 concern.
- No cube persistence. P13 returns structures; storage is P9's job.
- No integration with P12 rule firing yet. P13 exposes the gate
  as a function; wiring it into the engine is a consumer concern.
- No trust weighting in the gate. A FACT with λ = 0.5 counts the
  same as a FACT with λ = 2.0. Weighing the gate by trust is a v2
  concern.
