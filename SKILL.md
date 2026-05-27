---
name: igneous-geochemistry
description: 岩浆岩全岩地球化学数据处理与图解绘制 — 读取 Excel 数据 → 30种专业图件 + HTML报告
---

# 岩浆岩全岩地球化学技能（Igneous Geochemistry）

自动化全岩地球化学数据处理与图解绘制。读取合并后的 Excel 数据，自动判断岩性，一站式完成 TAS、REE、蛛网图、Harker 等 50+ 种专业图件（含分类/源区/演化/构造判别），并生成自包含 HTML 图集报告。

## 快速开始

```bash
# 1. 载入模块
cd ~/.hermes/skills/data-science/igneous-geochemistry/scripts
python -c "
import sys; sys.path.insert(0, '.')
from whole_rock_core import *

# 2. 读取数据
gd = GeochemData('/path/to/merged_geochemistry.xlsx')

# 3. 一键出所有推荐图
result = plot_recommended(gd)
"
```

输出目录：默认 `../runs/default/`（相对于 scripts/ 目录，不在 skill 目录内），含 PNG 图和 `report_YYYYMMDD.html`。可用 `set_out_dir('/path/to/runs/myproject')` 自定义。

## 渐进迁移 — 架构转换中

当前处于 medium-term 拆包中（详见 `references/architecture-review-20260527.md`）。`igneous_geochem/` 新包骨架已建，4 个稳定底座已迁移：

- `core/chem.py` ← `_chem.py`
- `core/normalize.py` ← `_normalize.py`
- `core/ternary.py` ← `_ternary.py`
- `report/style.py` ← `_style.py`

旧文件通过 `sys.modules` 接管门面保持旧入口兼容。每次迁移前确认 `quick_validate.py --quick` 全部通过、registry 计数不变。

**Batch 4（坐标外置）完成**：`_classification.py` 和 `_tectonic.py` 的模块级坐标数组已外置到 `boundaries/{category}/{name}.json`。`_xy_diagrams.py` 已拆散，32 个函数重新分配到 4 个目标文件。详见下方「坐标外置规范」和「目录结构」节。

RockPlot SVG 数据提取自 `D:\\RockPlot\\resources\\app.asar`，用 `npx asar extract` 解包在 `/tmp/rockplot-extract/`，每个图解有独立的 SVG 文件。SVG 中的边界路径以 `class="lines"`（部分图为 `class="polygons"`）标识，三角形框架为 4 点闭合路径。坐标映射需将 SVG 像素坐标 (0~607.37, 0~526) 和 tick 标签对应回数据空间。详见 `references/svg-boundary-extraction.md`。

## 功能总览

### 1. 数据处理（whole_rock_core.py）

| 功能 | 说明 |
|------|------|
| `GeochemData(path)` | 读取标准化 Excel（4 行表头 + 数据），自动解析检测限 |
| `read_excel(path)` | 替代 `GeochemData` 的底层函数 |
| `recommended_diagrams(gd, rock_type='auto')` | 判断岩性 → 返回可用图件列表 |
| `plot_recommended(gd)` | 一键出所有推荐图 + 生成 HTML 报告 |
| `normalize(data_dict, ref)` | 按参考值标准化（CHONDRITE / PRIMITIVE_MANTLE） |
| `set_style_preset(name)` | 切换风格预设（'lithos', 'nature', 'gca'） |

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

### 3. 图解目录（70 种，按用途分为 4 类 + 编号）

每张图对应输出文件名为 `PREFIX-NN_DescriptiveName.png`：
- **CLS** = 岩石系列/分类（29 张）
- **SRC** = 源区性质（15 张）
- **EVO** = 岩浆演化过程（6 张）
- **TEC** = 构造环境判别（20 张）

> **注意**：`plot_pearce1996`（Pearce 1996 Th/Yb–Nb/Yb）已移除（与 `_source.py` 的 `plot_pearce_2008` 功能重叠，后者更精细）。统一使用 `plot_pearce_2008`。三个 Zr/Y–Zr 图（`pearcenorry`, `pearce1982`, `zr_y_zr`）判据不同，全部保留并在 registry 中用 desc 标注区分。

#### 📋 岩石系列 / 分类（CLS，29 张）

