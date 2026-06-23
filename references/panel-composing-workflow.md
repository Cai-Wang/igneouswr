# Panel Composing Workflow — Session Notes

This reference documents the step-by-step process and iteration history for composing IgneousWR panel figures (REE + spider diagram side-by-side on A4 canvas).

## Proven Workflow

### Step 1: Load data with GeochemData
```python
gd = GeochemData("/path/to/data.xlsx")
# Auto-detects layout. Check: gd._detected_mode
```

### Step 2: Compute auto y-axis limits from actual normalized data
Do NOT hardcode yticks. Compute the data range dynamically:
```python
import numpy as np
def get_range(gd, labels, elements, normalizer):
    vals = []
    for i in range(len(labels)):
        for el in elements:
            v = gd.get(el)
            if v is not None and el in normalizer:
                try:
                    vi = float(v[i])
                    if not np.isnan(vi) and vi > 0:
                        vals.append(vi / normalizer[el])
                except: pass
    a = np.array(vals)
    return np.min(a), np.max(a)

ree_min, ree_max = get_range(gd, gd.labels, REE_ORDER, CHONDRITE)
sp_min, sp_max = get_range(gd, gd.labels, SPIDER_ORDER, PRIMITIVE_MANTLE)

# Round to nearest decade
ree_ylim = (10**np.floor(np.log10(ree_min)), 10**np.ceil(np.log10(ree_max)))
sp_ylim = (10**np.floor(np.log10(sp_min)), 10**np.ceil(np.log10(sp_max)))
```

### Step 3: Create A4 canvas with A4Grid + auto_gap（推荐，自适应间距）

```python
from matplotlib import pyplot as plt

# A4Grid 类来自 skill 'matplotlib-scientific-layout'
# layout = A4Grid(1, 2, paper='A4', left=..., right=..., wspace=5)
# ax_l = layout.add_subplot(0, 0, label='L')
# ax_r = layout.add_subplot(0, 1, label='R')
# ... 画图、设 ylabel ...
# layout.auto_gap('L', 'R')   # ← 实测文字，自动重排 gap
# layout.save('output.png')
```

**不要手动算 gap。** `auto_gap()` 用 renderer 实测 ylabel 的真实像素宽度，换算出 mm，自动重设 wspace 并重排 axes。换字体、换字号、换文字内容，结果都不一样。

### Step 4: Draw using component API
Import from `igneous_wr_core` and submodules:
```python
from igneous_wr_core import GeochemData
from igneous_wr.core.normalize import REE_ORDER, CHONDRITE, SPIDER_ORDER, PRIMITIVE_MANTLE, normalize
from igneous_wr.report.style import style_ax, get_group_colors, get_color, MK_SIZE_SINGLE, MK_EDGE_COLOR, MK_EDGE_WIDTH
```

Loop over samples, plot lines + scatter using group colors.

### Step 5: Save
```python
fig.savefig("/path/to/output.png", dpi=400)
```

## Publication Formatting Rules (from user feedback on 2026-06-19)

### Y-axis: log + real-number labels
```python
ax.set_yscale('log')
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.0f}'))
ax.yaxis.set_minor_formatter(ticker.NullFormatter())
```

### No figure labels
No `(a)` / `(b)` in titles. Just plain "REE chondrite-normalized" and "Trace element spider diagram".

### No legend
Do not call `ax.legend()`.

### X-axis: alternating top/bottom labels, no rotation
```python
ax.tick_params(right=False, top=False)
for i, label in enumerate(ax.get_xticklabels()):
    if i % 2 == 1:
        label.set_y(0.02)
        label.set_va('bottom')
```

### No top/right tick marks
```python
ax.tick_params(right=False, top=False)
```

### Gap between panels (auto_gap)

**不要手动算 gap。** 用 A4Grid 的 `auto_gap()` 方法：

```python
layout.auto_gap('L', 'R', extra_padding_mm=3)
```

原理：`fig.canvas.draw()` → renderer → `text.get_window_extent()` → 测右图 ylabel + panel label 的真实像素宽度 → mm → 设 wspace → `ax.set_position()` 重排。

换字体、字号、文字内容，auto_gap 自动适配，不用改代码。

auto_gap 技术详情见 `matplotlib-scientific-layout` skill 的 `references/auto-gap-technique.md`。

## Known Pitfalls from Iteration History

### Bbox confusion (fixed)
- ❌ OFF: `bbox_inches='tight'` on full A4 canvas clips the layout
- ✅ RIGHT: No bbox_inches on full A4; use bbox_inches='tight' only when figure size == plot body

### Hardcoded yticks (fixed)
- ❌ OFF: `ax.set_yticks([0.01, 0.1, 1, 10, 100])` doesn't match data range -> excess empty space
- ✅ RIGHT: Compute ylim from actual normalized data, let matplotlib auto-pick ticks

### Line-copying approach (rejected by user)
- ❌ OFF: Create separate figures with `plot_ree(gd, save=False)` then copy artists. Styling doesn't transfer.
- ✅ RIGHT: Use component-level API on a shared A4 canvas

### Scientific notation on log y-axis (fixed 2026-06-19)
- ❌ OFF: matplotlib defaults to 10⁰, 10¹, 10² style ticks on log plots
- ✅ RIGHT: Use `FuncFormatter` to show plain numbers (1, 10, 100, 1000)

### Figure height
- Height 80mm is too short for two subplots (data squeezed, labels overlap)
- Height 120mm gives better proportion (~40% of A4 height)
- User preference: adjust visually until spacing looks right

### Plot body centering
- Plot body centered on A4 canvas using `(1 - fig_w) / 2` math
- Gap between subplots: 0.035 figure-fraction (~7.35mm on A4)
- Each subplot gets ~(160 - 7.35)/2 ≈ 76.3mm width

### IgneousWR warning noise
- The `K` and `P` element warnings from IgneousWR's `check_elements` are harmless — those elements are not in the data but the spider diagram code checks for them internally. Ignore these warnings in output.
