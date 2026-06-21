---
name: IgneousWR
description: >
  Igneous Whole-Rock geochemical plotting engine. Reads Excel data →
  19 geochemical diagrams (content only, styling downstream)
  + HTML report. Cross-agent compatible.
license: MIT
compatibility: Requires Python 3.10+, matplotlib, numpy, openpyxl
metadata:
  version: "2.0.0"
  author: Chen Yuyang
  email: asukswpu@163.com
  repository: https://github.com/Cai-Wang/igneouswr
  hermes:
    tags: [geochemistry, petrology, plotting, data-science, research]
    related_skills: [isoplotr]
---

# IgneousWR — Agent Usage Manual

## 设计哲学（v2.0）

**IgneousWR 是地化内容引擎，不是设计工具。** 它保证：
- 数据标准化正确（Sun & McDonough 1989 CI Chondrite / Primitive Mantle）
- 边界线和多边形与参考文献一致（TAS 源自 GCDkit，Pearce 2008 经用户校准）
- 轴标签和范围符合各图型惯例
- 引用和来源自动标注

**IgneousWR 不负责：**
- 字体、颜色、线粗（这些是 LLM 的工作）
- 排版布局、A4 拼版（由下游处理）
- 风格预设、SciencePlots 集成（v2.0 已全部移除）

**统一模式（v2.1）：调用方建画布传 ax，IgneousWR 只画内容。** 不再有独立/拼版之分。

| 用法 | 适用场景 |
|------|---------|
| `ax = layout.add_subplot(...) 或 plt.subplots(); plot_ree(gd, ax=ax)` | A4 拼版 / 裸图预览——调用方建好 ax 传进来 |

IgneousWR 只提供内容，所有视觉参数（线粗、点大小、边缘）通过参数传入，字号/字体通过 plt.rcParams 设。

---

## Core API Reference

### Import

```python
from igneous_wr_core import (
    GeochemData,          # data container (main entry)
    plot_recommended,     # batch plot: auto-selects diagrams based on data
    set_out_dir,          # override output directory
    DIAGRAM_REGISTRY,     # dict of all diagram specs
    recommended_diagrams, # returns list of diagram IDs for a GeochemData
)

# 单图函数（全部需要 ax 参数——v2.1 不再自动建画布）
from igneous_wr_core import (
    plot_tas, plot_ree, plot_spider, plot_k2o_sio2,
    plot_afm, plot_winchester_floyd, plot_co_th,
    plot_pearce_2008, plot_miyashiro, plot_shervais,
    # ... 全部 19 个图函数
)

# 后置轴样式函数（时序敏感：finalize + apply_format 之后调用）
from igneous_wr_core import (
    apply_spider_axis_style,   # Spider X 轴刻度交替 + 标签偏移 + Y 竖排 + Y 网格
    apply_ree_axis_style,      # REE Y 竖排 + Y 网格
)

# 拼版模式需要 figkit
from figkit.layout import A4Grid
```

### 数据加载 — `GeochemData(path, **kwargs)`

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

### 单图模式 — `plot_*(gd, ax=None, *, linewidth=1.2, markersize=8, marker_edge_color=None, marker_edge_width=0)`

**必须传 ax。** v2.1 不再自动建画布。调用方负责建好 ax 传入。

```python
# 裸图预览：调用方建画布
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(77.5/25.4, 257/25.4))
plot_ree(gd, ax=ax, linewidth=1.0, markersize=8)
fig.savefig('ree_bare.png')
```

**视觉参数：** 线粗 `linewidth`（默认 1.2）、点大小 `markersize`（默认 8）、点边缘色 `marker_edge_color`、边缘宽 `marker_edge_width`。不传则用默认值。

所有 19 个图函数从此统一：
```python
def plot_*(gd, ax=None, *, **visual_kwargs):
    # ax 为必填——不传则出错
```

### 批量出图 — `plot_recommended(gd, out_dir=None, rock_type='auto')`

```python
set_out_dir("/path/to/output")
result = plot_recommended(gd)
```

Returns:
```python
{
    "success": [("plot_tas", "CLS-01_TAS.png"), ...],   # (function_name, filename) tuples
    "skipped": [("AFM (Irvine & Baragar 1971)", ["FeOt"]), ...],  # (description, reason) tuples
}
```

The HTML report is also auto-generated as a side effect when `generate_report_html` is available.

### 推荐列表 — `recommended_diagrams(gd)` → list of diagram IDs

### A4 拼版示例（新流程 v2.1）

**正确的调用顺序（时序敏感）：**