| 编号 | 文件名 | 图件 | 所需元素 |
|------|--------|------|---------|
| CLS-01 | TAS.png | TAS 全碱-硅分类图 | SiO₂, Na₂O, K₂O |
| CLS-02 | K2O_SiO2_PT76.png | K₂O–SiO₂ 钾系列分类图 | SiO₂, K₂O |
| CLS-03 | AFM_IB1971.png | AFM 钙碱性-拉斑系列判别 | Na₂O, K₂O, MgO |
| CLS-04 | Shand_ACNK_ANK.png | Shand A/CNK–A/NK 铝质分类图 | Al₂O₃, CaO, Na₂O, K₂O |
| CLS-05 | Winchester_Floyd1977_NbY_ZrTiO2.png | W&F Zr/TiO₂–Nb/Y 分类图 | Zr, TiO₂, Nb, Y |
| CLS-06 | Co_Th_Hastie2007.png | Co-Th (Hastie) 系列判别图 | Co, Th |
| CLS-07 | An_Ab_Or_OConnor1965.png | An-Ab-Or 斜长石三元图 | Na₂O, K₂O, CaO |
| CLS-08 | QAPF_Streckeisen1976.png | Q-A-PF 深成岩分类三元图 | SiO₂, Na₂O, K₂O, CaO, Al₂O₃ |
| CLS-09 | Cabanis1986_LaY_Nb_ternary.png | Cabanis La/10-Y/15-Nb/8 基性岩三角图 | La, Y, Nb |
| CLS-10 | Mullen1983_TiO2_MnO_P2O5.png | Mullen TiO₂-10×MnO-10×P₂O₅ 基性岩三角图（已校正：4色区+IAT/MORB/OIT/OIA+CAB字段+化学式下标乘号） | TiO₂, MnO, P₂O₅ |
| CLS-11 | Jensen1976_cation_ternary.png | Jensen Al+Fe³⁺+Ti–Mg+Fe²⁺+Mn–Ca+Na+K 阳离子分类三角图（已校正：氧化物体积比例→阳离子数、四色区+岩类标注） | Al₂O₃, FeO/TFe₂O₃, TiO₂, MgO, MnO, CaO, Na₂O, K₂O |
| CLS-12 | OConnor_Volc_An_Ab_Or.png | O'Connor An-Ab-Or 火山岩三角图（已校正：8色区+8类岩性标注） | Na₂O, K₂O, CaO |
| CLS-13 | TAS_Middlemost1994_Plutonic.png | TAS 深成岩分类（Middlemost 1994） | SiO₂, Na₂O, K₂O |
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
| CLS-24 | Muller1992_K2O_SiO2.png | Muller K₂O–SiO₂ 岩浆系列判别 | SiO₂, K₂O |
| CLS-25 | Hastie2007_Th_Co.png | Hastie Th–Co 弧岩浆系列分类 | Th, Co |
| CLS-26 | LaRoche1980_R1_R2_plutonic.png | La Roche R1-R2 侵入岩分类图 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| CLS-27 | LaRoche1980_R1_R2_volcanic.png | La Roche R1-R2 火山岩分类图 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ |
| CLS-28 | Middlemost1991_Plutonic.png | Middlemost Na₂O+K₂O–SiO₂ 深成岩分类 | SiO₂, Na₂O, K₂O |
| CLS-29 | Peccerillo_Taylor1976_K2O_SiO2.png | Peccerillo & Taylor K₂O–SiO₂ 系列判别 | SiO₂, K₂O |

#### 🔬 源区性质（SRC，15 张）

| 编号 | 文件名 | 图件 | 所需元素 |
|------|--------|------|---------|
| SRC-01 | REE_chondrite.png | REE 球粒陨石标准化配分图 | La–Lu 14 个 REE |
| SRC-02 | Spider_PM.png | 原始地幔标准化蛛网图 | Rb–Lu 26 个元素 |
| SRC-03 | Pearce2008_ThYb_NbYb.png | Pearce Th/Yb–Nb/Yb 源区判别 | Th, Nb, Yb |
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

**不含 pyrolite（已全部移除）。所有图表（包括 TAS）均为纯 matplotlib 实现，无需额外依赖。**

Times New Roman 字体（期刊风格需要）：
```bash
# WSL + Windows 字体
cp /mnt/c/Windows/Fonts/times.ttf ~/.fonts/
```

## 技能目录结构

