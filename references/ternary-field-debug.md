# Ternary Diagram Field Boundary Debugging

> 当三元图投点全部落在场外（图例显示 None）时的系统排查方法。

## 诊断步骤

### 1. 确认场界顶点量级

三元图判别图的场界多边形顶点坐标（PTS_* 字典）是**百分比制**的，三轴分量之和必须归一化到 100%。

检查代码中顶点的数据格式：

```python
# 例如 Pearce & Cann (1973):
PTS_PC = {
    'a':(22,38,40),  # 表示在该点上：Ti占22%, Zr占38%, Y×3占40%
    ...
}
```

看**最大 Ti 值是多少**（如 22），这个值就是场界的"天花板"。

### 2. 检查数据归一化后的 Ti% 

计算数据点的 axis 分量，看归一化百分比是否超过场界上限：

```python
from whole_rock_core import *

gd = GeochemData(EXCEL, sample_filter=SAMPLE_FILTER)
tio2 = gd.get('TiO2'); zr = gd.get('Zr'); y = gd.get('Y')
ti_ppm = tio2 * 10000 * 47.867 / 79.866

# 检查不同标度下的归一化 Ti%
for scale in [100, 1000]:
    ti_scaled = ti_ppm / scale
    y3 = y * 3
    for i in range(len(gd.labels)):
        s = ti_scaled[i] + zr[i] + y3[i]
        pti = ti_scaled[i] / s * 100
        print(f"Ti/{scale}: Ti%={pti:.1f}%")
```

如果 Ti% > 场界顶点中的最大 Ti%，数据点必然无法落在任何场内。

### 3. 检查三元图每个场对数据点的包容性

```python
from matplotlib.path import Path

# 用场界顶点构造多边形，逐点测试
PTS_PC = { ... }
cart = {k: ternary_to_xy(*v) for k, v in PTS_PC.items()}
FIELDS = { 'A': ['a','i','h','d','e'], ... }

for name, vkeys in FIELDS.items():
    pts = [(cart[k][0], cart[k][1]) for k in vkeys]
    path = Path(pts, closed=True)
    for i in range(len(gd.labels)):
        xd, yd = ternary_to_xyz(...)
        if path.contains_point((xd[i], yd[i])):
            print(f"{gd.labels[i]} in {name}")
```

### 4. 网格扫描找出空区

用 5% 步长扫描整个三元图，标记哪些网格点不在任何场中：

```python
for pct_ti in range(0, 101, 5):
    for pct_zr in range(0, 101-pct_ti, 5):
        pct_y = 100 - pct_ti - pct_zr
        x, y = ternary_to_xy(pct_ti, pct_zr, pct_y)
        # 测试是否在任何场内，记录空区
```

## 已知案例：Pearce & Cann (1973) Ti-Zr-Y 图的 Ti/100 vs Ti/1000 bug

### 第一次修复（2026-05-xx，GCDkit 约定）
**问题**：`plot_pearce_cann()` 中用 `ti_arr / 100.0` 归一化数据点，但场界顶点 PTS_PC 中最大 Ti% = 22%。对于 TiO₂ > 1% 的样品，归一化 Ti% 可达 35-42%，全部落在场外。

**解决方案**：将 `ti_arr/100.0` 改为 `ti_arr/1000.0`，对应轴标改为 "Ti/1000"。

**根因**：不同文献及软件对 Ti 轴使用不同的标度因子——原始 Pearce & Cann (1973) 原文用 Ti/100，但许多后来的教科书和软件包(Texbook, GCDkit, ioGAS) 实际上使用 Ti/1000。当前场界顶点数据来源于 Ti/1000 约定，与代码中 Ti/100 的换算矛盾。

### 第二次修复（2026-05-18，回归原文 Ti/100 约定）
**触发**：用户指出图顶顶点应为 Ti/100（原文标准），Zr（左下）和 Y（右下）是标准排列。

**修改**：
- 数据公式：`Ti/1000`→`Ti/100`，取消 `Y×3` 缩放
- 顶点标签：`Ti/1000`→`Ti/100`，`Y×3`→`Y`
- 场界多边形 **未改**（仍基于 GCDkit Ti/1000 约定设计）

**后果**：Ti/100 体系下数据点在图中位置整体上移，而场界仍位于底部的 Ti/1000 位置，样品全部落在场外。需获取原文 Ti/100-Zr-Y 场界的精确数字化坐标后更新 PTS_PC。
