---
name: IgneousWR
description: 岩浆岩全岩地球化学数据处理与图解绘制 — Igneous Whole-Rock 绘图引擎，读取 Excel 数据 → 19种精选图件 + HTML报告
---

# IgneousWR — Igneous Whole-Rock 绘图引擎

自动化全岩地球化学数据处理与图解绘制。读取合并后的 Excel 数据，自动判断岩性，一站式完成 TAS、REE、蛛网图、Miyashiro 等 **19 种精选图件**（含分类/源区/演化/构造判别），并生成自包含 HTML 图集报告。

## 快速开始

```bash
cd scripts
pip install -e .

python3 -c "
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir
set_out_dir('/tmp/runs/myproject')
gd = GeochemData('/path/to/data.xlsx')
result = plot_recommended(gd)
"
```

输出目录含 PNG 图和 `report_YYYYMMDD.html`。可用 `set_out_dir()` 自定义。

## 精选图目录（19 张）

### 📋 分类 / 岩石系列（12 张）

| # | 文件名 | 图件 | 校正 |
|---|--------|------|------|
| CLS-01 | TAS_Middlemost1994_Volcanic.png | TAS 全碱-硅分类图（火山岩，Middlemost 1994）— 16 个多边形，源自 GCDkit TASMiddlemostVolc.r；Sodalitite 和 Silexite 为纯文本标签 | verified |
| CLS-02 | Middlemost1985_K2O_SiO2.png | K₂O–SiO₂ 钾系列分类 (Middlemost 1985) — 标签参考 GCDkit Peccerillo & Taylor 1976 布局（右侧右对齐 + Shoshonite 左边缘左对齐） | verified |
| CLS-03 | AFM_IB1971.png | AFM 钙碱性-拉斑判别 (Irvine & Baragar 1971) | verified |
| CLS-04 | CLS-04_PeccerilloTaylor1976_K2O_SiO2.png | K₂O–SiO₂ 钾系列分类 (Peccerillo & Taylor 1976) — 多段折线边界，源自 GCDkit PeceTaylor.r | needs_review |
| CLS-05 | Winchester_Floyd1977_NbY_ZrTiO2.png | Zr/TiO₂–Nb/Y 分类 (Winchester & Floyd 1977) | verified |
| CLS-06 | Co_Th_Hastie2007.png | Co-Th 系列+岩性判别 (Hastie 2007) | verified |
| CLS-10 | Mullen1983_TiO2_MnO_P2O5.png | Mullen TiO₂-MnO-P₂O₅ 基性岩三角图 | experimental |
| CLS-13 | TAS_Middlemost1994_Plutonic.png | TAS 全碱-硅分类图（深成岩，Middlemost 1994，x轴 34–90） | verified |
| CLS-17 | Frost2001_Fenum_SiO2.png | Frost Fe# vs SiO₂ 铁质-镁质分类 | verified |
| CLS-29 | Pearce1996_NbY_ZrTi.png | Pearce Zr/Ti–Nb/Y 火山岩分类 | verified |
| CLS-30 | Frost2001_MALI_SiO2.png | Frost MALI vs SiO₂ 碱-钙分类 | verified |
| CLS-31 | Frost2001_ASI_ANK.png | Frost ASI vs A/NK 铝饱和分类 | verified |

### 🔬 源区性质（3 张）

| # | 文件名 | 图件 |
|---|--------|------|
| SRC-01 | SunMcDonough1989_REE.png | REE 球粒陨石标准化配分图（无引用注释） |
| SRC-02 | SunMcDonough1989_Spider.png | 原始地幔标准化蛛网图（无引用注释） |
| SRC-03 | Pearce2008_ThYb_NbYb.png | Pearce Th/Yb–Nb/Yb 源区判别 |

### 🧬 岩浆演化（1 张）

| # | 文件名 | 图件 |
|---|--------|------|
| EVO-02 | Miyashiro1974_FeOtMgO_SiO2.png | Miyashiro FeOt/MgO–SiO₂ |

### 🌍 构造环境判别（3 张）

