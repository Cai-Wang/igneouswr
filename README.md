# IgneousWR

**Igneous Whole-Rock Geochemical Plotting Engine** · 全岩地球化学批量成图工具

输入 Excel 全岩地球化学数据，一键输出 19 张期刊投稿级图件（PNG）+ 自包含 HTML 报告。纯 Python，无需 R 环境，无需 GUI。

---

## 快速开始

```bash
pip install igneouswr   # 安装
igneouswr run data.xlsx # 出图
```

输出：`./runs/` 目录下 19 张 PNG + HTML 报告，每张图右下角印有引用来源。

---

## 已实现 19 张图解

### 分类 · 岩石系列（12 张）

| 图解 | 参考文献 |
|------|---------|
| TAS 全碱-硅分类（火山岩） | Middlemost (1994) |
| TAS 全碱-硅分类（深成岩） | Middlemost (1994) |
| K₂O–SiO₂ 钾系列分类 | Middlemost (1985) |
| K₂O–SiO₂ 钾系列分类 | Peccerillo & Taylor (1976) |
| AFM 钙碱性-拉斑系列判别 | Irvine & Baragar (1971) |
| Zr/TiO₂–Nb/Y 分类 | Winchester & Floyd (1977) |
| Zr/Ti–Nb/Y 火山岩分类 | Pearce (1996) |
| Co–Th 系列+岩性判别 | Hastie et al. (2007) |
| TiO₂–MnO–P₂O₅ 基性岩构造判别 | Mullen (1983) |
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

---

## 数据格式

输入为 Excel 文件（.xlsx），**自动识别三种常见布局**：

| 布局 | 第 1 行 | 第 A 列 |
|------|---------|---------|
| 宽格式（推荐） | 元素名（SiO₂, TiO₂…） | 样品名 |
| 标准格式 | 样品名 | 元素名 |
| 转置格式 | 同宽格式，自动检测 | |

标准物质行（BCR、BHVO、AGV 等）自动跳过。检测下限可配置为半值、零或 NaN。

---

## 数据质量

- 标准化参考数据（球粒陨石、原始地幔、MORB、OIB）来自 **GCDkit 6.3.0** 内置数据源，经多轮事实性审查
- CHONDRITE_MS95 全部 14 个 REE 值与 **georefdatar** 权威源一致
- Eu/Eu\* 和 Ce/Ce\* 使用**几何平均**公式（非算术平均）
- 引文库 72 篇，每张图右下角印有引用来源，报告末尾有完整文献列表
- Pm 已从 REE 标准化数据集中移除（无稳定同位素）

---

## 项目结构

```
scripts/
├── igneous_wr_core.py           # 统一入口
├── igneous_wr/
│   ├── core/                    # 数据容器、化学计算、标准化
│   ├── io/                      # Excel 导入
│   ├── diagrams/                # 19 张图件 + 注册表
│   ├── boundaries/              # 分界线坐标（JSON）
│   ├── report/                  # Matplotlib 样式 + HTML 报告
│   ├── batch/                   # 批量出图
│   └── references/              # 引文库（72 篇）
```

---

## License

MIT — Copyright (c) 2026 Chen Yuyang

Repository: [github.com/Cai-Wang/igneouswr](https://github.com/Cai-Wang/igneouswr)
