# Pearce Th/Yb-Nb/Yb 判别图（SRC-03）技术参考

> **2026-07-17 重大更新：** 本图底图已从 Th/Nb=0.04/0.14 平行对角线带（旧版）重写为 GCDkit 6.3.0 精确底图。以下内容反映当前代码实现。

## 来源文献

- **原始文献**: Pearce, J.A. (2008) Geochemical fingerprinting of oceanic basalts with applications to ophiolite classification and the search for Archean oceanic crust. Lithos, 100, 14-48. → Fig. 2
- **参考值**: Sun, S.S. & McDonough, W.F. (1989) Chemical and isotopic systematics of oceanic basalts. GSA Special Publication 42, 313-345.
- **底图来源**: GCDkit 6.3.0 — `PearceNbThYb.r` + `Geotectonic/PearceNbThYb.r` 两文件
- **岩石标准参考**: GCDkit 6.3.0 — `data/Reservoirs.data`

## 原理

Th/Nb 的比率在部分熔融过程中几乎不变（Th 和 Nb 都是强不相容元素），但 Nb 在俯冲带中不活动而 Th 可以随俯冲流体迁移，所以高 Th/Nb（即高 Th/Yb-Nb/Yb 偏离）指示俯冲带影响。

用 Yb 标准化（Th/Yb vs Nb/Yb）消除了部分熔融程度变化的影响，比原始 Th-Nb 二元图更精确。

## 图面布局（GCDkit 6.3.0 底图标准）

**坐标轴**：双对数 log-log
- X = Nb/Yb, 范围 0.1-100
- Y = Th/Yb, 范围 0.01-10

### 底图实现（GCDkit 标准）

GCDkit 底图由一个背景填充多边形 + 一条单根虚线组成，而非平行对角线带：

1. **背景填充多边形**（淡蓝半透明 #B0D4F1, alpha=0.35）：
   ```
   fill_x = [0.1, 0.3, 100, 100, 80, 0.1]
   fill_y = [0.01, 0.01, 4.8, 10, 10, 0.01]
   ```
   左下角从 (0.1,0.01) 先右到 (0.3,0.01)，再沿底部直线到 (100,0.01)，然后上到 (100,4.8)——这是数据密集型区域的上限——再到 (80,10)，最后从 (80,10) 沿顶部回到 (0.1,0.01)。

2. **MORB-OIB 虚线阵列**（灰色虚线 --, lw=1.5, alpha=0.5）：
   - 一条斜率为 1.0196 的直线
   - 从 (Nb/Yb=0.1, Th/Yb=0.01) 到 (Nb/Yb=100, Th/Yb=10)
   - 标注 "MORB-OIB array" 于 X≈20, Y≈1.8 位置

### 参考点（均来自 GCDkit reservoirs.data → Sun & McDonough 1989 原始 ppm 值严格计算）

| 端元 | Th (ppm) | Nb (ppm) | Yb (ppm) | Nb/Yb | Th/Yb |
|------|----------|----------|----------|-------|-------|
| N-MORB | 0.12 | 2.33 | 3.05 | **0.764** | **0.0393** |
| E-MORB | 0.60 | 8.30 | 2.37 | **3.502** | **0.2532** |
| OIB | 4.00 | 48.0 | 2.16 | **22.222** | **1.852** |

注意：Pearce (2008) 原文 Fig.2 中印刷的参考点位置是近似值（N-MORB~0.98, E-MORB~4.30, OIB~26.67），使用了不同的 Yb 参考值。GCDkit 严格按 reservoirs.data 的 Yb 值计算，产生略有不同的结果。当前实现采用 GCDkit 精确值。

### 判别逻辑

- **蓝色多边形内**：非俯冲带环境（MORB, OIB, 洋脊）
- **向上偏离多边形**（高 Th/Yb 相对 Nb/Yb）：SSZ（俯冲带）环境
  - 微弱偏离 → 大洋弧 / 初始俯冲
  - 强烈偏离 → 大陆弧 / 地壳混染
- **阵列线**：MORB-OIB 趋势中心参考

### 与相关图件的关系

| 图号 | 图名 | 关系 |
|------|------|------|
| SRC-03 | Th/Yb-Nb/Yb (Pearce 2008) 本图 | GCDkit 底图版本 |
| SRC-11 | Nb/Yb-Th/Yb (Pearce 1995) | 坐标轴对调，较旧版本 |
| SRC-12 | Ti/Yb-Nb/Yb (Pearce 2008) | 配套图。用 Ti/Yb 判别地幔温度/柱深 |
| TEC-06 | Th/Yb-Ta/Yb (Pearce 1983) | 用 Ta 替代 Nb，区分 MORB/板内/钙碱性 |

## 代码位置

`igneous_wr/diagrams/_source.py` 中 `plot_pearce_2008()` 函数。

## 常见问题

1. **Nb 低于检测限** → 图跳过。检查 Th/Yb 值是否异常高
2. **Yb 接近 0 或缺失** → Th/Yb 和 Nb/Yb 都不可用
3. **数据完全在蓝色多边形内但用户期望是 SSZ** → 检查样品是否不是基性岩

## 校准历史

| 日期 | 变更 | 原因 |
|------|------|------|
| 2026-07-17 | 整函数重写为 GCDkit 6.3.0 底图 | 用户要求"用 GCDkit 底图信息"绘制；旧版使用 AI 猜测的 Th/Nb=0.04/0.14 平行带，缺少 GCDkit 实际的 polygon+single-array-line 设计；参考点从近似值改为 reservoirs.data 精确值；移除冗余元素（UCC/1:1/箭头） |
| 2026-06-25 | 旧版修正（原 Th/Nb=0.04/0.14 带 + 近似参考点 + UCC） | 用户当时要求修正底图——后被 07-17 更新完全取代 |

## 与 GCDkit R 源码的对应关系

- `PearceNbThYb.R`（主底图脚本）：定义 THYB/NBYB 比值，绘制背景多边形和 MANTA 虚线
- `Geotectonic/PearceNbThYb.r`（地体构造分类版）：与主脚本共享底图逻辑，增加构造区域标注
- `data/Reservoirs.data`：N-MORB/E-MORB/OIB 的 Th/Nb/Yb ppm 来源
