# Pearce (1996) 对 Winchester & Floyd (1977) 的修改（GCDkit 实现）

*A user's guide to basalt discrimination diagrams* (Pearce, 1996) 中重新校准了 WF1977
的 Zr/TiO₂ vs Nb/Y 判别图。**⚠️ GCDkit 实现版本（被 `CLS-29` 采用）使用的 Y 轴为 Zr/Ti 而非 Zr/TiO₂，且范围不同。**

## 1. 坐标系对比

| 项目 | WF1977 (原始) | Pearce (1996) 原文 | GCDkit 实现 (CLS-29) |
|------|---------------|---------------------|----------------------|
| Y轴 | Zr/TiO₂ (双对数) | Zr/TiO₂ (双对数) | **Zr/Ti (双对数)** |
| Y轴范围 | 0.001 ~ 1 | 10 ~ 1000 | **0.0007 ~ 3** |
| X轴 | Nb/Y (双对数) | Nb/Y (双对数) | Nb/Y (双对数) |
| X轴范围 | 0.01 ~ 15 | 0.1 ~ 10 | **0.008 ~ 120** |

换算关系：
- Zr/TiO₂ (原始 WF1977 比值) = Zr(ppm) / TiO₂(wt%)
- Zr/Ti (GCDkit 实现) = Zr(ppm) / Ti(ppm)
- 关系：Zr/TiO₂ ≈ Zr/Ti × 0.599（因 Ti = TiO₂ × 0.599）

因此 CLS-29 的 Y 轴数值范围大约是 CLS-05（WF1977 v11）的 0.599 倍。

## 2. 亚碱性/碱性分界线修改

**WF1977 (原始)：**
- 以 Nb/Y≈0.6 的垂直虚线为界
- 左侧 = Subalkaline series，右侧 = Alkaline series

**Pearce (1996) / GCDkit (CLS-29)：**
- 重新定义为正斜率 4 点多段线（在 log-log 空间中对角线）
- 端点：`(Nb/Y=0.01, Zr/Ti=0.0076)→(0.67,0.024)→(2.81,0.0355)→(50,0.0781)`
- 以 Nb/Y=0.67 和 Nb/Y=2.81 作辅助垂直虚线

## 3. GCDkit 中的字段分布（CLS-29 精确底图）

在 log-log 双对数坐标系下，10 个区域被定义：

| 区域 | Nb/Y范围 | Zr/Ti范围 | 填充色 |
|------|----------|-----------|--------|
| Basalt | <0.67 | <0.024 | 绿色 |
| Alkali Basalt | 0.67~2.81 | <0.0355 | 蓝色 |
| Foidite | >2.81 | <0.0781 | 浅蓝 |
| Andesite / Basaltic Andesite | <0.67 | 0.024~0.082 | 黄色 |
| Trachyandesite | 0.67~2.81 | 0.0355~0.12 | 橙色 |
| Tephriphonolite | >2.81 | 0.0781~0.2663 | 红色 |
| Rhyolite / Dacite | <0.67 | >0.082 | 深红 |
| Trachyte | 0.67~2.81 | >0.12 | 橙黄 |
| Phonolite | >2.81 | >0.2663 | 紫色 |
| Alkali Rhyolite | 顶部V形 | 0.2~2 | 红色 |

上下两条对角线：
- 下分界线（subalkaline/alkaline）：`(0.01,0.0076)→(0.67,0.024)→(2.81,0.0355)→(50,0.0781)`
- 上分界线（andesite/rhyolite-dacite）：`(0.01,0.026)→(0.67,0.082)→(2.81,0.12)→(50,0.2663)`
- 顶部 V 形：`(0.065,2)→(0.67,0.2)→(5.52,2)`
- 垂直虚线：Nb/Y=0.67, Nb/Y=2.81

## 4. 当前代码中的实现

### CLS-05 (`plot_winchester_floyd`)
- 用户逐点校准的 v11 数据（67 节点 × 9 条边），来自 `wf1977_v11.py`
- Y 轴: Zr/TiO₂ 比值（原始 WF1977 版本）
- 坐标已逐点核实

### CLS-29 (`plot_pearce1996`)
- 新增于 2026-06-01
- 坐标来自 GCDkit `Pearce1996.r` 源码精确提取
- Y 轴: Zr/Ti（与 CLS-05 不同）
- 10 个区域彩色填充 + 黑色边界线 + 竖虚线
- log-log 双对数坐标系
- 注册为 `CLS-29_Pearce1996_NbY_ZrTi.png`

## 5. 参考资料

- Pearce, J.A., 1996. A user's guide to basalt discrimination diagrams. *Trace element geochemistry of volcanic rocks: applications for massive sulphide exploration*, 12, pp.79-113.
- Winchester, J.A. and Floyd, P.A., 1977. Geochemical discrimination of different magma series and their differentiation products using immobile elements. *Chemical Geology*, 20, pp.325-343.
- GCDkit 6.3, `Pearce1996.r`, `/tmp/GCDkit/inst/Diagrams/Classification/English/Pearce1996.r`