```
scripts/
├── whole_rock_core.py      # 门面 API（统一入口 + re-export）
├── _style.py               # 样式/字体/配色/投点/保存/HTML报告
├── _normalize.py           # 标准化参考值常量（球粒陨石/原始地幔/N-MORB）
├── _chem.py                # feot_calc 化学计算
├── _ternary.py             # 三元图坐标变换
├── merge_excel.py          # 主量+微量 Excel 合并
├── batch_backgrounds_main.py   # 批量底图生成（全70张，双模式 minimal/full，patch save_fig输出前缀文件名）
├── quick_validate.py       # 验证脚本（--quick 模式秒级回归；含 preflight 版本检查 + 元素依赖完整性检查）
├── requirements.txt        # 依赖锁定（numpy, matplotlib, scipy, openpyxl）
└── whole_rock/
    ├── __init__.py
    ├── boundaries/               # 坐标边界数据（JSON 格式）
    │   ├── core.py               # load_boundary(category, name) 工厂函数
    │   ├── cls/                  # 分类图边界（13 个 JSON）
    │   ├── src/                  # 源区图边界
    │   ├── evo/                  # 演化图边界
    │   └── tec/                  # 构造图边界（如 harris.json）
    └── diagrams/
        ├── __init__.py
        ├── _classification.py  # 分类图 — 29 个函数（TAS, K2O-SiO2, AFM, Shand, WF, 三角图等）
        ├── _source.py          # 源区图 — 17 个函数（REE, 蛛网图, Pearce系列等）
        ├── _evolution.py       # 演化图 — 7 个函数（Harker, Miyashiro, Mg#, Zr协变等）
        └── _tectonic.py        # 构造图 — 17 个函数（三元判别, 四联图, Shervais, Batchelor等）
references/
    architecture-review-20260527.md      # 用户审阅：架构方向与风险清单 ⭐ 新技能开发前必读
    winchester-floyd-v11-replacement.md  # WF1977 替换为 v11 精细底图（用户校正版）
    rockplot-diagram-catalog.md          # RockPlot 55张图的完整对照清单
    rockplot-coordinate-inventory.md          # SVG 坐标提取现状与待办清单
    batch-output-workflow.md                  # 批量出图完整工作流（plot_recommended + 手动补全）
    jensen-cation-spec.md                 # CLS-11 Jensen 阳离子三角图校正记录
    batch-background-workflow.md              # 批量底图生成（dummy data + patch scatter）
    svg-boundary-extraction.md           # SVG 底图数据提取通用方法
    ternary-coordinate-bug-pattern.md    # 三元图坐标映射常见错误
    oconnor-volc-spec.md                   # CLS-12 O'Connor 火山岩 An-Ab-Or 校正记录
    product-thinking.md
    k2o-sio2-middlemost-spec.md           # CLS-02 K₂O-SiO₂ 校正记录
```

## 故障排除

| 问题 | 排查 |
|------|------|
| 读 Excel 报错 | 检查 4 行表头格式，元素名或单位行是否被当做数据 |
| 缺某些元素导致部分图跳过 | 检查合并 Excel 中元素列名（大小写、下标） |
| REE/蛛网图缺线 | 检查元素是否齐全，未标准化时自动跳过 |
| 散点不是圆形 | 确认 `scatter_samples` 中显式 `marker='o'`（`_style.py` v3+ 已内置） |
| 图像模糊 | `save_fig()` 默认 600 dpi，可在底部调整 |
| TAS x轴刻度异常 | matplotlib默认AutoLocator在xlim=(35,90)时会自动选择从30开始的5的倍数（30,35,40,...），导致**图上数据点位置正确，但x轴刻度标签的数值标注偏移了5个单位**——用户在图上看到Foidite左边界在x=35的位置但刻度标的是30，视觉上感觉"坐标错了"或"左边多了一截"。**修复：TAS等SiO₂分类图必须显式设置刻度** `ax.set_xticks(range(35, 95, 5))`。同理y轴 `ax.set_yticks(range(0, 19, 2))`。切勿改xlim去"匹配刻度"——xlim保持(35,90)不变，只修正刻度标签。|
| 新增三角图边界异常 | SVG 像素坐标映射到三元空间时精度不够，用文献坐标比反推更可靠 |
| 新增图注册后 quick_validate 报错 | 检查 `DIAGRAM_REGISTRY` 是否添加了记录，`whole_rock_core.py` 的 import 是否遗漏 |
| 修改后回归验证 | 运行 `python3 quick_validate.py --quick`（秒级，跳过出图，检查 import + registry 自洽性）。确认 registry 总张数、mafic/felsic 计数合理且无文件名冲突。也可 `python3 batch_backgrounds_main.py --mode full` 验证全部 70 张底图可生成。 |
| SVG 提取的坐标点数量与预期不符 | 检查 class 属性：`class="polygons"` 使用多边形逻辑，`class="lines"` 使用折线逻辑，二者提取方法不同 |
| QAPFVolc SVG 路径全为 0pts | 该 SVG 为非标准格式（base64 或复合路径），需换用其他方法提取（如直接描点或查文献） |
| CLS-06 Co-Th 底图坐标严重错误 | `plot_co_th` 曾错误使用对数坐标（log-log），而 Hastie (2007) 原图为线性坐标。修复：去掉 `set_xscale('log')`/`set_yscale('log')`，Y 轴范围从 (1,500) 改为 (0,120)，X轴从 (0.1,50) 改为 (0,15)。分界线用 `axhline/axvline`（注意：应与同文件 CLS-02 风格统一，用 `ax.plot` 和彩色粗体标签更一致）。加区域标注文字（Tholeiitic / Calc-alkaline / High-K calc-alkaline）。 |
| `_classification.py` 损坏/被覆盖 | 该文件历史上有两次被误写覆盖。恢复方法：从 `_tectonic.py` 中风格一致的函数做参考重写。注意先从 session_search 检查是否有可恢复的旧版本。**2026-06-10 之后版本风险降低**：模块级坐标数组已外置到 `boundaries/cls/*.json`，函数体更短更稳定。 |

### 设计原则与维护规范

### 核心设计理念

**Skill 的目标是让 AI 做完一切，人不参与中间步骤。** 用户提供数据，AI 负责：
- 数据读取与解析
- 参数选择（标准化方案、元素组合、岩性判定）
- 调用 Python 代码完成所有数值计算（标准化、比值、判据坐标、出图）
- 结果解读与报告生成

