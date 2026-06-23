---
name: IgneousWR
description: >
  Igneous Whole-Rock geochemical plotting engine. Reads Excel data →
  23 publication-ready diagrams (TAS, REE, spider, tectonic discrimination, Harker, etc.)
  + HTML report. Cross-agent compatible.
license: MIT
compatibility: Requires Python 3.10+, matplotlib, numpy, openpyxl
metadata:
  version: "2.2.0"
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

### 关键架构决策（2026-06-21）

**IgneousWR 不再分模式（`_standalone` 已移除）。** 此前 `plot_spider()` 和 `plot_ree()` 用 `if _standalone:` 区分独立出图和 figkit 拼版两种模式——这导致 figkit 拼版时部分内容（刻度交替、Y网格、Y竖排）不执行。现已统一：所有内容设置都在函数体主路径。

**`save` 和 `out_dir` 参数已移除（v2.1），`tight_layout` 由调用方负责。** 图函数签名统一为 `(gd, ax, *, linewidth=1.2, markersize=8, ...)`。IgneousWR 只画内容、返回 `(fig, ax)`。调用方必须传 ax：

```python
fig, ax = plt.subplots(figsize=(8, 5))
plot_ree(gd, ax=ax, linewidth=1.0, markersize=8)
fig.savefig("output.png")
```

figkit 拼版时由 A4Grid + finalize + save 处理布局和保存，IgneousWR 的角色完全相同（`plot_spider(gd, ax=ax)`）。

**`style_ax()` 不再设字体字号。** IgneousWR 的 `style_ax()` 只设：刻度方向(in)、刻度长度(内容默认值)、副刻度开关、轴框线粗(spine linewidth)、轴标签文本内容。

**图例创建已全部移交给调用方（v2.1）。** IgneousWR 只画线设 `label=` 分组名，不画图例。裸图时需手动 `ax.legend()`。

**子图编号 (a)(b) 由调用脚本负责。** 子图编号是图面组合层的事——不属于任何一张图的数据内容，也不属于排版引擎。调用脚本在 finalize 后用 `ax.text(..., transform=ax.transAxes)` 标注。位置用轴分数坐标，和 cell 尺寸无关。

### 与 figkit 的分工合约（v2.1）

**核心原则：图型特有的视觉 → IgneousWR，全局统一的格式 → figkit（但新流程改用 plt.rcParams 前置传入）。**
**时序约束：Tick 对象级样式必须在 finalize() 之后设置。 apply_format/apply_style 已废弃——tick_params 全量重置。
**时序铁律：** `plot_*` → `finalize` → `auto_xlim_padding` → `apply_*_axis_style` → `save`。**

| 谁 | 管什么 | 禁止做什么 | 调用时机 |
|----|--------|----------|----------|
| **IgneousWR `plot_*`** | 轴标签文本、边界线/多边形、标准化数据、轴范围/尺度、参考线、数据分组、刻度位置/值、画线设 `label=` | 禁止设 `fontsize=`；禁止调 `tick_params`；禁止画图例 | 内容阶段（任意顺序） |
| **figkit `finalize`** | 子图位置重排、auto_gap 间距测量 | 不能设刻度风格、字体 | finalize 之后不再调 set_position() |
| **IgneousWR `apply_spider_axis_style`** | Spider X 轴刻度交替内外、标签偏移、Y 竖排 | 不能动子图位置 | **finalize 之后**，save 之前 |
| **IgneousWR `apply_ree_axis_style`** | REE Y 竖排 + X 轴刻度交替内外 + 标签偏移（和 spider 同格式） | 不能动子图位置 | **finalize 之后**，save 之前 |
| **IgneousWR `auto_xlim_padding`** | 自适应扩大 xlim 防止首尾标签溢出边框（内容级，独立函数） | 不能动 Tick 对象 | **finalize 之后**，apply_* 之前 |
| **DEPRECATED: apply_format/apply_style** | 不再调用 | — | — |

---

## Core API Reference

### Import

