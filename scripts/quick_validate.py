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
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(111)
        try:
            result = fn(gd_min, ax=ax)
            status = "✓" if result[0] is not None else "⚠ none"
        except TypeError:
            # 旧签名函数（无 ax 参数），退回到无 ax 调用
            fig, ax = plt.subplots()
            result = fn(gd_min)
            status = "✓" if result[0] is not None else "⚠ none"
        del fig, ax
    except Exception as e:
        status = f"❌ {e}"
    print(f"  {spec.filename}: {status}")
print("Done.")