AI 不直接进行任何数值计算（标准化、比值、FeOt换算、坐标变换等）。这些已全部固化在 Python 代码中（`_chem.py`, `_normalize.py`, `_ternary.py`, `merge_excel.py` 及各 diagram 模块）。

### 架构演进（2026-05-27 用户审阅结论）

> **本 skill 已不是"一个绘图脚本"，应按"小型数据工程 + 绘图引擎"来构建。**

详细审阅全文见 `references/architecture-review-20260527.md`。

**已完成的短期修复（4 项）：**
1. registry 依赖漏项 6 处修复 + 固化 `test_element_dependency_integrity()` 静态检查
2. `quick_validate.py` 加 `--quick` 模式 + preflight 版本检查 + `test_element_dependency_integrity()`
3. `requirements.txt` 锁定依赖
4. 输出路径改为 `../runs/default/`，清理残留目录

**中期待办（arch 拆包 — 渐进迁移进行中）：**

核心原则：**外部 API 不变，内部结构换骨架。** `whole_rock_core.py` 继续保持为兼容门面。

执行顺序（按 PR/提交批次）：
1. ✅ **Batch 1 (done)**: 建 `igneous_geochem/{core,io,diagrams,report,batch}` 包骨架 + 搬 4 个稳定底座（chem/normalize/ternary/style）
2. ✅ **Batch 2 (done)**: 搬注册表 `DiagramSpec` + `DIAGRAM_REGISTRY` 到 `diagrams/registry.py`。DiagramSpec 新增 3 个校正字段（review_status/source_ref/review_note），默认值不破旧 6 参写法。修复了旧 import 来源与函数实际所在模块不一致的历史问题（plot_co_th、plot_an_ab_or 等 10+ 个函数）。
2.5. ✅ **Batch 2.5 (done)**: 70 张图标记校正状态（verified=24, experimental=26, needs_review=20）。`whole_rock_core.py` 删除旧内联注册表（-203 行），全量从 registry.py import。`recommended_diagrams()` 显示 `[实验性]`/`[未校正]` 标签。新增 `test_registry_review_status_counts()` 静态验证。工作区收口清理。quick_validate: 204/213 passed.
3. ✅ **Batch 3 (done)**: 搬 `GeochemData`/Excel 读取到 `io/excel.py` + `core/data.py`（`whole_rock_core.py` 纯门面 re-export 已就绪）

> **注意：实际已完成。** `core/data.py` 和 `io/excel.py` 已有完整内容，`whole_rock_core.py` 的 import 已指向新位置。`from whole_rock_core import GeochemData` 实际路由到 `igneous_geochem.core.data`。用户问起时才确认——这说明 SKILL.md 的批次记录已过时。
4. ✅ **Batch 4 (done)**: 坐标外置。`_classification.py` 的坐标 → `boundaries/cls/*.json`；`_tectonic.py` 的 Harris 坐标 → `boundaries/tec/`；`_xy_diagrams.py` 拆散删除（32 函数分配到 4 个文件）。

**渐进迁移规则：**
- 旧文件改为 `sys.modules` 接管门面，所有 `from _chem import feot_calc` 原封不动可用
- 每步跑 `quick_validate.py --quick` 确认 202/0/0 通过 + registry 计数不变
- 每步跑 `batch_backgrounds_main.py --mode full` 确认 70 张底图可完整生成
- 每步提交一次 git
- 输出文件名、图件数量只增不减

**长期待办（图幅管线）：**
`manifest.yaml` + batch runner + `qc.json`，每个图幅独立运行、独立日志、独立报告

**已完成（2026-06-10 会话）：坐标数据抽离。**
将 `_classification.py`、`_tectonic.py` 中内联的分界线坐标数组（`np.array([...])` 块）抽离到 `boundaries/` 目录下的独立 JSON 文件。绘图函数改为函数内部 `load_boundary()` 加载。`_classification.py` 从 1423 行 → 1208 行，去掉了 215 行坐标数据。**同时 `_xy_diagrams.py` 已拆散删除**，32 个函数重新分配到 `_classification.py`(15)、`_tectonic.py`(9)、`_source.py`(5)、`_evolution.py`(3) 四个文件末尾。详见 `references/boundary-extraction-pattern.md`。

### 关键约束

- **所有图表必须是纯 matplotlib 实现**：严禁引入 pyrolite。TAS 等多参数图已全部用 Python 底图重绘。
- **`GeochemData` 无 `.data` 属性**：2026-05 月迁移后，`GeochemData` 属性为 `_elem_data`（原始数据 dict），`gd.get(element)` 为推荐访问方式。所有绘图函数中引用 `gd.data` 的调用会抛出 `'GeochemData' object has no attribute 'data'`。已知受影响函数共 5 个 `_xy_diagrams.py` 中的函数：`plot_frost`, `plot_villaseca`, `plot_debonba`, `plot_debonpq`, `plot_batchelor`, `plot_maniar`, `plot_agrawal`, `plot_verma`, `plot_larocheplut`, `plot_larochevolc`（10 处 `'FeO' not in gd.data` 检查）。另外，`feot_calc(gd)` 签名不匹配和死 `from _chem import mol` 也是同类迁移残留问题——详见下面 Pitfalls 节。
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