```python
from igneous_wr_core import (
    GeochemData, plot_recommended, set_out_dir,
    DIAGRAM_REGISTRY, recommended_diagrams,
    plot_ree, plot_spider, plot_pearce_2008,
    # ... 其余图函数
    apply_spider_axis_style, apply_ree_axis_style, auto_xlim_padding,
)
```

### 数据加载 — `GeochemData(path, **kwargs)`

```python
gd = GeochemData("data.xlsx")
gd = GeochemData("data.xlsx", sheet_name=0, dl_strategy="half")
```

Auto-detects 3 layouts: wide (Row 1 = element names, Col A = sample names), standard (transposed), transposed (same as wide, heuristic).

## 图型清单（23图，v2.2 全部支持 ax 拼版）

| 编号 | 函数 | 说明 | 类别 |
|------|------|------|------|
| CLS-01 | `plot_tas` | TAS 火山岩 | 分类 |
| CLS-02 | `plot_k2o_sio2` | K₂O-SiO₂ (Middlemost) | 分类 |
| CLS-03 | `plot_afm` | AFM | 分类 |
| CLS-04 | `plot_k2o_sio2_peccerillo` | K₂O-SiO₂ (Peccerillo) | 分类 |
| CLS-05 | `plot_winchester_floyd` | Zr/TiO₂-Nb/Y | 分类 |
| CLS-06 | `plot_co_th` | Co-Th | 分类 |
| CLS-10 | `plot_mullen` | TiO₂-MnO-P₂O₅ | 分类 |
| CLS-13 | `plot_tasmiddlemostplut` | TAS 侵入岩 | 分类 |
| CLS-17 | `plot_frost_fenr` | Fe#-SiO₂ | 分类 |
| CLS-29 | `plot_pearce1996` | Nb/Y-Zr/Ti | 分类 |
| CLS-30 | `plot_frost_mali` | MALI-SiO₂ | 分类 |
| CLS-31 | `plot_frost_asi_ank` | ASI-A/NK | 分类 |
| CLS-32 | `plot_shand_acnk_ank` | A/CNK-A/NK | 分类 |
| CLS-33 | `plot_whalen_ga_al` | Ga/Al-NK (A-type) | 分类 |
| SRC-01 | `plot_ree` | REE 标准化 | 源区 |
| SRC-02 | `plot_spider` | 蛛网图 | 源区 |
| SRC-03 | `plot_pearce_2008` | Th/Yb-Nb/Yb | 源区 |
| EVO-02 | `plot_miyashiro` | FeOt/MgO-SiO₂ | 演化 |
| EVO-03 | `plot_mgo_sio2` | MgO-SiO₂ 动态轴◊ | 演化 |
| EVO-04 | `plot_p2o5_sio2` | P₂O₅-SiO₂ 动态轴◊ | 演化 |
| TEC-01 | `plot_meschede` | Nb-Zr-Y | 构造 |
| TEC-02 | `plot_wood` | Hf-Th-Ta | 构造 |
| TEC-05 | `plot_shervais` | Ti-V | 构造 |

◊ EVO-03/04 是纯散点哈克图解，无底图边界线，轴范围从数据自动计算（±5% padding，Y 轴不设负值）。

### 单图模式（v2.1+）

**必须传 ax。** v2.1 不再自动建画布。

```python
# 裸图预览：调用方建画布
fig, ax = plt.subplots(figsize=(8, 5))
plot_ree(gd, ax=ax, linewidth=1.0, markersize=8)
fig.savefig("ree_bare.png")

# 拼版模式：ax 来自 A4Grid
layout = A4Grid(1, 2, ...)
ax = layout.add_subplot(0, 0, label='ree')
plot_ree(gd, ax=ax, **style)
```

**视觉参数：** `linewidth`（默认 1.2）、`markersize`（默认 8）、`marker_edge_color`、`marker_edge_width`。不传则用默认值。

**全部 23 个图函数均已支持 ax 参数（v2.2，2026-07-02）。** 旧签名 `(gd, out_dir, save)` 可ax，新签名 `(gd, ax=None, out_dir=None, save=True)` 可接受外部 ax 进行拼版。`new_fig` 标志门控 `tight_layout` 和 `save` 的调用——使用外部 ax 时不调这两个。

