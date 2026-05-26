# 多子图拼版架构分析（2026-05-11）

## 背景

用户提出了"一张图里塞 4-6 个子图"的场景优化需求。本文件记录 whole_rock 现有的多子图实现模式、发现的问题、以及架构改进方向。

## 现有模式

### 模式 A：单元图（单 ax）
适用：TAS、K₂O-SiO₂、AFM、Shand、Winchester-Floyd、REE、蛛网图、Pearce 系列、Miyashiro、Mg# 等。

```python
fig, ax = plt.subplots(figsize=(8, 6))
# 画一个子图
plt.tight_layout(pad=0.3)
save_fig(fig, 'xxx.png')
```

### 模式 B：内部多面板（多 axes 写死在函数里）
适用：Harker (2×3)、Zr 协变 (3×3)、四联比值图 (2×2)

```python
fig, axes = plt.subplots(2, 3, figsize=(12, 7))
axes = axes.flatten()
for idx, (ylabel, ydata) in enumerate(...):
    ax = axes[idx]
    scatter_samples(ax, x, y, ...)
    style_ax(ax, xlabel, ylabel)
# 抽取第一个子图的图例，整个 fig 共用
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, ...)
plt.tight_layout(rect=[0,0,1,0.96], pad=0.5)
save_fig(fig, 'xxx.png')
```

### 模式 C：推荐出图独立保存
`plot_recommended()` 内循环调用各图的 `fn(gd)` 函数。每个图存为独立 PNG，最后 HTML 报告合并展示。

## 分析发现的问题

### 问题 1：图例重复绘制
Harker 2×3/三协变 3×3 中，`scatter_samples()` 在每个子图上都加了一次数据点和图例句柄，然后靠 `fig.legend()` 覆盖掉多余的。数据图层重复绘制了 m×n 遍（Harker = 6 遍，Zr = 9 遍），浪费绘图性能，且在大样品量时可能产生重叠伪影。

### 问题 2：Harker 缺失统计信息
Zr 协变图（`plot_zr_covariance`）在每个子图上都计算了线性回归和 R²。Harker 图（`plot_harker`）没有——6 个子图纯粹分散点，没有任何趋势线和统计量。对演化趋势定性分析来说不够直观。

### 问题 3：没有通用的跨图拼版函数
目前论文投稿场景需要手动写 gridspec 组合 TAS + REE + Harker 等。没有统一入口。每次需求不同 = 每次重写拼版代码。

### 问题 4：子图间无交互
静态 PNG 出图后，无法做联动十字线、点击高亮等交互。这是 PNG 格式的天花板，项目早期形态可接受。若未来需要，可考虑 plotly/交互式 HTML。

## 架构改进方案：FigureComposer

### 核心思路

一个 `FigureComposer` 类负责将多个独立图解函数合并到一张大图。它封装 gridspec 管理，支持单元格合并（colspan/rowspan），统一配色和图例。

### 使用示例（设计稿）

```python
composer = FigureComposer(grid=(2, 3), figsize=(18, 12))

# 格子 (0,0) → TAS
composer.add(0, 0, plot_tas, gd)

# 格子 (0,1) ~ (0,2) → REE 横跨两列
composer.add(0, 1, plot_ree, gd, colspan=2)

# 格子 (1,0) → AFM
composer.add(1, 0, plot_afm, gd)

# 格子 (1,1) ~ (1,2) → Harker 精简版（横跨两列，只画关键氧化物）
composer.add(1, 1, plot_harker, gd, colspan=2,
             kwargs={'select_oxides': ['MgO', 'CaO', 'TiO2']})

composer.set_title('Figure 2. 全岩地球化学特征')
composer.save('Figure2_combined.png')
```

### 可选的实现方式

**方案 A：独立 _compositor.py 模块**
- 在 `whole_rock/diagrams/` 下新增 `_compositor.py`
- 不修改现有 22 个绘图函数签名
- `composer.add()` 允许 `colspan` / `rowspan`
- `composer.set_global_legend()` 统一图例

**方案 B：扩展现有函数**
- 给 `plot_tas` 等函数增加可选的 `ax` 参数（如 `plot_tas(gd, ax=ax)`），支持直接画到指定 axes 上
- 现有调用 `plot_tas(gd, ax=None)` 时创建新 fig, ax（保持向后兼容）
- 优点：改动最小，复用现有函数
- 缺点：需要改 22 个函数的签名，侵入性强