| # | 文件名 | 图件 |
|---|--------|------|
| TEC-01 | Meschede1986_ternary.png | Meschede Nb–Zr–Y 构造判别（三元） |
| TEC-02 | Wood1980_Hf3_Th_Ta.png | Wood Hf/3–Th–Ta 构造判别（三元） |
| TEC-05 | Shervais1982_Ti_V.png | Shervais Ti-V 构造判别图 |

## 校正状态

| 状态 | 数量 | 含义 |
|------|------|------|
| verified | 15 | 已校正，底图/坐标经用户确认 |
| experimental | 3 (CLS-10, TEC-01, TEC-02) | 框架完整但未逐点校正 |
| needs_review | 1 (CLS-04) | 新增 P&T 1976 图，待用户验证 |

## 参考文件

- `references/gcdkit-polygon-translation.md` — GCDkit `lines` R 格式 → IgneousWR JSON 多边形坐标翻译手册

## 核心原则

- **线段风格统一标准**（2026-06-09 统一）：
  - 主分界线（分类/判别/构造区边界）：实线 `color='#333333'`, **lw=1.5**
  - 次分界线（子分区、辅助划分）：虚线 `color='#666666'`, **lw=1.2**
  - TAS 类多边形（边数多需避免视觉杂乱）：实线 `color='#333333'`, **lw=0.8**
  - 辅助参考线（y=1, ASI-ANK 十字等）：虚线 `color='#666666'`, **lw=0.8**
  - 三元图场界线：实线 `color='#333333'`, **lw=1.5**（与二元图统一）
  - Shervais 型射线：主判别线（Ti/V=50）实线 `color='#333333'`, lw=1.5；辅助线虚线 `color='#666666'`, lw=1.0
  - 所有 `ax.plot()` 禁用 fmt 字符串颜色（如 `'k-'`）以消除 `color is redundantly defined` 警告，统一使用 `color=` 关键字
- **标签风格统一标准**（2026-06-09 统一）：
  - 所有标签统一使用 `#444444`（深灰，纯黑白风格），禁用彩色标签（Frost系列、Mullen、Co-Th、Miyashiro、Shervais 等例外均已统一）
  - 二元图区域标签字号统一 **10**（Frost Fe#/MALI/ASI-ANK、K₂O-SiO₂组）
  - TAS 多边形内标签字号 **8.5**（火山岩+深成岩）、纯文本说明字号 **8**
  - 三元图区域标签字号统一 **11**（AFM, Mullen, Meschede, Wood）
  - WF1977 标签字号统一 **9.5**（代码覆盖 JSON 内 fontsize 字段）
  - Pearce1996 标签字号统一 **10**
  - Shervais 区域标签 **10**、射线标签 **8**
  - REE 配分图 x 轴标签字号 **8.5**、蛛网图 **7.5**（45°旋转）
  - 标引注统一由 `save_fig()` 自动添加（读取 registry 中 `source_ref` 字段），禁用手写 `ax.text()` citation
- **所有图表纯 matplotlib 实现**，无需 pyrolite
- **AI 不做数值计算**（标准化、FeOt换算、坐标变换等全部固化在 Python 代码中）
- **边界数据外置 JSON**（`igneous_wr/boundaries/`），修改坐标不翻函数文件
- **每个修改后 `python3 quick_validate.py --quick`**：秒级回归
- **二元图全部通过 `_style.style_ax()` 统一坐标轴风格**（刻度向内、Times New Roman 字体；默认无网格——`style_ax()` 不添加网格线）。所有二元图无一例外使用 `style_ax()`，禁止手写 `set_xlabel`/`set_ylabel`/`minorticks_on`/`grid`
- **三角图外框线宽统一为 SPINE_WIDTH**：`draw_ternary_frame()` 线宽从 `SPINE_WIDTH * 3.0` 改为 `SPINE_WIDTH`（2026-06-09），三角图边框与二元图四边外框现在视觉一致
- **三元图与二元图视觉完全统一**：边框线宽同 `SPINE_WIDTH`、无网格、刻度标签同号(`TICK_LENGTH+4`≈9)同字体(`times_prop`)同色(`#333333`)、顶点标签字号12对齐`xlabel_size=12`。所有差异参数集中在 `ternary.py` 的 `draw_ternary_frame/grid/ticks` 和 `label_ternary_vertices` 四个函数。修改三元图外观时必须检查二元图对应风格参数，保持同步。
- **化学式下标统一用 LaTeX `$_n$` 语法**（如 `FeO$_t$`, `SiO$_2$`, `Na$_2$O`, `TiO$_2$`），禁止 Unicode 下标符号和纯文本（`FeOt`）。三元图顶点标签例外（用 Unicode 字符通过 `label_ternary_vertices` 传入）
- **底图默认纯黑白线框风格**：除 SRC-03 Pearce2008 Th/Yb-Nb/Yb 外，所有图不渲染分区彩色填充（fill/fill_between/Polygon 色块）。分界线用 ax.plot 纯色描边，分区文字标注保留。SRC-03 是唯一例外，因其源区判别依赖色块视觉区分。如需为某张图添加色区填充，先向用户确认
- **对数轴刻度标签必须用真数**：所有对数坐标轴的刻度标签必须显示实际数值（如 `0.01`, `0.1`, `1`, `10`），不可用科学计数法（如 `10⁻²`, `10⁻¹`, `10⁰`, `10¹`）。设置方式：显式 `ax.set_xticks([...])` + `ax.set_xticklabels(['0.01', '0.1', '1', '10'])`，不可依赖 matplotlib 默认格式。这条规则应用于所有带对数坐标的图（CLS-05, CLS-06, CLS-29, SRC-01, SRC-02, SRC-03）

