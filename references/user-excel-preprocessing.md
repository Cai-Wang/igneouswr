# User Excel Preprocessing (Common Layouts)

## Scenario: Transposed Layout (Elements in Rows, Samples in Columns)

User Excel files often have a **transposed layout** where:

- Row 1: `Sample` header then sample names in columns (MT01A1, MT01A2, …)
- Rows 2–3: Non-data headers (Lithology, Major element (wt.%))
- Rows 4+: Element names in column A, data in columns 2+
- Row N+: Computed/meta rows interleaved (LOI, Total, Mg#, Eu/Eu*, ΣREE, (La/Yb)N, (Dy/Yb)N, notes)

### Preprocessing Steps

1. Identify skip rows: Lithology header, section header rows (e.g. "Major element (wt.%)", "Trace element (ppm)"), computed rows (Total, Mg#, Eu/Eu*, ΣREE, (La/Yb)N, (Dy/Yb)N), and any row where the first data cell is None (string-only row).

   **典型 skip rows 示例（MT01-04 主微量文件）：**
   ```python
   skip_rows = {2, 3,       # Lithology, "Major element (wt.%)"
                14,         # LOI (空行)
                15, 16,     # Total, Mg#（计算行）
                50, 51,     # Eu/Eu*, ΣREE
                52, 53, 54} # (La/Yb)N, (Dy/Yb)N, Note
   ```

2. Transpose: create a standard-format Excel where:
   - Row 1 = header (`Sample` then element names)
   - Rows 2+ = one row per sample, columns = elements

3. Use Python + openpyxl (not IgneousWR's `GeochemData` directly — load from the cleaned file).

### Python Snippet

```python
import openpyxl

src = '/mnt/c/Users/opcry/Desktop/文件.xlsx'
wb = openpyxl.load_workbook(src, data_only=True)
ws = wb.active

skip_rows = {2, 3, ...}  # non-data rows
samples = [ws.cell(1, c).value for c in range(2, ws.max_column + 1)]

rows_data = []
for r in range(1, ws.max_row + 1):
    if r in skip_rows: continue
    if ws.cell(r, 1).value is None: continue
    if ws.cell(r, 2).value is None: continue  # string-only rows
    vals = [ws.cell(r, c).value for c in range(2, ws.max_column + 1)]
    rows_data.append((ws.cell(r, 1).value, vals))

wb_out = openpyxl.Workbook()
ws_out = wb_out.active
ws_out.cell(1, 1).value = 'Sample'
for j, (elem, _) in enumerate(rows_data):
    ws_out.cell(1, j + 2).value = elem
for i, sample in enumerate(samples):
    ws_out.cell(i + 2, 1).value = sample
    for j, (_, vals) in enumerate(rows_data):
        ws_out.cell(i + 2, j + 2).value = vals[i]
wb_out.save('/tmp/cleaned.xlsx')
```

Then load with `gd = GeochemData('/tmp/cleaned.xlsx')`.

## Known Element Name Issues

- User Excel may use `TFe2O3` (total iron) — IgneousWR should handle this alias
- Spider plot requires `K` and `P` (not `K2O`/`P2O5`). If data only has `K2O`/`P2O5`, spider will warn missing `K`/`P`
