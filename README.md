# IgneousWR

**Igneous Whole-Rock Geochemical Plotting Engine**

IgneousWR 是一个全岩地球化学批量成图工具。输入 Excel 数据文件，自动生成 19 张精选图件（分类图解、源区性质、岩浆演化、构造环境判别）并输出一份自包含的 HTML 报告。

面向地质学者和岩石地球化学研究者，无需 GUI 操作，一条命令出全套图。

## 图解一览（19 张）

### 分类 · 岩石系列（12 张）

| 图解 | 参考文献 |
|------|---------|
| TAS 全碱-硅分类（火山岩，Middlemost 1994） | Middlemost (1994) |
| K₂O–SiO₂ 钾系列分类（Middlemost 1985） | Middlemost (1985) |
| K₂O–SiO₂ 钾系列分类（Peccerillo & Taylor 1976） | Peccerillo & Taylor (1976) |
| AFM 钙碱性-拉斑系列判别 | Irvine & Baragar (1971) |
| Zr/TiO₂–Nb/Y 分类（Winchester & Floyd 1977） | Winchester & Floyd (1977) |
| Zr/Ti–Nb/Y 火山岩分类（Pearce 1996） | Pearce (1996) |
| Co–Th 系列+岩性判别 | Hastie et al. (2007) |
| TiO₂–MnO–P₂O₅ 基性岩三角图 | Mullen (1983) |
| TAS 全碱-硅分类（深成岩，Middlemost 1994） | Middlemost (1994) |
| Fe# vs SiO₂ 铁质-镁质分类 | Frost et al. (2001) |
| MALI vs SiO₂ 碱-钙分类 | Frost et al. (2001) |
| ASI vs A/NK 铝饱和分类 | Frost et al. (2001) |

### 源区性质（3 张）

| 图解 | 参考文献 |
|------|---------|
| REE 球粒陨石标准化配分图 | Sun & McDonough (1989) |
| 原始地幔标准化蛛网图 | Sun & McDonough (1989) |
| Th/Yb–Nb/Yb 源区判别图 | Pearce (2008) |

### 岩浆演化（1 张）

| 图解 | 参考文献 |
|------|---------|
| FeOt/MgO–SiO₂ 构造判别 | Miyashiro (1974) |

### 构造环境判别（3 张）

| 图解 | 参考文献 |
|------|---------|
| Nb–Zr–Y 三元构造判别 | Meschede (1986) |
| Hf/3–Th–Ta 三元构造判别 | Wood (1980) |
| Ti–V 构造判别图 | Shervais (1982) |

所有图件的多边形边界均对照 GCDkit 或原始文献验证，风格统一为线框模式。

## 快速开始

```bash
cd scripts
pip install -e .

python3 -c "
from igneous_wr_core import GeochemData, plot_recommended, set_out_dir

set_out_dir('./my_runs')
gd = GeochemData('./my_data.xlsx')
result = plot_recommended(gd)
"
```

输出：`my_runs/` 目录下生成 19 张 PNG 图件 + HTML 报告。

## 数据格式

输入为 Excel 文件（.xlsx），自动识别三种布局：

- **宽格式（推荐）**：第 1 行 = 元素名，第 A 列 = 样品名
- **标准格式**：第 1 行 = 样品名，第 A 列 = 元素名
- **转置格式**：同宽格式，通过启发式自动检测

标准物质行（BCR、BHVO、AGV 等）自动跳过。检测下限可配置为半值、零或 NaN。

## 项目结构

```
scripts/
├── igneous_wr_core.py              # 统一入口
├── igneous_wr/
│   ├── core/                       # 数据容器、化学计算、标准化
│   ├── io/                         # Excel 导入
│   ├── diagrams/                   # 19 张图件 + 注册表
│   ├── boundaries/                 # 分界线坐标（JSON）
│   ├── report/                     # 样式与 HTML 报告
│   ├── batch/                      # 批量出图
│   └── references/                 # 引文库（72 篇）
├── quick_validate.py               # 快速验证
├── generate_test_data.py           # 生成测试数据
└── run_test.py                     # 端到端测试
```

## 数据质量

标准化参考数据（球粒陨石、原始地幔、MORB、OIB、地壳等）来自 GCDkit 6.3.0 内置数据源，经多轮事实性审查。

- Pm（钷）已从所有标准化数据集中移除（Pm 无稳定同位素，不存在天然丰度）
- EM1/EM2/HIMU 地幔端元仅保留同位素比值，不预存 εNd（避免自相矛盾）
- CHONDRITE_MS95 全部 14 个 REE 值与 georefdatar 权威源一致
- Eu/Eu\* 和 Ce/Ce\* 使用几何平均公式

## 参考文献引用

每张图件右下角印有引用来源。完整参考文献列表（72 篇）见 HTML 报告末尾。

## License

MIT — Copyright (c) 2026 Chen Yuyang