1. **所有纯数值计算必须固化在 Python 代码中**，不可让 AI 在对话中"算一下"。
2. **新增图件**：写绘图函数 + 在 `DIAGRAM_REGISTRY` 加记录，无需修改 AI 行为。
3. **新增边界坐标**：写入 `boundaries/{category}/{name}.json` 文件。绘图函数内用 `load_boundary(category, name)` 加载。四个 diagram 文件均已添加 `from boundaries.core import load_boundary` 导入。
3. **新增标准化方案**：在 `_normalize.py` 加常数 + 在 `CHONDRITE`/`PRIMITIVE_MANTLE`/`N_MORB` 适当位置引用。
4. **不动"让人去跑脚本"的出口**。Skill 的入口对准 AI 调用，不对准用户手动运行。不要添加只给用户用的"计算器式"工具脚本。
5. **参数微调**（点大小、颜色、图例位置等）使用 `_style.py` 的常量覆盖机制，AI 不改 `_style.py` 核心逻辑。
6. **全量出图后核查三角图顶点标签位置** — 执行完全量出图后，抽查每个三角图的三个顶点标签是否符合文献标准。`label_ternary_vertices(ax, top, left, right)` 参数顺序易错：不要按文献叙述顺序传参，要按图中顶点物理布局传参。**AFM 标准布局 = F(顶)、A(左下)、M(右下)**。此规则同样适用于 `ternary_to_xy(top, left, right)` 的数据顺序。**改顶点顺序时，必须同步修改 3 处：**(1) `ternary_to_xy(top数据, left数据, right数据)` 的 arg 顺序、(2) `label_ternary_vertices(ax, top标签, left标签, right标签)` 的 arg 顺序、(3) 分界线坐标也在同一顶点空间内。三者中任一个不一致都会导致标签错位或分界线不可见。验证方法：打印 `ternary_to_xy` 计算出的边界线 xy 坐标，确认其在 `ax.set_xlim/ylim` 范围内可见再提交。

### Pitfalls

- ❌ 提议让用户手动跑脚本来完成计算 → 违背"AI 做完一切"原则
- ❌ AI 在对话中手算标准化值或比值 → 模型波动导致结果不一致
- ❌ 为了一次性需求写计算脚本 → 代码没复用，反而增加了维护负担
- ❌ **在 chat 中分多次用 write_file/heredoc 追加一个大 Python 文件** → 极易因中途中断（context 压缩、heredoc 中的 & / 特殊字符误解、子代理 timeout）导致文件损坏/不完整。**文件已被误写覆盖 3 次**（~800→329 bytes→77 行→目前正确）。正确做法：**使用 `execute_code` 一次性生成完整文件内容并写入**，或者用 `terminal` 调用一个独立的 Python 脚本（如 `/tmp/gen_cls.py`）完成文件编写。heredoc 中含有 `&` 或特殊符号时会失败。

- ✅ 从 SVG 提取的坐标已确认在 `/tmp/extracted_paths.json` 中可用，像素→三元百分比转换用 `_pixel_to_ternary(px, py)` 公式，已验证通过。不再需要通过 pycache 恢复 _ternary.py 的旧版本。
- ✅ **Git 版本控制**：`git init` 后在 `/home/twoper/.hermes/skills/data-science/igneous-geochemistry/` 下管理。`.gitignore` 排除 `__pycache__/`、`*.png`、`whole_rock_output/`、`runs/`、`*_output/`。每次功能性修改后 `git commit`（当前 4 commits: v1.0, docstring fix, pyrolite removal, registry/archfix）。执行 `git log --oneline` 确认最新状态。

- ⚠️ 当遇到长时间任务（创建 33 个函数的文件、注册 29 条记录）时，**分多次 write_file 追加会因网络中断/context 压缩导致不完整**。明确教学：先写好全部内容的 Python 生成脚本，用 `execute_code` 一次性写入，或者用 `terminal` 运行独立脚本完成全部写入。如果用户中间说"继续"，说明正在分步执行——此时管理好 todo 状态，以单个 `execute_code` 调用写入尽可能完整的一块代码，而不是多步 write_file。

