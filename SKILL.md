---
name: IgneousWR
description: >
  Igneous Whole-Rock geochemical plotting engine. Reads Excel data →
  19 publication-ready diagrams (TAS, REE, spider, tectonic discrimination, etc.)
  + HTML report. Cross-agent compatible (Hermes, Claude Code, Codex, Cursor, Copilot).
license: MIT
compatibility: Requires Python 3.10+, matplotlib, numpy, openpyxl
metadata:
  version: "1.0.0"
  author: Chen Yuyang
  email: asukswpu@163.com
  repository: https://github.com/Cai-Wang/igneouswr
  hermes:
    tags: [geochemistry, petrology, plotting, data-science, research]
    related_skills: [gcdkit-translator, isoplotr]
---

# IgneousWR — Igneous Whole-Rock 绘图引擎

全岩地球化学数据处理与图解绘制。读取 Excel 数据 → 19 张精选图件 + HTML 报告。
An AI-agent-powered geochemical plotting engine: Excel in, publication-ready figures out.

---

## Quick Start / 快速开始

```bash
cd scripts
pip install -e .

python3 -c "
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir
set_out_dir('/tmp/runs/myproject')
gd = GeochemData('/path/to/data.xlsx')
result = plot_recommended(gd)
"
```

---

## Diagram Catalog / 精选图目录（19 张）

### Classification / Rock Series / 分类 · 岩石系列（12）

| ID | Diagram | Status |
|----|---------|--------|
| CLS-01 | TAS (volcanic, Middlemost 1994) — 16 polygons | verified |
| CLS-02 | K₂O–SiO₂ (Middlemost 1985) | verified |
| CLS-03 | AFM (Irvine & Baragar 1971) | verified |
| CLS-04 | K₂O–SiO₂ (Peccerillo & Taylor 1976) | needs_review |
| CLS-05 | Zr/TiO₂–Nb/Y (Winchester & Floyd 1977) | verified |
| CLS-06 | Co–Th (Hastie 2007) | verified |
| CLS-10 | TiO₂–MnO–P₂O₅ ternary (Mullen 1983) | experimental |
| CLS-13 | TAS (plutonic, Middlemost 1994) | verified |
| CLS-17 | Fe# vs SiO₂ (Frost 2001) | verified |
| CLS-29 | Zr/Ti–Nb/Y (Pearce 1996) | verified |
| CLS-30 | MALI vs SiO₂ (Frost 2001) | verified |
| CLS-31 | ASI vs A/NK (Frost 2001) | verified |

### Source Characteristics / 源区性质（3）

| ID | Diagram | Status |
|----|---------|--------|
| SRC-01 | REE chondrite-normalised (Sun & McDonough 1989) | verified |
| SRC-02 | Primitive-mantle spider diagram (Sun & McDonough 1989) | verified |
| SRC-03 | Th/Yb–Nb/Yb (Pearce 2008) | verified |

### Magmatic Evolution / 岩浆演化（1）

| ID | Diagram | Status |
|----|---------|--------|
| EVO-02 | FeOt/MgO–SiO₂ (Miyashiro 1974) | verified |

### Tectonic Discrimination / 构造环境判别（3）

| ID | Diagram | Status |
|----|---------|--------|
| TEC-01 | Nb–Zr–Y ternary (Meschede 1986) | experimental |
| TEC-02 | Hf/3–Th–Ta ternary (Wood 1980) | experimental |
| TEC-05 | Ti–V (Shervais 1982) | verified |

**Status legend:** verified = user-approved, experimental = framework complete but not point-corrected, needs_review = newly added, awaiting verification.

---

## Data Input / 数据输入

Auto-detects 3 Excel layouts — **wide** (recommended), **standard**, and **transposed**:

| Layout | Row 1 | Column A |
|--------|-------|----------|
| **Wide** (recommended) | Element names (e.g. SiO₂, TiO₂…) | Sample names |
| **Standard** | Sample names | Element names |
| **Transposed** | Same as wide, detected via heuristics | |

Detection limits: parsed as half-value, zero, or NaN (configurable via `dl_strategy`).
Reference material rows (BCR, BHVO, AGV…) are auto-skipped.
View detected mode with `print(gd._detected_mode)`.

---

## Architecture / 目录结构

```
scripts/
├── igneous_wr_core.py           # Public API — re-exports everything
├── igneous_wr/
│   ├── core/
│   │   ├── data.py              # GeochemData container
│   │   ├── chem.py              # FeOt calc, chemistry helpers
│   │   ├── normalize.py         # Chondrite & PM normalisation
│   │   └── ternary.py           # Ternary↔XY transform, frame, ticks
│   ├── io/excel.py              # Excel import (3-layout auto-detect)
│   ├── diagrams/
│   │   ├── registry.py          # DiagramSpec, DIAGRAM_REGISTRY (19 entries)
│   │   ├── _classification.py   # CLS-xx group
│   │   ├── _source.py           # SRC-xx group
│   │   ├── _evolution.py        # EVO-xx group
│   │   └── _tectonic.py         # TEC-xx group
│   ├── boundaries/              # Polygon coordinates (JSON, one file per diagram)
│   ├── report/style.py          # Matplotlib style system, save_fig, scatter, HTML report
│   ├── batch/                   # plot_recommended, recommended_diagrams, batch backgrounds
│   └── references/              # Citation database (refs.json, 72 entries)
├── quick_validate.py            # Sanity check — tests all 18 diagrams via FakeGeochemData
├── generate_test_data.py        # Generate 10-sample × 41-element test Excel file
├── run_test.py                  # End-to-end: generate → plot → check output
└── merge_excel.py               # Merge major + trace element files
```

