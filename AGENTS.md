# IgneousWR

Igneous Whole-Rock geochemical plotting engine. Reads Excel data → 19 publication-ready diagrams + HTML report.

Python 3.10+, matplotlib, numpy, openpyxl.

---

## Commands

```bash
# ── Install ──
cd scripts
pip install -e .

# ── Quick sanity check (import + FakeGeochemData, runs against all 19 diagrams) ──
python3 quick_validate.py

# ── Full pipeline with synthetic data ──
python3 generate_test_data.py /tmp/test_geochem_standard.xlsx
python3 run_test.py

# ── Batch background generation (regenerates all 19 blank backgrounds) ──
python3 -c "from igneous_wr.batch.backgrounds import run_batch; run_batch()"
```

---

## Architecture

```
scripts/
├── igneous_wr_core.py           # Public API (re-exports everything)
├── igneous_wr/
│   ├── core/                    # GeochemData data container, chemistry, normalisation, ternary transforms
│   ├── io/                      # Excel import (auto-detects wide/standard/transposed layouts)
│   ├── diagrams/                # 19 diagram functions + registry
│   │   ├── registry.py          # DiagramSpec, DIAGRAM_REGISTRY (19 entries), mafic/felsic lists
│   │   ├── _classification.py   # CLS-xx: TAS, K2O-SiO2, AFM, Winchester-Floyd, Co-Th, Mullen, etc.
│   │   ├── _source.py           # SRC-xx: REE, spider, Pearce 2008
│   │   ├── _evolution.py        # EVO-xx: Miyashiro
│   │   └── _tectonic.py         # TEC-xx: Meschede, Wood, Shervais
│   ├── boundaries/              # Polygon boundary data (JSON files, one per diagram type)
│   ├── report/                  # Matplotlib style system, HTML report generation
│   ├── batch/                   # plot_recommended(), recommended_diagrams(), batch backgrounds
│   └── references/              # Reference database (refs.json, 72 entries)
├── quick_validate.py            # Import/instantiation sanity check (no pytest)
├── generate_test_data.py        # Creates synthetic 10-sample × 41-element Excel file
├── run_test.py                  # End-to-end: generate data → plot_recommended → check output
└── merge_excel.py               # Utility: merge major + trace element Excel files
```

---

## Code Style (this project only)

- **No pytest.** Validation is done via `quick_validate.py` (import + run against `FakeGeochemData`).
- **All diagrams must be registered** in `registry.py` `DIAGRAM_REGISTRY` as `DiagramSpec` entries.
- **Boundary coordinates live in JSON**, not in function code (`boundaries/cls/`, `boundaries/src/`, etc.).
- **All binary plots** must use `style_ax()` for axes styling. No handwritten `set_xlabel`/`minorticks_on`.
- **All ternary plots** must use the shared `ternary.py` helper functions (`draw_ternary_frame`, etc.).
- **Line style convention:** main boundaries `lw=1.5, color='#333333'`, secondary boundaries `lw=1.2, color='#666666'`, TAS polygons `lw=0.8`.
- **No coloured fills** (pure wireframe style). Exception: Pearce 2008 Th/Yb-Nb/Yb.
- **Log-scale axes must use real-number tick labels** (0.01, 0.1, 1, 10 — not scientific notation).
- **LaTeX for chemical subscripts:** `FeO$_t$`, `SiO$_2$`, `Na$_2$O` (not Unicode, not plain text).
- **No scipy dependency** — the three `from scipy import stats` in diagram files have been removed. Do not reintroduce.

---

## Workflow Rules

- Every Python file change → run `python3 quick_validate.py` to confirm no import/instantiation breakage.
- After adding or removing a diagram → update `registry.py` **and** the diagram count in comments/docs.
- JSON boundary files go in `boundaries/<prefix>/`, named by diagram theme (e.g. `tas.json`, `afm.json`).
- When translating a diagram from GCDkit R source: adjacent polygons must share **identical vertex sequences** on shared edges (no one-side-straight, other-side-polyline).

---

## For AI Agents

This repository contains a **Hermes Agent skill** (`SKILL.md` at the repo root, also mirrored in the skills catalog at `~/.hermes/skills/data-science/IgneousWR/`).

If you are an AI coding agent assisting with this project:

1. Read `SKILL.md` **first**. It documents every diagram's verification status, the full styling system, known pitfalls from past fixes, and the deletion workflow.
2. The SKILL.md is the authoritative reference. It may contain project-specific rules not duplicated here.
3. If the user says "load IgneousWR skill", look in `~/.hermes/skills/data-science/IgneousWR/SKILL.md` (Hermes) or `SKILL.md` at repo root (agentskills.io compatible).

---

## Files the agent should NOT modify without explicit instruction

- `scripts/igneous_wr/references/refs.json` — citation database, 72 entries, auto-loaded by the HTML report
- `.gitignore` — filters output directories (runs/, *_output/, *.png, *.html)
- `pyproject.toml` — package metadata, build config, dependencies
