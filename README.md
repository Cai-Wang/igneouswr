# IgneousWR

**Igneous Whole-Rock geochemical plotting — an AI Agent skill for igneous petrology.**

This is a **skill for AI agents** (Hermes Agent, Claude Code, Codex CLI, or any LLM agent with tool-use capability). When loaded, the agent can read Excel geochemical data, automatically generate 19 publication-ready diagrams (classification, source, evolution, tectonic discrimination), and produce a self-contained HTML report.

No manual clicking, no GUI — the agent handles everything from data loading to final figure output.

## Diagrams (19 total)

| Prefix | Category | Count |
|--------|----------|-------|
| CLS | Classification / Rock series | 12 |
| SRC | Source characteristics | 3 |
| EVO | Magmatic evolution | 1 |
| TEC | Tectonic discrimination | 3 |

**Classification:** TAS (volcanic & plutonic), K₂O–SiO₂ (Middlemost 1985 & Peccerillo-Taylor 1976), AFM, Winchester & Floyd 1977, Co-Th (Hastie 2007), Mullen ternary, Pearce 1996 Zr/Ti–Nb/Y, Frost Fe#/MALI/ASI-ANK

**Source:** REE chondrite-normalised, Primitive-mantle spider diagram, Pearce 2008 Th/Yb–Nb/Yb

**Evolution:** Miyashiro 1974 FeOt/MgO–SiO₂

**Tectonic:** Meschede Nb–Zr–Y ternary, Wood Hf/3–Th–Ta ternary, Shervais Ti–V

Each diagram is verified against GCDkit or original literature references, with accurate polygon boundaries and consistent styling.

## How AI agents use it

```bash
# Load the skill, then in your agent prompt:
cd scripts
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir

set_out_dir('./my_runs')
gd = GeochemData('./my_data.xlsx')
result = plot_recommended(gd)
```

The agent handles data format detection (wide / standard / transposed), normalisation to chondrite/primitive-mantle, and layout/annotation — all automated.

## Data format

`GeochemData` auto-detects three Excel layouts:

- **Wide**: Row 1 = element names, Column A = sample names
- **Standard**: Row 1 = sample names, Column A = element names
- **Transposed**: Same as wide but detected via heuristics

Detection limits: parsed as half-value, zero, or NaN.

## Architecture

```
scripts/
  igneous_wr_core.py      # Public API
  igneous_wr/
    core/                  # GeochemData, chemistry, normalisation, ternary transforms
    io/                    # Excel reading
    diagrams/              # 19 diagram functions + registry
    report/                # Matplotlib style, HTML report generation
    batch/                 # plot_recommended, batch background generation
    boundaries/            # Polygon boundary data (JSON)
    references/            # Reference database (refs.json, 72 entries)
```

## References

All diagrams include a citation imprint in the bottom-right corner. Full reference list appears in the HTML report.

## License

MIT — Copyright (c) 2026 Chen Yuyang
