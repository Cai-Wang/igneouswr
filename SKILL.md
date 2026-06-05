---
name: IgneousWR
description: 岩浆岩全岩地球化学数据处理与图解绘制 — Igneous Whole-Rock 绘图引擎，读取 Excel 数据 → 68种专业图件 + HTML报告
---

# 岩浆岩全岩地球化学技能（Igneous Geochemistry）

自动化全岩地球化学数据处理与图解绘制。读取合并后的 Excel 数据，自动判断岩性，一站式完成 TAS、REE、蛛网图、Harker 等 68 种专业图件（含分类/源区/演化/构造判别），并生成自包含 HTML 图集报告。

## 快速开始

```bash
# 1. 安装（推荐）
cd ~/.hermes/skills/data-science/IgneousWR/scripts
pip install -e .

# 2. 载入
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir

# 3. 读取数据
gd = GeochemData('/path/to/merged_geochemistry.xlsx')

# 4. 一键出所有推荐图
result = plot_recommended(gd)
```
```

输出目录：默认 `../runs/default/`（相对于 scripts/ 目录，不在 skill 目录内），含 PNG 图和 `report_YYYYMMDD.html`。可用 `set_out_dir('/path/to/runs/myproject')` 自定义。

## 架构状态 — 已完成

架构迁移已完成。全部活跃代码在 `igneous_wr/` 包中。

**遗留 shim 已清理（2026-06-05）**：`scripts/` 根目录下的 4 个 `sys.modules` 门面文件（`_style.py`, `_chem.py`, `_ternary.py`, `_normalize.py`）已删除。包内所有 import 已改为直接引用 `igneous_wr.report.style` / `igneous_wr.core.chem` 等完整包路径。包括 3 处函数体内延迟 import（`_source.py:371 PRIMITIVE_MANTLE`、`:648 CHONDRITE`、`_tectonic.py:440 N_MORB`）和 docstring 示例引用全部已清理。`scripts/_mullen_swap.py` 也已删除。

**双源映射已消除（2026-06-05）**：
- `_SHORT_TO_LONG`（style.py 硬编码字典）→ 替换为 `_build_short_to_long_index()`，从 `DIAGRAM_REGISTRY` 懒初始化
- `DIRECTION_MAP`（style.py 硬编码字典）→ 替换为 `_get_direction(fn_name)`，从注册表 filename 前缀自动推断
- `FILENAME_MAP`（registry.py 硬编码字典）→ 删除，`batch/recommend.py` 改为直接遍历 `DIAGRAM_REGISTRY`

**开源脚手架已添加（2026-06-05）**：`pyproject.toml`（setuptools 构建）、`LICENSE`（MIT）、`README.md`（面向开源用户）、`.gitignore`（增 `*.bak`、`*.json.bak`、`references/dev-notes/`）

**dev-notes 已分离**：24 个调试/重构/工作流记录移至 `references/dev-notes/`，`.gitignore` 排除。学术参考 + 边界 spec 约 31 个文件保留在 `references/` 根目录。

每次修改后确认 `quick_validate.py --quick` 通过。

## 功能总览

### 0. 参考文献库（references/）

**当前状态**：refs.json 已有 83 条记录，其中 62 条（75%）填写了完整的 full 字段引用信息（来源：GCDkit PDF 经 MinerU 提取）。
参考文献批量填充由 `scripts/ig_refs_update.py` 完成（若需重做：从 refs.json.bak + gcd-pdf-full-references.md 重新映射）。
仍有 21 条无 full 字段——其中 ~9 条为占位条目（SVG 边界/未核实公式，无标准引用），其余 12 条为 PDF 中无对应记录的文献（Stern 2006, Hickey-Vargas 2018, Pearce 1983, Xia 2014 等），需从原文补充。
`references/gcd-pdf-full-references.md` 是 GCDkit PDF 完整 ~55 条参考文献的原始提取。

`igneous_wr/references/` 目录管理所有图件的参考文献：

- **`refs.json`**：文献库，每条记录一个 key。格式：`key → {short, full, type}`
- **`loader.py`**：加载与查询模块，支持按 key 解析、报告列表生成
- **注册表 `source_ref` 统一用 key 引用**（如 `"lebas1992"` 而非 `"Le Bas et al. 1992"`）
- 出图时 `save_fig()` 自动查注册表，在图右下角印灰色斜体引用（如 *Irvine & Baragar (1971)*）
- HTML 报告末尾自动生成参考文献列表
- 你校正图片时直接往 `refs.json` 的 `full` 字段填完整引用信息就行

### 1. 数据处理（whole_rock_core.py）

| 功能 | 说明 |
|------|------|
| `GeochemData(path)` | 读取标准化 Excel（4 行表头 + 数据），自动解析检测限 |
| `read_excel(path)` | 替代 `GeochemData` 的底层函数 |
| `recommended_diagrams(gd, rock_type='auto')` | 判断岩性 → 返回可用图件列表 |
| `plot_recommended(gd)` | 一键出所有推荐图 + 生成 HTML 报告 |
| `normalize(data_dict, ref)` | 按参考值标准化（CHONDRITE / PRIMITIVE_MANTLE） |
| `set_style_preset(name)` | 切换风格预设（'lithos', 'nature', 'gca'） |

#### 输出文件名约定

所有输出 PNG 文件必须带注册表编号前缀，格式为 `{CLASS}-{NN}_{DescriptiveName}.png`：

| 类别 | 前缀 | 示例 |
|------|------|------|
| 分类 | CLS | `CLS-01_TAS.png` |
| 源区 | SRC | `SRC-01_REE_chondrite.png` |
| 演化 | EVO | `EVO-01_Harker_6panel.png` |
| 构造 | TEC | `TEC-01_Meschede1986_ternary.png` |

**实现机制：** 每个绘图函数内部硬编码调用 `_style.save_fig(fig, '短名.png', out_dir)`，`save_fig` 通过 `_build_short_to_long_index()` 从 `DIAGRAM_REGISTRY` 自动反查带编号的长名。新增图件时只需在 registry 添加 `DiagramSpec` 记录，`save_fig` 会自动补编号前缀。（历史：`_SHORT_TO_LONG` 硬编码字典已于 2026-06-04 删除，替换为注册表动态构建。）

### 2. 数据预处理（merge_excel.py）

合并独立的**主量 + 微量 Excel 文件**为标准化格式。自动检测标准/转置格式，按样品编号对齐，排除标准物质行。

```bash
python merge_excel.py 主量文件.xlsx 微量文件.xlsx -o 输出.xlsx
```

输出 Excel 格式：
```
Row 1: 样品编号
Row 2: Major / Trace 类别（合并单元格）
Row 3: 元素符号
Row 4: 单位（wt% / ppm）
Row 5+: 数据
```

自动计算常用比值（ΣREE、Eu/Eu*、标准化比值、Zr/Hf 等）。

## 图解目录（68 种，按用途分为 4 类 + 编号）

每张图对应输出文件名为 `PREFIX-NN_DescriptiveName.png`：
- **CLS** = 岩石系列/分类（27 张）
- **SRC** = 源区性质（15 张）
- **EVO** = 岩浆演化过程（6 张）
- **TEC** = 构造环境判别（20 张）

> **注意**：旧版 `plot_pearce1996`（Pearce 1996 Th/Yb–Nb/Yb）已移除（与 `_source.py` 的 `plot_pearce_2008` 功能重叠）。现 `plot_pearce1996` 为 **Pearce (1996) 修改版 Zr/Ti–Nb/Y 火山岩分类图**（`CLS-29`），Y 轴为 Zr/Ti（非 Zr/TiO₂），底图坐标来自 GCDkit `Pearce1996.r` 源码精确提取。三个 Zr/Y–Zr 图（`pearcenorry`, `pearce1982`, `zr_y_zr`）判据不同，全部保留并在 registry 中用 desc 标注区分。

#### 📋 岩石系列 / 分类（CLS，27 张）

| 编号 | 文件名 | 图件 | 所需元素 |\n|------|--------|------|---------|\n| CLS-01 | TAS.png | TAS 全碱-硅分类图 | SiO₂, Na₂O, K₂O |\n| CLS-02 | Middlemost1985_K2O_SiO2.png | K₂O–SiO₂ 钾系列分类图 (Middlemost 1985) | SiO₂, K₂O |\n| CLS-03 | AFM_IB1971.png | AFM 钙碱性-拉斑系列判别 | Na₂O, K₂O, MgO |\n| CLS-04 | Shand_ACNK_ANK.png | Shand A/CNK–A/NK 铝质分类图 | Al₂O₃, CaO, Na₂O, K₂O |\n| CLS-05 | Winchester_Floyd1977_NbY_ZrTiO2.png | W&F 原始版 Zr/TiO₂–Nb/Y 分类图（v11 用户校准；Pearce 1996 修改版见 CLS-29） | Zr, TiO₂, Nb, Y |\n| CLS-06 | Co_Th_Hastie2007.png | Co-Th (Hastie) 火山弧岩浆系列+岩性分类图 | Co, Th |
| CLS-08 | QAPF_Streckeisen1976.png | Q-A-PF 深成岩分类三元图 | SiO₂, Na₂O, K₂O, CaO, Al₂O₃ |
| CLS-09 | Cabanis1986_LaY_Nb_ternary.png | Cabanis La/10-Y/15-Nb/8 基性岩三角图 | La, Y, Nb |
| CLS-10 | Mullen1983_TiO2_MnO_P2O5.png | Mullen TiO₂-10×MnO-10×P₂O₅ 基性岩三角图（6色区：OIT/IAT/MORB/CAB/OIA/Bon；实线L1+L2虚线L3+L4；坐标取自用户逐点校准的独立脚本） | TiO₂, MnO, P₂O₅ |
| CLS-11 | Jensen1976_cation_ternary.png | Jensen Al+Fe³⁺+Ti–Mg+Fe²⁺+Mn–Ca+Na+K 阳离子分类三角图（已校正：氧化物体积比例→阳离子数、四色区+岩类标注） | Al₂O₃, FeO/TFe₂O₃, TiO₂, MgO, MnO, CaO, Na₂O, K₂O |
| CLS-12 | OConnor_Volc_An_Ab_Or.png | O'Connor An-Ab-Or 火山岩三角图（已校正：8色区+8类岩性标注） | Na₂O, K₂O, CaO |
| CLS-13 | TAS_Middlemost1994_Plutonic.png | TAS 深成岩分类（Middlemost 1994）——坐标源自 GCDkit 6.3.0 TASMiddlemostPlut.r，16+2 封闭多边形 | SiO₂, Na₂O, K₂O |
| CLS-14 | TAS_Middlemost1994_Volcanic.png | TAS 火山岩分类（Middlemost 1994） | SiO₂, Na₂O, K₂O |
| CLS-15 | TAS_Cox1979_Plutonic.png | TAS 深成岩分类（Cox 1979） | SiO₂, Na₂O, K₂O |
| CLS-16 | TAS_Cox1979_Volcanic.png | TAS 火山岩分类（Cox 1979） | SiO₂, Na₂O, K₂O |
| CLS-17 | Frost2001_Fenum_SiO2.png | Frost Fe-number vs SiO₂ 铁质-镁质分类 | SiO₂, MgO |
| CLS-18 | Whalen1987_GaAl_Zr.png | Whalen 10000×Ga/Al–Zr A型花岗岩 | Ga, Al₂O₃, Zr |
| CLS-19 | Whalen1987_GaAl_Nb.png | Whalen 10000×Ga/Al–Nb A型花岗岩 | Ga, Al₂O₃, Nb |
| CLS-20 | Whalen1987_GaAl_CeYZr.png | Whalen 10000×Ga/Al–Ce+Y+Zr A型花岗岩 | Ga, Al₂O₃, Ce, Y, Zr |
| CLS-21 | Villaseca1998_ASI_FMM.png | Villaseca ASI–FMM 花岗岩源区分类 | Al₂O₃, CaO, Na₂O, K₂O, MgO, TiO₂ |
| CLS-22 | Debon1983_BA_diagram.png | Debon B-A 花岗岩矿物分类图 | Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| CLS-23 | Debon1983_PQ_diagram.png | Debon P-Q 花岗岩矿物分类图 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| CLS-26 | LaRoche1980_R1_R2_plutonic.png | La Roche R1-R2 侵入岩分类图 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| CLS-27 | LaRoche1980_R1_R2_volcanic.png | La Roche R1-R2 火山岩分类图 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| CLS-28 | Middlemost1991_Plutonic.png | Middlemost Na₂O+K₂O–SiO₂ 深成岩分类 | SiO₂, Na₂O, K₂O |
| CLS-29 | Pearce1996_NbY_ZrTi.png | Pearce (1996) Zr/Ti–Nb/Y 火山岩分类图（GCDkit 精确坐标，log-log，10 区域彩色填充；2026-06-02 校准） | Zr, Ti, Nb, Y |

#### 🔬 源区性质（SRC，15 张）

| 编号 | 文件名 | 图件 | 所需元素 |
|------|--------|------|---------|
| SRC-01 | REE_chondrite.png | REE 球粒陨石标准化配分图 | La–Lu 14 个 REE |
| SRC-02 | Spider_PM.png | 原始地幔标准化蛛网图 | Rb–Lu 26 个元素 |
| SRC-03 | Pearce2008_ThYb_NbYb.png | Pearce Th/Yb–Nb/Yb 源区判别（GCDkit v6.3 底图：淡蓝多边形背景 + 虚线MORB-OIB阵列 + 三个精确 S&M89 参考点；无UCC/1:1线/箭头） | Th, Nb, Yb |
| SRC-04 | UTh_ZrNb_Stern2006.png | U/Th-Zr/Nb (Stern) 源区判别 | U, Th, Zr, Nb |
| SRC-05 | SmYb_LaSm_partial_melting.png | (Sm/Yb)PM-(La/Sm)PM 部分熔融图 | La, Sm, Yb |
| SRC-06 | Sc_V_HickeyVargas2018.png | Sc-V (Hickey-Vargas) 氧化条件判别 | Sc, V |
| SRC-07 | BaTh_LaSm_PearceRobinson2010.png | Ba/Th-La/Sm 流体 vs 熔体判别 | Ba, Th, La, Sm |
| SRC-08 | GdYb_DyDystar_Davidson2013.png | Gd/Yb vs Dy/Dy* 稀土分馏模式 | La, Gd, Tb, Dy, Ho, Yb |
| SRC-09 | DyYb_LaYb_garnet_depth.png | Dy/Yb vs La/Yb 石榴石深度判别 | Dy, Yb, La |
| SRC-10 | Ohta_Arai2007_MFW.png | Ohta & Arai M-F-W 俯冲带源区三角图 | La, Sm, Nb, Ce, Zr, Y |
| SRC-11 | Pearce1995_NbYb_ThYb.png | Pearce Nb/Yb–Th/Yb 源区判别 | Nb, Th, Yb |
| SRC-12 | Pearce1995_TiYb_NbYb.png | Pearce Ti/Yb–Nb/Yb 源区判别 | Ti, Nb, Yb |
| SRC-13 | Sylvester1989_CaONa2O_Al2O3.png | Sylvester CaO/Na₂O–Al₂O₃ 花岗岩源区判别 | CaO, Na₂O, Al₂O₃ |
| SRC-14 | LaYb_vs_Yb.png | La/Yb vs Yb 源区部分熔融判别 | La, Yb |
| SRC-15 | Ross2009_LaSm_LaYb.png | Ross La/Sm–La/Yb 岩浆过程判别 | La, Sm, Yb |

#### 🧬 岩浆演化过程（EVO，6 张）

| 编号 | 文件名 | 图件 | 所需元素 |
|------|--------|------|---------|
| EVO-01 | Harker_6panel.png | Harker 六合一协变图 | SiO₂, MgO, Al₂O₃, CaO, Na₂O, TiO₂ |
| EVO-02 | Miyashiro1974_FeOtMgO_SiO2.png | Miyashiro FeOt/MgO–SiO₂ | SiO₂, MgO |
| EVO-03 | MgNo_vs_SiO2.png | Mg# vs SiO₂ 演化图 | SiO₂, MgO |
| EVO-04 | Zr_covariance.png | Zr 协变 3×3 图 | Zr, Nb, Hf, Th, Y, Yb, La, Sm, Ba, Sr |
| EVO-05 | Hollocher2012_VSc.png | Hollocher V/Sc–V+Sc 氧化条件 | V, Sc |
| EVO-06 | Hollocher2012_VSc_ZrCe.png | Hollocher Zr/Ce–V/Sc 分类 | V, Sc, Zr, Ce |

#### 🌍 构造环境判别（TEC，20 张）

| 编号 | 文件名 | 图件 | 所需元素 |
|------|--------|------|---------|
| TEC-01 | Meschede1986_ternary.png | Meschede Nb–Zr–Y 构造判别（三元） | Nb, Zr, Y |
| TEC-02 | Wood1980_Hf3_Th_Ta.png | Wood Hf/3–Th–Ta 构造判别（三元） | Hf, Th, Ta |
| TEC-03 | PearceCann1973_TiZrY.png | Pearce & Cann Ti–Zr–Y 构造判别（三元） | Ti, Zr, Y |
| TEC-04 | V_Ti_Sc_ThNb_BaTh_4panel.png | 四联比值���造判别图 | Ti, V, Sc, Th, Nb, Ba |
| TEC-05 | Shervais1982_Ti_V.png | Shervais Ti-V 构造判别 | Ti, V |
| TEC-06 | ThYb_TaYb_Pearce1983.png | Th/Yb–Ta/Yb (Pearce 1983) 构造判别 | Th, Ta, Yb |
| TEC-07 | NbN_ThN_Saccani2015.png | NbN–ThN (Saccani 2015) 构造判别 | Nb, Th |
| TEC-08 | ZrY_Zr_Xia2014.png | Zr/Y vs Zr (Xia 2014) 岛弧 vs 大陆弧 | Zr, Y |
| TEC-09 | NbLa_ThLa_Cabanis1986.png | Nb/La vs Th/La 构造判别 | Nb, Th, La |
| TEC-10 | Pearce1977_FeOt_MgO_Al2O3.png | Pearce FeOt-MgO-Al₂O₃ 基性岩构造三角图 | MgO, Al₂O₃ |
| TEC-11 | Harris1986_Rb30_Hf_3Ta.png | Harris Rb/30-Hf-3Ta 花岗岩构造三角图 | Rb, Hf, Ta |
| TEC-12 | Muller2000_Kternary.png | Muller Th-Ta-Hf 三子图构造判别 | Th, Ta, Hf |
| TEC-13 | Pearce_Norry1979_ZrY_Zr.png | Pearce & Norry Zr/Y–Zr 构造判别 | Zr, Y |
| TEC-14 | Pearce1982_ZrY_Zr.png | Pearce (1982) Zr/Y–Zr + Ti/Nb/Sr | Zr, Y, Ti, Nb, Sr |
| TEC-15 | Pearce1984_Granite_Rb_YNb.png | Pearce Rb–Y+Nb 花岗岩构造判别 | Rb, Y, Nb |
| TEC-16 | Schandl2004_Y_Zr.png | Schandl Y–Zr 花岗岩构造判别 | Y, Zr |
| TEC-17 | Batchelor1985_R1_R2.png | Batchelor & Bowden R1-R2 花岗岩构造判别 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| TEC-18 | Maniar1989_Granite_disc.png | Maniar & Piccoli 花岗岩构造判别 | SiO₂, Al₂O₃, MgO, CaO, Na₂O, K₂O, TiO₂ |
| TEC-19 | Agrawal2004_DF1_DF2.png | Agrawal DF1-DF2 基性岩构造判别 | TiO₂, Al₂O₃, MgO, CaO, Na₂O, K₂O, MnO, P₂O₅, SiO₂ |
| TEC-20 | Verma_discriminant_DF1_DF2.png | Verma 判别函数 基性岩构造判别 | TiO₂, Al₂O₃, MgO, CaO, Na₂O, K₂O, MnO, P₂O₅, SiO₂ |

### 4. 风格预设系统

```python
from whole_rock_core import set_style_preset

