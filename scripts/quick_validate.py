#!/usr/bin/env python3
"""Quick validate — check all diagram functions import and instantiate correctly."""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY
print(f"Registry OK: {len(DIAGRAM_REGISTRY)} diagrams")

from igneous_wr.batch.backgrounds import FakeGeochemData
gd_min = FakeGeochemData(mode='minimal')

for spec in DIAGRAM_REGISTRY:
    try:
        fn = spec.fn
        fig, ax = fn(gd_min, out_dir=None, save=False)
        status = "✓" if fig is not None else "⚠ none"
    except Exception as e:
        status = f"❌ {e}"
    print(f"  {spec.filename}: {status}")
print("Done.")
