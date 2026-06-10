# Shand vs Frost ASI-ANK — 历史对照

**注：Shand (CLS-04) 已于 2026-06-09 删除，不再在 IgneousWR 中维护。** 本文档作为 Frost ASI-ANK (CLS-31) 相关问题的历史背景保留。

## Shand (1947) — CLS-04（已删除）

| 项目 | 内容 |
|------|------|
| X轴 | A/CNK = Al₂O₃ / (CaO + Na₂O + K₂O) |
| Y轴 | A/NK = Al₂O₃ / (Na₂O + K₂O) |
| 范围 | x: 0.5~1.5, y: 0~7 |
| 线条 | h=1 (虚线) + v=1 (虚线) + **y=x 对角线 (虚线)** |
| 分区 | Metaluminous / Peraluminous / Peralkaline / Undefined (4个矩形框) |

对角线 y=x 的来源：Shand 定义中，Peralkaline 的判据是 A/NK < 1 (Na₂O+K₂O > Al₂O₃)，Metaluminous 是 A/CNK < 1 且 A/NK > 1。对角线 y=x 分隔 Peralkaline 区与未定义区的边界助记。

## Frost et al. (2001) Plot 3 — CLS-31

| 项目 | 内容 |
|------|------|
| X轴 | ASI = Al₂O₃ / (2CaO - 3.33P₂O₅ + Na₂O + K₂O) |
| Y轴 | A/NK = Al₂O₃ / (Na₂O + K₂O) |
| 范围 | x: 0.5~1.9, y: 0.6~3.5 |
| 线条 | **h=1 (虚线) + v=1 (虚线) 只有** |
| 分区 | metaluminous / peraluminous / peralkaline (3个区) |

**Frost 没有对角线。** GCDkit 源码 (Frost.r plot 3):
```r
lines1=list("abline", h=1)    # y=1 水平线
lines2=list("abline", v=1)    # x=1 垂直线
```
(见 Diagrams/Geotectonic/Frost.r 第 106-107 行)

## 公式差异

Shand 的 A/CNK 分母是 `CaO + Na₂O + K₂O`（忽略 P₂O₅）。

Frost 的 ASI 分母是 `2CaO - 3.33P₂O₅ + Na₂O + K₂O`（含 P₂O₅ 校正），且 CaO 系数为 2（不是 1）。注释中还保留了原始 Shand ASI（`Al₂O₃ / (CaO - 1.67P₂O₅ + Na₂O + K₂O)`）备查。
