# matplotlib Tick 方向/尺寸 操控踩坑记录

**验证环境：matplotlib 3.10.9，Python 3.12 | 最后更新：2026-06-25（新增根因：Tick 对象重建）**

## 核心结论

控制 X 轴刻度方向（向内/向外）的唯一正确做法：

```python
t.tick1line.set_marker(2)  # 2=向上(向内)
t.tick1line.set_marker(3)  # 3=向下(向外)
```

## 根因：fig.canvas.draw() 会重建 Tick 对象（2026-06-25 发现）

matplotlib 3.8+ 中，`fig.canvas.draw()` 内部调用 `Axis._update_ticks()`，它会：
1. 销毁当前所有 Tick 对象
2. 根据当前 tick 位置/标签创建新的 Tick 对象
3. 新 Tick 的 `tick1line` 使用默认 marker=2（全部向内）

这意味着：**任何在 `fig.canvas.draw()` 之前做的 `set_marker(2/3)` 都会被冲掉。**

### 后果
| 现象 | 根因 | 修复 |
|------|------|------|
| 拼版后刻度交替消失（全变向内） | auto_gap 内部的 draw() 重建了 Tick | set_marker/标签偏移拆入后置函数 |
| 独立出图时正常 | 独立模式只有一次 draw（在 plot_spider 尾部） | — |

### 修复方案
把 Tick 对象级样式从 `plot_spider()` 拆出为 `apply_spider_axis_style(ax)`，在 finalize 和 apply_format **之后**调用。
调用顺序：`plot_* → finalize (draw) → apply_format → apply_*_axis_style (draw) → save`

## 已证实的无效方法

| 方法 | 结果 | 原因 |
|------|------|------|
| `t._direction = 'out'` | ❌ 不生效 | `_direction` 属性在 matplotlib 3.10 中被渲染器忽略 |
| `t.tick1line.set_ydata([0, -length])` | ❌ 不生效 | ydata 不影响渲染——matplotlib 用 marker 绘制刻度线 |

## `ax.tick_params()` 的行为陷阱

`tick_params()` **不是增量更新**——即使只传 `length` 和 `width` 参数，它也会**重置所有 tick 的属性**，包括 marker 类型。

```python
ax.tick_params(length=3.5, width=0.55)
# → 所有刻度的 marker 被重置为 2（全部向内），先前设的 2/3 交替消失
```

### 正确做法：画图前通过 rcParams 设尺寸

**绝不在画图后调 `tick_params`。** 改用 `plt.rcParams` 在 IgneousWR 画图前设好：

```python
import matplotlib.pyplot as plt

# 放在 plot_spider() / plot_ree() 之前
plt.rcParams['xtick.major.size'] = 3.5   # 主刻度长度
plt.rcParams['xtick.major.width'] = 0.55 # 主刻度粗细
plt.rcParams['xtick.minor.size'] = 2.0   # 副刻度长度
# Y 轴同理
plt.rcParams['ytick.major.size'] = 3.5
plt.rcParams['ytick.major.width'] = 0.55
plt.rcParams['ytick.minor.size'] = 2.0
```

IgneousWR 各图函数内部会调 `fig.canvas.draw()`，此时 rcParams 里的尺寸值已被读取，后续的 `set_marker(2/3)` 调用也能存活。

## 长度与字号缩放

默认 IgneousWR 在字号 12pt 时使用：

| 参数 | 12pt 默认值 |
|------|------------|
| TICK_LENGTH (主刻度) | 5 |
| TICK_LENGTH_M (副刻度) | 3 |
| TICK_WIDTH | 0.8 |

缩放公式：`新长度 = 原长度 × (新字号 / 12)`

例如字号 8pt → 5 × (8/12) ≈ 3.5

figkit 的 `formats.py` 中 `format_params` 存储这些值，出图脚本在 `plot_*` 前读取并设 rcParams。
