# ScaledTranslation — 绝对单位的 Tick 标签偏移

## 问题

`apply_spider_axis_style` 需要将 X 轴标签错落排列（偶数字标签向上偏移、奇数字向下偏移）。最初用 `lbl.set_y(0.04)`，单位是 axes fraction（相对图高百分比）：

- 图高 127mm (8x5 inch)：0.04 x 127 = 5mm，合理
- 图高 257mm (A4 cell)：0.04 x 257 = 10.3mm，翻倍，标签飞到图中间

## 解法 — ScaledTranslation

用 matplotlib 的 `ScaledTranslation`，偏移量用 points（绝对单位，1pt = 1/72 inch）：

```python
from matplotlib.transforms import ScaledTranslation

offset_inner = ScaledTranslation(0, 6/72., fig.dpi_scale_trans)   # 轴内 6pt
offset_outer = ScaledTranslation(0, -4/72., fig.dpi_scale_trans)  # 轴外 4pt
trans = ax.get_xaxis_transform()

for i, lbl in enumerate(ax.get_xticklabels()):
    if i % 2:
        lbl.set_transform(trans + offset_outer)
        lbl.set_verticalalignment('top')
    else:
        lbl.set_transform(trans + offset_inner)
        lbl.set_verticalalignment('bottom')
```

关键点：
- `ScaledTranslation` 绑定 `dpi_scale_trans`，确保在任意 DPI 下物理距离一致
- 偏移量和 `get_xaxis_transform()` 复合，不影响标签的 X 位置
- 6pt 永远是 6pt，不随图高变化

## 替代方案为什么不work

| 方案 | 问题 |
|------|------|
| `set_y(0.04)` | axes fraction，图高变化后偏移失真 |
| `transform=ax.transData + offset` | 数据坐标转换，不适用于轴标签位置 |