```python
from igneous_wr_core import GeochemData, plot_ree, plot_spider, apply_spider_axis_style, apply_ree_axis_style
from figkit.layout import A4Grid

gd = GeochemData("data.xlsx")

# ── 步骤1：定风格 ──
style = {
    'linewidth': 1.0,
    'markersize': 8,
}
plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'axes.linewidth': 0.6,
})

# ── 步骤2：建画布 + cell ──
layout = A4Grid(1, 2, paper='A4',
                left=25, right=25, top=25, bottom=25,
                hspace=0, wspace=12)
ax_ree = layout.add_subplot(0, 0, label='ree')
ax_sp  = layout.add_subplot(0, 1, label='sp')

# ── 步骤3：绘图（一次画到位） ──
plot_ree(gd, ax=ax_ree, **style)
plot_spider(gd, ax=ax_sp, **style)

# ── 步骤4：排版 + 后置轴样式 ──
layout.finalize(pairs=('ree', 'sp'))
apply_ree_axis_style(ax_ree)       # 必须在 finalize 之后
apply_spider_axis_style(ax_sp)     # 必须在 finalize 之后

# ── 步骤5：保存 ──
layout.save('ree_spider.png')
```

**3×2 多对版：**

```python
layout = A4Grid(3, 2, paper='A4',
                left=25, right=25, top=25, bottom=25,
                hspace=12, wspace=12)
pairs = []
for r in range(3):
    ax_ree = layout.add_subplot(r, 0, label=f'ree{r}')
    ax_sp  = layout.add_subplot(r, 1, label=f'sp{r}')
    plot_ree(gd_list[r], ax=ax_ree, **style)
    plot_spider(gd_list[r], ax=ax_sp, **style)
    pairs.append((f'ree{r}', f'sp{r}'))

layout.finalize(pairs=pairs)
for r in range(3):
    apply_ree_axis_style(layout.get_ax(f'ree{r}'))
    apply_spider_axis_style(layout.get_ax(f'sp{r}'))
layout.save('ree_spider_3pairs.png')
```

## 图件内容说明（IgneousWR 负责的部分）

### 分类图（CLS-xx）

IgneousWR 负责：
- 边界多边形绘制（TAS 16 区、AFM Irvine-Baragar 线、Winchester-Floyd 分区……）
- 数据散点按分组着色（颜色从 `_style` 取，可被 LLM 覆盖）
- 轴标签（化学式：`SiO$_2$`、`Na$_2$O`）
- 轴范围（各图型有固定的 xlim/ylim）
- 图例

### 源区图（SRC-xx）

IgneousWR 负责：
- REE/蛛网图标准化计算（CI Chondrite / Primitive Mantle）
- 按元素顺序绘制
- Pearce 2008 判别区填充

### 演化 / 构造图（EVO/TEC-xx）

IgneousWR 负责：
- 边界曲线 / 射线绘制
- 三角图框架、网格、刻度
- 判别区域标注

## 被移除的功能（v2.0）

v2.0 移除了所有"越界做设计"的功能：

| 移除项 | 原因 | 替代 |
|--------|------|------|
| `set_style_preset()` | 风格预设不属于内容引擎 | LLM 直接配置 matplotlib rcParams |
| SciencePlots 集成 | 样式选择是 LLM 的工作 | LLM 自行选择是否安装 SciencePlots |
| `style_ax()` 的 tick/spine 设置 | tick 方向、边框属于排版 | 下游 LLM 用 rcParams 或 tick_params 设置 |
| `plt.tight_layout()` | 排版是下游的责任 | 下游 LLM 用 `plt.tight_layout()` 或手动布局 |
| `figsize=(8,5)` 硬编码（plot_ree/plot_spider） | 尺寸应随排版确定 | 调用方建画布，IgneousWR 不设 figsize |
| `lw=1.2` / `s=None` 硬编码 | 视觉参数应可覆盖 | 改为 `linewidth=` / `markersize=` 参数，默认值保留 |
| `out_dir` / `save` 参数 | 保存是下游的职责 | 调用方建画布后自行 `fig.savefig()` |
| `add_legend()` 自动调用 | 图例创建已移交给 figkit | figkit `apply_style()` 统一创建，裸图需手动 `ax.legend()` |
| `fontproperties=times_prop` | 字体选择是设计决策 | LLM 通过 rcParams 设置 |

## GeochemData 属性参考

```python
gd.labels         # List of sample IDs
gd.idxs           # List of sample indices
gd.all_labels     # Full sample list before filtering
gd._elem_data     # Dict {element_name: [values]}
gd._detected_mode # 'standard', 'transposed', or 'wide'
gd.get("SiO2")    # Access element values by name
gd.groups         # Group labels (auto-detected from sample prefix)
```

## Excel Data Workflow

