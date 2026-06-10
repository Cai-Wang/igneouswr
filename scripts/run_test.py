#!/usr/bin/env python3
"""Generate test plots with synthetic data."""
import sys
sys.path.insert(0, ".")
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir

OUT_DIR = "./runs/default"
DATA = "/tmp/test_geochem_standard.xlsx"

set_out_dir(OUT_DIR)
gd = GeochemData(DATA)
result = plot_recommended(gd)
print(f"\n=== 完成: {len(result['success'])} 张图，跳过 {len(result['skipped'])} ===")
for name, fname in result['success']:
    print(f"  ✓ {name} → {fname}")
for desc, reason in result['skipped']:
    print(f"  ✗ {desc} ({reason})")
