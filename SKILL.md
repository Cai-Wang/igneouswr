---
name: IgneousWR
description: >
  Igneous Whole-Rock geochemical plotting engine. Reads Excel data →
  19 publication-ready diagrams (TAS, REE, spider, tectonic discrimination, etc.)
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
- **底图信息正确**（边界线、多边形判别区、轴标签/范围、标准化参考线）——这些是 IgneousWR 该管的
- **数据标准化正确**（Sun & McDonough 1989 CI Chondrite / Primitive Mantle）
- **边界线与参考文献一致**（TAS 源自 GCDkit，Pearce 2008 经用户校准）
- **引用和来源自动标注**

**IgneousWR 不负责（这些是 LLM 的工作）：**
- **数据点样式**（散点颜色、大小、边缘、线型、标记符号）
- 字体选择、排版布局、A4 拼版
- 风格预设、SciencePlots 集成（v2.0 已全部移除）

### 与 figkit 的分工合约（2026-06-21 确立）

**核心原则：图型特有的视觉 → IgneousWR，全局统一的格式 → figkit。**

| 谁 | 管什么 | 禁止做什么 |
|----|--------|----------|
| **IgneousWR** | 轴标签文本/元素名、边界线/多边形、标准化数据、轴范围/尺度、参考线(y=1虚线)、数据分组逻辑、刻度位置/值、**图型特有的刻度格式**（如蛛网图 X 轴刻度交替内外+标签偏移）、画线时设 `label=` 供 figkit 创建图例 | 禁止设 `fontsize=`；禁止调 `tick_params`（方向/大小）；禁止画图例（`add_legend()` 已全部移除）；禁止设轴框线粗 |
| **figkit apply_format** | 字体族、字号（轴标签/刻度/底图文本/图例统一）、刻度方向/大小、轴框线粗、图例边框、Y轴刻标竖排、X轴多标签自动缩小 | — |
| **figkit apply_style** | 读取 IgneousWR 画线时设的 `label=` 创建**共享图例**（仅色点不显示线，放第一个子图）；覆盖数据线粗/点大小/颜色（全局默认值，各图相同） | 不能给不同子图不同风格；不能动刻度或标签排列 |

**图例移交说明（2026-06-21）：** IgneousWR 中 15 处 `_style.add_legend(ax)` 已全部移除。IgneousWR 只画线设 `label=` 分组名，图例创建和样式由 figkit `apply_style()` 统一处理。独立模式（`plot_*(gd)` 不接 figkit）时图例不再自动生成——需手动调用 `ax.legend()`。

**`style_ax()` 变更（2026-06-21）：** `top=True, right=True` → `top=False, right=False`。所有二元图的刻度仅出现在左/下两边，上/右保留框线但无刻度。标准科学出版格式。

**Spider X 轴刻度交替内外（2026-06-21 修复）：**
**Spider X 轴刻度交替内外（2026-06-21 修复，第三次才正确）：**

`plot_spider()` 内 `if _standalone:` 块中放 `tight_layout + fig.canvas.draw()` 之后：

- `ax.xaxis.set_minor_locator(ticker.NullLocator())` — 关闭 X 副刻度
- `t.tick1line.set_marker(3 if i % 2 else 2)` — 刻度标记内外交替。marker=2=向上(向内)、marker=3=向下(向外)
- `lbl.set_y(-0.025)` for odd (向外标签) / `lbl.set_y(0.04)` for even (向内标签) — 标签跟刻度走
- `ax.tick_params(axis='y', rotation=90)` + `set_verticalalignment('center')` — Y 轴竖排
- `ax.axhline(y=tv, ...)` 遍历 `ticks[1:-1]` 跳过 y=1 — Y 虚线网格（除 y=1 和上下边缘外）