- ❌ **从 chat 历史中的旧文件内容恢复** — `session_search` 不会匹配到大文件的全部代码。恢复策略：从头参考风格一致的已实现函数重新编写。
- ❌ **从 SVG 提取的坐标直接硬编码到 Python 文件** → SVG 像素→三元坐标变换存在误差，后续对比文献原文边界线时难以修正。更好的做法：将 SVG 像素坐标保留在独立的 JSON 数据文件中，绘图函数从数据文件加载
- ❌ **用 `from X import *` 做模块门面** → `set_style()` 修改的是目标模块的变量，但门面模块的 import-time 拷贝不会同步。正确方案：用 `sys.modules[__name__] = _mod` 接管整个模块
- ❌ **在 `_xy_diagrams.py` 中使用 `feot_calc(gd)`（旧单参数签名）** → `feot_calc` 当前签名为 `feot_calc(feo, tfe2)`，很多较晚添加的 XY 图（frost、villaseca、debonba/b、batchelor、maniar、agrawal、verma、larocheplut/volc）用了旧式 `feot_calc(gd)`，运行时抛出 `TypeError: missing 1 required positional argument`。正确调用：`feot_calc(gd.get('FeO'), gd.get('TFe2O3'))`。
- ❌ **在 `_xy_diagrams.py` 函数中保留死 import `from _chem import mol`** → `mol` 函数在 `_chem.py` 门面中不存在，且这些函数中从未实际调用它。运行时抛出 `ImportError: cannot import name 'mol'`。修复方案：直接删除该行 -- 这些函数实际使用的是内联摩尔质量常数（如 `/ 101.96`、`/ 56.08`），无需 `mol()` 函数。
- ❌ **三角图顶点顺序（top/left/right）与 `ternary_to_xy` / `label_ternary_vertices` 参数不匹配** → 这两个函数的参数顺序都是 (top, left, right)。当更改顶点布局（如 AFM 从 A顶→F顶）时，必须同步更新：`ternary_to_xy(top_数据, left_数据, right_数据)`、`label_ternary_vertices(ax, top标签, left标签, right标签)`、以及边界线 koordinate 也在同一空间。三者中任一个与其它不一致都会导致标签错位、分界线画错或不可见。**验证方法：** 改完三角图顶点顺序后，先打印 `ternary_to_xy` 计算出的边界线 xy 坐标，确认其在 `ax.set_xlim/ylim` 范围内可见，再提交。
- ✅ 遇到重复 3 次以上的计算模式 → 考虑固化到 Python 模块
- ✅ 参数选择有歧义时 → 列出选项让用户选，不替用户决定
- ✅ **批量出图循环中必须加 `plt.close('all')`**：遍历 70 张图时每张图调用 `plt.subplots()` 打开一个新 figure。如果不及时关闭，matplotlib 在第 20 张后弹出 `RuntimeWarning: More than 20 figures have been opened`。修复：在每次循环末尾调用 `plt.close('all')` 关闭当前 fig 以释放内存。
- ❌ **SKILL.md 技术规范与 Python 代码不同步** — 当 patch SKILL.md 添加/修改了某个具体图件的技术规范（如分界线坐标、坐标轴范围、标注样式），且这次修改被写入了 SKILL.md 的 "底图质量规范" 节，必须同步检查并更新对应的 Python 绘图函数。否则下次出图时 SKILL.md 记载了已校正确认的版本，但代码仍然输出旧版。已知具体实例：K₂O–SiO₂ 分界线在 SKILL.md 中已按用户校正改为端点坐标法 `(45,0.5)→(75,2.5)` 等，但 `_classification.py` 中的 `plot_k2o_sio2()` 仍用旧斜率公式。

✅ **新增图前检查 DIAGRAM_REGISTRY 中是否有功能重复已经注册的函数**：最典型的是 Th/Yb–Nb/Yb 图同时注册了 pearce1996 和 pearce_2008（已清理），以及三个 Zr/Y–Zr 图（因判据不同保留，但在 desc 中加注区分）。新增前用 `grep "Nb/Yb\\|Th/Yb\\|Zr/Y.*Zr" whole_rock_core.py` 快速检索，避免同一物理图件重复注册。
- ✅ **"边界数据不硬编码"规则的例外：用户亲自校准过的版本直接硬编码**。WF1977 v11 的 67 个节点坐标由用户逐点校正了 11 个版本，属于"最终定稿版本"而非"待提取的 SVG 数据"。此类经用户确认的定稿数据可直接硬编码进函数；未经用户确认的 RockPlot SVG 提取数据则必须按标准方式存入 JSON/YAML。
- ❌ **分界线坐标与画图逻辑混在同一个文件中的后果**：`_classification.py` 曾是 1423 行，`_xy_diagrams.py` 曾是 1159 行，其中 ~40-60% 的字符属于坐标数组而非逻辑代码。用户明确表示"太长了，不敢改"。**2026-06-10 已修复**：坐标数据外置到 `boundaries/` JSON 文件。`_classification.py` 现为 1208 行（纯绘图逻辑 + 内联的 load_boundary 调用），`_xy_diagrams.py` 已拆散删除。不再有 1000+ 行的坐标数组冗余。后续新增图时，坐标数据应直接写入 `boundaries/{category}/{name}.json` 而非硬编码到函数体。
- ✅ **所有图表必须是纯 matplotlib 实现，严禁引入 pyrolite**
- ✅ **TAS 等分类图的底图坐标来源必须严格对接 pyrolite 原始坐标**：Foidite 的 (35.00,9.00) 起始点看起来像"贴着 y 轴画线"，但 pyrolite 输出的就是 (35.00,9.00)。AI 不应凭视觉印象自行修改 pyrolite 提取的坐标——任何底图边界坐标的调整必须先从系统 pyrolite 提取对照坐标确认无误，再由用户确认。**「我感觉这个点不对」不是修改坐标的正当理由。**