### A4 拼版示例（新流程 v2.1）

```python
from figkit.layout import A4Grid
from igneous_wr_core import plot_ree, plot_spider, apply_spider_axis_style, apply_ree_axis_style, auto_xlim_padding
import matplotlib.pyplot as plt

style = {'linewidth': 1.0, 'markersize': 8}
plt.rcParams.update({'font.size': 7, 'font.family': 'serif', 'axes.linewidth': 0.5})

layout = A4Grid(1, 2, paper='A4', left=25, right=25, top=123, bottom=124, hspace=0, wspace=10)
ax_ree = layout.add_subplot(0, 0, label='ree')
ax_sp  = layout.add_subplot(0, 1, label='sp')
plot_ree(gd, ax=ax_ree, **style)
plot_spider(gd, ax=ax_sp, **style)
result = layout.finalize(pairs=('ree', 'sp'))   # auto_gap v2: 只报告
auto_xlim_padding(ax_ree)
auto_xlim_padding(ax_sp)
apply_ree_axis_style(ax_ree)
apply_spider_axis_style(ax_sp)
layout.save('panel.png')
```

## Special behavior of plot_ree / plot_spider (v2.1+)

| Feature | REE | Spider | Where | Calling constraint |
|---------|-----|--------|-------|-------------------|
| Y-axis auto range (log, clean integer labels) | (log) | (log) | plot_ree / plot_spider | None (content level) |
| Y-axis integer labels | ✅ | ✅ | plot_ree / plot_spider | None (content level) |
| Y-axis grid (dashed) | ✅ | ✅ | plot_ree / plot_spider | Content level (main path) |
| x=1 reference line | ✅ | ✅ | plot_ree / plot_spider | None (content level) |
| Y-axis labels vertical (90°) | ✅ | ✅ | apply_ree_axis_style / apply_spider_axis_style | **After finalize** |
| X-axis tick alternating in/out | ✅ | ✅ | apply_ree_axis_style / apply_spider_axis_style | **After finalize** |
| X-axis label staggering (ScaledTranslation, ±7pt) | ✅ | ✅ | apply_ree_axis_style / apply_spider_axis_style | **After finalize** |
| X-axis edge-label overflow guard | ✅ | ✅ | auto_xlim_padding | **After finalize**, before apply_* |

## 图型特有说明

### REE / Spider Y 轴：对数，标签用真数整数（用户偏好）

`plot_ree` 和 `plot_spider` 使用完全一致的 Y 轴对数处理模式：`set_yscale('log')` → `FixedLocator` 锁定刻度 → `FuncFormatter` 标签 → `NullLocator` 关闭次要刻度。**两者 Y 轴范围计算也统一了（Spider 不再额外延伸 decade）**，避免范围过宽导致标签拥挤。

**Spider Y 轴稀疏标签（>7 decade 时触发）：** 当 decade 数量 >7（极端数据跨 8+ 个数量级），`FuncFormatter` 按 decade 指数奇偶跳显——`round(np.log10(v)) % 2 == 0` 的 decade 才标（如 -2/0/2/4 → 0.01、1、100、10000），奇数 decade（-1/1/3 → 0.1、10、1000）跳过。网格线保留全部 decade。

**关键模式（避免 matplotlib 自动加 0.xx 刻度）：** 设 `set_yscale('log')` 之后必须用 `FixedLocator` 锁定刻度位置、用 `NullLocator` 关闭次要刻度——否则 matplotlib 的 LogFormatter 会自动插入 0.1、0.01 等小数刻度。

```python
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

clean_ticks = [t for t in ticks if t >= 1]       # 不要 <1 的刻度
ax.set_ylim(clean_ticks[0], clean_ticks[-1])
ax.yaxis.set_major_locator(FixedLocator(clean_ticks))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:g}'))
ax.yaxis.set_minor_locator(NullLocator())          # 关掉次要刻度
```

