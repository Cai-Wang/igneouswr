# GLITTER 4.0 / ICPMSDataCal — LA-ICP-MS Trace Element Format Quirks

## GLITTER 4.0 CSV (`.csv`)

### Structure

```
GLITTER4.0: Laser Ablation Analysis Results

<path/to/file>
<timestamp>

All values are reported in ppm

GLITTER!: Trace Element Concentrations MDL filtered.
Element,
spot001,spot002,spot003,...
Si29,
327104.38,153225.19,...
Ti49,442.51,5.11,...
Y89,455.17,117.36,...
La139,
459.01,<0.0126,0.222,...
Ce140,
452.60,2.348,...
```

### Key quirks

1. **⚠️ 行格式不一致** — 同一文件内有些元素数据在 **下一行**（Si29、Zr91），有些数据在 **同一行**（Ti49、Y89、La139~Lu175）。解析时必须先检查当前行的 parts[1:] 是否有数值/`<MDL`，没有再读下一行。

   旧版脚本的 BUG：总是读下一行，导致 La 取了 Ce 的数据、Ce 取了 Pr 的数据……每个 REE 元素错位一格。修正后要每个元素行先检查 `has_numbers = any(re.match(r'^[\\d.<]', v) for v in vals_raw[:5] if v)`。

2. **Spot header row**: The line `Element,\nspot001,spot002,...` is the column header. However, the parser skips it because it begins with `Element` or `Element,`. Spot IDs are unused — the script auto-generates `_spot001` IDs.

3. **Element name format**: `Si29`, `Ti49`, `Y89`, `Zr91`, `Nb93`, `La139`, `Ce140`, `Pr141`, `Nd146`, `Sm147`, `Eu153`, `Gd157`, `Tb159`, `Dy163`, `Ho165`, `Er166`, `Tm169`, `Yb172`, `Lu175`. The script strips the isotope number and uses the capitalised element symbol.

4. **Non-REE elements** (Si, Ti, Zr, Y, Nb, Hf, Ta, Pb, Th, U) are present. Zr and Si MUST be collected for standard filtering.

### ⚠️ 标准过滤（CSV 最重要的问题）

**旧的 CSV 解析器完全不过滤 NIST 610 标样点！** GLITTER 导出的 CSV 里混入的 NIST610（标准玻璃）测点必须去掉：

- **NIST 610 玻璃**：Zr ≈ 440 ppm, Si ≈ 327104 ppm
- **锆石**：Zr ≈ 450000 ppm, Si ≈ 153225 ppm

过滤策略：
```
优先用 Zr > 10000 ppm 判断（锆石=真，标样=假）
如果 CSV 没有 Zr 列（如 SA11AEL.csv），回退用 Si < 200000 ppm 判断
如果两者都没有，跳过该点
```

**这要求解析器必须收集 Si 和 Zr 元素！** 所以元素过滤器不能只收 REE：
```python
if elem not in CHONDRITE and elem not in ('Zr', 'Si'):
    continue
```

### Detection limit syntax

- `<0.0126` (the number after `<` is the MDL value)
- `<0.00` (truncated value, parser may return NaN or 0.0 depending on strategy)
- The `half` strategy replaces `<X` with `X/2`

### Known pitfalls

- **GLITTER 4.0 CSV encoding**: May include Chinese characters in the metadata lines. The parser uses `errors='replace'`.
- **Line endings**: `\r\n` (Windows CRLF) — handled by Python's universal newline.
- **Trailing commas**: Some spot columns have trailing empty columns from the export. Parser handles this by checking `re.match(r'^[\d.<]', v)` to distinguish real values from empties.
- **No standard labels**: Unlike ICPMSDataCal XLS, there is no separate "std" column. Standards MUST be identified by Zr/Si composition.

- **⚠️ 多个数据块（CSV 最隐蔽的坑）**：有些 CSV 文件（如 SA11AEL）的元素行在同一文件内出现多次（Si29 出现在 line 6, 36, 66, 96），分别是不同的测量块。解析器逐行遍历时会**覆盖** `elem_lines['Si']`，最终只保留最后一块的数据。如果最后一块 Si≈2（而非正常的 327104/153225），所有标样都会通过过滤。**修复：只取第一次出现的元素行**：`if e in seen_elements: continue`，并在存储后 `seen_elements.add(e)`。

- **⚠️ `if ... continue; seen.add(e)` 语法 BUG** — Python 中 `if e in seen: continue; seen.add(e)` 的 `seen.add(e)` **永远不执行**：当 `e in seen` 为真时 `continue` 跳过后续；为假时整个 if 块被跳过，`seen.add(e)` 也不执行。正确的写法是两行：
  ```python
  if e in seen: continue
  seen.add(e)
  ```
  这个 BUG 导致所有 CSV 的 Th/U 数据来自最后一块（Si≈2），所有 NIST610 标样通过过滤混入图中。

- **Th232 和 U238 在 CSV 中必须明确收集** — 元素名 `Th232` 和 `U238` 会被正则 `^([A-Z][a-z]?)\d*` 正确解析为 `Th` 和 `U`。但解析器的白名单必须包含它们：`if e not in CHONDRITE and e not in ('Zr','Si','Y','Th','U'): continue`。旧版没有加 `Th` 和 `U`，导致所有 CSV 缺少 Th/U 数据。

---

## ICPMSDataCal XLS (`.xls`)

### Structure

Multi-sheet binary Excel with the following key sheets:

