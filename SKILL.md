---
name: IgneousWR
description: >
  Igneous Whole-Rock geochemical plotting engine. Reads Excel data →
  23 publication-ready diagrams (TAS, REE, spider, tectonic discrimination, Harker, etc.)
  + HTML report. Cross-agent compatible.
license: MIT
compatibility: Requires Python 3.10+, matplotlib, numpy, openpyxl
metadata:
  version: "2.3.0"
  author: Chen Yuyang
  email: asukswpu@163.com
  repository: https://github.com/Cai-Wang/igneouswr
  hermes:
    tags: [geochemistry, petrology, plotting, data-science, research]
    related_skills: [isoplotr]
---

# IgneousWR — Agent Usage Manual

## 使用触发条件（Agent Agenda）

**涉及全岩地球化学出图时，IgneousWR 是默认工具。** 用户已明确指出：地化出图应当用 IgneousWR，而不是自己写 matplotlib 脚本拼图。不要等用户说了"用 IgneousWR"才行动。

以下信号自动触发 IgneousWR：
- 用户上传/引用含主量元素（SiO₂、TiO₂、Al₂O₃、TFe₂O₃、MgO、CaO、Na₂O、K₂O、P₂O₅）+ 微量元素（REE、Rb、Sr、Zr、Nb、Th 等）的 Excel 文件
- 用户要求"出图"、"画图"、"plot"、"裸图"——除非明确指定非地化图
- 用户提到具体图型：TAS、REE、蜘蛛图、K₂O-SiO₂、构造判别、Harker 图、AFM、Winchester-Floyd 等
- 数据来源为全岩分析（非锆石/单矿物）

**IgneousWR 不覆盖的场景（回退给手动 matplotlib 或对应 skill）：**
- 单矿物数据图（锆石 REE 等用 `zircon-trace-element` skill）
- IsoplotR 谐和图
- 非地化通用图表

## 设计哲学（v2.0）

**IgneousWR 是地化内容引擎，不是设计工具。** 它保证：
- **底图信息正确**（边界线、多边形判别区、轴标签/范围、标准化参考线）——这些是 IgneousWR 该管的
- **数据标准化正确**（Sun & McDonough 1989 CI Chondrite / Primitive Mantle）
- **边界线与参考文献一致**（TAS 源自 GCDkit，Pearce 2008 经用户校准）
- **引用和来源自动标注**

**IgneousWR 不负责（这些是 LLM 的工作）：**
- **数据点样式**（散点颜色、大小、边缘、线型、标记符号）
- 字体选择、排版布局
- 风格预设、SciencePlots 集成（v2.0 已全部移除）

### 关键架构决策（2026-06-21）

**IgneousWR 不再分模式（`_standalone` 已移除）。** 此前 `plot_spider()` 和 `plot_ree()` 用 `if _standalone:` 区分独立出图和外部 ax 两种模式——这导致外部 ax 时部分内容（刻度交替、Y网格、Y竖排）不执行。现已统一：所有内容设置都在函数体主路径。

**`save` 和 `out_dir` 参数已移除（v2.1），`tight_layout` 由调用方负责。** 图函数签名统一为 `(gd, ax, *, linewidth=1.2, markersize=8, ...)`。IgneousWR 只画内容、返回 `(fig, ax)`。调用方必须传 ax：

```python
fig, ax = plt.subplots(figsize=(8, 5))
plot_ree(gd, ax=ax, linewidth=1.0, markersize=8)
fig.savefig("output.png")
```

**`style_ax()` 不再设字体字号。** IgneousWR 的 `style_ax()` 只设：刻度方向(in)、刻度长度(内容默认值)、副刻度开关、轴框线粗(spine linewidth)、轴标签文本内容。

**图例创建已全部移交给调用方（v2.1）。** IgneousWR 只画线设 `label=` 分组名，不画图例。裸图时需手动 `ax.legend()`。

**子图编号 (a)(b) 由调用脚本负责。** 子图编号是图面组合层的事——不属于任何一张图的数据内容，也不属于排版引擎。

**注意：`apply_spider_axis_style`、`apply_ree_axis_style`、`auto_xlim_padding` 已在 v2.3 实现，可直接从 `igneous_wr_core` 导入。**

---

## 字体架构（GCDkit cex 模式，v2.4 重构）

### 设计思路

底图文字（"Gabbro"、"metaluminous" 等分区标注）不硬编码绝对 pt 值，而是 **相对当前全局字号的 cex 比例**，模仿 GCDkit 的方式。