**方案 A 更推荐**，因为它不对现有函数做侵入式修改，compositor 内部直接调用现有 `fn(gd)` 然后提取 fig.axes 嵌入。但得注意从 fig 提取子图数据到另一个 fig 的技术细节（matplotlib 的 `figure.subplots` 不可跨 fig 复用 artists 对象——需要用 `OOR` 画法或重新采样数据）。

### 实际可行方案：数据驱动法

由于 matplotlib 的 artists 不可跨 figure 复用，最稳健的做法是：

```python
class FigureComposer:
    def __init__(self, grid=(2,2), figsize=(16, 12)):
        self.fig, self.axes = plt.subplots(*grid, figsize=figsize)
        self.grid = grid
        self._entries = []

    def add(self, row, col, plot_fn, gd, colspan=1, rowspan=1, kwargs=None):
        # 不保存函数引用，而是记录配置
        self._entries.append({
            'fn': plot_fn,
            'gd': gd,
            'row': row, 'col': col,
            'colspan': colspan, 'rowspan': rowspan,
            'kwargs': kwargs or {},
        })

    def render(self):
        for entry in self._entries:
            # 先调原函数生成独立的 fig, ax
            fn = entry['fn']; gd = entry['gd']
            sub_fig, sub_ax = fn(gd, save=False, **(entry['kwargs']))
            # 从 sub_ax 提取数据点坐标 → 重新画到目标 axes
            target = self.axes[entry['row'], entry['col']]
            for line in sub_ax.lines:
                target.plot(line.get_xdata(), line.get_ydata(),
                           marker=line.get_marker(), ...)
            # 复制轴范围、标签、网格等
            target.set_xlim(sub_ax.get_xlim())
            target.set_ylim(sub_ax.get_ylim())
            target.set_xlabel(sub_ax.get_xlabel())
            target.set_ylabel(sub_ax.get_ylabel())
            # 关闭临时 figure
            plt.close(sub_fig)
```

这种"调用原函数 → 提取 artists 数据 → 重组到目标 axes"模式工作量大（要处理三元图特殊情况），但不对现有函数做任何修改。

### 更激进的做法：修改函数签名

给全部 22 个函数增加 `ax` 参数：

```python
def plot_tas(gd, out_dir=None, save=True, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure
    # ... 现有绘图代码（全部用 ax 操作，不用 plt.xxx）...
```

然后在 composer 中直接传 ax：

```python
composer = FigureComposer(grid=(2,2))
fig, axes = composer.render()
plot_tas(gd, ax=axes[0,0])
plot_ree(gd, ax=axes[0,1])
```

缺点是 22 个函数全部要修改。优点是一劳永逸、编译器可检查、无数据复制损失。

## 当前结论（2026-05-11）

用户询问了架构看法，尚未下达"开始实现"的指令。已分析但不执行。待用户确认方向后，选择方案 A（独立 compositor）或签名修改法实施。

### 2026-05-12 更新：FigureComposer 已实现为独立 skill

根据用户决策，拼版功能**不放在 igneous skill 内**，而是作为独立 skill `figure-composer` 创建：

- 路径：`~/.hermes/skills/productivity/figure-composer/`
- Python 包：`scripts/figure_composer/`，暴露 `compose()` 和 `ComposerGird`
- 可实现数据驱动法（调用原函数 → 提取 artists 数据 → 重组到目标 axes）的 V1
- 详见 `figure-composer` skill

### 同次会议决定的其他改进

- **Harker 图已加强**（2026-05-12）：
  - 新增 `only_oxides` 参数，支持动态子集和网格自适应
  - 新增 `trendline=True` 参数，默认子图画线性回归线并标注 R²
  - 解决了原先"Zr 协变有 R² 但 Harker 没有"的不一致问题
- **多余 subplot 隐藏**：动态网格不再留空 subplot（原来是硬编码 2×3）

## 关联

- ���版器完成后再更新此处文档
- 可复用 `DIAGRAM_REGISTRY` 的 `desc` 字段作为子图标题
- 图例统一由拼版器管理，不依赖各图独立 `add_legend()`
