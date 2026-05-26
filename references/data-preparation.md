# Data Preparation Reference

This file documents how to merge separate major and trace element Excel files into the standardized format required by `igneous-geochemistry`. The merge logic is implemented as a standalone Python script in `scripts/merge_excel.py`.

## When to Use

- You have separate Excel files for major elements and trace elements
- You need to merge them into the standardized format

## Quick Start

```bash
python /home/twoper/.hermes/skills/data-science/igneous-geochemistry/scripts/merge_excel.py \
    /mnt/c/Users/opcry/Desktop/主量元素.xlsx \
    /mnt/c/Users/opcry/Desktop/微量元素.xlsx \
    -o /mnt/c/Users/opcry/Desktop/Hermes\ output/merged_geochemistry.xlsx
```

### 如果工作表名不是默认的

```bash
python merge_excel.py 主量文件.xlsx 微量文件.xlsx \
    --sheet-major "Sheet1" --sheet-trace "数据页"
```

### 在 Python 中调用

```python
from merge_excel import read_element_data, merge_major_trace, write_merged_excel

# 然后按 data-preparation.md（旧版存档）/ SKILL.md（I 部分）的流程调用：
#   wb -> ws -> find_data_region -> read_element_data -> merge_major_trace -> write_merged_excel
```

## 完整工作流

```python
import openpyxl
from merge_excel import find_data_region, read_element_data, merge_major_trace, write_merged_excel

MAJOR_PATH = '/mnt/c/Users/opcry/Desktop/主量元素.xlsx'
TRACE_PATH = '/mnt/c/Users/opcry/Desktop/微量元素.xlsx'
OUTPUT_PATH = '/mnt/c/Users/opcry/Desktop/Hermes output/merged_geochemistry.xlsx'

import os; os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# 主量
wb_maj = openpyxl.load_workbook(MAJOR_PATH, data_only=True)
sn_maj = wb_maj.sheetnames[2] if len(wb_maj.sheetnames) > 2 else wb_maj.sheetnames[0]
ws_maj = wb_maj[sn_maj]
elem_row_maj, col_start_maj, _ = find_data_region(ws_maj)
maj_ids, maj_data = read_element_data(ws_maj, elem_row_maj, col_start_maj)
print(f"主量样品: {maj_ids}")
print(f"主量元素: {list(maj_data.keys())}")

# 微量
wb_trace = openpyxl.load_workbook(TRACE_PATH, data_only=True)
sn_trace = wb_trace.sheetnames[2] if len(wb_trace.sheetnames) > 2 else wb_trace.sheetnames[0]
ws_trace = wb_trace[sn_trace]
elem_row_trace, col_start_trace, _ = find_data_region(ws_trace)
trace_ids, trace_data = read_element_data(ws_trace, elem_row_trace, col_start_trace)
print(f"微量样品: {trace_ids}")
print(f"微量元素: {list(trace_data.keys())}")

# 合并 + 输出
all_samples, merged = merge_major_trace(maj_data, trace_data, maj_ids, trace_ids)
write_merged_excel(all_samples, merged, OUTPUT_PATH)
```

## 工作原理

| 步骤 | 函数 | 做什么 |
|------|------|--------|
| 1 | `find_data_region(ws)` | 扫描前20行，通过元素关键字（SiO2/TiO2等）自动定位元素名行 |
| 2 | `read_element_data(ws, ...)` | 读取所有样品编号 + 元素名 + 数据（保留检测限字符串如 `<0.50`） |
| 3 | `merge_major_trace(...)` | 以主量样品顺序为准，按样品编号对齐微量数据 |
| 4 | `sort_elements(merged_data)` | 预定义顺序优先排序，未匹配元素自动追加末尾 |
| 5 | `write_merged_excel(...)` | 输出论文附件格式的 Excel |

## 标准化输出格式

合并脚本输出的格式与期刊论文附表一致——**element × sample 矩阵，无类别/单位行**：

| Excel Row | Col A    | Col B~N          |
|-----------|----------|------------------|
| 1         | 'Sample' | 样品编号         |
| 2+        | 元素符号  | 数值数据          |

> 注：ΣREE、Eu/Eu*、(La/Yb)N 等计算比值自动过滤，不输出到合并文件。

## 格式变更记录

- **2026-05-09**: 从 4 行表头改为论文附件格式（Sample + 元素数据行，无类别/单位行）。同一天加入 Fe2O3T → TFe2O3 别名映射。
- **2026-05-07**: 加入 Ti 到 TRACE_ORDER
- 旧格式: 4 行表头（Sample ID / 类别合并单元格 / Element / Unit），数据从 Row 5 开始

## 已知问题

| 问题 | 解决方法 |
|------|----------|
| 找不到数据页 | 用 `--sheet-major` / `--sheet-trace` 手动指定 |
| 微量元素漏读 | 检查文件中的元素名，确认不是特殊缩写 |
| 样品顺序不一致 | `merge_major_trace` 按样品编号自动对齐 |
| Ti (ppm) 被漏掉 | 2026-05-07 已修复：`TRACE_ORDER` 列表中加入了 `'Ti'` |
| 元素名带 Unicode 下标（TiO₂） | `_normalize()` 自动转换 `₂₃₁₄₅₆` → `23456`，不影响匹配 |
| Fe2O3T 不识别为 TFe2O3 | 2026-05-09 已修复：`ELEM_ALIAS` 中加入 `'Fe2O3T': 'TFe2O3'` |
