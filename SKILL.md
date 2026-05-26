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

旧文件通过 `sys.modules` 接管门面保持旧入口兼容。下一步：搬注册表到 `diagrams/registry.py`，再拆 `GeochemData` 和 Excel 读取。每次迁移前确认 `quick_validate.py --quick` 全部通过、registry 计数不变。

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

### 3. 图解目录（70 种，含 37 个绘图函数在 4 个模块 + 32 张 XY 二元图在 _xy_diagrams.py）

> **注意**：`plot_pearce1996`（Pearce 1996 Th/Yb–Nb/Yb）已移除（与 `_source.py` 的 `plot_pearce_2008` 功能重叠，后者更精细）。统一使用 `plot_pearce_2008`。三个 Zr/Y–Zr 图（`pearcenorry`, `pearce1982`, `zr_y_zr`）判据不同，全部保留并在 registry 中用 desc 标注区分。

#### 📋 岩石系列 / 分类（5 种）

| 图解 | 所需元素 |
|------|---------|
| TAS 全碱-硅分类图 | SiO₂, Na₂O, K₂O |
| K₂O–SiO₂ 钾系列分类图 | SiO₂, K₂O |
| AFM 钙碱性-拉斑判别 | Na₂O, K₂O, MgO, FeO/TFe₂O₃ |
| Shand A/CNK–A/NK 铝质分类 | Al₂O₃, CaO, Na₂O, K₂O |
| Winchester & Floyd Zr/TiO₂–Nb/Y | Zr, TiO₂, Nb, Y | <- v11 精细底图（67 节点 × 9 条校正边，含岩性标签） |

#### 🔬 源区性质（11 种）

| 图解 | 所需元素 |
|------|---------|
| REE 球粒陨石标准化配分图 | La–Lu 14 个 REE |
| 原始地幔标准化蛛网图 | Rb–Lu 26 个元素 |
| Pearce Th/Yb–Nb/Yb 源区判别 | Th, Nb, Yb |
| Co-Th (Hastie) 系列判别 | Co, Th |
| U/Th–Zr/Nb (Stern) 源区判别 | U, Th, Zr, Nb |
| (Sm/Yb)PM–(La/Sm)PM 部分熔融 | La, Sm, Yb |
| Sc-V (Hickey-Vargas) 氧化条件 | Sc, V |
| Ba/Th–La/Sm 流体 vs 熔体判别 | Ba, Th, La, Sm |
| Gd/Yb vs Dy/Dy* 稀土分馏 (Davidson 2013) | La, Gd, Tb, Dy, Ho, Yb |
| Dy/Yb vs La/Yb 石榴石源区深度 (Zhang 2018) | La, Dy, Yb |
| Nb/La vs Th/La 构造判别 (Cabanis 1986) | Nb, Th, La |

#### 🧬 岩浆演化过程（4 种）

| 图解 | 所需元素 |
|------|---------|
| Harker 六合一协变图 | SiO₂, MgO, Al₂O₃, CaO, Na₂O, TiO₂, +FeO(TFe₂O₃可选) |
| Miyashiro FeOt/MgO–SiO₂ | SiO₂, MgO, FeO/TFe₂O₃ |
| Mg# vs SiO₂ 演化图 | SiO₂, MgO, FeO/TFe₂O₃ |
| Zr 协变 3×3 图 | Zr, Nb, Hf, Th, Y, Yb, La, Sm, Ba, Sr（需 ≥3 种其他元素） |

#### 🌍 构造环境判别（10 种）