```
GCDkit:     text(cex=0.8) → 80% 的设备基础字号
IgneousWR:  ax.text(fontsize=base_fs(ax, scale=0.8)) → 80% 的 rcParams['font.size']
```

所有调用站统一使用 `base_fs(ax, scale=M)`，M 是 GCDkit cex 等价的相对比例。
不再出现 `fontsize=N * base_fs(ax)` 这种硬编码 pt 值（2026-07-01 全面改造，44+ 处替换）。

### base_fs(ax, scale=1.0)  —— `scripts/igneous_wr/report/style.py`

```python
def base_fs(ax, scale=1.0):
    """返回当前 ax 下适配的有效字号（pt）。
    - 读取 plt.rcParams['font.size'] 作为基础字号
    - 乘以 ax 物理宽度比例 (ax_w_mm / 203) 保持裸图→拼版视觉比例
    - 下限 55% 防止拼版 cell 里缩到不可读

    ax 203mm, font.size=8 → 8pt（裸图基准）
    ax 75mm,  font.size=8 → max(8×0.37, 8×0.55) = 4.4pt
    """
```

### scale 值对应表（旧硬编码 → 新 cex 等价）

| 旧 pt | 新 scale | 用途 |
|-------|----------|------|
| 8  | 0.80 | 最小号标注 |
| 8.5 | 0.85 | 小号分区名 |
| 9  | 0.90 | 较小文字 |
| 9.5 | 0.95 | 稍小文字 |
| 10 | **1.0** | **正常文字（scale 不传时默认值）** |
| 11 | 1.10 | 加粗/强调 |

### 调用示例

```python
# 正常分区名（如 TAS 中的 "Basalt"）
ax.text(48.5, 2.8, "Basalt", fontsize=_style.base_fs(ax))

# 小号标注（cex=0.8）
ax.text(43, 1.55, "Picrobasalt", fontsize=_style.base_fs(ax, scale=0.8))

# 加粗（cex=1.1）
ax.text(0.5, 0.53, "Tholeiite Series", fontsize=_style.base_fs(ax, scale=1.1))
```

### 为何要读 rcParams

v2.3 的 base_fs 返回无量纲比例 (ax_w_mm/203)，不读全局字号。结果：figkit 设 font.size=8，轴标签 8pt，底图文字 3.7pt（75mm cell），视觉脱节。v2.4 修复：base_fs **读 rcParams['font.size'] 做基准**，返回实际 pt 值。

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

### 数据预处理 — 转置格式（用户常见场景）

用户提供的 Excel 文件经常是**元素在行、样品在列**的转置格式，且混杂了计算行（LOI、Mg#、ΣREE 等）。需要预处理后才能交给 `GeochemData` 加载。参见 `references/user-excel-preprocessing.md`。

### 数据加载 — `GeochemData(path, **kwargs)`

```python
gd = GeochemData("data.xlsx")
gd = GeochemData("data.xlsx", sheet_name=0, dl_strategy="half")
```

Auto-detects 3 layouts: wide (Row 1 = element names, Col A = sample names), standard (transposed), transposed (same as wide, heuristic).

## 图型清单（23图，v2.2 全部支持 ax 参数）

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

### 单图模式（v2.4+ — rcParams 统一传参）

**必须传 ax。** v2.1 不再自动建画布。**v2.4+ 视觉参数通过 `plt.rcParams` 全局设置，无需 STYLE 字典：**

```python
plt.rcParams.update({
    'lines.linewidth': 1.0,
    'lines.markersize': 8,
    'font.size': 9,
    'font.family': 'serif',
})

# 出图：不传视觉参数，自动读 rcParams
fig, ax = plt.subplots(figsize=(8, 5))
plot_ree(gd, ax=ax)
auto_xlim_padding(ax)
apply_ree_axis_style(ax)
fig.savefig("ree_bare.png")
```

**视觉参数解析规则（plot_ree / plot_spider / plot_pearce_2008）：**

| 参数 | rcParams 键 | 不传/不设 rcParams 时的默认值 |
|------|-----------|---------------------------|
| `linewidth` | `lines.linewidth` | 1.2 (IgneousWR 默认) |
| `markersize` | `lines.markersize` | 8 (IgneousWR 默认) |
| `marker_edge_color` | `lines.markeredgecolor` | None（无边） |
| `marker_edge_width` | `lines.markeredgewidth` | 0 (IgneousWR 默认) |