> **matplotlib ≥3.8 踩坑（三次才修对，详见 references/matplotlib-tick-workarounds.md）：**
> 1. `Tick._direction` — 存值但不渲染 ❌
> 2. `tick1line.set_ydata([0, ±length])` — 改了坐标但渲染器不认（用 marker 渲染） ❌
> 3. `tick1line.set_marker(2/3)` — ✅ 唯一有效方式，但必须 `fig.canvas.draw()` 之后设置

**REE/Spider 无图名（2026-06-21）：** `plot_ree()` 和 `plot_spider()` 中 `style_ax(ax, 'Rare Earth Elements', 'Chondrite-normalized')` 改为 `style_ax(ax, '', '')`。图名由图版作曲家（figkit 或人工）在拼版时添加，不属于 IgneousWR 的职责。

**Spider 附加刻度和标签调整（2026-06-21）：** 独立模式（`if ax is None:` 块，`tight_layout` + `draw` 之后）额外执行：
- `ax.xaxis.set_minor_locator(ticker.NullLocator())` — 关闭 X 轴副刻度（29 个元素名不需要）
- `ax.tick_params(axis='y', rotation=90)` + `set_verticalalignment('center')` — Y 轴刻度标签竖排

**Spider X 轴标签不再强制 45° 旋转（2026-06-21）：** `rotation=45, ha='right'` 已移除，改为水平排列。

**REE / Spider Y 轴自动适配（2026-06-21 新增）：** 原硬编码 `yticks=[0.001,0.01,...,1000]` 已替换为根据数据实际最小最大值自动计算 decade 刻度的逻辑：`ymin = 10^floor(log10(min*0.8))`, `ymax = 10^ceil(log10(max*1.2))`。

IgneousWR 各图函数的 `fontsize=` 硬编码已清理（`_source.py` 的 `plot_ree`/`plot_spider` 数据文本）。`_classification.py` 中的 basemap 分区名 fontsize 保留——这些属于底图内容文本，不是 figkit 该管的。

**两种使用模式：**

| 模式 | 用法 | 适用场景 |
|------|------|---------|
| 独立模式 | `plot_tas(gd)` → 自动建画布，出图 | 快速预览单张图 |
| 拼版模式 | `plot_tas(gd, ax=existing_ax)` → 画到指定子图 | A4 拼版，多图组合 |

拼版模式下，IgneousWR 只提供内容，所有样式决策由 LLM 完成。

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

# 单图函数（全部可选 ax 参数）
from igneous_wr_core import (
    plot_tas, plot_ree, plot_spider, plot_k2o_sio2,
    plot_afm, plot_winchester_floyd, plot_co_th,
    plot_pearce_2008, plot_miyashiro, plot_shervais,
    # ... 全部 19 个图函数
)
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

### 单图模式 — `plot_*(gd, save=True, out_dir=None, ax=None)`

**不传 ax（默认）：** 自动建光板画布，保存到文件，返回 `(fig, ax)`。

```python
fig, ax = plot_tas(gd)                # 独立出图，无任何样式
```

**传 ax：** 画到指定子图位置（拼版模式），不创建画布。

```python
# 拼版模式示例：ax 来自下游排版系统
fig, ax_right = plt.subplots()      # 下游创建的画布
fig, ax_left = plt.subplots()
plot_tas(gd, ax=ax_left)            # 画到左下
plot_ree(gd, ax=ax_right)           # 画到右下
```

所有 19 个图函数签名一致：
```python
def plot_*(gd, out_dir=None, save=True, ax=None):
```

> **⚠ ax 参数验证（2026-06-21 修复）：** `_source.py` 中的 `plot_ree()` 和 `plot_spider()` 在本次会话前 **不支持 ax 参数**（签名只有 `(gd, out_dir=None, save=True)`），已补上。出图前务必确认目标函数签名，不要相信 SKILL.md 声称的"所有函数都支持 ax"——逐一验证。

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

### 分组规则 — `infer_groups()`

`GeochemData` 自动从样品名推断分组。三种模式按序匹配：

