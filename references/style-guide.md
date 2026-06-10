# 绘图风格指南

所有风格集中通过 `_style.py` 管理。提供两层接口：
- **高层**：`set_style_preset(name)` — 一键切换预设
- **低层**：`set_style(**kwargs)` — 单常量覆盖（向后兼容）

## 风格预设（建议首选）

内置 7 套预设，覆盖常见期刊需求（最后两套需要 `pip install SciencePlots`）：

| 预设 | 适用场景 | 调色板 | 散点大小 | 网格 | 图例位置 |
|------|---------|--------|---------|------|---------|
| `default` | 通用出图 | default | 60 | 灰虚线 0.4pt | 右上角 |
| `nature` | Nature 期刊风格 | nature | 50 | 灰点线 0.2pt | 左上角 |
| `lithos` | Lithos 期刊风格 | colorbrewer | 55 | **无网格** | 右下角 |
| `journal_chinese` | 中文地质期刊 | default | 70 | 灰虚线 0.3pt | 右上角 |
| `high_contrast` | 黑白打印/演示 | high_contrast | 70 | 实线 0.5pt | 右上角 |
| `science` | SciencePlots 科学期��风格 | scienceplots (6 色) | 55 | 灰虚线 0.4pt | 右上角 |
| `nature_journal` | Nature 官方模板风格 | nature (学术低饱和) | 55 | 灰点线 0.2pt | 左上角 |

```python
import whole_rock_core as gc
gc.set_style_preset('nature')                  # 一键切换
gc.set_style_preset('nature', MK_SIZE_SINGLE=80)  # 预设+覆盖
```

## 全部可调参数

| 常量 | 默认值 | 含义 |
|------|--------|------|
| `MK_SIZE_SINGLE` | 60 | 二元图散点大小（`scatter(s=...)`） |
| `MK_SIZE_TERNARY` | 15 | 三元图散点大小（`plot(markersize=...)`，标度不同） |
| `MK_MARKER` | `'o'` | 散点形状 |
| `MK_EDGE_COLOR` | `'none'` | 散点边框颜色 |
| `MK_EDGE_WIDTH` | 0.0 | 散点边框宽度 |
| `MK_EDGE_WIDTH_T` | 0.0 | 三元图边框宽度 |
| `ANNOTATE_OFFSET` | (6, 4) | 标注偏移量 (px) |
| `ANNOTATE_FONTSIZE` | 7 | 标注字号 |
| `LEGEND_LOC` | `'upper right'` | 图例位置 |
| `TICK_LENGTH` | 5 | 主刻度长度 (px) |
| `TICK_LENGTH_M` | 3 | 副刻度长度 (px) |
| `TICK_WIDTH` | 0.8 | 刻度线宽 |
| `SPINE_WIDTH` | 0.8 | 坐标轴边框线宽 |
| `GRID_LW` | 0.4 | 网格线宽 |
| `GRID_STYLE` | `'--'` | 网格线型 |
| `GRID_ALPHA` | 0.6 | 网格透明度 |

## 调色板

### 可用调色板

| 名称 | 说明 | 适合场景 |
|------|------|---------|
| `default` | 10 色 Tableau 风格 | 日常出图 |
| `scienceplots` | SciencePlots 6 色推荐循环 | SciencePlots 模式 |
| `nature` | 学术低饱和度 | Nature 期刊 |
| `colorbrewer` | 色盲友好 (Set2+Dark2) | Lithos 等 |
| `high_contrast` | 高对比度 | 演示/黑白打印 |
| `grayscale` | 灰色渐变 | 黑白印刷 |

### 切换调色板

```python
gc.set_palette('nature')         # 仅切换配色，不影响其他参数
```

## 分组着色

分组着色让同一样品组在图上有相同颜色，图例按组合并，实现自动隐式分组。

### 自动推断分组（推荐方式）

`GeochemData` 在 `__init__` 末尾自动调用 `infer_groups()`，无需手动设置。规则如下：

1. 对每个样品编号，找到第一个连字符 `-` 的位置
2. 如果连字符前有字母前缀，该前缀即为组名
3. 否则该样品单独为一组

例：
- `SGT-1`, `SGT-2`, `SGT-5` → 组 `"SGT"`
- `YK-01`, `YK-02`, `YK-03` → 组 `"YK"`
- `B12`（无连字符）→ 每个样品独自一组
- `12-B`（连字符前是数字）→ 每个样品独自一组

分组结果存在 `gd.groups` 属性，类型为 `list[str]`，长度与 `gd.labels` 相同。每个位置的值是该样品���组名。

```python
import whole_rock_core as gc

gd = gc.GeochemData('data.xlsx')
print(gd.groups)   # ['SGT', 'SGT', 'SGT', 'YK', 'YK', 'YK']
```

### 手动指定分组

如需自定义分组，直接赋值 `gd.groups`：

```python
gd.groups = ['玄武岩', '玄武岩', '玄武岩', '安山岩', '安山岩', '流纹岩']
```

### 筛选后分组同步

使用 `gd.filter()` 筛选样品后，`gd.groups` 自动同步过滤，不需要重新调用 infer_groups：

```python
gd.filter_by_bool(gd['SiO2'] > 50)   # 过滤后 gd.groups 自动同步
```

### 绘图函数自动使用分组

所有绘图函数已经内置 `groups=gd.groups`，无需手动传参：