set_style_preset('lithos')   # Lithos 期刊风格（默认）
set_style_preset('nature')   # Nature 期刊风格
set_style_preset('gca')      # GCA 期刊风格
```

支持对单个参数进行覆盖：
```python
import _style
_style.MK_SIZE_SINGLE = 80       # 散点大小
_style.LEGEND_LOC = 'lower right'
_style.FIGSIZE = (12, 8)
```

### 5. HTML 图集报告

`plot_recommended()` 执行完毕后自动在输出目录生成 `report_YYYYMMDD.html`：

- 所有图以 2 列网格排列，按 4 个方向分组（📋分类 ��� 🔬源区 → 🧬演化 → 🌍构造）
- 单击缩略图 lightbox 放大，查看全尺寸 PNG
- 顶部显示数据来源、样品数量、岩性判定
- 跳过图件透明列出（缺哪些元素）
- 无需 Python / 服务器，可发给合作者直接打开

## 安装

安装依赖（仅标准科学计算库）：
```bash
pip install matplotlib numpy openpyxl Pillow
```

或者（推荐，2026-06-05 起可用）：
```bash
cd ~/.hermes/skills/data-science/IgneousWR/scripts
pip install -e .
```

**不含 pyrolite（已全部移除）。所有图表（包括 TAS）均为纯 matplotlib 实现，无需额外依赖。**

Times New Roman 字体（期刊风格需要）：
```bash
# WSL + Windows 字体
cp /mnt/c/Windows/Fonts/times.ttf ~/.fonts/
```

## 技能目录结构

```
scripts/
├── igneous_wr_core.py      # 门面 API（统一入口 + re-export；不再有遗留 shim 文件）
├── igneous_wr/             # 全部活跃代码（2026-06-05: 4 个 sys.modules shim 已删除）
├── merge_excel.py          # 主量+微量 Excel 合并
├── batch_backgrounds_main.py   # 批量底图生成（全67张，双模式 minimal/full）
├── quick_validate.py       # 验证脚本（--quick 秒级回归；含 preflight 版本检查 + 元素依赖完整性）
├── requirements.txt        # 依赖锁定（numpy, matplotlib, scipy, openpyxl。2026-06-05: 移除已为 stdlib 的 dataclasses）
├── igneous_wr/        # 当前活跃目录
    ├── boundaries/          # 坐标边界数据（JSON）。cls/ 下 14 个 JSON，tec/ 下 3 个（harris, shervais, pearce_norry），evo/ 下 2 个（miyashiro, mgno），src/ 下 1 个（pearce_2008）。不仅限多边形坐标——也包含文字标注、参考点、比值射线等图面信息。
    │   ├── core.py          # load_boundary(category, name)
    │   ├── cls/ src/ evo/ tec/  # 四类 JSON 边界数据
    ├── __init__.py
    ├── core/
    │   ├── chem.py         # 化学计算
    │   ├── normalize.py    # 标准化参考值
    │   ├── ternary.py      # 三元坐标变换
    │   └── data.py         # GeochemData 数据类
    ├── io/
    │   └── excel.py        # Excel 读取
    ├── diagrams/
    │   ├── registry.py     # DIAGRAM_REGISTRY + DiagramSpec
    │   ├── _classification.py  # 分类图 — 27 个函数
    │   ├── _source.py      # 源区图 — 15 个函数
    │   ├── _evolution.py   # 演化图 — 6 个函数
    │   └── _tectonic.py    # 构造图 — 20 个函数
    ├── report/
    │   └── style.py        # 样式系统
    └── batch/
        ├── recommend.py    # plot_recommended
        └── backgrounds.py  # 批量底图
