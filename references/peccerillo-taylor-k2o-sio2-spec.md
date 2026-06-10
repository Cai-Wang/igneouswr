# K₂O–SiO₂ Peccerillo & Taylor (1976) 分类图规范

## 来源
GCDkit `PeceTaylor.r`，extrapolated=TRUE（默认），引用 Peccerillo & Taylor (1976) Fig.2（经 Rickwood 1989 改编）。

## 坐标轴
- X 轴: SiO₂ (wt.%), 范围 45–78
- Y 轴: K₂O (wt.%), 范围 0–7

## 三条分界线（多段折线，源自 GCDkit 精确坐标）

| 分界 | 点序列 | 特征 |
|------|--------|------|
| Tholeiite / Calc-alkaline | (48,0.3)→(52,0.5)→(56,0.7)→(63,1)→(70,1.3)→(78,1.6) | 最左侧起始 |
| Calc-alkaline / High-K | (48,1.2)→(52,1.5)→(56,1.8)→(63,2.4)→(70,3)→(75,3.43) | 中等斜率 |
| High-K / Shoshonite | (48,1.6)→(52,2.4)→(56,3.2)→(63,4)→(70,4.8) | 最陡，止于 x=70 |

注意：GCDkit 支持 extrapolated=TRUE/FALSE 切换。extrapolated=TRUE 是默认值，边界向右延伸至 x=78/75。

## 四个��域标签（参考 GCDkit PeceTaylor.r temp3）

| 标签 | 位置 | 对齐 |
|------|------|------|
| "Tholeiite Series" | x=77, y=0.7 | ha='right', va='center' |
| "Calc-alkaline\nSeries" | x=77, y=2.4 | ha='right', va='center' |
| "High-K calc-alkaline\nSeries" | x=77, y=4 | ha='right', va='center' |
| "Shoshonite Series" | x=47, y=4.5 | ha='left', va='center' |

标签风格与 CLS-02 Middlemost 1985 一致：统一颜色 `#444444`，不分区着色。

## 与 CLS-02 Middlemost 1985 区别

| 对比项 | CLS-02 (Middlemost 1985) | CLS-04 (P&T 1976) |
|--------|--------------------------|-------------------|
| 分界线 | 3条直线（端点坐标法） | 3条多段折线（5-6点） |
| xlim | 42–82 | 45–78 |
| ylim | 0–8 | 0–7 |
| 分类名 | Low-K Tholeiitic / Medium-K / High-K / Shoshonitic | Tholeiite / Calc-alkaline / High-K calc-alkaline / Shoshonite |
| 标签 y 位置 | 右边缘 x=80 处各区间中点 | GCDkit 硬编码位置 |