- ⚠️ **用户对TAS底图的视觉判断标准非常严格**：即使坐标与pyrolite完全一致，用户仍可能认为底图"是错的"。**应对方式：不要解释"坐标来自pyrolite所以是对的"**，直接问用户具体哪里看起来不对，让用户明确指出来后再去修改。**TAS底图出问题的系统排查步骤**（按优先级执行）：\n  (1) 检查x轴刻度标签——matplotlib AutoLocator默认从30开始标，导致Foidite左边界x=35处标着30，用户视觉上觉得"左边多出一截"。→ `ax.set_xticks(range(35, 95, 5))` 修复。\n  (2) 检查y轴刻度标签——同理。\n  (3) 检查Foidite最左侧坐标(35,9)是否贴在x=35的轴线上——这是pyrolite原始坐标，但如果用户说"左边变成了一条直线边"，回答：这是pyrolite原始设计，Foidite最左点在x=35处，需要我微调xlim让它离开轴线吗？\n  (4) 检查matplotlib版本是否低于3.7——polygon渲染差异会改变底图观感。\n  (5) 用系统pyrolite生成参考图对比底图（仅对比底图，不绕过_style.py的输出机制）。**不要做的事**：不改xlim去适配刻度、不改pyrolite原始坐标、不换色块填充方案。|
- ✅ **做重大架构变更前先读 `references/architecture-review-20260527.md`**：用户审阅明确给出了架构方向、风险清单、中远期路径。新增图、拆包、加新功能前必须参照，避免偏离已共识的方向。
- ✅ **每次修改后运行 `python3 quick_validate.py --quick`**：秒级回归。检查 registry 总张数、依赖完整性、文件冲突。完整模式确认出图正常后再 commit。
- ✅ **每批迁移前确保工作区干净**：`git status --short` 应为空或仅含当前批的预期文件。上一个批次的文档尾巴（uncommitted 的 mdocs、新 references/ 文件）必须在开始新批前全部提交。混合批次的 diff 会阻塞回滚。用户明确说"我不建议立刻做 Batch 3"就是因为 SKILL.md 和 references/ 未提交 + `whole_rock_core.py` 旧内联注册表残留。

### 渐进迁移陷阱（2026-05-27 实际踩坑记录）

**`import → 内联定义覆盖` 陷阱（Batch 2 关键教训）**

`whole_rock_core.py` 中先 `from igneous_geochem.diagrams.registry import DIAGRAM_REGISTRY`，但 200 行后有 `DIAGRAM_REGISTRY = [...]` 内联定义覆盖了 import 版本。结果 `from whole_rock_core import DIAGRAM_REGISTRY` 拿到的是旧内联版本（无 review_status 字段）。

**根因**：Python 中模块顶层变量定义（即使在后）会覆盖先执行的 import 绑定。`import` 执行了，但被同一模块的同名赋值覆盖。

**验证方法**：检查 `DIAGRAM_REGISTRY[0]` 是否有新增字段（如 `review_status`）。有则来自新包，无则仍在使用旧内联版本。

**修复方案**：删除内联定义，只保留 import（全量通过 `re-export` 实现向后兼容）。不要只 patch import 语句而不删除旧定义。

**门面模块的 sys.modules 接管模式**

`from X import *` 做门面时有变量隔离问题：`set_style()` 修改的是目标模块的变量，但门面模块的 import-time 拷贝不会同步。正确方案：

