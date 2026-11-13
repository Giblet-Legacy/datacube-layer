# datacube-layer — P13 DataCube

README.md — repository purpose and layer contract for P13 DataCube.

Function:
    This repository implements primitive layer P13 of the Forge Stack:
    the six-face classifier and the Keystone Gate. It defines the
    structure of a claim (six faces), the inspection grades, and the
    rule that an UNKNOWN hypothesis cannot contradict FACT, COUNTER,
    or CONTEXT.

Layer:    P13 — DataCube
Depends:  P12 Rules, P14 Leighton Engine
Consumed: P15 HAL, SC-OS, The Cockpit
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   2.0.0 (v1 frozen; new code imports datacube_v2 — see SPEC_V2.md).
          datacube_v3.py (SPEC_V3.md: polarity-aware Keystone Gate) frozen at 3.0.0.
