---
name: IgneousWR
description: 岩浆岩全岩地球化学数据处理与图解绘制 — Igneous Whole-Rock 绘图引擎，读取 Excel 数据 → 19种精选图件 + HTML报告
---

# IgneousWR — Igneous Whole-Rock 绘图引擎

全岩地球化学数据处理与图解绘制。读取合并的 Excel，自动判断岩性，完成 **19 种精选图件**并生成 HTML 图集报告。

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

## 精选图目录（19 张）

### 分类/岩石系列（12 张）
- CLS-01 Middlemost 1994 TAS（火山岩）— verified
- CLS-02 Middlemost 1985 K₂O-SiO₂ — verified
- CLS-03 Irvine & Baragar 1971 AFM — verified
- CLS-04 Peccerillo & Taylor 1976 K₂O-SiO₂ — needs_review
- CLS-05 Winchester & Floyd 1977 Zr/TiO₂-Nb/Y — verified
- CLS-06 Hastie 2007 Co-Th — verified
- CLS-10 Mullen 1983 TiO₂-MnO-P₂O₅ — experimental
- CLS-13 Middlemost 1994 TAS（深成岩）— verified
- CLS-17 Frost 2001 Fe#-SiO₂ — verified
- CLS-29 Pearce 1996 Zr/Ti-Nb/Y — verified
- CLS-30 Frost 2001 MALI-SiO₂ — verified
- CLS-31 Frost 2001 ASI-A/NK — verified

### 源区性质（3 张）
- SRC-01 Sun & McDonough 1989 REE 配分图 — verified
- SRC-02 Sun & McDonough 1989 蛛网图 — verified
- SRC-03 Pearce 2008 Th/Yb-Nb/Yb — verified

### 岩浆演化（1 张）
- EVO-02 Miyashiro 1974 FeOt/MgO-SiO₂ — verified

### 构造环境判别（3 张）
- TEC-01 Meschede 1986 Nb-Zr-Y 三角图 — experimental
- TEC-02 Wood 1980 Hf/3-Th-Ta 三角图 — experimental
- TEC-05 Shervais 1982 Ti-V — verified

## 数据输入

3 种 Excel 布局自动检测（wide / standard / transposed）。推荐 wide 格式：Row1=元素名横铺，Col A=样品名。自动跳过标准物质行（BCR/BHVO等）。检测模式可用 `print(gd._detected_mode)` 查看。

## 目录结构

```
scripts/
├── igneous_wr_core.py          # 门面 API
├── igneous_wr/
│   ├── boundaries/             # 坐标边界 JSON
│   ├── core/                   # 化学计算、标准化、三元变换、数据类
│   ├── io/excel.py             # Excel 读取
│   ├── diagrams/               # 绘图函数 + 注册表
│   ├── report/style.py         # 样式系统
│   └── batch/                  # 批量出图 + 推荐
├── tests/                      # 单元测试
├── quick_validate.py           # 验证脚本
├── generate_test_data.py       # 数据生成
└── merge_excel.py              # Excel 合并
```

## 删除图件流程

1. 删注册表条目（`registry.py` `DIAGRAM_REGISTRY`）
2. 删 import（`registry.py` 顶部、`igneous_wr_core.py` re-export）
3. 删函数体（`_classification.py` / `_source.py` / `_evolution.py` / `_tectonic.py`）
4. 清理残留引用 + 无用 import
5. 更新 SKILL.md 图目录和计数
6. 运行 `python3 quick_validate.py --quick` 验证

## 参考文件

- `references/code-review-checklist.md` — 审查清单
- `references/known-pitfalls.md` — 已知陷阱与修复原则
- `references/code-review-patches.md` — 审查问题修复模式

## 核心原则

- 线段风格：主分界线 `#333333` lw=1.5 实线，次分界线 `#666666` lw=1.2 虚线，TAS 多边形 lw=0.8，三元图场界线 lw=1.5
- 标签风格：统一 `#444444`，二元图区域=10，TAS 多边形=8.5，三元图区域=11
- 所有图表纯 matplotlib，无需 pyrolite。AI 不做数值计算（标准化、FeOt 换算等全在 Python 代码中）
- 边界数据外置 JSON（`boundaries/`），修改坐标不翻函数
- 每个修改后 `python3 quick_validate.py --quick` 回归验证
- 修改核心逻辑（chem/data/normalize）后运行 `python3 -m pytest tests/ -v` 确保单元测试通过
- 二元图全部通过 `style_ax()` 统一坐标轴（无网格、Times New Roman、刻度向内）
- 化学式 LaTeX 下标 `$_n$`，禁止 Unicode 下标
- 对数轴刻度用真数（0.01, 0.1, 1, 10…），禁用科学计数法
- 除 SRC-03 外所有图纯黑白线框，不渲染彩色填充

## 相关技能

- `gcdkit-translator` — GCDkit R → Python 翻译规范
