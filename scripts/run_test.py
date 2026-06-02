#!/usr/bin/env python3
"""Generate test plots with synthetic data."""
import sys
sys.path.insert(0, ".")
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir

OUT_DIR = "/mnt/c/Users/opcry/Desktop/igenous"
DATA = "/tmp/test_geochem_standard.xlsx"

set_out_dir(OUT_DIR)
gd = GeochemData(DATA)
result = plot_recommended(gd)
print(f"\n=== 完成: {len(result)} 张图 ===")
for r in sorted(result):
    print(f"  {r}")