### Common scenario: separate 主量 (major) and 微量 (trace) files

Use merge_excel.py first:
```bash
python3 merge_excel.py 主量.xlsx 微量.xlsx -o /output/path/merged.xlsx
```

### Known format pitfall

When an Excel file has Row 1 = element names in columns and Row 2+ = sample data (standard layout), GeochemData's `_detect_layout()` handles it. But if the file has a unit row (Row 2 = "%" etc.), it may misdetect. The merge_excel.py tool strips unit rows cleanly.

## LA-ICP-MS Spot Data

For **LA-ICP-MS spot data** from GLITTER or ICPMSDataCal, use the standalone script:

```bash
python3 scripts/glitter_zircon_ree.py /path/to/data/dir /path/to/output/dir
```

See the skill `zircon-trace-element` for detailed workflow.

---

## Diagram Catalog (19 total)

### Classification / Rock Series (12)

| ID | Diagram | Requires |
|----|---------|----------|
| CLS-01 | TAS volcanic (Middlemost 1994) | SiO₂, Na₂O, K₂O |
| CLS-02 | K₂O–SiO₂ (Middlemost 1985) | SiO₂, K₂O |
| CLS-03 | AFM (Irvine & Baragar 1971) | SiO₂, Na₂O, K₂O, FeOt, MgO |
| CLS-04 | K₂O–SiO₂ (Peccerillo & Taylor 1976) | SiO₂, K₂O |
| CLS-05 | Zr/TiO₂–Nb/Y (Winchester & Floyd 1977) | Zr, TiO₂, Nb, Y |
| CLS-06 | Co–Th (Hastie 2007) | Co, Th |
| CLS-10 | TiO₂–MnO–P₂O₅ ternary (Mullen 1983) | TiO₂, MnO, P₂O₅ |
| CLS-13 | TAS plutonic (Middlemost 1994) | SiO₂, Na₂O, K₂O |
| CLS-17 | Fe# vs SiO₂ (Frost 2001) | SiO₂, FeOt, MgO |
| CLS-29 | Zr/Ti–Nb/Y (Pearce 1996) | Zr, Ti, Nb, Y |
| CLS-30 | MALI vs SiO₂ (Frost 2001) | SiO₂, Na₂O, K₂O, CaO |
| CLS-31 | ASI vs A/NK (Frost 2001) | SiO₂, Al₂O₃, CaO, Na₂O, K₂O |

### Source Characteristics (3)

| ID | Diagram | Requires |
|----|---------|----------|
| SRC-01 | REE chondrite-normalised | ≥1 REE |
| SRC-02 | Primitive-mantle spider | trace elements |
| SRC-03 | Th/Yb–Nb/Yb (Pearce 2008) | Th, Yb, Nb |

### Magmatic Evolution (1)

| ID | Diagram | Requires |
|----|---------|----------|
| EVO-02 | FeOt/MgO–SiO₂ (Miyashiro 1974) | SiO₂, FeOt, MgO |

### Tectonic Discrimination (3)

| ID | Diagram | Requires |
|----|---------|----------|
| TEC-01 | Nb–Zr–Y ternary (Meschede 1986) | Nb, Zr, Y |
| TEC-02 | Hf/3–Th–Ta ternary (Wood 1980) | Hf, Th, Ta |
| TEC-05 | Ti–V (Shervais 1982) | Ti, V |

---

## Styling Conventions (v2.1)

**IgneousWR 不再有任何视觉默认值。** 所有视觉参数通过函数参数和 plt.rcParams 传入：

- **边界线**：IgneousWR 用 `_style.LINE_COLOR_MAIN='#333333'` 和 `_style.LINE_COLOR_SECONDARY='#666666'`
- **数据点**：`plot_ree(gd, ax=ax, linewidth=1.0, markersize=8, marker_edge_color=None, marker_edge_width=0)`
- **字号/字体**：调用方通过 `plt.rcParams` 设置（`font.size`, `font.family`, `axes.linewidth`）
- **图例**：IgneousWR 不画图例，只设 `label=`。figkit `apply_style()` 或手动 `ax.legend()`
- **后置轴样式**：`apply_spider_axis_style(ax)` 和 `apply_ree_axis_style(ax)` 在 `finalize()` 之后调用

**不再使用 `_style` 模块常量：**
```python
# ❌ v2.0 旧用法
_style.MK_SIZE_SINGLE = 40

# ✅ v2.1 新用法
plot_ree(gd, ax=ax, markersize=8)
```

---

## Verification

```bash
python3 quick_validate.py            # import + instantiation test
python3 generate_test_data.py /tmp/t # create synthetic data
python3 run_test.py                  # end-to-end pipeline
```
