# Forge Stack Context — P13 DataCube

CLAUDE.md — Context briefing for AI assistants working in this repository.

## The Immutable Rule
Never rewrite a primitive. Add a layer.

## Dual-Device Workflow
We build on an S24 (Termux) and a laptop (VS Code). State is confirmed, never assumed. Always use LF line endings. Commit messages must be clear. We use the Good/Bad/Ugly CHANGELOG format (latest at top).

## Header Discipline
Every file MUST have a top header paragraph explaining its function.
Every function MUST have a numbered header.

## P13 Architecture Specifics
- Depends on P12 (Rules) and P14 (Leighton Engine).
- Six faces: FACT, COUNTER, OPINION, FICTION, CONTEXT, UNKNOWN.
- Faces are BINS, not scores. An empty COUNTER means disconfirmation was not sought, NOT that none exists.
- UNKNOWN is the Dream Space. It is policed by the Keystone Gate.
- Inspection grades: CRYSTALLINE (6 + human), COHERENT (5 + human), FORMING (2-4), SPARSE (0-1).
- Human validation is a separate signed attestation, NEVER a seventh face.

## Keystone Gate Rule (CRITICAL)
An UNKNOWN hypothesis cannot contradict a FACT, COUNTER, or CONTEXT face. The gate fires on write. If a contradiction is detected, the claim is rejected before it enters memory.

## v3 layer
`datacube_v3.py` (SPEC_V3.md, frozen 3.0.0): the gate refuses an UNKNOWN only
for the same subject and object with the opposite polarity, so a subject can hold
many claims. v2's rule is `contradicts_v2`. Cockpit v1.3 gates through v3.