**显式传参仍然有效**（覆盖 rcParams）——向后兼容旧脚本。**

## Special behavior of plot_ree / plot_spider (v2.1+)

| Feature | REE | Spider | Where | Calling constraint |
|---------|-----|--------|-------|-------------------|
| Y-axis auto range (log, clean integer labels) | (log) | (log) | plot_ree / plot_spider | None (content level) |
| Y-axis integer labels | ✅ | ✅ | plot_ree / plot_spider | None (content level) |
| Y-axis grid (dashed) | ✅ | ✅ | plot_ree / plot_spider | Content level (main path) |
| x=1 reference line | ✅ | ✅ | plot_ree / plot_spider | None (content level) |
| Y-axis labels vertical (90°) | ✅ | ✅ | apply_ree_axis_style / apply_spider_axis_style | **After last draw()** |
| X-axis tick alternating in/out | ✅ | ✅ | apply_ree_axis_style / apply_spider_axis_style | **After last draw()** |
| X-axis label staggering (ScaledTranslation, ±7pt) | ✅ | ✅ | apply_ree_axis_style / apply_spider_axis_style | **After last draw()** |
| X-axis edge-label overflow guard | ✅ | ✅ | auto_xlim_padding | **After last draw()**, before apply_* |

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

### X 轴标签偏移（2026-06-23 实现版本）

`apply_ree_axis_style` 和 `apply_spider_axis_style` 使用相同的标签偏移：奇数位 `set_y(-0.025)` + `va='top'`，偶数位 `set_y(0.04)` + `va='bottom'`。两者完全一致，使两图 X 轴视觉对齐。

> 注：SKILL.md 中曾描述 ScaledTranslation(±7pt) 方案，当前代码实际使用 set_y 偏移。如有需要可以改回 ScaledTranslation。

`ax.set_xlabel('Rare Earth Elements')` 和 `ax.set_xlabel('Trace Elements')` 已从 _source.py 删除。

### auto_xlim_padding — 自适应标签溢出防护

`plot_ree` 和 `plot_spider` 初始 xlim 固定 ±0.3 数据单位 padding。在小画布下数据 padding 塌缩，首尾标签（Cs/Lu）会和边框重叠。

`auto_xlim_padding(ax)` 实测首尾 xticklabel 的渲染 bbox，超出多少就扩大 xlim 多少。

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

**关键判别：** 如果这个设置在 `fig.canvas.draw()` 之后丢失，它就是 Tick 对象级，放后置函数。否则放主路径。

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

### REE / Spider 裸图出图清单（checklist，2026-06-23）

裸图出 REE 或 Spider 必须走完整流程，缺一步格式就错：
1. `fig, ax = plt.subplots(figsize=(8, 5))` — 建画布
2. `plot_ree(gd, ax=ax)` / `plot_spider(gd, ax=ax)` — 只画内容，no fontsize set
3. `auto_xlim_padding(ax)` — 防首尾标签溢出（必须先于 apply_*_axis_style）
4. `apply_ree_axis_style(ax)` / `apply_spider_axis_style(ax)` — Tick对象级：刻度交替+标签偏移+Y轴竖排
5. `fig.savefig('output.png')`

**常见错误：**
- 跳过步骤 3-4 直接 save → 刻度全朝同向、首尾标签被边框切掉
- 先 apply_axis_style 再 auto_xlim_padding → padding 失效（Tick 已锁定）
- 调用时传 linewidth=1.0, markersize=8 作为关键字参数（非 `**kwargs` 吞掉）

### 双机协作：WSL + Deepin 代码同步规则（2026-06-23）

WSL和Deepin共享同一仓库。Deepin可能在没有任何沟通的情况下推送改动。**在WSL上做任何改动前必须先 `git pull --rebase`，冲突时优先保留双方改动后再提交**。

**关键事故 2026-06-23：** WSL 实现了 `base_fs(ax)` 动态缩放（`_style.py`），Deepin 同日推送了 `set_font_scale()` 全局缩放（也放在 `_style.py`，同时改了 `_source.py` 的 fontsize 调用）。rebase 自动合并导致 `_source.py` 出现双重缩放——既调了 `set_font_scale(0.55)` 残留代码，又运行了 `base_fs(ax)` 新逻辑——最终字体极小。

