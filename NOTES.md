# NOTES — datacube-layer (P13 DataCube)

NOTES.md — open questions, divergences and decisions for P13 DataCube.

## Open questions
- Trust weighting: should a FACT with low λ (P14) still block an
  UNKNOWN outright, or only above a threshold? Needs a P14 consumer
  decision before v3.

## Divergences from SPEC.md v1.0.0 (found in laptop audit, 2026-11-12)
D1–D5 closed in datacube_v2.py (SPEC_V2.md). datacube.py is frozen
and unedited.

- D1 — `keystone_gate` never checks that the new claim is UNKNOWN
  (SPEC §4.5). A claim with `face="FACT"` is gated as if it were a
  hypothesis. Closed by SPEC_V2 §2.2.
- D2 — claims are not validated. Two claims with no `subject`
  compare `None == None` and raise a spurious contradiction; a cube
  can be created with no subject or object (SPEC §4.1 says "at
  minimum"). Closed by SPEC_V2 §2.1.
- D3 — `inspection_grade(cube, "no")` returns CRYSTALLINE: any truthy
  value counts as the human attestation. Closed by SPEC_V2 §2.7
  (`TypeError` on non-bool).
- D4 — an existing claim whose face label is unknown or mis-cased
  (`"fact"`) is silently skipped, so it never blocks a contradiction;
  a non-dict entry crashes with `AttributeError`. Closed by SPEC_V2
  §2.3 (fail closed with `ValueError`).
- D5 — comparison is raw string equality: `"Blue"` vs `"blue"` is a
  contradiction, while `"SKY"` vs `"sky"` escapes the gate. Closed by
  normalisation (SPEC_V2 §2.4).
- D6 — `inspection_grade` has a redundant condition
  (`count <= 1 and not (count == 5 or count == 6)`). Behaviour is
  correct; left in the frozen primitive.
- D7 — README status still read `0.0.0-dev` and the scaffold
  CHANGELOG entry had no heading. Fixed in docs.

## Decisions
- Faces are bins, not scores. An empty face is represented as None
  rather than an empty string to distinguish "not inspected" from
  "inspected and found empty". This matches the architecture:
  "An empty COUNTER means disconfirmation wasn't sought". v2 JSON
  preserves the None / "" distinction.
- Human validation is a boolean flag passed to inspection_grade,
  NOT a seventh face. The signed attestation for human validation
  lives in a higher layer (P15 HAL). P13 just needs to know whether
  the attestation exists. v2 rejects any extra cube key, so a
  `human_validated` field can never ride along as a face.
- Keystone Gate contradiction heuristic in v1.0.0: same `subject`
  and different `object` between UNKNOWN and any FACT/COUNTER/
  CONTEXT. Deliberately simple. Semantic contradiction is a v2
  concern.
- The gate raises ValueError rather than returning False. A
  contradiction is a policy violation, not a verification question.
  Silent rejection would hide the rejection from the caller.
- v2 fails closed: a corrupt memory entry rejects the write rather
  than being skipped. Letting a hypothesis in because memory was
  unreadable would defeat the gate.

## v2 option decisions (PROMPT_P13.md step 5)
- Semantic contradiction — PARTIAL. Adopted deterministic
  normalisation (NFKC, casefold, whitespace) and a `contradicts`
  hook that must return bool. No semantic model ships: it would add
  a heavy, non-deterministic dependency to a primitive. Consumers
  plug one in through the hook.
- P12 integration — ADOPTED as `register_gate_rule`. Duck-typed on
  `engine.register`, so P13 does not import P12 at module load. The
  rule defaults to priority 100 so it runs before ordinary rules;
  memory may be a callable so the rule sees current state.
- Cube merging — ADOPTED as `merge_cubes(older, newer, on_conflict)`.
  Default `"raise"`: faces are evidence bins, and silently dropping
  one side's content would lose evidence. Callers opt in to
  `keep_older` / `keep_newer`.
- JSON serialisation — ADOPTED with a `p13.cube/2` schema tag and
  strict loading. JSON is a format; storage stays P9's job.
- Write-time gate — ADOPTED as `write_claim` (not in the prompt's
  list): it makes "the gate fires on write" a single call instead of
  a convention every consumer must remember.
- Trust weighting — DEFERRED (see Open questions).