**为什么不能用 `set_yticks(ticks)`：** `set_yticks` 加上 `set_yscale('log')` 后，matplotlib 的 AutoLocator 会自动补充 0.1 刻度并渲染标签。必须用 `FixedLocator` 强制锁定。

Y 轴标签保留（`Primitive-mantle normalized`），X 轴标题已移除（元素名列表本身就是 xticklabels）。

### X 轴标签偏移——±7pt 对称（2026-06-26）

`apply_ree_axis_style` 和 `apply_spider_axis_style` 使用相同的 `ScaledTranslation(0, ±7/72., ...)` 偏移：偶数位标签向内 +7pt，奇数位向外 -7pt。两者完全一致，使两图 X 轴视觉对齐。

**为什么是 ±7pt 不是 6/-4pt：** `style_ax().TICK_LENGTH = 5pt`。旧版奇数位 -4pt 使标签距刻度尖仅 1pt（刻度 5pt 外 + 标签 4pt 外 = 几乎贴着），且偶数位距轴线 6pt、奇数位距轴线仅 4pt——不对称。±7pt 保证标签与刻度尖始终保持 2pt 间隙，内外对称。

`ax.set_xlabel('Rare Earth Elements')` 和 `ax.set_xlabel('Trace Elements')` 已从 _source.py 删除。

### auto_xlim_padding — 自适应标签溢出防护

`plot_ree` 和 `plot_spider` 初始 xlim 固定 ±0.3 数据单位 padding。这在裸图（~200mm 宽）下刚好够，但 A4 拼版 cell（~75mm）下数据 padding 塌缩，首尾标签（Cs/Lu）会和边框重叠。

`auto_xlim_padding(ax)` 在 finalize（cell 尺寸定型）后实测首尾 xticklabel 的渲染 bbox，超出多少就扩大 xlim 多少。裸图和拼版都调——拼版 cell 窄，自动扩得多；裸图宽，自动扩得少。两边物理效果一致。

**时序约束：** finalize → auto_xlim_padding → apply_*_axis_style → save。必须在 finalize 之后（cell 尺寸定型）和 apply_* 之前（xlim 是内容级，不应和 Tick 对象级混在一起）。

## 踩坑记录（本会话教训）

### 手术刀式修改原则

改造现有函数时，只做单处匹配替换，不是写整个函数体。以下信号说明在「重写」不是「改」：
- `old_string` 超过 15 行 -> 缩小范围，只匹配要改的那几行和前后 1-2 行上下文
- `new_string` 超过 20 行 -> 拆成多次 patch

**案例：** 改造 `plot_ree`/`plot_spider` 时，三处修改（删 figsize、参数化 lw/s、拆 set_marker）应该做三次 patch，每次只改目标段落。一次替换整个函数体导致用户之前调好的内容级功能被覆盖。

### 内容级 vs Tick 对象级——放哪里的判别

| 属于 | 特征 | 例子 |
|------|------|------|
| **内容级 -> plot_* 主路径** | 图型固有的，和图的数据/类型直接相关 | Y 轴范围/scale、网格线、参考线、`style_ax()` 刻度方向/副刻度、Y 轴自适应 decade 计算 |
| **Tick 对象级 -> apply_*_axis_style** | 会被 `fig.canvas.draw()` 打掉 | `set_marker(2/3)` 交替、标签偏移/旋转、`NullLocator` 关闭副刻度 |

**关键判别：** 如果这个设置在 `finalize->auto_gap` 的内部 draw 之后丢失，它就是 Tick 对象级，放后置函数。否则放主路径。

### Python 作用域陷阱：函数内 `from ... import` 遮蔽模块级导入

**Bug 表现：** `plot_ree` 内新增 `ax.xaxis.set_minor_locator(NullLocator())`（第61行），运行时抛出 `UnboundLocalError: cannot access local variable 'NullLocator'`，尽管模块顶部第3行已 `from matplotlib.ticker import NullLocator`。