| 模式 | 正则 | 示例 | 分组结果 |
|------|------|------|---------|
| 1. 连字符前缀 | `^([A-Za-z0-9]+)-` | `MT-01-A1` → 前缀 `MT` | 组 `MT` |
| 2. 字母+数字+字母核心，去末尾数字 | `^([A-Za-z]+[0-9]+[A-Za-z]+)\d*$` | `MT01A1` → 核心 `MT01A` | 组 `MT01A` |
| 3. 回退 | 都不匹配 | 整个样品名当组 | 每样品独立一组 |

**常见匹配失败：** 纯数字前缀（`1A`, `2B`）三组都不匹配，每样品独立。这时可手动覆盖：`gd.groups = ['GroupA', 'GroupA', ...]`。

> **2026-06-21 fix:** 原 SKILL.md 描述的模式2 `^([A-Za-z]+[0-9]+)` 会误将 `MT01A` 和 `MT01B` 合并为组 `MT01`，且实际代码中根本没有此模式。已修正为模式2 `^([A-Za-z]+[0-9]+[A-Za-z]+)\d*$`（提取字母+数字+字母核心，去掉末尾点号数字），并补上代码实现。

### 拼版模式注意事项

所有 19 个图函数签名一致支持 `ax` 参数用于拼版模式。**验证状态（2026-06-21）：**
- `plot_ree` / `plot_spider` — 已确认支持 `ax` ✓（此前代码缺失，已补上）
- 其余 17 个图函数 — 已在 registry 中正确传递 `ax` ✓

### 推荐列表 — `recommended_diagrams(gd)` → list of diagram IDs

### A4 拼版示例

**v2.0 拼版工作流（下游排版系统接管布局和样式）：**

```python
from igneous_wr_core import GeochemData, plot_tas, plot_ree

gd = GeochemData("data.xlsx")

# 以下由下游排版系统创建画布和子图
# 示例：2×2 网格
fig = plt.figure(figsize=(8.27, 11.69))
ax_a = fig.add_axes([0.1, 0.55, 0.35, 0.35])
ax_b = fig.add_axes([0.55, 0.55, 0.35, 0.35])
ax_c = fig.add_axes([0.1, 0.1, 0.35, 0.35])
ax_d = fig.add_axes([0.55, 0.1, 0.35, 0.35])

# IgneousWR 只提供内容
plot_tas(gd, ax=ax_a)
plot_ree(gd, ax=ax_b)
plot_k2o_sio2(gd, ax=ax_c)
plot_winchester_floyd(gd, ax=ax_d)

# 样式和排版由 LLM 在外部完成
# （字体、tick、边框、间距等不在 IgneousWR 范围内）
fig.savefig('4panel.png')
```

## 开发须知

### `_standalone` 模式（2026-06-21 踩坑教训）

IgneousWR 图函数同时支持独立出图和 figkit 拼版两种模式。判断通过 `ax` 参数：`ax=None` 为独立模式。

**⚠ 不要重复用 `if ax is None:` 判断：**

```python
# ❌ 错误：第二次检查永远为 False
if ax is None:
    fig, ax = plt.subplots()   # ax 被从 None 改成了 Axes 对象
if ax is None:                 # ← 永远 False！不会执行
    plt.tight_layout()

# ✅ 正确：用预存变量
_standalone = ax is None       # 在 ax 被赋值前记住
if ax is None:
    fig, ax = plt.subplots()
if _standalone:                # ← 用这个判断
    plt.tight_layout()
```

新增图函数时必须：
1. ✅ 支持 `ax` 参数（拼版模式）
2. ✅ 用 `_standalone` 控制 tight_layout + save_fig（仅独立模式执行）
3. ✅ 不设 `fontsize=`
4. ✅ 不调 `tick_params(direction=...)`
5. ✅ 不画图例（`add_legend` 已全部移除）
6. ✅ 图型特有的刻度/标签放函数内（figkit 不管）
7. ✅ 用 `_style.style_ax()` 统一轴风格（`top=False, right=False`）

