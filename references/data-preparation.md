# Data Preparation Reference

This file documents how to merge separate major and trace element Excel files into the standardized format required by IgneousWR. The merge logic is implemented as a standalone Python script in `scripts/merge_excel.py`.

## When to Use

- You have separate Excel files for major elements and trace elements
- You need to merge them into the standardized format

## Quick Start

```bash
python scripts/merge_excel.py \
    ./data/major_elements.xlsx \
    ./data/trace_elements.xlsx \
    -o ./data/merged_geochemistry.xlsx
```

### If sheet names are not default

```bash
python scripts/merge_excel.py major.xlsx trace.xlsx \
    --sheet-major "Sheet1" --sheet-trace "Data"
```

### From Python

```python
from merge_excel import read_element_data, merge_major_trace, write_merged_excel
```

## Full Workflow

```python
import openpyxl
from merge_excel import find_data_region, read_element_data, merge_major_trace, write_merged_excel

MAJOR_PATH = './data/major_elements.xlsx'
TRACE_PATH = './data/trace_elements.xlsx'
OUTPUT_PATH = './data/merged_geochemistry.xlsx'

import os; os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# Major
wb_maj = openpyxl.load_workbook(MAJOR_PATH, data_only=True)
sn_maj = wb_maj.sheetnames[2] if len(wb_maj.sheetnames) > 2 else wb_maj.sheetnames[0]
ws_maj = wb_maj[sn_maj]
elem_row_maj, col_start_maj, _ = find_data_region(ws_maj)
maj_ids, maj_data = read_element_data(ws_maj, elem_row_maj, col_start_maj)
print(f"Major samples: {maj_ids}")
print(f"Major elements: {list(maj_data.keys())}")

# Trace
wb_trace = openpyxl.load_workbook(TRACE_PATH, data_only=True)
sn_trace = wb_trace.sheetnames[2] if len(wb_trace.sheetnames) > 2 else wb_trace.sheetnames[0]
ws_trace = wb_trace[sn_trace]
elem_row_trace, col_start_trace, _ = find_data_region(ws_trace)
trace_ids, trace_data = read_element_data(ws_trace, elem_row_trace, col_start_trace)
print(f"Trace samples: {trace_ids}")
print(f"Trace elements: {list(trace_data.keys())}")

# Merge + output
all_samples, merged = merge_major_trace(maj_data, trace_data, maj_ids, trace_ids)
write_merged_excel(all_samples, merged, OUTPUT_PATH)
```

## How It Works

| Step | Function | Description |
|------|----------|-------------|
| 1 | `find_data_region(ws)` | Scans first 20 rows, auto-locates element name row via keywords (SiO2, TiO2, etc.) |
| 2 | `read_element_data(ws, ...)` | Reads sample IDs, element names, and data (preserves detection-limit strings like `<0.50`) |
| 3 | `merge_major_trace(...)` | Aligns trace data by sample ID, preserving major-element sample order |
| 4 | `sort_elements(merged_data)` | Predefined element order prioritised; unmatched elements appended |
| 5 | `write_merged_excel(...)` | Outputs to journal-article supplementary-table format |

## Output Format

The merged script outputs an **element × sample matrix** (journal-article style):

| Excel Row | Col A    | Col B~N          |
|-----------|----------|------------------|
| 1         | 'Sample' | Sample IDs       |
| 2+        | Element  | Numeric data     |

> Note: computed ratios (ΣREE, Eu/Eu*, (La/Yb)N, etc.) are automatically filtered out.

## Changelog

- **2026-05-09**: Changed from 4-row header to article-format (Sample + element row, no category/unit rows).
- **2026-05-07**: Added Ti to TRACE_ORDER.

## Known Issues

| Issue | Resolution |
|-------|-----------|
| Data sheet not found | Use `--sheet-major` / `--sheet-trace` to specify manually |
| Trace elements missing | Check element names in your file |
| Sample order mismatch | `merge_major_trace` auto-aligns by sample ID |
| Ti (ppm) dropped | Fixed 2026-05-07 |
| Unicode subscripts (TiO₂) | `_normalize()` auto-converts ₂₃₁₄₅₆ → 23456 |
| Fe2O3T not recognised as TFe2O3 | Fixed 2026-05-09: `ELEM_ALIAS` |
