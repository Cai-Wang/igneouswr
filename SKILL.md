---
name: IgneousWR
description: >
  Igneous Whole-Rock geochemical plotting engine. Reads Excel data →
  19 publication-ready diagrams (TAS, REE, spider, tectonic discrimination, etc.)
  + HTML report. Cross-agent compatible.
license: MIT
compatibility: Requires Python 3.10+, matplotlib, numpy, openpyxl
metadata:
  version: "1.0.0"
  author: Chen Yuyang
  email: asukswpu@163.com
  repository: https://github.com/Cai-Wang/igneouswr
  hermes:
    tags: [geochemistry, petrology, plotting, data-science, research]
    related_skills: [isoplotr]
---

# IgneousWR — Agent Usage Manual

This file tells you (the AI agent) exactly how to use IgneousWR: API signatures, parameter semantics, workflow order, and known pitfalls.

---

## Core API Reference

### Import

```python
from igneous_wr_core import (
    GeochemData,          # data container (main entry)
    plot_recommended,     # batch plot: auto-selects diagrams based on data
    plot_diagram,         # single diagram by ID
    set_out_dir,          # override output directory
    DIAGRAM_REGISTRY,     # dict of all diagram specs
    recommended_diagrams, # returns list of diagram IDs for a GeochemData
    plot_diagram_ids,     # plot a specific list of diagram IDs
)
```

### Data Loading — `GeochemData(path, **kwargs)`

```python
gd = GeochemData("data.xlsx")
gd = GeochemData("data.xlsx", sheet_name=0, dl_strategy="half")
```

| Param | Default | Options | Description |
|-------|---------|---------|-------------|
| `path` | (required) | str | Path to .xlsx file |
| `sheet_name` | 0 | int or str | Sheet index or name |
| `dl_strategy` | "half" | "half", "zero", "nan" | How to handle detection limits (<) |
| `repair` | False | bool | If True, re-parse as 'standard' then transpose |

Auto-detects 3 layouts: wide (Row 1 = element names, Col A = sample names), standard (transposed), transposed (same as wide, heuristic). Check `gd._detected_mode`.

Reference material rows (BCR, BHVO, AGV) are auto-skipped.

### Batch Plotting — `plot_recommended(gd, output_dir=None)`

```python
result = plot_recommended(gd)
```

Returns:
```python
{
    "output_dir": "./runs/...",
    "html_report": "./runs/.../report.html",
    "figures": [{"id": "CLS-01", "path": "...", "status": "generated", "error": None}, ...],
    "total": 19, "generated": 17, "failed": 0,
    "diagrams_plotted": [...],
    "diagrams_skipped": [...],
}
```

### Single Diagram — `plot_diagram(gd, diagram_id, output_dir=None)`

```python
result = plot_diagram(gd, "CLS-01")
```

### Custom Selection — `plot_diagram_ids(gd, diagram_ids, output_dir=None)`

### Recommended List — `recommended_diagrams(gd)` → list of diagram IDs

### Output Directory — `set_out_dir("/tmp/runs")` — defaults to `./runs/<timestamp>/`

### Registry — `DIAGRAM_REGISTRY` — dict of `DiagramSpec` objects

Each spec: `.id`, `.title`, `.category`, `.status`, `.required_elements`, `.func`

---

## Agent Workflow (correct order)

```
Step 1: gd = GeochemData(path)
        If layout misdetected (too few elements), try gd = GeochemData(path, repair=True)

Step 2: recommended_diagrams(gd) — check what diagrams can be plotted

Step 3: result = plot_recommended(gd)

Step 4: Report: generated count, skipped count + reasons, HTML report path
```

---

## Diagram Catalog (19 total)

### Classification / Rock Series (12)

| ID | Diagram | Status | Requires |
|----|---------|--------|----------|
| CLS-01 | TAS volcanic (Middlemost 1994) | verified | SiO₂, Na₂O, K₂O |
| CLS-02 | K₂O–SiO₂ (Middlemost 1985) | verified | SiO₂, K₂O |
| CLS-03 | AFM (Irvine & Baragar 1971) | verified | SiO₂, Na₂O, K₂O, FeOt, MgO |
| CLS-04 | K₂O–SiO₂ (Peccerillo & Taylor 1976) | needs_review | SiO₂, K₂O |
| CLS-05 | Zr/TiO₂–Nb/Y (Winchester & Floyd 1977) | verified | Zr, TiO₂, Nb, Y |
| CLS-06 | Co–Th (Hastie 2007) | verified | Co, Th |
| CLS-10 | TiO₂–MnO–P₂O₅ ternary (Mullen 1983) | experimental | TiO₂, MnO, P₂O₅ |
| CLS-13 | TAS plutonic (Middlemost 1994) | verified | SiO₂, Na₂O, K₂O |
| CLS-17 | Fe# vs SiO₂ (Frost 2001) | verified | SiO₂, FeOt, MgO |
| CLS-29 | Zr/Ti–Nb/Y (Pearce 1996) | verified | Zr, Ti, Nb, Y |
| CLS-30 | MALI vs SiO₂ (Frost 2001) | verified | SiO₂, Na₂O, K₂O, CaO |
| CLS-31 | ASI vs A/NK (Frost 2001) | verified | SiO₂, Al₂O₃, CaO, Na₂O, K₂O |

### Source Characteristics (3)

| ID | Diagram | Status | Requires |
|----|---------|--------|----------|
| SRC-01 | REE chondrite-normalised | verified | ≥1 REE |
| SRC-02 | Primitive-mantle spider | verified | trace elements |
| SRC-03 | Th/Yb–Nb/Yb (Pearce 2008) | verified | Th, Yb, Nb |

### Magmatic Evolution (1)

| ID | Diagram | Status | Requires |
|----|---------|--------|----------|
| EVO-02 | FeOt/MgO–SiO₂ (Miyashiro 1974) | verified | SiO₂, FeOt, MgO |

### Tectonic Discrimination (3)

| ID | Diagram | Status | Requires |
|----|---------|--------|----------|
| TEC-01 | Nb–Zr–Y ternary (Meschede 1986) | experimental | Nb, Zr, Y |
| TEC-02 | Hf/3–Th–Ta ternary (Wood 1980) | experimental | Hf, Th, Ta |
| TEC-05 | Ti–V (Shervais 1982) | verified | Ti, V |

**Status for agents:** verified = safe for publications; experimental = framework complete, not point-corrected (flag to user as preliminary); needs_review = newly added.

---

## Styling Conventions

- **Wireframe-only** (exception: SRC-03 Pearce 2008)
- Main boundaries `lw=1.5, color='#333333'`, secondary `lw=1.2, color='#666666'`
- Binary plots: use `style_ax()` — Times New Roman, inward ticks, no grid
- Ternary plots: use `ternary.py` helpers (`draw_ternary_frame`, etc.)
- Log-scale: real-number tick labels (`0.01, 0.1, 1, 10` — no scientific notation)
- LaTeX: `FeO$_t$`, `SiO$_2$` (ternary vertex labels: Unicode OK)
- No scipy dependency
- Boundary coordinates in JSON, not function code

---

## Verification

```bash
python3 quick_validate.py            # import + instantiation test
python3 generate_test_data.py /tmp/t # create synthetic data
python3 run_test.py                  # end-to-end pipeline
```

After adding/removing a diagram, update `DIAGRAM_REGISTRY` in `registry.py`.

---

## Related Skills

- `isoplotr` — U-Pb geochronology