references/
    README.md                         # 目录结构说明（2026-06-05 新增）
    dev-notes/                         # 开发调试记录（约 24 个 .md，不随开源发布；.gitignore 排除）
    afm-18point-boundary.md
    pearce1996-gcdkit-alignment-20260602.md
    ...（学术参考 + 边界 spec 约 31 个文件，开源版包含）
```

### style_ax dash bug（多次复现）

在 TAS 系列图（`plot_tas`, `plot_tasmiddlemostplut` 等）上调用 `_style.style_ax()` 会导致 `ValueError: At least one value in the dash list must be positive`。根因在 matplotlib backend 的 grid line dash 参数传递。修复办法：不在 TAS 图上调用 `style_ax`，改用手动设置坐标轴标签和网格：
```python
ax.set_xticks(range(35, 95, 5))
ax.set_yticks(range(0, 21, 3))
ax.set_xlabel(r'SiO$_2$ (wt.%)', fontsize=11)
ax.set_ylabel(r'Na$_2$O+K$_2$O (wt.%)', fontsize=11)
ax.minorticks_on()
ax.grid(True, which='major', alpha=0.15, lw=0.3)
```
Le Bas TAS (`plot_tas`) 不走 issue 路径的原因是它的 `ax.grid` 在 fill+plot 之后调用顺序不同。目前所有 TAS 变体（Middlemost Plut/Volc, Cox Plut/Volc）都应使用手动轴设置而非 `style_ax`。如未来修复 `style_ax` 根因，这些函数应统一改回 `style_ax`。

### 故障排除

### Excel 格式自动检测

`GeochemData` 用 `merge_excel.py` 中的 `_detect_format()` 自动判断两种格式：

**标准格式（推荐，行=元素，列=样品）：**
```
Row 1: 样品编号 | SA01 | SA02 | SA03 | ...
Row 2: SiO2       | 58.2 | 62.1 | 55.8 | ...
Row 3: TiO2       | 0.85 | 0.72 | 1.12 | ...
```

**转置格式（行=样品，列=元素）：**
```
Row 1: 样品编号 | SiO2 | TiO2 | Al2O3 | ...
Row 2: SA01       | 58.2 | 0.85 | 16.5  | ...
Row 3: SA02       | 62.1 | 0.72 | 15.8  | ...
```

判断规则：A1 含"样"/"Sample" → 转置；第1行含已知元素名 → 标准。

#### ✅ GeochemData 格式检测——已修复（2026-06-02）

**修复状态：已修复并验证通过。**

原 `_load()` 检测逻辑只靠一个单元格（B1）判断文件格式，过于脆弱——用户的标准地球化学表布局（A1=Sample, B1起铺元素名）恰好触发 transposed 路径，而 transposed 路径又写死从 Row4 读样品，导致数据读取不完整（陷阱 A：缺失微量元素列；陷阱 B：丢失前几行样品）。

**修复方案**——新增 `_detect_layout(ws)` 方法，不再单点判断，而是**统计 Row1（第2列起）和 Col A（第2行起）两轴上匹配 KNOWN_ELEMENTS 的数量**，取多者为元素轴。三种检测模式：

| 模式 | Row1 特征 | Col A 特征 | 判断依据 | 处理路径 |
|------|-----------|-----------|---------|---------|
| `wide` | B1起铺满元素名 | A1=Sample/空、A2起样品名 | Row1元素数>3 | `_load_wide()` ✅ |
| `standard` | Row1=样品名 | A2起元素名 | Col A元素数>3 | `_load_standard()` |
| `transposed` | Row1=元素名（旧格式带注释） | 混合/少 | 其他 | `_load_transposed()`（自适应起行） |

**修复细节**：

1. **新增 `_load_wide()`**：Row1=元素名横铺（A1=Sample/空）、Col A=样品名从 Row 2 起。自动跳过参考标准行（BCR, BHVO, AGV, GSP, SY, MRG, JB, JA, JG, JP, JR, NIM, SARM, DTS, PCC, W-2, DNC, BIR）。这是用户最常见的宽表格式，旧代码完全不被覆盖。

2. **修复 `_load_transposed()` 起始行**：旧代码写死 `range(4, ws.max_row + 1)`，跳过前3行。改为自 Row2 起向后扫描至 Row9，跳过空白行和标记行（元件/类别/单位等），直到找到含非空值的样品行。解决陷阱 B（样品行丢失）。

3. **新增 `_post_load_sanity_check()`**：wide 模式下自动校验——对比样品数 vs 文件行数、检查核心主量元素覆盖 >50%。非 wide 模式跳过避免误报。

4. **`KNOWN_ELEMENTS` 补全 `'Ti'`**：`KNOWN_ELEMENTS` 中缺少 `'Ti'`，导致合并后的 Excel 中 Ti (ppm) 微量元素列被跳过了读取。与 `TiO₂`（主量 wt%）是不同的两列——它们在合并后的文件中同时存在，图件按需取用各自的列。补上 `'Ti'` 后，CLS-29 / SRC-02 / SRC-12 / TEC-03 / TEC-04 / TEC-05 / TEC-14 这 7 张依赖 Ti (ppm) 的图不会再被跳过。

**验证结果**：4 种 Excel 格式（wide, standard, transposed, bypass）全部正确识别，5 个样品全读入，元素数 52~53，SiO2 值准确匹配。全量出图 46/47 张。

**故障诊断**：`print(gd._detected_mode)` 查看检测模式。如需强制指定路径，可在 `_load()` 中直接调用 `self._load_wide(ws)` 跳过检测。修改在 `igneous_wr/core/data.py`。

`GeochemData._load()` 判断格式的逻辑：
```python
r1_c2 = ws.cell(1, 2).value  # 第1行第2列
if r1_c2 in KNOWN_ELEMENTS: transposed = True
```

这意味着：**当你用 pandas 保存为标准格式（Row 1 = 元素名如 SiO2, Col A = 样品名）时，`r1_c2` = 'SiO2' 在 KNOWN_ELEMENTS 中，导致 `transposed = True`**。

**陷阱 A（已知 — 元素缺失）：** `_load_transposed` 从 Row 1 第 2 列起只匹配 KNOWN_ELEMENTS 列表里的元素（~42 个），文件中不属于 KNOWN_ELEMENTS 的元素列不会被读取。结果 Zr/Nb/Y/V/REE 等微量元素全部丢失。解决：确保数据文件格式时 Row 1 前 80 列全部在 KNOWN_ELEMENTS 中，或使用标准格式文件。

**陷阱 B（样品行丢失 — 2026-06-02 新发现）：** `_load_transposed` 写死从 `range(4, ws.max_row + 1)` 开始读样品（Column A）。但用户常见的 Excel 格式是：
```
Row 1: Sample | Al2O3 | Ba | CaO | ... （54列 — r1_c2=Al2O3触发transposed检测）
Row 2: 24TJ02-1 | 8.119 | 56.2 | 13.8 | ...
Row 3: 24TJ02-2 | 5.488 | 18.1 | 4.4 | ...
Row 4: 24TJ02-3 | 6.459 | 13.0 | 4.2 | ...
Row 5: 24TJ02-4 | 5.866 | 25.4 | 4.3 | ...
Row 6: 24TJ02-5 | 6.494 | 18.5 | 4.7 | ...
```
Row 4 开始读只能读到 24TJ02-3/-4/-5，Row 2-3 的 24TJ02-1/-2 被跳过。根本原因：`_load_transposed` 假设 Row 2-3 是类别/单位注释行，但许多 Excel 没有这些行，样品直接从 Row 2 开始。

**修复方法**：不要直接用含有"Row 1=元素名+Sample在A1"这种格式的文件喂给 GeochemData。建议：

**(a) 使用 bypass 文件**：建一个副本，把 A1 单元格改为一个非 Sample/非元素名的值（如 "NoMatch" 或 "Data"），这样 r1_c2 不会被 KNOWN_ELEMENTS 匹配，自动走标准格式路径。

**(b) 使用 final 格式文件（推荐）**：用 pandas 保存为标准格式（Col A=元素名, Row 1=样品名）：
```python
orig = pd.read_excel("24TJ02_with_Ti.xlsx")
# orig 格式: Row1=元素名(A1=Sample), ColA=样品名
df = orig.set_index('Sample').T.reset_index().rename(columns={'index': 'Element'})
df.to_excel("24TJ02_final.xlsx", index=False)
```

**(c) 直读模式���临时绕行）**：直接 openpyxl 读取后手动构造 GeochemData（设置 gd._elem_data, gd.all_labels, gd.labels, gd.idxs, gd._all_elem_data, gd._lithology 再调用 gd._init_groups()）。详见 session 2026-06-02 的 /tmp/plot_24tj02_v5.py。

**设计缺陷根源分析（2026-06-02 诊断）**：
检测逻辑只靠一个单元格（B1）判断文件格式，过于脆弱。用户的标准地球化学表布局是 A1=Sample, B1起铺元素名，这触发了 transposed 检测，但 transposed 路径又写死从 Row 4 读样品——两条路径都没能正确覆盖这种常见格式。根本改进方向参考 pyrolite 的做法：统计整行/整列的元素名匹配数做交叉验证，而非单点判断。目前未修（用户要求先看到图输出）。

**验证方法**：读取后检查 len(gd.all_labels) 是否等于实际样品数。如果只有 3 个但文件有 5 个样品，说明触发了陷阱 B。

**流程故障诊断**：当投图结果表现为"可出图但图数很少（14/47张）"或"总是缺同一组元素"，不应认为是投图引擎有问题，应首先怀疑数据读取管线。直接检查 gd.all_labels 和 gd.get('SiO2')。典型的脱节现���是：数据进了 Excel 读取，卡在格式识别环节走了错误的解析路径，导致投图引擎拿到的是残缺数据但仍在安静地出图，没有警告。前置检查：len(gd.all_labels) == 预期的样品数；len(gd._elem_data) == 预期的元素数；gd.get('SiO2') 不返回 NaN 或空数组。

### 快速测试

`scripts/generate_test_data.py` 生成 10 样品×41 元素的示例数据，配合以下代码完整验证出图：

```bash
cd ~/.hermes/skills/data-science/IgneousWR/scripts
python3 generate_test_data.py
python3 -c "
import sys; sys.path.insert(0, '.')
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir
set_out_dir('/tmp/test_output')
gd = GeochemData('/tmp/test_geochem_standard.xlsx')
result = plot_recommended(gd)
print(f'完成: {len(result)} 张')
"
```

验证重点：42+ 张图 + `report_YYYYMMDD.html` 在输出目录。元素齐全时仅跳过 Ti/Pb 依赖图（蛛网图/Pearce&Cann/Shervais 等 6 张图需要 Ti；蛛网图还需要 Pb）。

元素齐全时的预期结果（见 `quick_validate.py` 的 [14] 元素依赖完整性扫描）：
  - 68 张图出图成功，7 张跳过（仅因人造数据缺 Ti/Pb/MnO/P2O5）
  - `review_status` 分布：verified=24, experimental=26, needs_review=20, deprecated=0
  - 2 处代码vs注册表不一致（Shand/Jensen）：不影响功能，代码多读的元素仅用于背景着色
  - `known_elements` 中无 `Ti`（仅有 `TiO₂`）：6 张 Ti 依赖图无法用纯 TiO₂ 数据触发

| 问题 | 排查 |
|------|------|
| 读 Excel 报错 | 检查 4 行表头格式，元素名或单位行是否被当做数据 |
| 缺某些元素导致部分图跳过 | 检查合并 Excel 中元素列名（大小写、下标）。注意 Ti vs TiO₂ 问题详见 `references/migration-validation-20260527.md` |
| REE/蛛网图缺线 | 检查元素是否齐全，未标准化时自动跳过 |
| 散点不是圆形 | 确认 `scatter_samples` 中显式 `marker='o'`（`_style.py` v3+ 已内置） |
| 图像模糊 | `save_fig()` 默认 600 dpi，可在底部调整 |
| TAS x轴刻度异常 | matplotlib默认AutoLocator在xlim=(35,90)时会自动选择从30开始的5的倍数（30,35,40,...），导致**图上数据点位置正确，但x轴刻度标签的数值标注偏移了5个单位**——用户在图上看到Foidite左边界在x=35的位置但刻度标的是30，视觉上感觉"坐标错了"或"左边多了一截"。**修复：TAS等SiO₂分类图必须显式设置刻度** `ax.set_xticks(range(35, 95, 5))`。同理y轴 `ax.set_yticks(range(0, 19, 2))`。切勿改xlim去"匹配刻度"——xlim保持(35,90)不变，只修正刻度标签。|
| 新增三角图边界异常 | SVG 像素坐标映射到三元空间时精度不够，用文献坐标比反推更可靠 |
| 新增图注册后 quick_validate 报错 | 检查 `DIAGRAM_REGISTRY` 是否添加了记录，`whole_rock_core.py` 的 import 是否遗漏 |
| 修改后回归验证 | 运行 `python3 quick_validate.py --quick`（秒级，跳过出图，检查 import + registry 自洽性）。确认 registry 总张数（当前67）、mafic/felsic 计数合理且无文件名冲突。也可 `python3 batch_backgrounds_main.py --mode full` 验证全部 67 张底图可生成。 |
| SVG 提取的坐标点数量与预期不符 | 检查 class 属性：`class="polygons"` 使用多边形逻辑，`class="lines"` 使用折线逻辑，二者提取方法不同 |
| QAPFVolc SVG 路径全为 0pts | 该 SVG 为非标准格式（base64 或复合路径），需换用其他方法提取（如直接描点或查文献） |
| CLS-06 Co-Th 底图坐标严重错误 | `plot_co_th` 曾错误使用对数坐标（log-log），而 Hastie (2007) 原图为线性坐标。修复：去掉 `set_xscale('log')`/`set_yscale('log')`，Y 轴范围从 (1,500) 改为 (0,120)，X轴从 (0.1,50) 改为 (0,15)。分界线用 `axhline/axvline`（注意：应与同文件 CLS-02 风格统一，用 `ax.plot` 和彩色粗体标签更一致）。加区域标注文字（Tholeiitic / Calc-alkaline / High-K calc-alkaline）。 |
| `Ti` vs `TiO₂` 不一致导致图被跳过 | 6张图（SRC-02蛛网图、TEC-03 Ti-Zr-Y、TEC-04 四联、TEC-05 Ti-V、TEC-14 Pearce1982、SRC-12 Ti/Yb-Nb/Yb）在 registry 的 `needed` 中写了元素 `Ti`，但 `KNOWN_ELEMENTS` 中只有 `TiO₂`，缺少 `'Ti'` 条目。**用户实际数据中 Ti (ppm) 是微量元素，会在合并后的 Excel 中存在**（列名写为 `Ti`，值单位 ppm），只是因为不在 `KNOWN_ELEMENTS` 白名单中，数据读取时就被跳过了。与 `TiO₂`（主量元素，wt%）是两套独立数据——图件要什么就用什么，不需要换算。修复：在 `KNOWN_ELEMENTS` 中补上 `'Ti'`。代码中的 `gd.get('Ti')` 和 `gd.get('TiO2')` 各自取各自的数据，互不干涉。 |
| 代码实际使用元素 vs 注册表 needed 不一致 | `quick_validate.py --quick` 的元素依赖完整性扫描会检测到此类不一致。当前已知 2 处：`plot_shand` 代码多读 Nb/TiO₂/Y/Zr（着色用），`plot_jensen` 代码多读 CaO/K₂O/MnO/Na₂O（阳离子转换用）。不影响出图，但应留意。（注：这些与 FILENAME_MAP / _SHORT_TO_LONG 无关——`_quick_validate.py` 2026-06-05 重构后不再依赖这些已删除的映射。） |
| `_classification.py` 损坏/被覆盖 | 该文件历史上有两次被误写覆盖。恢复方法：从 `_tectonic.py` 中风格一致的函数做参考重写。注意先从 session_search 检查是否有可恢复的旧版本。当前文件位置：`igneous_wr/diagrams/_classification.py`。坐标数据在 `igneous_wr/boundaries/cls/*.json`。 |

### 设计原则与维护规范

### 核心设计理念

**Skill 的目标是让 AI 做完一切，人不参与中间步骤。** 用户提供数据，AI 负责：
- 数据读取与解析
- 参数选择（标准化方案、元素组合、岩性判定）
- 调用 Python 代码完成所有数值计算（标准化、比值、判据坐标、出图）
- 结果解读与报告生成

AI 不直接进行任何数值计算（标准化、比值、FeOt换算、坐标变换等）。这些已全部固化在 Python 代码中（`_chem.py`, `_normalize.py`, `_ternary.py`, `merge_excel.py` 及各 diagram 模块）。

### 架构演进 — 已完成

> **本 skill 已不是"一个绘图脚本"，应按"小型数据工程 + 绘图引擎"来构建。**

详细审阅全文见 `references/architecture-review-20260527.md`。

**全部已完成批次：**

核心原则：**外部 API 不变，内部结构换骨架。** `whole_rock_core.py` 继续保持为兼容门面。

1. ✅ **Batch 1**: 建包骨架 + 搬 4 个稳定底座
2. ✅ **Batch 2**: 搬注册表，新增 review 字段
3. ✅ **Batch 2.5**: 70 张图标记校正状态，旧内联注册表删除
4. ✅ **Batch 3**: `GeochemData`/Excel 读取迁移
5. ✅ **Batch 4**: 坐标外置，`_xy_diagrams.py` 拆散
6. ✅ **Batch 5 (完结)**: 绘图函数从 `whole_rock/diagrams/` 迁入 `igneous_wr/diagrams/`。旧包保留为备份，代码全部指向新包

**迁移教训（后续重构时参考）：**
- 旧文件改为 `sys.modules` 接管门面，所有 `from _chem import feot_calc` 原封不动可用
- 每步跑 `quick_validate.py --quick` 确认 registry 计数不变
- **一次搬完，不留半成品**。这个 skill 的架构迁移曾经"渐进搬了一半"整整两周，用户明确要求"一次搬完，进入新状态"——搬资源目录 + 改 import + 删旧目录三个步骤应一次完成，不做中间态

**长期待办（图幅管线）：**
`manifest.yaml` + batch runner + `qc.json`，每个图幅独立运行、独立日志、独立报告

### 关键约束

- **所有图表必须是纯 matplotlib 实现**：严禁引入 pyrolite。TAS 等多参数图已全部用 Python 底图重绘。
- **`GeochemData` 无 `.data` 属性**：`GeochemData` 属性为 `_elem_data`（原始数据 dict），`gd.get(element)` 为推荐访问方式。所有绘图函数中引用 `gd.data` 的调用会抛出 `AttributeError`。
- **新增图前检查 registry 重复**：同一物理图件不得重复注册。用 `grep "功能关键词" whole_rock_core.py` 确认。
- **图幅数据不进 skill 本体**：Skill 只放工具和规则。图幅数据归项目工作区(manifest.yaml + data/ + runs/)。
- **边界数据不硬编码（SVG 提取的数据存 JSON/YAML，函数只加载不硬编码）**：这是为了两个目的：(1) 改坐标时不需深入 1000+ 行的函数文件去搜 `np.array([...])`；(2) 避免 SVG 像素→三元空间的变换误差影响绘图函数本身。用户明确抱怨 `_classification.py` 1423 行太长、"不敢改"。**例外**：用户亲自逐点校准过的定稿版本（如 WF1977 v11）可直接硬编码，因已不再修改。

### 工程边界

| 层 | 负责 | 由谁做 |
|----|------|--------|
| 推理层 | 需求解析、参数选择、异常判断、结果判读 | AI |
| 调度层 | 图件选择、数据流编排 | AI + `recommended_diagrams()` |
| 计算层 | 标准化、比值、坐标变换、出图 | Python 代码 |
| 数据层 | 参考值常量、标准曲线坐标 | Python 代码 |

### 维护规范

1. 所有纯数值计算必须固化在 Python 代码中，不可让 AI 在对话中「算一下」。
2. 不留遗留债务：当用户要求修复某类问题时（如架构债务、数据不一致），必须一次性全部解决，不留下「已知但暂缓」的遗留项。如果用户指定范围按用户指定做；如果用户说「全部解决」则 grep 扫描所有相关位置后逐一清理。用户明确厌恶「这个问题留着以后再说」的处理方式。
3. 新增图件：写绘图函数 + 在 DIAGRAM_REGISTRY 加记录，无需修改 style.py。save_fig 自动从 registry 反查长名。
3. **新增边界坐标或图面标注**：写入 `igneous_wr/boundaries/{category}/{name}.json` 文件。绘图函数内用 `from igneous_wr.boundaries.core import load_boundary` 导入后调用 `load_boundary(category, name)`。图面标注信息（文字位置/颜色/样式、参考点坐标、比值射线、区域标签等）属于"图面数据"而非"绘图逻辑"，应一并外置。可根据图件类型自定义 JSON schema（lines/fill_regions/annotations/reference_points/rays/region_labels 等），不要求统一格式。
4. **新增标准化方案**：在 `_normalize.py` 加常数 + 在 `CHONDRITE`/`PRIMITIVE_MANTLE`/`N_MORB` 适当位置引用。
5. **不动"让人去跑脚本"的出口**。Skill 的入口对准 AI 调用，不对准用户手动运行。不要添加只给用户用的"计算器式"工具脚本。
6. **参数微调**（点大小、颜色、图例位置等）使用 `_style.py` 的常量覆盖机制，AI 不改 `_style.py` 核心逻辑。
7. **每次修改后运行 `python3 quick_validate.py --quick`**：秒级回归。确认 registry 总张数、依赖完整性、文件冲突。如涉及底图生成逻辑，运行 `python3 batch_backgrounds_main.py --mode full` 验证 68 张底图可完整生成。
8. **全量出图后核查三角图顶点标签位置** — 执行完全量出图后，抽查每个三角图的三个顶点标签是否符合文献标准。`label_ternary_vertices(ax, top, left, right)` 参数顺序易错：不要按文献叙述顺序传参，要按图中顶点物理布局传参。**AFM 标准布局 = F(顶)、A(左下)、M(右下)**。此规则同样适用于 `ternary_to_xy(top, left, right)` 的数据顺序。**改顶点顺序时，必须同步修改 3 处：**(1) `ternary_to_xy(top数据, left数据, right数据)` 的 arg 顺序、(2) `label_ternary_vertices(ax, top标签, left标签, right标签)` 的 arg 顺序、(3) 分界线坐标也在同一顶点空间内。三者中任一个不一致都会导致标签错位或分界线不可见。验证方法：打印 `ternary_to_xy` 计算出的边界线 xy 坐标，确认其在 `ax.set_xlim/ylim` 范围内可见再提交。

### Pitfalls

- ❌ 提议让用户手动跑脚本来完成计算 → 违背"AI 做完一切"原则
- ❌ AI 在对话中手算标准化值或比值 → 模型波动导致结果不一致
- ❌ 为了一次性需求写计算脚本 → 代码没复用，反而增加了维护负担
- ❌ **在 chat 中分多次用 write_file/heredoc 追加一个大 Python 文件** → 极易因中途中断（context 压缩、heredoc 中的 & / 特殊字符误解、子代理 timeout）导致文件损坏/不完整。**文件已被误写覆盖 3 次**（~800→329 bytes→77 行→目前正确）。正确做法：**使用 `execute_code` 一次性生成完整文件内容并写入**，或者用 `terminal` 调用一个独立的 Python 脚本（如 `/tmp/gen_cls.py`）完成文件编写。heredoc 中含有 `&` 或特殊符号时会失败。

- ✅ **从 SVG 提取的坐标已确认在 `/tmp/extracted_paths.json` 中可用**，像素→三元百分比转换用 `_pixel_to_ternary(px, py)` 公式，已验证通过。不再需要通过 pycache 恢复 _ternary.py 的旧版本。**从独立调试脚本迁移坐标到 JSON 的规范见 `references/debug-script-to-json-migration.md`**。
- ✅ **Git 版本控制**：`git init` 后在 `/home/twoper/.hermes/skills/data-science/IgneousWR/` 下管理（如有 skill 名变更注意 git mv + 重设 remote）。`.gitignore` 排除 `__pycache__/`、`*.png`、`whole_rock_output/`、`runs/`、`*_output/`。每次功能性修改后 `git commit`。

- ⚠️ 当遇到长时间任务（创建 33 个函数的文件、注册 29 条记录）时，**分多次 write_file 追加会因网络中断/context 压缩导致不完整**。明确教学：先写好全部内容的 Python 生成脚本，用 `execute_code` 一次性写入，或者用 `terminal` 运行独立脚本完成全部写入。如果用户中间说"继续"，说明正在分步执行——此时管理好 todo 状态，以单个 `execute_code` 调用写入尽可能完整的一块代码，而不是多步 write_file。

- ❌ **从 chat 历史中的旧文件内容恢复** — `session_search` 不会匹配到大文件的全部代码。恢复策略：从头参考风格一致的已实现函数重新编写。
- ❌ **从 SVG 提取的坐标直接硬编码到 Python 文件** → SVG 像素→三元坐标变换存在误差，后续对比文献原文边界线时难以修正。更好的做法：将 SVG 像素坐标保留在独立的 JSON 数据文件中，绘图函数从数据文件加载
- ❌ **用 `from X import *` 做模块门面** → `set_style()` 修改的是目标模块的变量，但门面模块的 import-time 拷贝不会同步。正确方案：用 `sys.modules[__name__] = _mod` 接管整个模块
- ❌ **在 `igneous_wr.diagrams._evolution` 等文件中使用 `feot_calc(gd)`（旧单参数签名）** → `feot_calc` 当前签名为 `feot_calc(feo, tfe2)`。正确调用：`feot_calc(gd.get('FeO'), gd.get('TFe2O3'))`。
- ❌ **在文件中保留死 import `from _chem import mol`** → `mol` 函数在 `_chem.py` 门面中不存在。
- ❌ **三角图顶点顺序（top/left/right）与 `ternary_to_xy` / `label_ternary_vertices` 参数不匹配** → 这两个函数的参数顺序都是 (top, left, right)。当更改顶点布局（如 AFM 从 A顶→F顶）时，必须同步更新：`ternary_to_xy(top_数据, left_数据, right_数据)`、`label_ternary_vertices(ax, top标签, left标签, right标签)`、以及边界线 koordinate 也在同一空间。三者中任一个与其它不一致都会导致标签错位、分界线画错或不可见。**验证方法：** 改完三角图顶点顺序后，先打印 `ternary_to_xy` 计算出的边界线 xy 坐标，确认其在 `ax.set_xlim/ylim` 范围内可见，再提交。
- ✅ **架构迁移原则（本 skill 历史教训）**：做迁移（搬文件、改目录、改 import）时，**一次搬完，不留中间态**。不要分多步执行——每步之间如果跨越实际日历时间，会因为文件引用不一致而停机。本 skill 的 `whole_rock/diagrams/`→`igneous_wr/diagrams/` 迁移和 `whole_rock/boundaries/`→`igneous_wr/boundaries/` 迁移，用户明确要求"一次搬完，进入新状态"。搬资源目录 + 改 import + 删旧目录三个步骤应一次完成，不保留备份目录做"安全网"——备份目录不再被引用又占空间，最终还要再删一遍。
- ✅ 遇到重复 3 次以上的计算模式 → 考虑固化到 Python 模块
- ✅ 参数选择有歧义时 → 列出选项让用户选，不替用户决定
- ✅ **批量出图循环中必须加 `plt.close('all')`**：遍历 68 张图时每张图调用 `plt.subplots()` 打开一个新 figure。如果不及时关闭，matplotlib 在第 20 张后弹出 `RuntimeWarning: More than 20 figures have been opened`。修复：在每次循环末尾调用 `plt.close('all')` 关闭当前 fig 以释放内存。
- ✅ **输出文件名自动补注册表编号前缀**：每个绘图函数内部调用 `_style.save_fig(fig, '短名.png', out_dir)`。实际保存时 `save_fig` 从 `DIAGRAM_REGISTRY` 自动反查带编号的长名。**新增图件时只需在 registry 加 `DiagramSpec` 记录**，不需要改 style.py。
- ✅ **新增图件时 source_ref key 要同步 refs.json**：注册表的 `source_ref` 字段现在是 key（如 `"lebas1992"`）而非字符串。新增图时：
  1. 如果图引用一篇 refs.json 中没有的文献，**先**加 refs.json 条目（short + full）
  2. **再**在 registry.py 中设置 `source_ref="newkey"`
  3. 不要图方便直接写字符串——下次 loader 解析会找不到。
  refs.json 和 registry.py::DiagramSpec.source_ref — 新增一张图需要同步 2 处（FILENAME_MAP 和 _SHORT_TO_LONG 已分别于 2026-06-05 和 2026-06-04 删除，改为从 DIAGRAM_REGISTRY 自动构建）。
- ❌ **SKILL.md 技术规范与 Python 代码不同步** — 当 patch SKILL.md 添加/修改了某个具体图件的技术规范（如分界线坐标、坐标轴范围、标注样式），且这次修改被写入了 SKILL.md 的 "底图质量规范" 节，必须同步检查并更新对应的 Python 绘图函数。否则下次出图时 SKILL.md 记载了已校正确认的版本，但代码仍然输出旧版。已知具体实例：K₂O–SiO₂ 分界线在 SKILL.md 中已按用户校正改为端点坐标法 `(45,0.5)→(75,2.5)` 等，但 `_classification.py` 中的 `plot_k2o_sio2()` 仍用旧斜率公式。

- ❌ **新增图前检查 DIAGRAM_REGISTRY 中是否有功能重复已经注册的函数**：将同类物理图件重复注册（如 CLS-02/24/29 三张 K₂O-SiO₂）→ 浪费维护成本。新增前用 `grep "Nb/Yb\\\\|Th/Yb\\\\|K2O.*SiO2" registry.py` 快速检索，确认同一作者/同一物理图件来源不重复注册。如果多个版本来自不同作者（如 Middlemost vs Peccerillo & Taylor），先确认用户是否需要保留多版本，再注册。
边界数据不硬编码（SVG 提取的数据存 JSON/YAML，函数只加载不硬编码）：改坐标时不需深入 1000+ 行的函数文件去搜 `np.array([...])`。用户明确抱怨 `_classification.py` 1423 行太长、"不敢改"。
- **边界外置不仅适用于多边形坐标——图面标注信息（文字位置/颜色/样式、参考点坐标、比值射线斜率、区域标签等）也应外置**：SRC-03 (Pearce 2008) 的 MORB-OIB 阵列参数、N-MORB/E-MORB/OIB 参考点坐标及偏移标注、Volcanic arc array 文字位置；Shervais 的 Ti/V 射线斜率和 ARC/OFB/WPB 区域标签；Miyashiro 的 TH/CA 分界线及标注等，现已全在 JSON 中。改文字内容、调标注位置、换参考点颜色，改 JSON 即可，不翻 Python 代码。
- 分界线坐标与画图逻辑混在同一个文件中的后果：`_classification.py` 曾是 1423 行，其中 ~50% 的字符属于坐标数组。用户明确表示"太长了，不敢改"。**已修复**：坐标数据外置到 `boundaries/` JSON 文件。后续新增图时，坐标数据应写入 `boundaries/{category}/{name}.json` 而非硬编码到函数体。

**架构清理陷阱（详见 `references/dev-notes/arch-import-chain-lessons.md`）：**

- ❌ commit message 声称的修改范围与实际 staging 不一致 — 全局替换后选择性 git add 易漏文件
- ❌ 函数体内的延迟 import 在顶层搜索中遗漏 — 必须覆盖全部代码深度
- ❌ docstring 中的 import 示例与删除 shim 后的 API 不同步
- ❌ import 修正与功能校正混合在同一批次中无法干净分离
- ✅ **所有图表必须是纯 matplotlib 实现，严禁引入 pyrolite**
- ✅ **TAS 等分类图的底图坐标来源必须严格对接 pyrolite 原始坐标**：Foidite 的 (35.00,9.00) 起始点看起来像"贴着 y 轴画线"，但 pyrolite 输出的就是 (35.00,9.00)。AI 不应凭视觉印象自行修改 pyrolite 提取的坐标——任何底图边界坐标的调整必须先从系统 pyrolite 提取对照坐标确认无误，再由用户确认。**「我感觉这个点不对」不是修改坐标的正当理由。**

- ⚠️ **用户对TAS底图的视觉判断标准非常严格**：即使坐标与pyrolite完全一致，用户仍可能认为底图"是错的"。**应对方式：不要解释"坐标来自pyrolite所以是对的"**，直接问用户具体哪里看起来不对，让用户明确指出来后再去修改。**TAS底图出问题的系统排查步骤**（按优先级执行）：\n  (1) 检查x轴刻度标签——matplotlib AutoLocator默认从30开始标，导致Foidite左边界x=35处标着30，用户视觉上觉得"左边多出一截"。→ `ax.set_xticks(range(35, 95, 5))` 修复。\n  (2) 检查y轴刻度标签——同理。\n  (3) 检查Foidite最左侧坐标(35,9)是否贴在x=35的轴线上——这是pyrolite原始坐标，但如果用户说"左边变成了一条直线边"，回答：这是pyrolite原始设计，Foidite最左点在x=35处，需要我微调xlim让它离开轴线吗？\n  (4) 检查matplotlib版本是否低于3.7——polygon渲染差异会改变底图观感。\n  (5) 用系统pyrolite生成参考图对比底图（仅对比底图，不绕过_style.py的输出机制）。**不要做的事**：不改xlim去适配刻度、不改pyrolite原始坐标、不换色块填充方案。|
- ✅ 做重大架构变更前先读 `references/architecture-review-20260527.md`：用户审阅明确给出了架构方向、风险清单、中远期路径。新增图、拆包、加新功能前必须参照，避免偏离已共识的方向。：用户审阅明确给出了架构方向、风险清单、中远期路径。新增图、拆包、加新功能前必须参照，避免偏离已共识的方向。
- ✅ **每次修改后运行 `python3 quick_validate.py --quick`**：秒级回归。检查 registry 总张数、依赖完整性、文件冲突。完整模式确认出图正常后再 commit。
- ✅ **每批迁移前确保工作区干净**：`git status --short` 应为空或仅含当前批的预期文件。上一个批次的文档尾巴（uncommitted 的 mdocs、新 references/ 文件）必须在开始新批前全部提交。混合批次的 diff 会阻塞回滚。用户明确说"我不建议立刻做 Batch 3"就是因为 SKILL.md 和 references/ 未提交 + `whole_rock_core.py` 旧内联注册表残留。

### 渐进迁移陷阱（2026-05-27 实际踩坑记录）

**`import → 内联定义覆盖` 陷阱（Batch 2 关键教训）**

`whole_rock_core.py` 中先 `from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY`，但 200 行后有 `DIAGRAM_REGISTRY = [...]` 内联定义覆盖了 import 版本。结果 `from whole_rock_core import DIAGRAM_REGISTRY` 拿到的是旧内联版本（无 review_status 字段）。

**根因**：Python 中模块顶层变量定义（即使在后）会覆盖先执行的 import 绑定。`import` 执行了，但被同一模块的同名赋值覆盖。

**验证方法**：检查 `DIAGRAM_REGISTRY[0]` 是否有新增字段（如 `review_status`）。有则来自新包，无则仍在使用旧内联版本。

**修复方案**：删除内联定义，只保留 import（全量通过 `re-export` 实现向后兼容）。不要只 patch import 语句而不删除旧定义。

**门面模块的 sys.modules 接管模式**

`from X import *` 做门面时有变量隔离问题：`set_style()` 修改的是目标模块的变量，但门面模块的 import-time 拷贝不会同步。正确方案：

```python
"""_style.py — 兼容门面"""
import sys
_mod = sys.modules.get('igneous_wr.report.style')
if _mod is None:
    import igneous_wr.report.style as _mod
_mod.__dict__['__name__'] = __name__
sys.modules[__name__] = _mod
```

### 底图质量规范（2026-05-27 用户校正确立）

以下标准适用于所有 CLS 系列分类底图：

#### K₂O–SiO₂（CLS-02）
- **分界线（Middlemost 1975 / Le Maitre et al. 2002, Fig. 4.4）：**
  - Low-K / Medium-K: `(45, 0.5)` → `(75, 2.5)` 黑色实线
  - Medium-K / High-K: `(50, 1.5)` → `(75, 4.0)` 黑色虚线
  - High-K / Shoshonitic: `(55, 2.5)` → `(75, 6.0)` 黑色点划线
- **不要用斜率公式通线性归零**（如 `y = 0.025*x - 2.0`），那会使所有界线从 K₂O=0 的 X 轴出发，与地质事实不符
- **去网格**：分类图不需要网格线
- **刻度向内**：`tick_params(direction='in', top=True, right=True)`
- **四色背景区域填充**：Low-K 淡黄、Medium-K 淡绿、High-K 淡蓝、Shoshonitic 淡粉
- 区域标注用英文：Low-K Tholeiitic / Medium-K Calc-alkaline / High-K Calc-alkaline / Shoshonitic

#### AFM（CLS-03）
- **分界线（Irvine & Baragar 1971）：** 18 点精确坐标曲线，数据格式为三元百分比（%A=F%, %B=A%, %C=M%）
- 分界线数据独立存放在函数体内，不抽离为外部文件（用户逐点校准版可直接硬编码）
- **区域填充：** Tholeiitic（淡粉，分界线上方）、Calc-Alkaline（淡蓝，分界线下方）
- 堆积顺序：区域填充 zorder=1 在底，分界线 zorder=3 在上，标注 zorder=4，散点 zorder=5

#### Shand A/CNK–A/NK（CLS-04）
- 三根分界线：垂直线 A/CNK=1、水平线 A/NK=1、对角线 1:1
- 三色区域填充：Metaluminous（淡绿左上）、Peraluminous（淡蓝右上）、Peralkaline（淡粉下方）
- **标注用英文**（Matplotlib 默认字体不含中文，WSL 环境中文缺失引发 Glyph missing warning）

#### Frost Fe-number vs SiO₂（CLS-17）
- **分界线（Frost et al. 2001）：**
  - Y=0.8 水平虚线：Ferroan/Magnesian 主分界线
  - X=56 灰色点线：适用起始 SiO₂ 含量界线
- **不可出现的冗余界线：**
  - **Y=0.6 水平线**属于 Irvine & Baragar (1971) Tholeiitic/Calc-alkaline 判别体系，与 Frost 的 Ferroan/Magnesian 体系不同，严禁画在同一张图上
  - **X=71 垂直线**同样不是 Frost 原文中的界线
- **背景色填充：** Ferroan（淡粉 #ffcccc, alpha=0.20）在上方，Magnesian（淡蓝 #cce5ff, alpha=0.20）在下方
- **场域标签：** Ferroan 红色粗体 (#cc3333)，Magnesian 蓝色粗体 (#3366cc)
- **引用 imprint：** 右下角 "After Frost et al. (2001)" 灰色斜体

#### 通用规范
- 分类图不要网格线 → `ax.grid(False)` 必须在 `_style.style_ax()` **之后**调用（style_ax 默认开网格）
- 刻度向内；封闭四边边框
- 中文字体在 WSL 默认 matplotlib 中不可用 → 所有标注用英文
- 除背景填充外，投点/图例/标签等要素应保持在正确 zorder 以确保可见性

#### SRC 图件质量规范（适用于 SRC-03 等 Pearce 系列比值图）

这些图与 CLS 分类图不同，主要是双对数散点图 + 参考阵列/参考线，而非多边形区域填充：

- **具体实现以 GCDkit 源码为准**：SRC-03 (Pearce 2008 Th/Yb-Nb/Yb) 现已按 GCDkit 6.3.0 精确底图实现——淡蓝半透明背景填充多边形 + 单根灰色虚线 MORB-OIB 阵列线，而非早期 AI 猜测的平行对角线带。修改前先查 `references/pearce-thyb-nbyb-spec.md` 确认当前实现方式。
- **参考点用方块标注**：N-MORB(蓝)、E-MORB(绿)、OIB(橙)
- **参考点 ppm 值来源**：必须从 GCDkit `reservoirs.data` 严格计算（S&M 1989），而非 Pearce (2008) 印刷图中的近似值
- **不要添加 GCDkit 底图没有的元素**：如 UCC 端元、1:1 参考线、俯冲方向箭头——这些是早期 AI 添加的，已被用户明确否决
- **异于 CLS 的设计**：这些图不��要多边形区域填充（除背景底图本身外），不需要像 CLS-02 那样的四色分类区
- **引用 imprint**：标注 "After Pearce (2008)" 灰色斜体，右下角

#### 三元图底图规范（适用于 CLS-09/10/11/12 等 SVG 提取的三角图）
- **顶点标签化学式规范**：数字必须下标（如 `TiO₂`、`P₂O₅`、`MnO`），不要写 `TiO2`、`P2O5`
- **坐标值与坐标系的分离规则**：当调试脚本使用与最终图件不同的数据列序（如脚本按 (MnO×10, TiO₂, P₂O₅×10) 排列但目标图坐标系是顶角=TiO₂、左下=MnO×10、右下=P₂O₅×10），需要**只交换端点数值的列顺序**，绝对不动三元坐标系（顶点标签映射）。典型操作：`points_old = {'A': (23, 77, 0)}  # (MnO, Ti, P) → points_new['A'] = (77, 23, 0)  # (Ti, Mn, P)`，然后传入 `ternary_to_xy(Ti, Mn, P)` 让顶点按 (top=Ti, left=Mn, right=P) 自然映射。三元坐标系的顶点标签布局是最终图件的规范，不受中间数据格式的干扰——数据应当迁就坐标系，而不是坐标系迁就数据格式。**错误的做法**：把顶点标签对调（把顶角从TiO₂改成MnO×10），用户会明确指出"没让你动坐标系"。
- **系数表达规范**：使用 `10×MnO` 或 `10×MnO (wt.%)`，不要写 `10MnO`（后者易被误解为"10倍的MnO含量"）。乘号用 Unicode `×` (U+00D7) 而非 `x` 或 LaTeX `\\times`（后者在 matplotlib text 渲染中会触发 ParseFatalException）
- **场域文字标注**：每条分界线围成的区内必须有对应的场域名称（如 IAT / MORB / WPB / CAB），不能只有界线无标签
- **引用文献 imprint**：在 figure 底部或图注中包含 "After [Author], [Year]"
- **背景色填充**：各场域用淡色填充（alpha=0.20），颜色参照 Cabanis 风格（橙/蓝/绿/粉）
- **场域标签颜色应与填充区域匹配**：区域文字标签用与该场域填充色同色系的粗体颜色，而非统一灰色
- 坐标轴标签（top/left/right）字号不小于 10pt，场域标注 8-9pt 彩色粗体，置于场内不压界线

#### 修改单图时的风格对齐检查
- 当需要修改某个具体绘图函数时（如修复坐标、加标注、调颜色），**必须先阅读同文件中相同类型的图**，确认其标注风格（字体大小、颜色、权重、是否填充背景等），再按该风格修改，而不是自行 invent 一份新风格
- 具体地：`_classification.py` 内所有图都应参照 CLS-02（K₂O-SiO₂）的风格——彩色粗体场域标签 + 填充色 + 不同线型
- 不要引入 axhline/axvline 替代 ax.plot 保持模块内写法统一
- 如果不确定风格，优先问用户，不要自己猜
- **典型失败案例**：本 skill 的 CLS-06 (Co-Th) 修复时，用了 `axhline/axvline` + `fontsize=9, fontstyle='italic', alpha=0.7` 的通用注解样式，而同一文件中的 CLS-02 已明确使用 `ax.plot` + 彩色粗体 (`color='#xxx', fontweight='bold'`) + 背景色填充。修复时必须走一遍同文件风格扫描再动笔。
- **重复注册修复经验**：CLS-06（`_classification.py`中的`plot_co_th`）和CLS-25（`_tectonic.py`中的`plot_hastie`）是同一物理图件（Hastie 2007 Co-Th）的不同实现版本，都含有错误。修复方案：保留CLS-06并用文献精确坐标重写，删除CLS-25（包括registry记录、模块import）。删除重复图件时，需检查4处：1) registry.py的DiagramSpec；2) registry.py的import；3) igneous_wr_core.py的import；4) 被删除的绘图函数所在文件。任意一处遗漏都会导致import错误。删除后quick_validate总张数减少1。

### 图件手动校正流程

当用户开始逐张校正底图时，遵循此流程：

1. **打基线 tag**：开始校正前 `git tag -f calibration-baseline`，确保任何修改可回退
2. **加 `.gitattributes`**：`*.py text eol=lf` 等消除 LF/CRLF 噪音，避免 diff 污染
3. **出 review card**：对于每张图，输出简洁的结构化评估（边界线类型/分类区/坐标范围/输出文件名/需要确认的要点清单）
4. **用户确认后更新 registry**：修改 `registry.py` 中的 `review_status`, `source_ref`, `review_note`
5. **每 1-3 张图一个独立 commit**：commit message 写明具体修改内容和 source_ref
6. **校正期间暂停 Batch 3**：数据入口一动样品点位可能变化，会污染人工校正判断

review card 格式示例（对用户输出时保持简洁，不要塞满代码）：

```
[图名] Review Card
边界线: <描述>
分类区/标签: <描述>
坐标范围: <X范围, Y范围>
输出文件名: <xxx.png>
需要你确认:
  1. <问题1>
  2. <问题2>
```

#### 用户提供专家审查的图件校正模式（两类输入）

A型（纠错型）：用户以"资深岩石地球化学专家与SCI期刊制图编辑"身份提供每张图的详细审查报告。
B型（参数交付型）：用户提供自称为"最终严谨版/最终版"的独立参数文档，包含原始ppm数据+计算比值+地质意义解释。

两类通用处理原则（适用于A和B）：
1. 用户说的话直接按字面执行，不重新推导、不查文献验证、不质疑
2. 审查报告中的 Python 代码块通常不可用——AI生成的审查报告中嵌入的代码示例使用的是不存在的库。只有文字结论（边界坐标对、比值取值范围、分割线端点）是实际有用的

B型（参数交付型）特殊规则：
- 用户已完成了全部ppm→比值计算和文献核对，Agent不应重复验证
- 用户提供了原始ppm值和计算比值的对照表，应以计算比值为准
- "代码复现建议"节直接按字面执行
- 如果用户注明了"不要教育我"，就只做代码修改，不加解释（2026-05-27 确立）

Agent 需遵循此协作模式：

1. **用户发 review** → Agent **不要解释/辩解**，直接去读当前代码确认问题
2. **读代码确认** → 理解审查报告的每条错误诊断
3. **按审查规格改代码** → 用 patch 做精准替换，不要全部重写已有代码中正确的部分
4. **重新生成单图验证** → 用 `batch_backgrounds_main.py --mode minimal` 或直接调用函数
5. **如果审查报告包含精确坐标** → 直接硬编码到函数体重写分界线

**重要：审查报告中的 Python 代码块通常不可用。** AI 生成的审查报告中嵌入的 Python 代码示例使用的是不存在的库（如 `import ternary`）、虚假坐标、与代码库不兼容的 API（参数签名、类方法名、渲染逻辑均不同）。只有审查报告中的**文字结论**（边界坐标对、比值取值范围、分类名称、分割线端点）是实际有用的。代码块应忽略。

**关键禁忌：**
- 不要解释"为什么旧代码这样写"——用户不需要听理由
- 不要尝试用旧代码逻辑解释问题——直接按审查报告方案改
- 如果审查报告说"禁止斜率公式归零"，就**删除**所有斜率公式，用端点坐标法
- 如果审查报告说"颜色区域填充"，直接加 `ax.fill()` 多边形，不做"先改好线再看"
- 如果审查报告提到"刻度向内/去网格/线型区分"等排版规范，一次性处理完，不分开做
- **审查报告可能误判图件类型**：AI 审查报告可能将 O'Connor 标准矿物分类图误判为矿物学长石分类图。确认 registry 记录的图件类型和来源文献后按图纸源类型修正，不必完全接受审查报告的"用途不匹配"投诉。但审查报告中的排版规范（刻度大小、外框线宽、顶点标签完整性）是通用的，仍需采纳。
- **修改单图时不要自行引入新风格**：用户明确说"你最后去整合风格"。在用户提供逐张审查报告的校正模式下，Agent 应只做审查指出的功能/坐标/标注修正，**不要同时自作主张翻新风格**（字体/颜色/线型/标注位置等）。风格统一应作为独立的工作阶段，用户定标准后一次性执行。如果有多张图需要修复，先批量修完功能问题，风格问题留给后续统一处理。

### 数据来源验证（2026-06-02 新增）

当需要验证两份独立 Excel 文件中的主量元素数据**是否为同一套去LOI归一化版本**时，参考 `references/data-verification-loicorrection.md`。

典型场景：
- 单独的 MT 主量文件 vs 合并后的 MT 主微量文件
- 需要确定合并文件中的主量是原始数据还是去LOI版
- 验证方法：两步验证（TOTAL检查 + 氧化物比值对比 + LOI列检查）

### 数据表格输出

除了出图外，用户有时需要将地球化学数据输出为排版整洁的 Excel 表格。完整流程和实现代码见 `references/geochem-table-formatting.md`。核心要点：

- **用户偏好布局**：元素在行、样品在列；分节（主量/主量参数/微量/微量元素比值）；蓝色表头
- **结构顺序**：主量元素 → 主量参数（紧跟在主量下面）→ 微量元素（标准地化序）→ 微量元素比值（紧跟在微量下面）
- **K(ppm) 和 Al(ppm) 不是微量元素**，不应放在微量区域
- **低于检出限用原始文本表达**（如 `<0.00`），不填0也不填½DL除非用户明确指示
- **自动计算比值**：主量参数6个（Na₂O+K₂O, K₂O/Na₂O, Mg# molar, A/CNK, A/NK, K₂O/Al₂O₃）+ 微量元素比值4组26个（REE参数、HFSE比值、LILE比值、过渡金属比值）
- **不同精度**：主量2位、REE比值2位、Eu/Eu* 3位、Rb/Sr 4位、K/Rb 1位、Nb/Y 3位等
- 使用 openpyxl 从头构建，而非修改已有 Excel，避免格式冲突
- 参考 `_chem.py` 中的 `mg_number(mode='molar')` 计算 Mg#，`calc_A_CNK()` 计算 A/CNK/A/NK

#### 已完成的 CLS 图件系统校正

| 图号 | 图名 | 日期 | 修正内容 | 参考文件 |
|------|------|------|---------|---------|
| SRC-03 | Pearce Th/Yb-Nb/Yb | 2026-07-17 ✅ | 整函数重写：从 Th/Nb=0.04/0.14 平行对角线改为 GCDkit 6.3.0 底图——淡蓝填充多边形 + 虚线MORB-OIB阵列(斜率1.0196经过Nb/Yb=0.8,Th/Yb=10)；参考点从近似值(N-MORB=0.98/E-MORB=4.30/OIB=26.67)改为 GCDkit reservoirs.data 精确计算值(N-MORB=0.764/E-MORB=3.502/OIB=22.222)；移除UCC/1:1/SZ箭头；参考点标记从星号改为方块；背景从淡黄变为淡蓝透明 | `_source.py::plot_pearce_2008` |
| CLS-13 | TAS Middlemost 1994 Plutonic | 2026-07-02 ✅ | 整函数重写：原来只有3条假线（y=0.07x-1.8等）→ GCDkit 6.3.0 精确坐标，16主多边形+2叠加层(Tawite/Quartzolite)，去重边绘制，JSON 边界文件外置 | `igneous_wr/boundaries/cls/tas_middlemost_plut.json` |
| CLS-02 | K₂O–SiO₂ | 2026-05-27 | 斜率归零→端点坐标法；四色填充；去网格 | `references/k2o-sio2-middlemost-spec.md` |
| CLS-03 | AFM | 2026-05-27 | 5点粗线→18点精确曲线；Th/CA颜色分区 | `references/afm-18point-boundary.md` |
| CLS-04 | Shand | 2026-05-27 | 虚线框架→三分区三界线；英文标注 | `references/shand-spec.md` |
| CLS-06 | Co-Th Hastie | 2026-06-10→重写 | X=Co,Y=Th,据Hastie(2007) Figure 7四条直线分界线端点坐标：IAT/CA=(70,0.245)→(0,1.35), CA/HK-SHO=(70,2.2)→(0,9)；B-BA/A=(38.4,0.01)→(24,100), BA/A-D/R=(23,0.01)→(7,100)。三色背景填充(IAT淡粉/CA淡蓝/HK-SHO淡绿)。同时显示岩浆系列+岩性分类。删除_tectonic.py中的plot_hastie重复函数，仅保留_classification.py中的plot_co_th。 | |
| CLS-07 | An-Ab-Or O'Connor | 2026-05-27 | 空框架→7条O'Connor界线+8色区+花岗岩类命名 | `references/an-ab-or-oconnor-spec.md` |
| CLS-08 | QAP Streckeisen | 2026-05-27 | 空框架→Q等值线+A/(A+P)射线+16区命名+P+F→P | `references/qap-streckeisen-spec.md` |
| CLS-09 | Cabanis La/10-Y/15-Nb/8 | 2026-05-27 | 空框架→WPB/IAB/MORB 3色区+场域标注（精度受限） | |
| CLS-10 | Mullen TiO₂-10×MnO-10×P₂O₅ | 2026-07-13 ✅ | 6个场域标签位置从随意三元值修正为 GCDkit Mullen.r 源码精确坐标（OIT/IAT/MORB/CAB/OIA/Bon 全部用 GCDkit text 元素位置反算）；Bon 拼写 BON→Bon | |
| CLS-11 | Jensen Al+Fe³⁺+Ti–Mg+Fe²⁺+Mn–Ca+Na+K | 2026-06-10 | 端元校正（wt%氧化物→阳离子数）；4色区+Komatiitic/Tholeiitic/Calc-alkaline标注 | |\n| CLS-12 | O'Connor Volc An-Ab-Or | 2026-06-10 | 空框架→8色区+8类岩石标注(Anorthite至Syenogranite)+长顶点名 | |\n| CLS-17 | Frost Fe-number vs SiO₂ | 2026-05-28 | 删除Y=0.6/X=71多余界线（属于I&B体系非Frost原文）；加色区填充+引用 | |
| CLS-17/EVO-03 | 两张底图风格同步 | 2026-06-10 | CLS-17: 背景色填充+引用; EVO-03: Y轴改为"Mg# (molar)"、Mg#=50粗虚线、加SiO₂岩类参考垂直线+填充 | |
| CLS-02/24/29 | K₂O-SiO₂ 系列图去重 | 2026-06-10 | CLS-02更正为Middlemost 1985; 删除CLS-24 (Muller 1992)和CLS-29 (P&T 1976); registry 70→68条 | |
| DIAGRAM_REGISTRY 重排 | 核心图提前 | 2026-05-28 | 核心图移到每类前部: CLS前5(TAS/K₂O/AFM/Shand/WF1977), SRC前3(REE/蛛网/Pearce2008), EVO前2(Harker/Mg#), TEC前5(Shervais/Meschede/Wood/PearceGranite/Harris) | |\n\n### 用户交互风格

- **先做后问**：当可以用现有工具直接查出答案时，不要反问用户。只有真正有歧义且无法从现有数据推断时，才简短确认。
- **不要教育用户**：用户清楚自己要什么，Agent 是执行工具。解释只讲思路和操作步骤，不试图"教学"。
- **规划/决策会议时**：用户说"我先想一下"时安静等待。不主动提问、不执行命令、不读文件——直到用户说"开始"。
- **用户批复时间可能较长**，耐心等待，不催促。

## 相关技能

- `geochemical-plotting` → `whole-rock-geochemistry` → `igneous-geochemistry` → `IgneousWR`（更名历史：2026-05-26 `igneous-geochemistry` 重命名为 `IgneousWR`，详见 `references/rename-history.md`。原目录 `/home/twoper/.hermes/skills/data-science/igneous-geochemistry/` 如无子技能依赖可删除。）
- `igneouswr-gcd`：兄弟工程，相同架构但图件数据全部来自 GCDkit 6.3.0 R 源码翻译。两套图件可互相验证。开发/维护时参照 `references/gcdkit-brother-project.md` 了解两工程的分工协作约定。

- 含 `winchester-floyd-boundary-data` 的分界线数据（`references/winchester-floyd-boundary-data.md`）
- Pearce (1996) 对 WF1977 的修改说明（`references/pearce1996-wf1977-modification.md`）—— 区别包括 Y 轴从 Zr/TiO₂×0.0001 改为 Zr/TiO₂、范围从 0.001~1 改为 10~1000、亚碱性/碱性分界线从垂直线改为正斜率对角线