| Sheet | Content |
|-------|---------|
| `TraceEle` | Trace element concentrations |
| `Age` | U-Pb age data (isotope ratios, ages) |
| `CoverInformation` | Laboratory metadata |
| `PlotDat1..N` | Concordia / weighted average plot data |
| `<SampleName>` | Same structure as Age sheet |

### TraceEle sheet layout

```
       col0    col1         col2      col3  col4    col5  col6  col7   col8  col9   col10 ...
Row 0: <header>
Row 1: <blank>|Contents...| <blank> |blank| SiO2  | Ti   | Y   | ZrO2 | Nb   | La   | Ce   | Pr   | Nd   | Sm   | Eu   | Gd   | Tb   | Dy   | Ho   | Er   | Tm   | Yb   | Lu   | Hf  | Ta   | Hg  | Pb  | Pb  | Th   | U
Row 2: <blank>|<blank>    | <blank> |blank|  29   |  49  | 89  |  91  |  93  | 139  | 140  | 141  | 146  | 147  | 153  | 157  | 159  | 163  | 165  | 166  | 169  | 172  | 175  | 178 | 181  | 202 | Pb  | Tot | 232  | 238
Row 3: <blank>|<blank>    | <blank> |blank|  wt%  | ppm  | ppm | wt%  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm  | ppm | ppm  | ppm | ppm | ppm | ppm  | ppm
Row 4+: type  | timestamp | stdName |blank| data  | data  | ... (one row per spot)
```

Row 0-3 are headers. Data starts at row 4 (0-indexed).

### ⚠️ 标准过滤（XLS 的关键）

**三重过滤，缺一不可：**

1. **col0 = 'std' | 'ref.' | 'standard'** — 跳过主标样行
2. **col2 含已知标准名** — 必须检查 col2，**不是 col1**！
   - 旧版 BUG：检查的是 `spot_name.lower()`（col1，测点编号如 'Sep10T08'），根本不会匹配任何标准名
   - 正确的做法：`col2 = str(row.iloc[2]).strip().lower()`
   - 已知标准名：`srm`, `gj-1`, `nist`, `ple`, `91500`, `qh`（青湖）, `qdh`
3. **ZrO2 < 10 wt%** — 锆石 ZrO2 ≈ 60–68 wt%，标样 < 1 wt%

### Other quirks

1. **Row 1 = element names**, Row 2 = atomic masses, Row 3 = units (the script reads from Row 1, 0-indexed).

2. **Column B (index 1)** = spot/Rep names. Used for labeling, **NOT for standard filtering**.

3. **Old binary XLS format**: Requires `xlrd >= 2.0`. If you get "xlrd.biffh.XLRDError: Excel xlsx file; not supported", the file is actually XLSX — rename to `.xlsx` or open in a real copy. The script uses `pd.read_excel(path, sheet_name='TraceEle', header=None)` which routes through `xlrd` for `.xls` and `openpyxl` for `.xlsx`.

4. **Atomic mass row**: Row 2 has the isotope mass numbers — these are occasionally read as floats (29.0, 49.0). Skip by checking col1 (spot name) is non-empty.

5. **Data starts at row 4** (0-indexed): After the 3 header rows + row 3 (units) + row 4 (first spot).

### Spurious spot IDs

Some spots have IDs like `SA01A-01\b` or `std-01` — the `\b` is a backspace character from the original ICPMSDataCal export. The parser's `str(v).strip()` removes trailing whitespace but not `\b`. Not harmful for plotting.

---

## Age sheet (ICPMSDataCal XLS)

Used for Th/U vs Age plots.

### Structure

Same header pattern as TraceEle:
- Row 0-3: headers
- Row 4+: data (same spots as TraceEle)
- col2: spot name (matches TraceEle's col2 — use for cross-referencing)
- col5: Th (ppm)
- col6: U (ppm)

### ⚠️ Age column position varies between files

`206Pb/238U` Age and its 1sigma are NOT at fixed column positions. Some files have extra columns (e.g., a common-Pb ratio at col18). **必须动态查找列位置：**

```python
age_col = None
for j in range(df.shape[1]):
    h1 = str(df.iloc[1, j]).strip() if pd.notna(df.iloc[1, j]) else ''
    h2 = str(df.iloc[2, j]).strip() if pd.notna(df.iloc[2, j]) else ''
    if '206Pb/238U' in h1 and 'Age' in h2:
        age_col = j
        break
```

Then age = `row[age_col]`, 1sigma = `row[age_col+1]`.

### Data validation

Th/U from Age sheet should match Th/U from TraceEle sheet for the same spot. Cross-check by matching col2 spot names. If they differ >0.001, flag the mismatch.

---

## OCR/Document Parsing Warning

**MinerU PDF-to-markdown extraction can garble text badly.** In one session, the OCR extracted "Yb/Sm-Th/U图解,轮廓系数为0.13835" when the actual text was "Lu-Sm/Gd图解,轮廓系数为0.13839". Always cross-check:
1. Does the OCR text make geochemical sense? (Yb/Sm is a common ratio, but when ALL diagrams in a ranking show different element combinations, verify against the original figure)
2. If user provides a corrected excerpt, the OCR was almost certainly wrong.
3. Never trust OCR-rotated element symbols: Th≠Tm, Lu≠Yb, etc.

---

## Output

The REE plot script produces:
- `REE_AllSamples_<chondrite>.png` — combined plot, one colour per file
- `REE_<sample_name>.png` — per-file individual plots
- Default 300 dpi PNG output
- Y-axis: auto-adjusted from actual data range, not hardcoded
- Ticks: inward (`ax.tick_params(direction='in')`)
- Style: IgneousWR-style log REE diagram
