# Pearce Th/Yb-Nb/Yb 判别图（SRC-03）技术参考

## 来源文献

- **原始文献**: Pearce, J.A. (2008) Geochemical fingerprinting of oceanic basalts with applications to ophiolite classification and the search for Archean oceanic crust. Lithos, 100, 14-48. → Fig. 2
- **进阶应用**: Pearce, J.A. (2014) Immobile Element Fingerprinting of Ophiolites. Elements, 10(2), 101-108. → Fig. 5A
- **参考值**: Sun, S.S. & McDonough, W.F. (1989) Chemical and isotopic systematics of oceanic basalts. GSA Special Publication 42, 313-345.

## 原理

Th/Nb 的比率在部分熔融过程中几乎不变（Th 和 Nb 都是强不相容元素），但 Nb 在俯冲带中不活动而 Th 可以随俯冲流体迁移，所以高 Th/Nb（即高 Th/Yb-Nb/Yb 偏离）指示俯冲带影响。

用 Yb 标准化（Th/Yb vs Nb/Yb）消除了部分熔融程度变化的影响，比原始 Th-Nb 二元图更精确。

## 图面布局（Pearce 2014 Fig. 5A）

**坐标轴**：双对数 log-log
- X = Nb/Yb, 范围 0.05-80
- Y = Th/Yb, 范围 0.01-80

### MORB-OIB 阵列（灰色半透明带状区域）

三条参考对角线组成带状结构，基于 Pearce (2008) Fig. 2a 严格定义的对角线阵列：

- 下边界虚线: Th/Nb = **0.04**  → Th/Yb = 0.04 × (Nb/Yb)  |  log(Th/Yb) = log(Nb/Yb) − 1.398
- 上边界虚线: Th/Nb = **0.14**  → Th/Yb = 0.14 × (Nb/Yb)  |  log(Th/Yb) = log(Nb/Yb) − 0.854
- 填充: #D0D0D0 alpha=0.20

阵列在对数空间中为斜率为 1 的平行对角线。上界代表富集地幔极限（略高于 PM 的 ~0.12），下界代表极度亏损地幔下限（略低于 N-MORB 的 ~0.05）。

### 参考点（均来自 Sun & McDonough 1989 原始 ppm 含量计算）

| 端元 | Th | Nb | Yb | Nb/Yb | Th/Yb | Th/Nb |
|------|-----|-----|-----|-------|-------|-------|
| N-MORB | 0.12 | 2.33 | 2.37 | **0.98** | **0.051** | 0.0515 |
| E-MORB | 0.60 | 8.30 | 1.93 | **4.30** | **0.311** | 0.0723 |
| OIB | 4.00 | 48.0 | 1.80 | **26.67** | **2.222** | 0.0833 |
| 原始地幔 PM | 0.0795 | 0.658 | 0.441 | 1.49 | 0.180 | 0.1208 |

### 地壳混染端元

- **UCC (Rudnick & Gao 2003)**: Nb=12.0, Yb=2.2, Th=10.5 → (X=5.45, Y=4.77), Th/Nb=0.875
- 大陆地壳混染矢量指向右上方

### 判别逻辑

- **MORB-OIB 阵列内**（灰色带内）：非俯冲带环境（MORB, OIB, 洋脊）
- **向上偏离阵列**（高 Th/Yb 相对 Nb/Yb）：SSZ（俯冲带）环境
  - 微弱偏离 → 大洋弧 / 初始俯冲
  - 强烈偏离 → 大陆弧 / 地壳混染
- **1:1 线** (Th/Yb = Nb/Yb)：强烈 Th 富集的参考边界

### 参考区域（经验性）

- **Oceanic Arcs**: X=0.5-2.0, Y=0.4-2.0，淡橙半透明
- **Continental Arcs**: X=2.0-5.0, Y=0.8-6.0，更深橙半透明
- **SZ 箭头**: 从 Nb/Yb≈0.8 处垂直向上，标注俯冲带方向

## 与相关图件的关系

| 图号 | 图名 | 关系 |
|------|------|------|
| SRC-03 | Th/Yb-Nb/Yb (Pearce 2008) | 本图。Th/Nb 替代指标 |
| SRC-11 | Nb/Yb-Th/Yb (Pearce 1995) | 坐标轴对调，较旧版本 |
| SRC-12 | Ti/Yb-Nb/Yb (Pearce 2008) | 配套图。用 Ti/Yb 判别地幔温度/柱柱深度（洋脊类型细分） |
| TEC-06 | Th/Yb-Ta/Yb (Pearce 1983) | 用 Ta 替代 Nb（类似但 Ta 数据更少），区分 MORB/板内/钙碱性 |

## 代码位置

`igneous_wr/diagrams/_source.py` 中 `plot_pearce_2008()` 函数。

## 常见问题

1. **Nb 低于检测限** → 图跳过。检查 Th/Yb 值是否异常高（可能暗示 Nb 数据质量问题）
2. **Yb 接近 0 或缺失** → Th/Yb 和 Nb/Yb 都不可用。用原始 Th-Nb 图作为替代
3. **数据全部在阵列下方** → 可能 Nb 偏高（分析误差，如 Nb 被锆石污染）或 Th 偏低
4. **数据完全落在灰色带内但用户期望是 SSZ** → 检查样品是否不是基性岩（中酸性岩浆 Th-Nb 行为不同）

## 未来改进空间

- 从 Pearce (2008) 原文 Fig.2 经数字化提取更精确的阵列边界数据（当前使用 Th/Nb=0.04/0.14 对角线，与原文接近但可进一步验证）
- 加入文献中具体蛇绿岩数据（Troodos, Oman 等）作为参考系
- 考虑增加俯冲组分百分比示意箭头（如 5%, 10% 等比例）
- 当前代码未实现 Oceanic Arcs / Continental Arcs 参考区，spec 中提及但未编码
