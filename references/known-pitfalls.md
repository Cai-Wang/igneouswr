# IgneousWR 已知陷阱

## GCDkit 翻译陷阱

### 二元图多边形共享边错位
GCDkit 原版中每个分类区是独立填充色块，相邻多边形共享边即使顶点不一致（一边直线、另一边折线），填充色块也会遮盖底层线段不对外暴露。但在 IgneousWR 纯线框模式下，两条不同路径的线段同时可见，形成多余折角/线段交叉。

**修复原则**：翻译任何 GCDkit 分类图时，`lines` 列表中的相邻多边形共享边必须走完全相同的顶点序列——如果一方经过中间顶点，另一方也必须经过同一顶点，不能一边直线一边折线。

- 典型案例：TAS CLS-01 S3 (Trachyandesite) 右边原本为直线 `(57.6,11.7)→(63.0,7.0)`，但相邻 Td/T 走折线 `(57.6,11.7)→(61.0,8.6)→(63.0,7.0)`，偏差 0.14 个单位。修复后将 S3 补为 5 边形包含 (61.0,8.6) 中间顶点。
- 排查方法：用 `set()` 求相邻两个多边形边集合的交集，确认共享边完全匹配
- 正确的排查顺序：发现坐标问题后，先到 GCDkit 安装目录下找对应 R 源码（如 `Diagrams/Classification/English/TASMiddlemostVolc.r`）确认 GCDkit 的原始定义，再下结论

### 三元图多边形共享边对齐
当两个相邻区域共享一段边界时，它们的闭合顶点序列必须在共享段严格匹配。例如 Meschede TEC-01 中 B 区原为 `l→n` 直线、C 区为 `l→m→n` 折线，两者不共边导致重叠/缝隙。修复后 B 区改为 `l→m→n`，与 C 区完全共享折线。

**规律**：相邻多边形哪条边共享，就在两个多边形的 keys 列表里插相同的中间顶点，不可一边走直线一边走折线。

### 三元图右顶点标签对齐（ha=right → ha=left）
`label_ternary_vertices()` 中右顶点使用 `ha='right'` 会使文字从锚点向左延伸，可能覆盖三角区域。应使用 `ha='left'` 使文字向右延伸，始终在三角外部。与左顶点使用 `ha='right'` 向左伸出三角形成对称模式。

检查：所有 `ax.text()` 的 `ha` 参数应保证文字向外延伸而非向三角内。左顶点 `ha='right'`、右顶点 `ha='left'`。

### GCDkit R 坐标投影
`list("lines", x=xx, y=yy)` 中的值已是三元投影后的 XY 坐标，直接 `ax.plot()` 无需 `ternary_to_xy` 转换。

### R 源码 `\n` 在 Python 中必须用真换行符
R 字符串中的 `\n` 是真换行符（如 `"alkali\nbasalt"`），翻译到 Python 时也必须用真 `\n`（`'Low-K\nTholeiitic'`），不能用 `\\n`（双反斜杠-n 会显示为字面文本不换行）。

## 三元图

### 三角图标签替换字母为地质含义
TEC-01 Meschede 和 TEC-02 Wood 的 A/B/C/D/E 字母标签已替换为地质含义（WPA, N-MORB, CAB, IAT, P-MORB 等），删除下方小字子标签行。改动在 `_tectonic.py` 中两个绘图函数的分区标签渲染循环：`fd['sub']` → `fd['label']`。

### 三角图顶点顺序
`ternary_to_xy(top,left,right)` 与 `label_ternary_vertices(ax,top,left,right)` 参数顺序一致。改顶点时需同步更新 3 处：数据顺序、标签顺序、分界线坐标空间

### 三元图刻度/网格/颜色
- 三元图网格已禁用（2026-06-09）：`draw_ternary_grid()` 函数体已清空
- 三元图刻度颜色（2026-06-09）：从 `#666666` 改为 `#000000`（纯黑）
- 三角图刻度标签风格（2026-06-26 统一）：刻度标签字号改为 `TICK_LENGTH+4`（≈9），字体 `times_prop`

## 特定图件

### TAS 火山岩图（CLS-01）
坐标来源：当前使用 pyrolite 派生坐标（Le Bas 体系），Rhyolite 区边界来自 Middlemost 1994 TASMiddlemostVolc（69,8→71.8,13.5→85.9,6.8→87.5,4.7→77.3,0），Trachyte 拆分为 T1(Q<20%) 和 T2(Q>20%) 两区。

### TAS x 轴刻度
matplotlib AutoLocator 默认从 30 开始标 → 强制 `ax.set_xticks(range(35, 95, 5))`。

### Frost ASI-ANK（CLS-31）没有对角线
只有 h=1 + v=1 两条虚线。Shand A/CNK-A/NK 图（已于 2026-06-09 删除）才有 y=x 对角线。

### K₂O-SiO₂ 标签布局
CLS-02 的 4 个区域标签不应放在图中间居中对齐，而应将 Low-K/Medium-K/High-K 三个标签沿右边缘 x=80 右对齐（`ha='right'`），Shoshonite 沿左边缘 x=44 左对齐（`ha='left'`）。**坐标计算方法**：`y = (边界线1在x=80的值 + 边界线2在x=80的值) / 2`。

## 开源检查清单

- **pyproject.toml build-backend**：`setuptools.backends._legacy` 在 setuptools 81+ 中已不存在。正确的值是 `"setuptools.build_meta"`。
- **无用 import**：`_classification.py`、`_source.py`、`_tectonic.py` 三处都 `from scipy import stats` 但从未使用 `stats.`。scipy 从依赖中移除后这三行会导致 ImportError。
- **refs.json 不可含 `#` 前缀键**：Python json.load 能解析 `#README` 这类注释键，但不是标准 JSON。其他语言（Rust serde_json、Go encoding/json）会直接报错。

## 化学计算

### feot_calc 的 NaN 传播行为
`feot_calc(feo, tfe)` 使用 `np.where(np.isnan(feo), 0.8998*tfe, feo + 0.8998*tfe)`。注意如果 FeO 非 NaN 但 TFe₂O₃ 为 NaN，结果是 `feo + 0.8998*NaN = NaN`——两个参数都被要求、但其中一个 NaN 时整体为 NaN，不会"回退到仅 FeO"。仅有 ALL NaN 的数组才会走单一路径。

## 代码重构

### normalize.py 外置 JSON 的模式
当需要将 Python dict 常量外置到 JSON 时：
1. `tools/extract_normalize_json.py` 可以 AST 解析旧 normalize.py 自动提取所有 dict、NORM_DICT、别名和元素顺序
2. JSON 文件放到 `igneous_wr/core/references/normalization.json`
3. normalize.py 重写为 JSON 加载器 + `normalize()` 函数 + 别名绑定（82 行即可，旧版 1490 行）
4. 修改标准化值时只需改 JSON 文件，再用 extract 脚本重新生成即可对比差异

## 其他

- 不遗留"已知但暂缓"项：用户明确厌恶。如果用户说"全部解决"，需 grep 扫描所有相关位置逐一清理。
- 一次性写入大文件：不要用多步 write_file/heredoc 追加——用独立脚本一次完成。