| 图解 | 所需元素 |
|------|---------|
| Meschede Nb–Zr–Y 构造判别（三元） | Nb, Zr, Y |
| Wood Hf/3–Th–Ta 构造判别（三元） | Hf, Th, Ta |
| Pearce & Cann Ti–Zr–Y 构造判别（三元） | Ti, Zr, Y |
| 四联比值构造判别图 | Ti, V, Sc, Nb, Yb, Th, La, Sm, Ba |
| Shervais Ti-V 构造判别 | Ti, V |
| Th/Yb–Ta/Yb (Pearce 1983) 构造判别 | Th, Ta, Yb |
| NbN–ThN (Saccani 2015) 构造判别 | Nb, Th |
| Zr/Y vs Zr (Xia 2014) 岛弧 vs 大陆弧 | Zr, Y |
| An-Ab-Or 长石分类三元图 (O'Connor 1965) | Na₂O, K₂O, CaO, Al₂O₃, SiO₂ |
| Q-A-PF 深成岩分类三元图 (Streckeisen 1976) | SiO₂, Na₂O, K₂O, CaO, Al₂O₃ |

#### ✅ RockPlot SVG 新增（8 张，2026-05-25 完成）

RockPlot SVG 数据提取并集成完成的 8 张三角/三元图（坐标从 `/tmp/extracted_paths.json` 提取，像素→三元坐标经 `ternary_to_xy` 转换，绘图函数已注册到 `DIAGRAM_REGISTRY`）：

| 图解 | SVG 文件 | 端元（顶/左下/右下） | 边界线数 | 所在文件 |
|------|---------|---------------------|---------|---------|
| Cabanis & Lecolle (1989) | Cabanis.svg | Y/15, La/10, Nb/8 | 1 条 | `_classification.py` |
| Mullen (1983) | Mullen.svg | TiO₂, 10MnO, 10P₂O₅ | 4 条 | `_classification.py` |
| Jensen (1976) | Jensen.svg | FeOt+TiO₂, Al₂O₃, MgO | 19 条（多边形填充） | `_classification.py` |
| O'Connor (1965) 火山变体 | OConnorVolc.svg | An, Ab, Or | 7 条直线分区 | `_classification.py` |
| Ohta & Arai (2007) | OhtaArai.svg | M, F, W | 4 条曲线 | `_classification.py` |
| Pearce (1977) | Pearce1977.svg | FeOt, MgO, Al₂O₃ | 4 条虚线边界 | `_classification.py` |
| Harris (1986) | Harris.svg | Rb/30, Hf, 3Ta | 5 条 | `_tectonic.py` |
| Muller et al. (K-ternary) | MullerKternary.svg | Th, Ta, Hf（3并列子图） | 等边小三角 | `_tectonic.py` |

#### XY 二元图（32 张，位于 `_xy_diagrams.py`）

| 类别 | 图件 | 所需元素 | 岩性适用 |
|------|------|---------|---------|
| **TAS 变体** | TASMiddlemostPlut | SiO₂, Na₂O, K₂O | 酸性 |
| | TASMiddlemostVolc | SiO₂, Na₂O, K₂O | 基性 |
| | CoxPlut | SiO₂, Na₂O, K₂O | 酸性 |
| | CoxVolc | SiO₂, Na₂O, K₂O | 基性 |
| | MiddlemostPlut | SiO₂, Na₂O, K₂O | 酸性 |
| **Pearce 系列** | PearceNorry Zr/Y–Zr | Zr, Y | 基性 |
| | Pearce1982 Zr/Y–Zr | Zr, Y | 基性 |
| | PearceGranite Rb–Y+Nb | Rb, Y, Nb | 酸性 |
| | PearceNbThYb Nb/Yb–Th/Yb | Nb, Th, Yb | 基性 |
| | PearceNbTiYb Ti/Yb–Nb/Yb | Ti, Nb, Yb | 基性 |
| **花岗岩专题** | Frost Fe-number–SiO₂ | SiO₂, MgO + FeO(T) | 酸性 |
| | Whalen1 10000×Ga/Al–Zr | Ga, Al₂O₃, Zr | 酸性 |
| | Whalen2 10000×Ga/Al–Nb | Ga, Al₂O₃, Nb | 酸性 |
| | Whalen3 10000×Ga/Al–Ce+Y+Zr | Ga, Al₂O₃, Ce, Y, Zr | 酸性 |
| | Sylvester CaO/Na₂O–Al₂O₃ | CaO, Na₂O, Al₂O₃ | 酸性 |
| | Villaseca ASI–FMM | Al₂O₃, CaO, Na₂O, K₂O, MgO, TiO₂ + FeO(T) | 酸性 |
| | Debon B-A | Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ + FeO(T) | 酸性 |
| | Debon P-Q | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ + FeO(T) | 酸性 |
| | Schandl Y–Zr | Y, Zr | 酸性 |
| | Batchelor R1-R2 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ + FeO(T) | 酸性 |
| **岩浆系列** | Muller K₂O–SiO₂ | SiO₂, K₂O | 基性 |
| | PeceTaylor K₂O–SiO₂ | SiO₂, K₂O | 基性 |
| | Hastie Th–Co | Th, Co | 基性 |
| **氧化条件** | Hollocher1 V/Sc–V+Sc | V, Sc | 基性 |
| | Hollocher2 Zr/Ce–V/Sc | V, Sc, Zr, Ce | 基性 |
| **多变量判别** | Maniar 花岗岩构造判别 | SiO₂, Al₂O₃, MgO, CaO, Na₂O, K₂O, TiO₂ + FeO(T) | 酸性 |
| | Agrawal DF1-DF2 | TiO₂, Al₂O₃, MgO, CaO, Na₂O, K₂O, MnO, P₂O₅, SiO₂ + FeO(T) | 基性 |
| | Verma DF1-DF2 | TiO₂, Al₂O₃, MgO, CaO, Na₂O, K₂O, MnO, P₂O₅, SiO₂ + FeO(T) | ���性 |
| **侵入/火山** | LaRoche R1-R2 侵入岩 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ + FeO(T) | 酸性 |
| | LaRoche R1-R2 火山岩 | SiO₂, Al₂O₃, K₂O, Na₂O, CaO, MgO, TiO₂ + FeO(T) | 基性 |
| **部分熔融** | La/Yb vs Yb | La, Yb | 通用 |
| | Ross La/Sm–La/Yb | La, Sm, Yb | 通用 |

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
├── quick_validate.py       # 验证脚本（--quick 模式秒级回归；含 preflight 版本检查 + 元素依赖完整性检查）
├── requirements.txt        # 依赖锁定（numpy, matplotlib, scipy, openpyxl）
└── whole_rock/
    ├── __init__.py
    └── diagrams/
        ├── _xy_diagrams.py      # X-Y 专题图（32张）
        ├── _classification.py  # 分类图（TAS, K2O-SiO2, AFM, Shand, WF）
        ├── _source.py          # 源区图（REE, 蛛网图, 源区判别）
        ├── _evolution.py       # 演化图（Harker, Miyashiro, Mg#, Zr协变）
        └── _tectonic.py        # 构造图（三元判别, 四联图, Shervais等）
references/
    architecture-review-20260527.md      # 用户审阅：架构方向与风险清单 ⭐ 新技能开发前必读
    winchester-floyd-v11-replacement.md  # WF1977 替换为 v11 精细底图（用户校正版）
    rockplot-diagram-catalog.md          # RockPlot 55张图的完整对照清单
    rockplot-coordinate-inventory.md     # SVG 坐标提取现状与待办清单
    svg-boundary-extraction.md           # SVG 底图数据提取通用方法
    ternary-coordinate-bug-pattern.md    # 三元图坐标映射常见错误
    classification-file-status.md        # _classification.py 损坏与恢复记录
```

## 故障排除

| 问题 | 排查 |
|------|------|
| 读 Excel 报错 | 检查 4 行表头格式，元素名或单位行是否被当做数据 |
| 缺某些元素导致部分图跳过 | 检查合并 Excel 中元素列名（大小写、下标） |
| REE/蛛网图缺线 | 检查元素是否齐全，未标准化时自动跳过 |
| 散点不是圆形 | 确认 `scatter_samples` 中显式 `marker='o'`（`_style.py` v3+ 已内置） |
| 图像模糊 | `save_fig()` 默认 600 dpi，可在底部调整 |
| 新增三角图边界异常 | SVG 像素坐标映射到三元空间时精度不够，用文献坐标比反推更可靠 |
| 新增图注册后 quick_validate 报错 | 检查 `DIAGRAM_REGISTRY` 是否添加了记录，`whole_rock_core.py` 的 import 是否遗漏 |
| 修改后回归验证 | 运行 `python3 quick_validate.py --quick`（秒级，跳过出图，检查 import + registry 自洽性）。确认 registry 总张数、mafic/felsic 计数合理且无文件名冲突 |
| SVG 提取的坐标点数量与预期不符 | 检查 class 属性：`class="polygons"` 使用多边形逻辑，`class="lines"` 使用折线逻辑，二者提取方法不同 |
| QAPFVolc SVG 路径全为 0pts | 该 SVG 为非标准格式（base64 或复合路径），需换用其他方法提取（如直接描点或查文献） |
| `_classification.py` 损坏/被覆盖 | 该文件已有两次被误写覆盖（~800行→329 bytes、77行）的记录。原因是 chat 中多次用 write_file 追加不完整内容。恢复方法：从 _tectonic.py 中风格一致的函数做参考重写，结合 _ternary.py 的坐标变换。注意先从 session_search 检查是否有可恢复的旧版本 |

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
2. ⬜ **Batch 2**: 搬注册表 `DiagramSpec` + `DIAGRAM_REGISTRY` 到 `diagrams/registry.py`
3. ⬜ **Batch 3**: 搬 `GeochemData` / Excel 读取到 `io/excel.py` + `core/data.py`
4. ⬜ **Batch 4**: batch runner + manifest 支持

**渐进迁移规则：**
- 旧文件改为 `sys.modules` 接管门面，所有 `from _chem import feot_calc` 原封不动可用
- 每步跑 `quick_validate.py --quick` 确认 202/0/0 通过 + registry 计数不变
- 每步提交一次 git
- 输出文件名、图件数量只增不减

**长期待办（图幅管线）：**
`manifest.yaml` + batch runner + `qc.json`，每个图幅独立运行、独立日志、独立报告

### 关键约束

- **所有图表必须是纯 matplotlib 实现**：严禁引入 pyrolite。TAS 等多参数图已全部用 Python 底图重绘。
- **新增图前检查 registry 重复**：同一物理图件不得重复注册。用 `grep "功能关键词" whole_rock_core.py` 确认。
- **图幅数据不进 skill 本体**：Skill 只放工具和规则。图幅数据归项目工作区(manifest.yaml + data/ + runs/)。
- **边界数据不硬编码**：SVG 提取的边界坐标存 JSON/YAML，绘图函数只加载不硬编码。

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
3. **新增标准化方案**：在 `_normalize.py` 加常数 + 在 `CHONDRITE`/`PRIMITIVE_MANTLE`/`N_MORB` 适当位置引用。
4. **不动"让人去跑脚本"的出口**。Skill 的入口对准 AI 调用，不对准用户手动运行。不要添加只给用户用的"计算器式"工具脚本。
5. **参数微调**（点大小、颜色、图例位置等）使用 `_style.py` 的常量覆盖机制，AI 不改 `_style.py` 核心逻辑。

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
- ✅ 遇到重复 3 次以上的计算模式 → 考虑固化到 Python 模块
- ✅ 参数选择有歧义时 → 列出选项让用户选，不替用户决定
- ✅ **新增图前检查 DIAGRAM_REGISTRY 中是否有功能重复已经注册的函数**：最典型的是 Th/Yb–Nb/Yb 图同时注册了 pearce1996 和 pearce_2008（已清理），以及三个 Zr/Y–Zr 图（因判据不同保留，但在 desc 中加注区分）。新增前用 `grep "Nb/Yb\\|Th/Yb\\|Zr/Y.*Zr" whole_rock_core.py` 快速检索，避免同一物理图件重复注册。
- ✅ **"边界数据不硬编码"规则的例外：用户亲自校准过的版本直接硬编码**。WF1977 v11 的 67 个节点坐标由用户逐点校正了 11 个版本，属于"最终定稿版本"而非"待提取的 SVG 数据"。此类经用户确认的定稿数据可直接硬编码进函数；未经用户确认的 RockPlot SVG 提取数据则必须按标准方式存入 JSON/YAML。
- ✅ **所有图表必须是纯 matplotlib 实现，严禁引入 pyrolite**
- ✅ **做重大架构变更前先读 `references/architecture-review-20260527.md`**：用户审阅明确给出了架构方向、风险清单、中远期路径。新增图、拆包、加新功能前必须参照，避免偏离已共识的方向。
- ✅ **每次修改后运行 `python3 quick_validate.py --quick`**：秒级回归。检查 registry 总张数、依赖完整性、文件冲突。完整模式确认出图正常后再 commit。

## 相关技能

- `geochemical-plotting` → `whole-rock-geochemistry` → `igneous-geochemistry`（更名历史见 `references/refactoring-history.md`）
- 含 `winchester-floyd-boundary-data` 的分界线数据（`references/winchester-floyd-boundary-data.md`）
