# `set_y` 的 axes fraction 陷阱

**发现日期：2026-06-25**（画布从 8" 变 257mm 后标签偏移翻倍）

## 问题

`lbl.set_y(value)` 使用 **axes fraction 坐标**（0-1，相对 axes 高度），不是绝对长度。

| 画布高度 | `set_y(0.04)` 实际偏移 | 结果 |
|----------|----------------------|------|
| 127mm (8×5") | 5.1mm | 合理 |
| 257mm (A4 cell) | 10.3mm | 翻倍 ❌ |
| 41mm (panel) | 1.6mm | 太小 ❌ |

## 正确做法：ScaledTranslation + points

```python
from matplotlib.transforms import ScaledTranslation

fig = ax.figure
fig.canvas.draw()

# 6pt = 6/72 inch，不随画布尺寸变化
offset_inner = ScaledTranslation(0, 6/72., fig.dpi_scale_trans)   # 轴内
offset_outer = ScaledTranslation(0, -4/72., fig.dpi_scale_trans)  # 轴外
trans = ax.get_xaxis_transform()

for i, lbl in enumerate(ax.get_xticklabels()):
    if i % 2:
        lbl.set_transform(trans + offset_outer)
        lbl.set_verticalalignment('top')
    else:
        lbl.set_transform(trans + offset_inner)
        lbl.set_verticalalignment('bottom')
```

- `ScaledTranslation` + `fig.dpi_scale_trans` = 绝对 points 偏移
- `ax.get_xaxis_transform()` = x 在 data 坐标、y 在 axes fraction → 标签沿轴排，Y 方向绝对偏移
- `set_transform()` 覆盖 `set_y()`，不同时使用

## 验证

6pt ≈ 2.1mm 在任何画布高度上恒定：
- 127mm 高图：2.1mm 贴轴 ✓
- 257mm 高图：2.1mm 贴轴 ✓
- 41mm cell：2.1mm 贴轴 ✓