## 数据输入

支持 3 种 Excel 布局自动检测（wide / standard / transposed）。推荐 wide 格式：Row1=元素名横铺（A1=Sample），Col A=样品名。自动跳过参考标准行（BCR/BHVO/AGV等）。

常见问题：如果 len(gd.all_labels) < 预期样品数，检查 Excel 格式是否被误判为 transposed。可用 `print(gd._detected_mode)` 查看检测模式。

## 删除图件流程

当需要删除某张图（如用户认为太老不再需要）时：

1. **删注册表条目** — 从 `registry.py` 的 `DIAGRAM_REGISTRY` 中移除对应 `DiagramSpec`
2. **删 import** — 同步更新 `registry.py` 顶部的 import、`igneous_wr_core.py` 的 re-export import
3. **删函数体** — 从 `_classification.py` / `_source.py` / `_evolution.py` / `_tectonic.py` 中删除对应 `def` 函数
4. **清理残留引用** — `grep -rn deleted_fn_name scripts/` 检查无遗漏
5. **清理无用 import** — 检查被删文件是否还 import 了不再需要的模块（如 `scipy.stats`）
6. **更新 SKILL.md** — 同步图目录、总数、分组计数、校正状态计数、核心原则中引用的编号
7. **运行批量生成验证** — `batch_backgrounds_main.py --mode full` 确保 19 图全部成功
8. **删除相关引用文件**（如不再引用的 `references/shand-vs-frost-distinction.md`）

已执行案例：EVO-01 (Harker) 于 2026-06-09 删除，注册表从 20→19 图。CLS-04 原为 Shand（已删除），编号已重新分配给 Peccerillo & Taylor 1976 K₂O-SiO₂。

## 目录结构

```
scripts/
├── igneous_wr_core.py          # 门面 API
├── igneous_wr/                 # 全部活跃代码
│   ├── boundaries/             # 坐标边界数据 (JSON)
│   │   ├── cls/                # 分类图边界 (7 JSON)
│   │   ├── src/                # 源区边界 (1 JSON)
│   │   ├── evo/                # 演化边界 (2 JSON)
│   │   └── tec/                # 构造边界 (2 JSON)
│   ├── core/                   # 化学计算、标准化、三元变换、数据类
│   ├── io/excel.py             # Excel 读取
│   ├── diagrams/               # 绘图函数 + 注册表
│   ├── report/style.py         # 样式系统
│   └── batch/                  # 批量出图 + 推荐
├── quick_validate.py           # 验证脚本
├── generate_test_data.py       # 测试数据生成
└── merge_excel.py              # 主量+微量 Excel 合并
```

## 已知陷阱

