# 2026-06-21 架构决策记录

> **2026-06-25 更新：本文件中 item 1、5、6 中的「主路径无条件执行」已被修正。**
> 详见下方各章节标注。
> 根因：`fig.canvas.draw()` 在 matplotlib 3.8+ 中通过 `_update_ticks()` 重建 Tick 对象，
> 导致 `set_marker(2/3)` 在 draw 后丢失。Tick 对象级样式必须拆入后置函数 `apply_spider_axis_style(ax)`。
> 完整分析见 `references/matplotlib-tick-workarounds.md` 的「根因」节。

## IgneousWR 架构变更

### 1. 移除 _standalone 分支
所有 plot_* 函数不再分“独立出图”和“figkit 拼版”两种模式。内容级设置全部在主路径无条件执行。
仅保留 `if ax is None:` 用于创建默认画布（裸出模式）。不再有 `if _standalone:`。

> **2026-06-25 修正：Tick 对象级样式（set_marker、标签偏移、Y竖排、Y网格）已从主路径**
> **拆入 `apply_spider_axis_style(ax)` 和 `apply_ree_axis_style(ax)`。**
> 见 SKILL.md「后置轴样式函数」节。

### 2. plot_* 函数签名
```python
def plot_ree(gd, ax=None, **kwargs):
def plot_spider(gd, ax=None, **kwargs):
```
废弃 `out_dir` 和 `save` 参数（用 `**kwargs` 吸收以兼容 batch 系统）。
调用方总负责 `plt.tight_layout()` + `fig.savefig()`。

### 3. style_ax() 变更
- 移除 `fontproperties=times_prop`、`labelsize=9`、`xlabel_size`/`ylabel_size` 参数
- `top=True, right=True` → `top=False, right=False`（刻度仅左/下）
- 签名简化为 `(ax, xlabel='', ylabel='')`

### 4. 图例移交
15 处 `_style.add_legend(ax)` 全部移除。IgneousWR 只画线设 `label=` 分组名。
图例创建和样式由 figkit `apply_style()` 统一处理。

### 5. REE/Spider 增强

> **2026-06-25 修正：Y竖排、Y网格、X副刻度关闭已从 plot_* 主路径拆入后置函数。**
> 留在 plot_* 主路径的：Y 轴自动范围、Y 整数标签、x=1 参考线。
> 在 apply_ree_axis_style / apply_spider_axis_style 中的：Y竖排、Y网格、X副刻度关闭。

- Y 轴自动范围（log decade，根据数据 min/max 计算）
- Y 轴整数标签格式（1 10 100 而不是 1.0）
- y=1 参考线实线
- ~~Y 轴竖排 90°~~ → 移入 apply_*_axis_style
- ~~Y 轴虚线网格（跳过 y=1 和上下边缘）~~ → 移入 apply_*_axis_style
- ~~X 副刻度关闭（NullLocator）~~ → 移入 apply_spider_axis_style

### 6. Spider 特有

> **2026-06-25 修正：X 轴刻度交替和标签偏移已从 plot_spider 主路径拆出。**
> 现在在 `apply_spider_axis_style(ax)` 中。

- X 轴刻度交替：`tick1line.set_marker(3 if i % 2 else 2)` + `fig.canvas.draw()`
- X 标签跟刻度走：向外 `y=-0.025 va=top` / 向内 `y=0.04 va=bottom`
- **移入位置：** `apply_spider_axis_style(ax)`
- **调用时序：** `finalize + apply_format 之后，save 之前`

## matplotlib tick 操控（踩坑三次）

### 无效方案
1. `Tick._direction = 'out'` — 存值但不渲染
2. `tick1line.set_ydata([0, -length])` — 改坐标但渲染器用 marker 渲染

### 有效方案
`tick1line.set_marker(2)` = 向内（向上指）
`tick1line.set_marker(3)` = 向外（向下指）

必须 `fig.canvas.draw()` 之后设置（tick 对象需要先初始化）。

> **2026-06-25 新增根因：`fig.canvas.draw()` 在 matplotlib 3.8+ 中通过 `Axis._update_ticks()`**
> **重建 Tick 对象。这意味着每次 draw 都会生成新 Tick，之前的 set_marker 丢失。**
> **解决方案：确保 `apply_*_axis_style` 是最后一次碰 Tick 对象的函数。**
> 详见 `references/matplotlib-tick-workarounds.md` 的「根因」节。

### tick_params 坑
`ax.tick_params(length=X, width=Y)` 不是“增量更新” —— 它会重置所有 tick 的属性，
包括精心设置的 marker(2/3)。不能用于画图后调整刻度尺寸。
正确做法：在画图前通过 `plt.rcParams` 设好刻度尺寸：
```python
plt.rcParams['xtick.major.size'] = 3.5
plt.rcParams['xtick.major.width'] = 0.55
plt.rcParams['xtick.minor.size'] = 2
```

### figkit刻度尺寸方案
在 `formats.py` 的 `format_params` 中定义 `tick_length`、`tick_width`、`tick_length_minor`。
默认值 5pt/0.8pt/3pt（对应 IgneousWR 的 `TICK_LENGTH=5`）。
字号缩小时同步缩放（8pt 对应 3.5pt / 0.55pt / 2pt）。
出图脚本在画图前通过 rcParams 设好这些值。
