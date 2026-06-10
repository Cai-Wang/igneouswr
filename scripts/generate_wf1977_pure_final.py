#!/usr/bin/env python3
"""
Final version — Pure Winchester & Floyd (1977) Zr/TiO₂-Nb/Y classification base map.
No sample points, just boundary lines and lithology labels.

Coordinate system (TRANSPOSED from JSON):
  JSON stores [Nb/Y, Zr/TiO₂] per node.
  We swap: X = Zr/TiO₂ (linear 0~500), Y = Nb/Y (log 0.01~10)
  
  X axis label: "Zr/TiO₂ (×10⁻⁴)" — values are Zr/TiO₂ × 100 for display
  Y axis label: "Nb/Y"

Key insight from analysis:
  JSON values are LINEAR ratios, not log10.
  Nb/Y range: 0.021~10.000
  Zr/TiO₂ range: 0.002~3.022
  
  Scale factor: 100 (max Zr/TiO₂=3.022 → 302 on 0~500 scale)
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Add IgneousWR to path (assumes running from project root or scripts/)
WR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')
if not os.path.isdir(WR_PATH):
    WR_PATH = '.'
sys.path.insert(0, WR_PATH)
os.chdir(WR_PATH)

from igneous_wr.boundaries.core import load_boundary

# ── Load boundary data ──────────────────────────────────────
_wf = load_boundary('cls', 'winchester_floyd')
nodes = {int(k): v for k, v in _wf['nodes'].items()}  # {id: [Nb/Y, Zr/TiO₂]}
edges = _wf['edges']
labels_raw = _wf['labels']  # list of dicts, x=Nb/Y, y=Zr/TiO₂

FACTOR = 100.0  # Scale Zr/TiO₂ by 100 to fit in 0~500

# ── Create figure ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))

# ── Draw 9 boundary lines (transposed) ─────────────────────
for edge in edges:
    xs_line = [nodes[n][1] * FACTOR for n in edge]  # Zr/TiO₂ → X
    ys_line = [nodes[n][0] for n in edge]             # Nb/Y → Y
    ax.plot(xs_line, ys_line, color='#333333', linewidth=1.5,
            solid_capstyle='round', zorder=2)

# ── Lithology labels (gray, transposed) ────────────────────
for lbl in labels_raw:
    x_pos = lbl['y'] * FACTOR   # Zr/TiO₂ → X
    y_pos = lbl['x']             # Nb/Y → Y
    text = lbl['text']
    fs = lbl.get('fontsize', 10)
    ax.text(x_pos, y_pos, text, fontsize=fs, color='#777777',
            ha='center', va='center', fontweight='normal', zorder=3)

# ── Reference text (bottom right, gray italic) ─────────────
ax.text(0.98, 0.02, 'Winchester & Floyd (1977)',
        transform=ax.transAxes, fontsize=9,
        ha='right', va='bottom', style='italic', color='grey')

# ── Axis settings ──────────────────────────────────────────
ax.set_xlim(0, 500)
ax.set_ylim(0.01, 10)
ax.set_yscale('log')

ax.set_xlabel('Zr/TiO₂ (×10⁻⁴)')
ax.set_ylabel('Nb/Y')

# X ticks
ax.set_xticks(range(0, 501, 50))
ax.tick_params(axis='both', which='major', labelsize=9)

# Grid
ax.grid(True, which='major', alpha=0.3, linestyle=':', color='#cccccc')
ax.grid(True, which='minor', alpha=0.15, linestyle=':', color='#cccccc')

plt.tight_layout(pad=0.3)

# ── Save ────────────────────────────────────────────────────
output_dir = './runs'
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'WF1977_ZrTiO2_NbY_pure.png')
fig.savefig(output_path, dpi=200, bbox_inches='tight')
plt.close(fig)

print(f"\n✅ Winchester & Floyd (1977) pure base map generated!")
print(f"   File: {output_path}")
print(f"   Size: {os.path.getsize(output_path):,} bytes")
print(f"   Axes: X=Zr/TiO₂ (linear 0~500), Y=Nb/Y (log 0.01~10)")
print(f"   Data points: None (pure classification boundaries only)")