- **二元图多边形共享边错位——GCDkit 填充色掩盖的陷阱**：GCDkit 原版中每个分类区是独立填充色块，相邻多边形共享边即使顶点不一致（一边直线、另一边折线），填充色块也会遮盖底层线段不对外暴露。但在 IgneousWR 纯线框模式下，两条不同路径的线段同时可见，形成多余折角/线段交叉。**修复原则**：翻译任何 GCDkit 分类图时，`lines` 列表中的相邻多边形共享边必须走完全相同的顶点序列——如果一方经过中间顶点，另一方也必须经过同一顶点，不能一边直线一边折线。
  - 典型案例：TAS CLS-01 S3 (Trachyandesite) 右边原本为直线 `(57.6,11.7)→(63.0,7.0)`，但相邻 Td/T 走折线 `(57.6,11.7)→(61.0,8.6)→(63.0,7.0)`，偏差 0.14 个单位。修复后将 S3 补为 5 边形包含 (61.0,8.6) 中间顶点。详见 `references/tas-s3-trachyandesite-edge-fix.md`
  - 排查方法：用 `set()` 求相邻两个多边形边集合的交集，确认共享边完全匹配
  - **正确的排查顺序**：发现坐标问题后，先到 GCDkit 安装目录下找对应 R 源码（如 `Diagrams/Classification/English/TASMiddlemostVolc.r`）确认 GCDkit 的原始定义，再下结论是否需要修复

- **三元图多边形共享边对齐**：当两个相邻区域共享一段边界时，它们的闭合顶点序列必须在共享段严格匹配。例如 Meschede TEC-01 中 B 区原为 `l→n` 直线、C 区为 `l→m→n` 折线，两者不共边导致重叠/缝隙。修复后 B 区改为 `l→m→n`，与 C 区完全共享折线。规律：**相邻多边形哪条边共享，就在两个多边形的 keys 列表里插相同的中间顶点**，不可一边走直线一边走折线。
- **TAS 火山岩图（CLS-01）坐标来源**：当前使用 pyrolite 派生坐标（Le Bas 体系），Rhyolite 区边界来自 Middlemost 1994 TASMiddlemostVolc（69,8→71.8,13.5→85.9,6.8→87.5,4.7→77.3,0），Trachyte 拆分为 T1(Q<20%) 和 T2(Q>20%) 两区。与 GCDkit TASMiddlemostVolc.r（Middlemost 1994 改编版）不完全一致，差异见 `references/tas-gcdkit-middlemost-comparison.md`
- **Frost ASI-ANK（CLS-31）没有对角线**：只有 h=1 + v=1 两条虚线。Shand A/CNK-A/NK 图（CLS-04，已于 2026-06-09 删除）才有 y=x 对角线。GCDkit `Frost.r` Plot 3 源码只有 `abline(h=1)` + `abline(v=1)`。如果被问到"Frost 图有没有斜线"，答案是没有
- **R 源码的 `\n` 在 IgneousWR 中必须用真换行符**：R 字符串中的 `\n` 是真换行符（如 `"alkali\\nbasalt"`），翻译到 Python 时也必须用真 `\n`（`'Low-K\\nTholeiitic'`），不能用 `\\\\n`（双反斜杠-n 会显示为字面文本不换行）。CLS-29 Pearce1996 和 CLS-02 都曾因此导致多行标签被挤在一行。验证方法：`cat -A <file> | grep "Low-K"` 应显示 `Low-K\\nTholeiitic`（单反斜杠 n），而非 `Low-K\\\\nTholeiitic`（双反斜杠）。**patch 工具写入字符串时对 `\n` 的行为取决于调用方的上下文**——在 `patch` 参数的 Python 字符串中写 `'\\n'` 会被解释为字面 `\n`（正确），写 `'\\\\n'` 则写入 `\\n`（错误）
- **三角图刻度标签风格**（2026-06-26 统一）：三元图刻度标签字号改为 `TICK_LENGTH+4`（≈9），与二元图 `style_ax(labelsize=9)` 一致。刻度标签字体使用 `times_prop`（Times New Roman）。顶点标签字号从 14 改为 12，与二元图 `xlabel_size=12` 统一。改动集中在 `ternary.py` 的 `draw_ternary_ticks()` 和 `label_ternary_vertices()`。
- **三元图网格已禁用**（2026-06-09）：`draw_ternary_grid()` 函数体已清空。为与二元图一律无网格的风格统一，三元图不再绘制灰色虚线网格。
- **三元图刻度颜色**（2026-06-09）：从 `#666666` 改为 `#000000`（纯黑），与二元图默认黑色刻度完全一致。
- **三角图标签替换字母为地质含义**（2026-06-26）：TEC-01 Meschede 和 TEC-02 Wood 的 A/B/C/D/E 字母标签已替换为地质含义（WPA, N-MORB, CAB, IAT, P-MORB 等），删除下方小字子标签行。改动在 `_tectonic.py` 中两个绘图函数的分区标签渲染循环：`fd['sub']` → `fd['label']`。
- **三角图顶点顺序**：`ternary_to_xy(top,left,right)` 与 `label_ternary_vertices(ax,top,left,right)` 参数顺序一致。改顶点时需同步更新 3 处：数据顺序、标签顺序、分界线坐标空间
- **GCDkit R 坐标投影**：`list("lines", x=xx, y=yy)` 中的值已是三元投影后的 XY 坐标，直接 `ax.plot()` 无需 `ternary_to_xy` 转换
- **TAS x 轴刻度**：matplotlib AutoLocator 默认从 30 开始标 → 强制 `ax.set_xticks(range(35, 95, 5))`
- **不遗留"已知但暂缓"项**：用户明确厌恶。如果用户说"全部解决"，需 grep 扫描所有相关位置逐一清理
- **一次性写入大文件**：不要用多步 write_file/heredoc 追加 -- 用独立脚本一次完成
- **K₂O-SiO₂ 标签布局需参考 GCDkit P&T 1976 风格**（2026-06-09 修正）：CLS-02 的 4 个区域标签**不应放在图中间居中对齐**（原写法的错误），而应将 Low-K/Medium-K/High-K 三个标签沿 **右边缘 x=80 右对齐**（`ha='right'`），Shoshonite 沿 **左边缘 x=44 左对齐**（`ha='left'`）。所有标签颜色统一 `#444444` 不分区着色。垂直位置取各区间在 x=80 处的 y 中点。该布局参考 GCDkit `PeceTaylor.r` `temp3` 块的 `adj=c(1,0.5)`（右侧）/ `adj=c(0,0.5)`（左侧）风格。**坐标计算方法**：`y = (边界线1在x=80的值 + 边界线2在x=80的值) / 2`

