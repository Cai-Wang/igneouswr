# 散点形状验证方法

当用户反馈"散点不是圆形"时，用此流程系统排查。

## 排查要点

1. **所有 `ax.scatter()` 调用必须有显式 `marker='o'`** — 不依赖 matplotlib 默认值
2. **`scatter_samples` 函数**（`_style.py`）是 95% 散点的入口，它已经（2026-05-07）加入了 `marker='o'`
3. **`_source.py`**（REE/蜘蛛图）直接调 `ax.scatter()` 而非 `scatter_samples()`，这两处已有 `marker='o'`
4. **`plot_samples_ternary`**（`_style.py`）用 `ax.plot('o', ...)`，格式字符串中的 `'o'` 不受 scatter 默认值影响

## 像素级验证脚本

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 生成测试散点（模拟 scatter_samples 方式）
fig, ax = plt.subplots(figsize=(6, 6))
for i in range(5):
    ax.scatter(i, i, marker='o', color='red', s=60,
               edgecolors='none', linewidths=0)
ax.set_xlim(-1, 6); ax.set_ylim(-1, 6)
plt.tight_layout()
fig.savefig('/tmp/shape_test.png', dpi=300, facecolor='white')

from PIL import Image
img = Image.open('/tmp/shape_test.png').convert('RGBA')
arr = np.array(img)
r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
red_mask = (r > 200) & (g < 160) & (b < 160) & (a > 200)
red_y, red_x = np.where(red_mask)
print(f'红色像素数: {len(red_y)}')

# 取第一个散点区域
if len(red_y) > 3:
    mid = len(red_y) // 2
    cy, cx = int(red_y[mid]), int(red_x[mid])
    crop = arr[cy-20:cy+20, cx-20:cx+20]
    red_crp = (crop[...,0] > 200) & (crop[...,1] < 160) & (crop[...,2] < 160) & (crop[...,3] > 200)
    for dy in range(red_crp.shape[0]):
        row = ''.join('R' if red_crp[dy,dx] else ' ' for dx in range(red_crp.shape[1]))
        print(row)
    # 验证宽高比
    r_y2, r_x2 = np.where(red_crp)
    w = r_x2.max() - r_x2.min() + 1
    h = r_y2.max() - r_y2.min() + 1
    print(f'宽={w} 高={h} 比例={max(w,h)/min(w,h):.2f}')
```

## Path 顶点分析法（无需 PIL）

```python
fig, ax = plt.subplots()
scatter_samples(ax, np.array([1.0]), np.array([1.0]), ['A'])
for child in ax.get_children():
    if hasattr(child, 'get_offsets') and len(child.get_offsets()) > 0:
        paths = child.get_paths()
        if paths:
            verts = paths[0].vertices
            codes = paths[0].codes
            from matplotlib.path import Path
            is_circle = sum(1 for c in codes if c in (3, 4)) > 0  # CURVE3/CURVE4
            y_range = verts[:,1].max() - verts[:,1].min()
            x_range = verts[:,0].max() - verts[:,0].min()
            print(f'圆形: {is_circle}, X/Y比例: {x_range/y_range:.3f}')
```

## 关键教训

即使本地 matplotlib 的 `rcParams['scatter.marker']` 是 `'o'`，目标环境（Windows 不同版本 matplotlib/不同后端/不同系统字体）下的默认值可能不同。**永远显式传 `marker='o'`**。