---

## 图件内容说明（IgneousWR 负责的部分）

### 分类图（CLS-xx）

IgneousWR 负责：
- 边界多边形绘制（TAS 16 区、AFM Irvine-Baragar 线、Winchester-Floyd 分区……）
- 数据散点按分组着色（`_style.get_group_colors(groups)` 用 `plt.cm.tab10`，LLM 可传自定义 `group_colors` dict 覆盖）
- 轴标签（化学式：`SiO$_2$`、`Na$_2$O`）
- 轴范围（各图型有固定的 xlim/ylim）
- ~~图例~~（图例已移交给 figkit apply_style，2026-06-21）

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
| `style_ax()` 的 tick/spine 设置 | tick 方向、边框属于排版 | 下游 `finalize()` 或 tick_params |
| `plt.tight_layout()` | 排版是下游的责任 | A4Grid 的 `finalize()` |
| `figsize` 硬编码 | 尺寸应随排版确定 | 不设 figsize，由画布决定 |
| `fontproperties=times_prop` | 字体选择是设计决策 | LLM 通过 rcParams 设置 |
| `MK_SIZE_SINGLE` 等数据点样式常量 | 数据点样式是 LLM 的职责 | scatter_samples 用 matplotlib 默认值，LLM 传参覆盖 |
| 模块级 `matplotlib.use('Agg')` | import 无副作用 | 已移除（fig.savefig 无需切换后端） |
| 图函数内硬编码 `fontsize=` | 字号是 LLM/figkit 的职责 | 45 处 fontsize= 全部删除，用 matplotlib 默认值替代 |

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

## Styling Conventions (for LLM agents)

Since v2.0, IgneousWR does NOT enforce any visual style. The following are **descriptions of what IgneousWR draws** — LLMs override all of these:

- **Boundary lines**: IgneousWR draws with `_style.LINE_COLOR_MAIN='#333333'` (main) and `_style.LINE_COLOR_SECONDARY='#666666'` (secondary). These are basemap info (IgneousWR's job).
- **Sample points**: `_style.scatter_samples()` uses `plt.cm.tab10` for group colors. **All data point styling** (marker, size, edge color, linewidth) uses **matplotlib defaults** — LLM must specify these explicitly. See design rule below.
- **No figure size**: IgneousWR creates a plain figure (no figsize) when in standalone mode.
- **No grid**: IgneousWR does not enable grid.
- **No global side effects**: importing IgneousWR does NOT change `matplotlib.use()`, `rcParams`, or font settings.
- **References**: `save_fig()` auto-appends a citation imprint in bottom-right corner.

### 底图 vs 数据点设计规则

```
IgneousWR 该管（底图信息）：
  ✓ 边界线/多边形（位置、线粗范围固定）
  ✓ 判别区标注文字和位置
  ✓ 轴标签、轴范围、刻度位置、刻度值
  ✓ 标准化参考线（y=1 虚线）
  ✓ 画数据线时设 label= 分组名（供 figkit 创建图例）
  （图例创建已移交给 figkit apply_style，2026-06-21）

LLM 该管（数据点样式）：
  ✓ 散点颜色、大小、边缘
  ✓ 线型、线粗、标记符号
  ✓ 所有传递给 scatter_samples() 的视觉参数
```

The `scatter_samples()` function signature:
```python
def scatter_samples(ax, x_arr, y_arr, labels, s=None, edgecolors=None, lw=None,
                    groups=None, group_colors=None, marker='o', **kw):
```

LLM can pass kwargs to control appearance:
```python
# LLM controls ALL data point styling
_style.scatter_samples(ax, x, y, labels, groups=gd.groups,
                       s=40, edgecolors='black', lw=0.5)
```

---

## Verification

```bash
python3 quick_validate.py            # import + instantiation test
python3 generate_test_data.py /tmp/t # create synthetic data
python3 run_test.py                  # end-to-end pipeline
```