- 分类图（5+种）：TAS、K2O-SiO2、AFM、Shand、Winchester-Floyd、Co-Th
- 源区图（11种）：REE 球粒陨石标准化、原始地幔蛛网图、Pearce Th/Yb-Nb/Yb、U/Th-Zr/Nb、(Sm/Yb)-(La/Sm)、Sc-V、Ba/Th-La/Sm、Gd/Yb-Dy/Dy* 等
- 演化图（4种）：Harker、Miyashiro、Mg#、Zr 协变
- 构造图（10种）：Meschede (Nb-Zr-Y)、Wood (Hf-Th-Ta)、Pearce-Cann (Ti-Zr-Y)、四联图、Shervais Ti-V、Th/Yb-Ta/Yb、Saccani NbN-ThN、Zr/Y-Zr、An-Ab-Or、QAPF

> 注：原"14 个原生图解"已扩展至 30 个（5分类 + 11源区 + 4演化 + 10构造）。

```python
gc.TAS(gd)            # 自动使用 gd.groups
gc.REE_chondrite(gd)  # 自动使用 gd.groups
```

### 手工调用 scatter_samples

```python
# 方式一：scatter_groups 专用函数
_style.scatter_groups(ax, x, y, labels, groups=groups)

# 方式二：scatter_samples 传 groups（不传时完全向后兼容）
_style.scatter_samples(ax, x, y, labels, groups=groups)

# 方式三：三元图同理
_style.plot_samples_ternary(ax, x, y, labels, groups=groups)
```

分组着色会自动从当前活跃调色板取色。

## 重要注意事项

### 散点大小统一原则

所有图件的散点大小已统一为 `MK_SIZE_SINGLE`（60）。
- 各 diagram 模块中不存在硬编码散点大小
- 如需调大/调小全部图的散点，只改一个变量

### 三元图散点标度不同

- 二元图用 `ax.scatter(s=MK_SIZE_SINGLE)`
- 三元图用 `ax.plot(markersize=MK_SIZE_TERNARY)`
- `s=60` 在 scatter 中 ≈ `markersize=15` 在 plot 中

### 白边处理

`MK_EDGE_COLOR='none'` + `MK_EDGE_WIDTH=0.0` 确保散点无外圈白线。

### 散点形状验证

所有散点默认 `marker='o'`。如果用户报告图形异常：

1. **确认看的是最新版代码生成的图**（旧图可能保留旧设置）
2. **Path 分析**：`ax.scatter()` 的 Path 对象应包含 CURVE4 曲线代码
3. **像素分析**：`PIL.Image.open` 提取散点区域做连通域分析，圆形度 ≈ 1.0
4. **后端测试**：强制 `matplotlib.use('Agg')` 生成对比
5. **`color` 参数注意事���**：`scatter_samples` 使用 `color=get_color(i)` + `edgecolors='none'` + `linewidths=0`。`color` 同时影响 facecolors 和 edgecolors，但有 `edgecolors='none'` 覆盖
6. **REE/蜘蛛图特殊**：`_source.py` 用直接 `ax.scatter()` 而非 `scatter_samples()`
7. **三元图特殊**：`plot_samples_ternary` 用 `ax.plot('o', markersize=...)`，渲染机制不同

### 分组着色故障排查

如果出图没有按组着色：

1. 确认使用的是修改后的代码——`gd.infer_groups()` 在 2026-05-09 才加入
2. 确认绘图的 GeochemData 对象是完整的（没有覆盖 gd.groups 为空列表）
3. 确认用的图解函数是 skill 内的原生函数（TAS/REE_chondrite 等），而非手工调用 scatter_samples
4. 确认没有在绘图前手动 `gd.groups = []` 覆盖
5. 测试：`print(gd.groups)` 看分组是否正确生成

## 用法

```python
import whole_rock_core as gc

# 推荐：预设
gc.set_style_preset('journal_chinese')

# 传统：单常量覆盖（仅预设不支持时使用）
gc.set_style(TICK_LENGTH=6, SPINE_WIDTH=1.0, GRID_LW=0.3)
```

> ⚠️ 不要用 `from whole_rock_core import *` 后再赋值——那只改局部变量，绘图函数读不到。必须用 `gc.set_style()` 或 `gc.set_style_preset()`。

## style_ax()

所有二元图统一调用 `style_ax(ax, xlabel, ylabel)`，动态读取全局常量设置：
- 刻度向内（top + right）
- 主/副刻度长度、刻度线宽从全局常量读取
- **全部图默认无网格**（`style_ax()` 中 `ax.grid()` 已在 2026-06-09 移除）
- 三角图网格（`draw_ternary_grid()`）已禁用（2026-06-09 统一风格：三元图不再绘制网格）

> 注：`style_ax()` 与 `draw_ternary_grid()` 的网格是独立的。二元图无网格，三元图网格已移除（2026-06-09 统一风格）。

## 不受 style_ax 影响的图

三元图（AFM、Meschede、Wood、Pearce-Cann）调用 `ax.axis('off')`。这些图通过 `draw_ternary_frame()` 和 `draw_ternary_ticks()` 单独控制外观。

### 三元图与二元图风格统一（2026-06-26 + 2026-06-09）

- **边框线宽**：`draw_ternary_frame()` 已使用 `SPINE_WIDTH`，与二元图 `style_ax()` 的 spine 一致
- **刻度标签字号**：`draw_ternary_ticks()` 字号 = `TICK_LENGTH + 4`（≈9），对齐二元图 `labelsize=9`
- **刻度标签颜色**：从 `#666666` 改为 `#000000`（纯黑），与二元图刻度颜色完全一致
- **刻度标签字体**：加 `fontproperties=_style.times_prop`，与二元图一致使用 Times New Roman
- **顶点标签字号**：`label_ternary_vertices()` 默认 fontsize 从 14→12，对齐二元图 `xlabel_size=12`
- **网格线**：`draw_ternary_grid()` 已禁用，三元图不再绘制网格线，与二元图无网格风格统一