**根因：** 函数体第62行有 `from matplotlib.ticker import FuncFormatter, FixedLocator, NullLocator`。Python 编译器扫描整个函数体，发现 `NullLocator` 在局部 `import` 中被赋值，于是将 `NullLocator` 标记为**局部变量**（整个函数作用域）。第61行使用 `NullLocator()` 时局部变量尚未赋值——`UnboundLocalError`。

**修复：** 把局部 `import` 挪到函数内第一次使用之前：
```python
# ✅ 局部 import 必须在第一次使用 NullLocator 之前
from matplotlib.ticker import FuncFormatter, FixedLocator, NullLocator
ax.xaxis.set_minor_locator(NullLocator())   # 现在 NullLocator 是局部变量，已赋值
```

**教训：** 在已有模块级 `import NullLocator` 的情况下，函数内再加 `from ... import NullLocator` 会导致整个函数体内 `NullLocator` 变成局部变量。要么只依赖模块级导入（删掉函数内的重复 import），要么把局部 import 放在所有使用之前。

`set_yscale('log')` 之后，matplotlib 的 LogFormatter 会自动添加 0.1、0.01 等下级 decade 刻度并渲染标签。手动 `set_yticks(ticks)` 也不够——必须用 `FixedLocator` 锁定 + `NullLocator` 关掉次要刻度。详见上面「Spider Y 轴：对数，标签用真数整数」节。

### 字号 vs 画布尺寸不匹配

`plt.rcParams['font.size']` 是绝对单位，同样字号在 8 英寸宽图上合适，在 75mm A4 拼版 cell 里就重叠。调用方需自行根据 cell 宽度调整字号：

| 画布宽 | 建议字号 | 场景 |
|--------|---------|------|
| 8 英寸 (203mm) | 9-10pt | 裸图预览 |
| 75mm (A4 拼版 cell) | 6-7pt | 投稿拼版 |

不能统一用一个字号——这是旧 apply_format 做的事，现在由调用方自己根据 layout 尺寸设。

### 底图文字硬编码 fontsize → 动态缩放（2026-06-23 已修复）

**根因：** 分类图（TAS、Shand、K₂O、Frost 系列等）的底图分区标注（"Gabbro"、"Diorite"、"metaluminous" 等）历史上用硬编码 `fontsize=8.5`~`11` 写在 plot 函数里——不受 `plt.rcParams['font.size']` 控制。

裸图 `figsize=(8,6)=203×152mm` 时 8.5pt 正常。拼版 `cell=75mm` 时相同字号相对大了约 2.7 倍。

**v2.3 修复：** 所有 `ax.text(fontsize=N)` 改为 `fontsize=N * _style.base_fs(ax)`，自动按 ax 物理宽度缩放。

`_style.base_fs(ax)` 实现：`ax_width_mm / 203.0`（裸图基准 8 英寸=203mm）。
- ax 宽 203mm → 返回 ≈1.0（裸图不变）
- ax 宽 75mm  → 返回 ≈0.37（拼版自动缩小）
- 下限 0.25（极小 cell 也不丢标签）

受影响的文件：`_classification.py`（42处）、`_source.py`（2处）、`_evolution.py`（1处）、`_tectonic.py`（4处）。JSON 驱动的 annotation fontsize 默认值也同步缩放（`ann.get('fontsize', 10) * base_fs(ax)`）。

调用方无需任何额外操作——传 ax 进 IgneousWR，底图文字自动适配 cell 尺寸。

JSON 边界数据中的 fontsize 字段也走同一条缩放路径（`json_val * base_fs(ax)`），不增加复杂度。详见 `references/json-fontsize-convention.md`。

### scatter_samples 不再自动标注样品名（2026-07-02）

`scatter_samples()` 中 `do_annotate = n <= 25` 逻辑已改为 `do_annotate = False`——不再自动在散点上标注样品名。同时移除了 `ax.annotate()` 代码块。裸图和拼版都是无标注的干净散点。图例通过分组着色 + 调用方手动 `ax.legend()` 添加。

---

## Verification

```bash
python3 quick_validate.py
python3 generate_test_data.py /tmp/t
python3 run_test.py
```
