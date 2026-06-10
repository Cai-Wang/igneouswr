# SVG 底图数据提取：从外部来源校核多边形边界

## 适用场景

当需要验证/对比/替换 skill 中某张地球化学判别图的底图（多边形/分界线）时，可以从第三方来源提供的 SVG 图中逆向提取数据坐标。本文件以 RockPlot Electron 应用为例，说明通用提取方法。

## 数据源要求

目标 SVG 必须包含：
1. **坐标轴刻度 Ticks**：`<g class="tick">` 内的 `transform="translate(x,y)"` 和 `<text>` 标签，提供像素到数值的映射基准
2. **多边形路径**：`<path class="polygons">` 或 `<path class="chart_optional_paths">` 的 `d="Mx,yLx2,y2..."` 属性

## 通用方法

### Step 1：确定坐标类型

检查 SVG 的 x/y 轴 `<g>` 标签中的 `transform` 属性，以及轴标签文本。

### Step 2：提取轴刻度映射

对于 X 轴（通常在 `id="x_axis"` 的 `<g>` 内），用正则提取 `translate(px,0)` + 相邻 `<text>` 的数值。

对于 Y 轴（在 `id="y_axis"` 内），提取 `translate(0,px)` + 相邻 `<text>` 数值。

### Step 3：区分线性 vs 对数坐标

从刻度间隔判断：
- 线性：等距 px → 线性 fit → `px = a x value + b`
- 对数：等距弹 log(value) → `px = a x log10(value) + b`

如果刻度只给少量主刻度（如 10、100、1000），px 以 ~log 方式递增，就是对数坐标。

### Step 4：计算映射参数

收集至少 2 个（最好 3 个）刻度的 (px, value) 对：

- 线性 X：`value = (px - intercept) / slope`
- 对数 X：`value = 10^((px - intercept) / slope)`
- 线性 Y（注意 SVG y 向下递增）：`value = (px - intercept) / slope`
- 对数 Y：`value = 10^((px - intercept) / slope)`（同上公式，但注意 px 方向）

### Step 5：提取多边形路径

从 `<path class="polygons">` 或 `<path class="chart_optional_paths">` 中提取 `d="Mx1,y1Lx2,y2..."`，解析出 (x, y) 点序列。

### Step 6：转换像素到数据坐标

将提取的 (px, py) 通过 Step 4 的映射公式转为数据坐标。

## 案例：RockPlot 的 SVG 结构

RockPlot 是一个 Electron 桌面应用（`D:\RockPlot`），其 `.rpp` 项目文件是 ZIP 包含 4 个 JSON。图的边界数据直接编码在 SVG 内，位于 `app.asar -> dist/svg/diagrams/*.svg`。

### 典型 SVG 结构

```xml
<svg width="949.58" height="696">
  <g transform="translate(100,50)">
    <g id="chart_polygons">
      <path d="M93.28,295.88..." class="polygons"/>
    </g>
  </g>
  <g id="x_axis" transform="translate(100,576)">...</g>
  <g id="y_axis" transform="translate(100,50)">...</g>
</svg>
```

关键参数：
- 图区域从 `translate(100,50)` 开始，宽约 700，高约 526
- X 轴域线 `M0.5,10V0.5H700.08V10`（px 从 0.5 到 700.08）
- Y 轴域线从 y=0.5 到 y=526.5（SVG y 向下增长）

### 从 SVG 文件名判别图

| SVG 文件名 | 文献 | 坐标类型 |
|---|---|---|
| `TAS.svg` | Le Bas et al., 1992 | 线性：SiO₂ 35-80, Na₂O+K₂O 0-16 |
| `PearceNorry.svg` | Pearce & Norry, 1979 | 对数-对数：Zr/Y vs Zr |
| `AFM.svg` | Irvine & Baragar, 1971 | 线性：MgO vs (Na₂O+K₂O+FeOₜ) |
| `WinFloyd1.svg` | Winchester & Floyd, 1977 | 对数-对数：Nb/Y vs Zr/TiO₂ |
| `Meschede.svg` | Meschede, 1986 | 三元图 |
| `Wood.svg` | Wood, 1980 | 三元图 |
| `PearceCann.svg` | Pearce & Cann, 1973 | 三元图 |
| `Pearce1996.svg` | Pearce, 1996 | 对数-对数：Th/Yb vs Nb/Yb |
| `Miyashiro.svg` | Miyashiro, 1974 | 线性：SiO₂ vs FeOt/MgO |

完整图清单可通过 `grep -oP 'diagrams/[A-Za-z0-9]+\\.svg'` 从应用的 JS bundle（`assets/index-*.js`）获取。

### 数据提取注意事项

1. **translate 偏移**：多边形路径 px 在 `<g transform="translate(100,50)">` 内，刻度 px 在各自的 axis `<g>` 内。坐标系一致，不用额外减去 translate。
2. **SVG Y 轴反向**：SVG y=0 在顶部、y=526 在底部。数据 Y 值从刻度标签映射时需考虑方向。
3. **三元图特殊处理**：需先确定三角形三个顶点在 SVG 中的像素坐标，然后建立重心坐标→像素的仿射变换映射。
4. **演示数据点忽略**：`<g id="data_points">` 包含示例投点，不是底图边界。

## 结果输出格式

提取的边界应序列化为 Python 代码或 JSON，供绘图函数直接读取：

```python
DIAGRAM_BOUNDARIES = {
    "field_WPB": {
        "x": [16.94, 34.88, 114.62, 58.81],
        "y": [1.35,  3.21,  3.21,   1.35]
    },
    "field_IAB": { ... }
}
```