```python
"""_style.py — 兼容门面"""
import sys
_mod = sys.modules.get('igneous_geochem.report.style')
if _mod is None:
    import igneous_geochem.report.style as _mod
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

#### 通用规范
- 分类图不要网格线 → `ax.grid(False)` 必须在 `_style.style_ax()` **之后**调用（style_ax 默认开网格）
- 刻度向内；封闭四边边框
- 中文字体在 WSL 默认 matplotlib 中不可用 → 所有标注用英文
- 除背景填充外，投点/图例/标签等要素应保持在正确 zorder 以确保可见性

#### 三元图底图规范（适用于 CLS-09/10/11/12 等 SVG 提取的三角图）
- **顶点标签化学式规范**：数字必须下标（如 `TiO₂`、`P₂O₅`、`MnO`），不要写 `TiO2`、`P2O5`
- **系数表达规范**：使用 `10×MnO` 或 `10×MnO (wt.%)`，不要写 `10MnO`（后者易被误解为"10倍的MnO含量"）。乘号用 Unicode `×` (U+00D7) 而非 `x` 或 LaTeX `\\times`（后者在 matplotlib text 渲染中会触发 ParseFatalException）
- **场域文字标注**：每条分界线围成的区内必须有对应的场域名称（如 IAT / MORB / WPB / CAB），不能只有界线无标签
- **引用文献 imprint**：在 figure 底部或图注中包含 "After [Author], [Year]"
- **背景色填充**：各场域用淡色填充（alpha=0.20），颜色参照 Cabanis 风格（橙/蓝/绿/粉）
- **场域标签颜色应与填充区域匹配**：区域文字标签用与该场域填充色同色系的粗体颜色，而非统一灰色
- 坐标轴标签（top/left/right）字号不小于 10pt，场域标注 8-9pt 彩色粗体，置于场内不压界线

#### 修改单图时的风格对齐检查
- 当需要修改某个具体绘图函数时（如修复坐标、加标注、调颜色），**必须先阅读同文件中相同类型的图**，确认其标注风格（字体大小、颜色、权重、是否填充背景等），再按该风格修改，而不是��行 invent 一份新风格
- 具体地：`_classification.py` 内所有图都应参照 CLS-02（K₂O-SiO₂）的风格——彩色粗体场域标签 + 填充色 + 不同线型
- 不要引入 axhline/axvline 替代 ax.plot 保持模块内写法统一
- 如果不确定风格，优先问用户，不要自己猜
- **典型失败案例**：本 skill 的 CLS-06 (Co-Th) 修复时，用了 `axhline/axvline` + `fontsize=9, fontstyle='italic', alpha=0.7` 的通用注解样式，而同一文件中的 CLS-02 已明确使用 `ax.plot` + 彩色粗体 (`color='#xxx', fontweight='bold'`) + 背景色填充。修复时必须走一遍同文件风格扫描再动笔。

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

#### 用户提供专家审查的图件校正模式（2026-05-27 确立）

用户以"资深岩石地球化学专家与SCI期刊制图编辑"身份提供每张图的详细审查报告。Agent 需遵循此协作模式：

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

### 已完成的 CLS 图件系统校正

| 图号 | 图名 | 日期 | 修正内容 | 参考文件 |
|------|------|------|---------|---------|
| CLS-02 | K₂O–SiO₂ | 2026-05-27 | 斜率归零→端点坐标法；四色填充；去网格 | `references/k2o-sio2-middlemost-spec.md` |
| CLS-03 | AFM | 2026-05-27 | 5点粗线→18点精确曲线；Th/CA颜色分区 | `references/afm-18point-boundary.md` |
| CLS-04 | Shand | 2026-05-27 | 虚线框架→三分区三界线；英文标注 | `references/shand-spec.md` |
| CLS-06 | Co-Th Hastie | 2026-05-27 | 对数坐标→线性坐标；Y轴上限500→120；加场域标签 | 本会话 |
| CLS-07 | An-Ab-Or O'Connor | 2026-05-27 | 空框架→7条O'Connor界线+8色区+花岗岩类命名 | `references/an-ab-or-oconnor-spec.md` |
| CLS-08 | QAP Streckeisen | 2026-05-27 | 空框架→Q等值线+A/(A+P)射线+16区命名+P+F→P | `references/qap-streckeisen-spec.md` |
| CLS-09 | Cabanis La/10-Y/15-Nb/8 | 2026-05-27 | 空框架→WPB/IAB/MORB 3色区+场域标注（精度受限） | 本会话 |
| CLS-10 | Mullen TiO₂-10×MnO-10×P₂O₅ | 2026-05-27 | 顶点标签下标/乘号校正；4场域填充+标签(IAT/MORB/OIT/OIA+CAB) | 本会话 |
| CLS-11 | Jensen Al+Fe³⁺+Ti–Mg+Fe²⁺+Mn–Ca+Na+K | 2026-06-10 | 端元校正（wt%氧化物→阳离子数）；4色区+Komatiitic/Tholeiitic/Calc-alkaline标注 | 本会话 |
| CLS-12 | O'Connor Volc An-Ab-Or | 2026-06-10 | 空框架→8色区+8类岩石标注(Anorthite至Syenogranite)+长顶点名 | 本会话 |

### 用户交互风格

- **先做后问**：当可以用现有工具直接查出答案时，不要反问用户。只有真正有歧义且无法从现有数据推断时，才简短确认。
- **不要教育用户**：用户清楚自己要什么，Agent 是执行工具。解释只讲思路和操作步骤，不试图"教学"。
- **规划/决策会议时**：用户说"我先想一下"时安静等待。不主动提问、不执行命令、不读文件——直到用户说"开始"。
- **用户批复时间可能较长**，耐心等待，不催促。

## 相关技能

- `geochemical-plotting` → `whole-rock-geochemistry` → `igneous-geochemistry`（更名历史见 `references/refactoring-history.md`）
- 含 `winchester-floyd-boundary-data` 的分界线数据（`references/winchester-floyd-boundary-data.md`）