---

## Verification / 验证

After any code change, run the quick sanity check:

```bash
python3 quick_validate.py
```

This tests all 19 diagrams against `FakeGeochemData` (import + instantiation smoke test).

For end-to-end testing with synthetic data:

```bash
python3 generate_test_data.py /tmp/test_geochem_standard.xlsx
python3 run_test.py
```

After adding or removing a diagram, update `registry.py` `DIAGRAM_REGISTRY`.

---

## Styling Conventions / 风格规范

All diagrams follow these rules. AI agents modifying diagram code MUST adhere to them:

- **Wireframe-only** — no coloured polygon fills (exception: SRC-03 Pearce 2008 uses fills for source field discrimination)
- **Line weights:** Main boundaries `lw=1.5, color='#333333'`, secondary `lw=1.2, color='#666666'`, TAS polygons `lw=0.8`
- **All binary plots** must use `style_ax()` for axes (Times New Roman, inward ticks, no grid)
- **All ternary plots** must use shared helpers from `ternary.py` (`draw_ternary_frame`, `draw_ternary_ticks`, `label_ternary_vertices`)
- **Log-scale axes** must use real-number tick labels (`0.01, 0.1, 1, 10` — never scientific notation)
- **Chemical subscripts** use LaTeX: `FeO$_t$`, `SiO$_2$`, `Na$_2$O` (not Unicode, not plain text). Ternary vertex labels are the exception (Unicode is fine)
- **No scipy dependency** — do not reintroduce `from scipy import stats`
- **Boundary coordinates live in JSON files** (`boundaries/<category>/`), not in function code

---

## For AI Agents

This is a **Hermes Agent skill**. It also works with any agent supporting the agentskills.io open standard (Claude Code, Codex CLI, Cursor, GitHub Copilot, etc.).

**Before modifying diagram code, read `AGENTS.md`** at the repo root for project-specific workflow rules and file modification boundaries.

**GCDkit R → Python translations:** When adding a diagram translated from GCDkit R source, load the `gcdkit-translator` skill for the complete translation guide, including ternary coordinate handling, log-axis preprocessing detection, and the shared-edge vertex alignment rule.

**Known pitfalls** (to avoid repeating past fixes):
1. Ternary boundary coordinates from GCDkit are **already projected** (x∈[0,1], y∈[0,0.866]) — do not pass through `ternary_to_xy()` again
2. Adjacent polygons must share **identical vertex sequences** on shared edges (no one-side-straight, other-side-polyline)
3. GCDkit's filled polygons can mask misaligned shared edges — wireframe mode exposes them
4. Log-space lines sometimes need extrapolation beyond GCDkit's fill-trimmed coordinates
5. R strings `"text\nwith\nnewlines"` use real `\n` — Python must use `'text\nwith\nnewlines'` (single backslash-n), not `'text\\nwith\\nnewlines'`
6. **Eu/Eu\* and Ce/Ce\* use geometric mean** (`√(SmN × GdN)`), not arithmetic mean (`(SmN + GdN) / 2`). Arithmetic mean in log-space interpolation produces scientifically wrong values. Caught in 2026-06-10 audit, fixed at `merge_excel.py:128,137`.
7. **Truthiness on float values** — `if ree_vals['Eu']` skips Eu=0.0 (valid data!). Always use `is not None` for nullable float values. Same for any chondrite-normalised ratio that could be zero.
8. **feot_calc NaN mixing** — when `FeO` is valid but `TFe2O3` is NaN, `feo + 0.8998 * NaN = NaN` silently drops valid data. The fixed logic at `chem.py:21` uses nested `np.where` to zero-out NaN before the multiply.
9. **ΣREE partial-sum trap** — old code required ALL 14 REE present (`all_ok`) before summing, dropping valid data for samples missing a single trace REE. Fixed to sum whatever is available.
10. **set_style_preset() globals() injection** — without a `valid_keys` whitelist, a corrupted `STYLE_PRESETS` dict can overwrite any module variable. Both `set_style()` and `set_style_preset()` now share a whitelist at `style.py:362`.

---

## References / 参考

All 72 citations are stored in `scripts/igneous_wr/references/refs.json` and auto-rendered in the HTML report. Each diagram has a citation imprint in the bottom-right corner.

## Git / Publishing Rules

This repo is for **end users** (geologists), not an agent development notebook. The README and all committed docs must be user-facing — describe the tool, not the agent.

- **Commit only** files that affect the tool's functionality: code, boundary JSONs, test scripts, README, AGENTS.md, pyproject.toml, .gitignore.
- **Do NOT commit:** audit reports, review checklists, data audit docs, dev-notes, fix annotations in docstrings, or any reference that documents "how the agent works on this project".
- Hermes skill `references/` and internal workflow documentation stay **local** in `~/.hermes/skills/data-science/IgneousWR/` — never push them to GitHub.
- **Pitfall: `git add -A` picks up new files in the repo root.** If you created a new markdown file locally (audit report, workflow doc, etc.), `git add -A` stages it. Always `git status` before committing to catch unintended new files.
- **Pitfall: every row in README diagram tables must have a non-empty reference citation.** The "引用" column is for user-facing author-year references (e.g. "Frost et al. (2001)"). Leaving it blank will be caught and corrected.
- If unsure whether a new file belongs in the package or is internal agent guidance, **ask the user before committing**.

Related skills (Hermes):
- `gcdkit-translator` — GCDkit R → IgneousWR Python translation guide
- `isoplotr` — U-Pb geochronology (separate package)
