# QAP Streckeisen (1976) 三角图校正规格

## 来源
用户审查（2026-05-27），基于 Streckeisen 1976 / Le Maitre et al. 2002 (IUGS)。

## 顶点
- **顶角 (top)**: Q (Quartz, 石英)
- **左下 (left)**: A (Alkali Feldspar, 碱性长石) — **不是 "P+F"**
- **右下 (right)**: P (Plagioclase, 斜长石)

## 分类界线

### Q 等值线（水平线，从 A 边到 P 边）
| Q 值 | 端点1 (Q, A, P) | 端点2 (Q, A, P) | 含义 |
|------|-----------------|-----------------|------|
| 20 | (20, 0, 80) | (20, 80, 0) | 贫/富石英分界 |
| 60 | (60, 0, 40) | (60, 40, 0) | 高石英区下限 |

线型：黑色实线 lw=1.2

### A/(A+P) 射线（从 Q 顶点沿 A-P 边出发）
公式：`A = K * (100 - Q)`, `P = (1 - K) * (100 - Q)`

| A/(A+P) | 端点1 (Q=0) | 端点2 (Q=90) | 含义 |
|---------|------------|------------|------|
| 0.10 | (0, 10, 90) | (90, 1, 9) | 斜长石/碱长石分界 |
| 0.35 | (0, 35, 65) | (90, 3.5, 6.5) | 花岗岩类分界 |
| 0.65 | (0, 65, 35) | (90, 6.5, 3.5) | 花岗岩类分界 |
| 0.90 | (0, 90, 10) | (90, 9, 1) | 碱长石富集分界 |

线型：黑色虚线 lw=0.8

## 区域名称（IUGS 标准，16 个）
从 Q 顶点到底边，按 A/(A+P) 和 Q 值交叉：

| Q 范围 | A/(A+P) 范围 | 岩石名称 |
|--------|-------------|---------|
| >60 | all | Quartzolite (>90% Q), Quartz-rich Granitoid (40~60% Q) |
| 20-60 | <0.10 | Alkali Granite (高 A) |
| 20-60 | 0.10-0.35 | Granite |
| 20-60 | 0.35-0.65 | Granodiorite |
| 20-60 | >0.65 | Tonalite |
| <20 | <0.10 | Quartz Alkali Syenite → Alkali Syenite (Q→0) |
| <20 | 0.10-0.35 | Quartz Syenite → Syenite (Q→0) |
| <20 | 0.35-0.65 | Quartz Monzonite → Monzonite (Q→0) |
| <20 | 0.65-0.90 | Quartz Monzodiorite → Monzodiorite (Q→0) |
| <20 | >0.90 | Quartz Diorite → Diorite/Gabbro (Q→0) |

## 颜色填充
Q>60 区：淡粉 #f8bbd0 alpha=0.20
20-60 区：淡绿 #c8e6c9 alpha=0.18
Q<20 区：淡黄 #fff9c4 alpha=0.12

## 坐标转换
```python
ternary_to_xy(Q%, A%, P%)  # top=Q, left=A, right=P
```
