"""
conftest.py — pytest path setup for P13 DataCube

Function:
    Puts this directory and the sibling P12, P2 and P1 directories
    (../rules-layer, ../sign-layer, ../envelope-layer) on sys.path,
    located from this file rather than the working directory, so
    test_datacube.py and test_datacube_v2.py run from any directory.
    The P12 integration tests skip if those siblings are absent.
    Contains no functions.

Layer:    P13 — DataCube
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

for _p in (
    os.path.join(_ROOT, "envelope-layer"),
    os.path.join(_ROOT, "sign-layer"),
    os.path.join(_ROOT, "rules-layer"),
    _HERE,
):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