**正确操作：** rebase 后手动检查 `_source.py`、`_style.py`、`_classification.py`、`_tectonic.py` 是否有冲突/双重改动。如果 Deepin 先推了 `set_font_scale` 方案，必须清理旧引用（`_SCALING` 变量、`set_font_scale()` 函数、`base_fs()/label_fs()/note_fs()` 三个旧函数），确保只有一套缩放逻辑生效。

### 批量正则替换要慎用（2026-06-23）

给多个函数加 ax 参数时，用 `re.sub` 批量替换 `plt.subplots(figsize=` 在不同函数中写法不一（换行、缩进、三元图没有 tight_layout、co_th 的 figsize 括号被正则切散），极易产生 SyntaxError。

**正确做法：** 用 patch 工具逐个函数精确改——每个函数的二处改动（签名、plt.subplots）用独立的 old_string/new_string。最多改当前需要出图的函数。

### 底图文字架构变迁（v2.3 → v2.4）

**v2.3（已废弃）：** `_style.base_fs(ax)` 返回无量纲比例 `ax_w_mm / 203.0`（下限 0.25）。所有 `ax.text(fontsize=N)` 改为 `N * base_fs(ax)`。不读 rcParams，硬编码 N 为基础字号。

**v2.4（当前）：** base_fs 返回实际 pt 值。读 `plt.rcParams['font.size']` 做基准，乘以 ax 比例。所有调用改用 `base_fs(ax, scale=M)` 模式，M 是 GCDkit cex 等价比例（scale=1.0 = 100% 当前字号）。新增下限 55% 防拼版 cell 中不可读。

**核心变化：** 不再有硬编码 pt 值，底图文字跟全局字号走。

### base_fs 全面重构：读 rcParams + 返回实际 pt + cex 模式（2026-07-01）

v2.3 的 base_fs 不读 `plt.rcParams['font.size']`，采用硬编码 pt × 无量纲比例。
v2.4 全面重构：

1. **读 rcParams**：`target_fs = plt.rcParams.get('font.size', 10)`，底图文字跟全局字号走
2. **返回实际 pt**：不再返回无量纲比例，返回 `target_fs × ratio × scale`
3. **cex 模式**：所有硬编码 N 替换为 `scale=N/10`，scale 即 GCDkit 的 cex 等价
4. **下限 55%**：`max(raw_fs, target_fs * 0.55)`，拼版 cell 里至少可读
5. **44+ 处调用替换**：`_classification.py`、`_evolution.py`、`_tectonic.py`

参考：`references/base-fs-scaling-issue.md`（旧文件，内容已过时，仅保留引用完整性）。

`scatter_samples()` 中 `do_annotate = n <= 25` 逻辑已改为 `do_annotate = False`——不再自动在散点上标注样品名。同时移除了 `ax.annotate()` 代码块。图例通过分组着色 + 调用方手动 `ax.legend()` 添加。

### rcParams markeredgecolor 陷阱（2026-06-24 修复）

`plt.rcParams['lines.markeredgecolor']` 的 matplotlib 默认值是字符串 `'auto'`，但 `ax.scatter(edgecolors='auto')` 不接受这个值——scatter 要求 None 或实际颜色。`_source.py` 中三个函数现在做 `None if _ec == 'auto' else _ec` 转换。

**不要直接在 `plt.rcParams` 里设 `lines.markeredgecolor = 'auto'`——要么不设，要么设具体颜色值。**

### `plot_pearce_2008` scatter_samples 参数名 bug（2026-06-24 修复）

`plot_pearce_2008` 中 `_style.scatter_samples(..., linewidths=marker_edge_width)` 用错了参数名。`scatter_samples` 的形参是 `lw`，而 `linewidths=` 被 `**kw` 捕捉后又和函数体内的 `linewidths=lw` 重复传给 `ax.scatter()`，导致 `multiple values for keyword argument 'linewidths'`。修复：改为 `lw=marker_edge_width`。

---

### 强制规则（对 LLM Agent）

**涉及地球化学全岩出图（TAS、K₂O-SiO₂、REE、Spider、Shand、AFM、判别图等），必须用 IgneousWR skill，禁止自己写 matplotlib 脚本从零画图。** 即使数据格式需要预处理（转置、重命名列），也先预处理数据然后用 IgneousWR 出图。

用户明确说过：如果不是用了 IgneousWR 出的图，就是走了歪路。这条规则优先于任何"我觉得这样更快"的判断。

```bash
python3 quick_validate.py
python3 generate_test_data.py /tmp/t
python3 run_test.py
```
