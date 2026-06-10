# IgneousWR

Igneous Whole-Rock geochemical plotting engine — reads Excel data and produces
publication-ready diagrams for igneous petrology. 19 diagrams covering
classification, source, evolution, and tectonic discrimination.

## Quick start

```bash
pip install numpy matplotlib scipy openpyxl
pip install -e .

cd scripts
python3 -c "
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir

set_out_dir('./my_runs')
gd = GeochemData('./my_data.xlsx')
result = plot_recommended(gd)
print(f'{len(result)} diagrams generated')
"
```

Your Excel file should have elements as rows and samples as columns (standard format),
or samples as rows and elements as columns (transposed format) — auto-detected.

## Output

An HTML report (`report_YYYYMMDD.html`) is generated alongside PNG files.
All diagrams are named with a prefix and number for easy reference:

| Prefix | Category | Count |
|--------|----------|-------|
| CLS | Classification / Rock series | 12 |
| SRC | Source characteristics | 3 |
| EVO | Magmatic evolution | 1 |
| TEC | Tectonic discrimination | 3 |

## Diagram examples

- **TAS** — Total Alkali-Silica (Middlemost 1994)
- **K₂O–SiO₂** — Potassium classification (Middlemost 1985)
- **AFM** — Alkali-FeO-MgO (Irvine & Baragar 1971)
- **Winchester & Floyd** — Zr/TiO₂ vs Nb/Y classification
- **Pearce 1996** — Zr/Ti vs Nb/Y volcanic rock classification
- **REE** — Chondrite-normalised REE patterns
- **Spider** — Primitive-mantle normalised multi-element diagrams
- **Pearce 2008** — Th/Yb vs Nb/Yb source discrimination
- **Frost series** — Fe#, MALI, ASI-ANK classification
- **Miyashiro** — FeOt/MgO vs SiO₂ discrimination
- **Shervais** — Ti-V tectonic discrimination
- **Mullen / Meschede / Wood** — Ternary discriminant diagrams

See the full registry in `scripts/igneous_wr/diagrams/registry.py`.

## Data format

`GeochemData` reads Excel files with auto-detection of three layouts:

- **Standard**: Row 1 = sample names, Column A = element names
- **Wide**: Row 1 = element names, Column A = sample names (A1 = "Sample" or empty)
- **Transposed**: Row 1 = element names, Column A = sample names from a readable row

Detection is based on counting known element names across Row 1 vs Column A.
Detection limits can be parsed as half-value, zero, or NaN.

## Architecture

```
scripts/
  igneous_wr_core.py      # Public API (re-export)
  igneous_wr/
    core/                  # GeochemData, chem, normalize, ternary
    io/                    # Excel reading
    diagrams/              # 19 diagram functions
      registry.py          # DiagramSpec + DIAGRAM_REGISTRY
    report/                # Style, HTML report generation
    batch/                 # plot_recommended, batch backgrounds
    boundaries/            # Boundary data (JSON)
    references/            # Reference database (refs.json)
```

## References

All diagrams include a citation imprint in the bottom-right corner.
The full reference list appears at the end of the HTML report.
The reference database (`refs.json`) contains 72 reference entries (72 unique publications).

## License

MIT
