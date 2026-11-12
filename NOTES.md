# NOTES — datacube-layer (P13 DataCube)

NOTES.md — open questions, divergences and decisions for P13 DataCube.

## Open questions
- (none)

## Divergences from v1.2.1 specification
- (none)

## Decisions
- Faces are bins, not scores. An empty face is represented as None
  rather than an empty string to distinguish "not inspected" from
  "inspected and found empty". This matches the architecture:
  "An empty COUNTER means disconfirmation wasn't sought".
- Human validation is a boolean flag passed to inspection_grade,
  NOT a seventh face. The signed attestation for human validation
  lives in a higher layer (P15 HAL). P13 just needs to know whether
  the attestation exists.
- Keystone Gate contradiction heuristic in v1.0.0: same `subject`
  and different `object` between UNKNOWN and any FACT/COUNTER/
  CONTEXT. Deliberately simple. Semantic contradiction is a v2
  concern.
- The gate raises ValueError rather than returning False. A
  contradiction is a policy violation, not a verification question.
  Silent rejection would hide the rejection from the caller.
