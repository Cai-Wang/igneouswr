# Boundaries JSON Schema Reference

`load_boundary(category, name)` 从 `boundaries/{category}/{name}.json` 加载底图坐标数据。
JSON 的作用是把"图面信息"（分界线坐标、文字位置、参考点、填充区域等）从 Python 代码中分离出来，让改图面数据时不需触碰绘图逻辑。

## 通用结构

所有边界 JSON 必须有 `_meta` 字段：

```json
{
  "_meta": {
    "name": "图件英文名（或原文标题）",
    "type": "XY_annotations | XY_lines | XY_polygons | XY_log_nodes | ternary_boundary | ternary_computed",
    "unit": "坐标单位描述",
    "source": "坐标来源（原始文献 / GCDkit / 用户校准）"
  }
}
```

`_meta.type` 决定后续字段的结构。`_meta.source` 用于追溯坐标来源，强制要求填写。

---

## 类型: `XY_annotations`
散点图类图件的图面标注信息：参考线、填充区域、文字标注。

### 适用图件
SRC-03 Pearce 2008, EVO-02 Miyashiro, EVO-03 Mg#, TEC-05 Shervais, TEC-13 Pearce & Norry

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `axes` | object | ✅ | `xlim`, `ylim`, `xlabel`, `ylabel`, 可选 `xscale`/`yscale` |
| `lines` | array | 选 | 线段对象列表：`{name, style, points: [[x1,y1],[x2,y2]], color, linewidth, zorder}` |
| `reference_lines` | array | 选 | 水平/垂直线列表：`{type: "hline"|"vline", x/y, color, ls, lw, label}` |
| `rays` | array | 选 | 从原点出发的射线列表（Shervais）：`{name, slope, color, ls, lw}` |
| `line_annotations` | array | 选 | 复杂曲线标注：`{type, name, style, formula, x_range, ...}` |
| `polygon_fills` | array | 选 | 背景填充多边形：`{name, fill_x, fill_y, color, alpha, zorder}` |
| `fill_regions` | array | 选 | 分界线填充区域：`{name, x, y_bottom/y_top, line_slope, line_intercept, color, alpha}` |
| `reference_points` | array | 选 | 参考点（含标注偏移）：`{name, x, y, offset_x, offset_y, color, marker, size}` |
| `annotations` | array | 选 | 自由文字标注：`{text, x, y, fontsize, color, rotation, ha, va}` |
| `ray_labels` | array | 选 | 射线旁边的文字标签：`{text, x, y, fontsize, color, fontstyle, ha, va}` |
| `region_labels` | array | 选 | 区域分类标签：`{text, x, y, fontsize, fontweight, color, ha, va}` |
| `grid` | bool | 选 | 是否显示网格线（默认 true） |

**fill_regions 的 line_slope / line_intercept 说明**：
当填充区域边界是一条直线时（如 Miyashiro 的 y=0.1578x-6.016），用 `line_slope` + `line_intercept` 两个数值字段表示，不要用字符串公式。
代码会自动计算 `y = line_slope * x + line_intercept`。

**line_annotations 的 formula 说明**：
对于幂函数阵列（如 Pearce 2008 的 MORB-OIB 阵列），使用：
```json
{
  "formula": {"type": "power_log", "a_intercept": 1.0988, "b": 1.0196},
  "x_range": [0.1, 100]
}
```
代码计算 `y = 10^a * x^b`。

---

## 类型: `XY_lines`
简单 XY 平面分界线集合，没有填充区域。

### 适用图件
CLS-02 K₂O-SiO₂, CLS-04 Shand

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `boundaries` | array | ✅ | 分界线列表：`{name, line_style, points: [[x1,y1],[x2,y2],...]}` |
| `fill_regions` | array | 选 | 填充区域定义（Shand 用 `lines` 代替 `boundaries`） |

**Shand 图的特殊结构**：用 `lines` 键，每条线直接是 `{Metaluminous/Peraluminous: {x: [...], y: [...]}}` 的 dict 形式。

---

## 类型: `XY_polygons`
XY 平面上的多边形分类区域（TAS 等）。

### 适用图件
CLS-01 TAS, CLS-26 TAS Middlemost Plutonic

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `fields` | dict | ✅ | `{field_name: {x: [x1,x2,...], y: [y1,y2,...]}}` 每个分类区的多边形顶点 |
| `labels` | dict | ✅ | `{field_name: {x, y, rotation, ...}}` 每个分类区的标签位置 |
| `fills` | dict | ✅ | `{field_name: {color, alpha}}` 每个分类区的填充色 |

---

## 类型: `XY_log_nodes`
对数坐标系中的节点-边网络图（Winchester & Floyd）。

### 适用图件
CLS-03 Winchester & Floyd

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `nodes` | dict | ✅ | `{node_name: {x, y}}` 所有顶点坐标 |
| `edges` | array | ✅ | `{from, to}` 连线列表（引用 nodes 中的键名） |
| `labels` | array | ✅ | `{text, x, y, fontsize, color, ...}` 终端纹理/分类标注 |

---

## 类型: `ternary_boundary`
三角图（ternary diagram）上的边界曲线。

### 适用图件
CLS-07 AFM, CLS-08 Cabanis, CLS-11 Jensen, CLS-12 Mullen,
CLS-14 O'Connor, CLS-15 Pearce 1977, CLS-16 Ohta & Arai,
TEC-11 Harris, TEC-? (+ ~10 more)

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `polygon` | array | 选 | 单个多边形（Cabanis）：`[{a,b,c}, ...]` 三元坐标 |
| `curves` | dict | 选 | 曲线集合：`{curve_name: {a: [...], b: [...], c: [...]}}` |
| `boundary` | array | 选 | 离散边界点（AFM）：`[{a,b,c}, ...]` |
| `fill_regions` | array | 选 | 填充区域标签 |

所有坐标在 `{a,b,c}` 三元空间（分量非归一化，对应三角图的三个顶点），
函数内通过 `ternary_to_xy(a,b,c)` 转换为笛卡尔坐标绘制。

---

## 类型: `ternary_computed`
三角图的分区由代码根据边界参数计算（QAP 等）。

### 适用图件
CLS-05 QAP (Streckeisen)

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `q_lines` | array | ✅ | Q 轴边界线：`{value, from, to, label}` |
| `ap_ratios` | array | ✅ | A/(A+P) 比值线：`{ratio, from, to, label}` |
| `rock_labels` | array | ✅ | 分类标注：`{q, ap, name, ...}` |

---

## 添加新 JSON 的检查清单

1. 确定底图类型，在 `_meta.type` 填写对应的枚举值
2. 填写 `_meta.source`（具体文献 + 页码 + 版本）
3. 用 `_meta` 之外的键存放坐标数据
4. 在对应���绘图函数中调用 `load_boundary(category, name)` 加载
5. 运行 `python3 quick_validate.py --quick` 确认无回归
6. 避免字符串公式（如 `y_formula: "0.1578*x-6.016"`），改用数值字段（`line_slope` + `line_intercept`）