## 相关技能

- `gcdkit-translator` — GCDkit R 源码-> IgneousWR Python 翻译规范

## 开源维护（commit → push 流程）

当需要将 IgneousWR 的修改推送到 GitHub 时：

### 日常修改后提交（常见场景）

```bash
cd ~/.hermes/skills/data-science/IgneousWR
git add -A
git commit -m "fix: 修改了XX内容"
git push
```

告诉用户"已推上去了"即可。用户不需要了解具体命令。

### 当 GitHub 需要首次设置时

用户是第一次接触 Git/GitHub，必须：
- **用浏览器操作说明**，不说终端命令。说"打开这个网页 → 点这个按钮 → 粘这段内容"
- 生成 SSH key 后，让用户去 `github.com/settings/keys` → New SSH key → 粘贴公钥
- 然后改为 SSH remote 地址再 push
- 每一步完成后给用户一句确认"粘好了告诉我，我继续"
- 参考 `references/first-time-github-publishing.md`

### README 注意事项

- GitHub 仓库的 About 字段应填写简短中文描述（如"岩浆岩全岩地球化学图解绘制工具"）
- README 开头应注明该项目同时也是 Hermes Agent skill（`~/.hermes/skills/data-science/IgneousWR/`）
- 当前 README 为英文即可，暂不需要中文版本

## 相关参考文件

- `references/pearce1996-label-audit.md` — CLS-29 全部标签文本、坐标、旋转角度、对齐方式的 GCDkit PNG 审计表
- `references/pearce1996-gap-fix-20260609.md` — CLS-29 底图在纯线框模式下的缺口修复计算
- `references/pearce1996-gcdkit-alignment-20260602.md` — CLS-29 xlim/ylim/分界线坐标对齐记录
- `references/tas-s3-trachyandesite-edge-fix.md` — CLS-01 TAS S3 右侧边修复（2026-06-29）
