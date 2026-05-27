# K₂O–SiO₂ Middlemost (1975) 分类图规范

## 来源
用户审查（2026-05-27），基于 Middlemost (1975) / Le Maitre et al. (2002, Fig. 4.4)。

## 坐标轴
- X 轴: SiO₂ (wt.%), 范围 42-82
- Y 轴: K₂O (wt.%), 范围 0-8

## 三条分界线（端点坐标法，禁止斜率公式归零）
| 分界 | 端点1 | 端点2 | 线型 |
|------|-------|-------|------|
| Low-K / Medium-K | (45, 0.5) | (75, 2.5) | 黑色实线 |
| Medium-K / High-K | (50, 1.5) | (75, 4.0) | 黑色虚线 |
| High-K / Shoshonitic | (55, 2.5) | (75, 6.0) | 黑色点划线 |

**禁止使用斜率公式**如 `y = 0.025*x - 2.0` — 此类公式将所有界线归零到 K₂O=0 的 X 轴，在地球化学上不合理（基性岩不可能 K₂O=0 且作为分界点）。

## 四个区域
| 区域 | 颜色 | 填充区域定义 |
|------|------|-------------|
| Shoshonitic | 淡粉 #f48fb1 | High-K分界线以上至y=8 |
| High-K Calc-alkaline | 淡蓝 #90caf9 | Medium-K与High-K分界线之间 |
| Medium-K Calc-alkaline | 淡绿 #a5d6a7 | Low-K与Medium-K分界线之间 |
| Low-K Tholeiitic | 淡黄 #fff9c4 | Low-K分界线以下至y=0 |

## 排版规范
- **去除网格**：`ax.grid(False)` 在 `style_ax()` **之后**
- **刻度向内**：`style_ax()` 已自动设置 `tick_params(direction='in')`
- **区域标注用英文**（WSL 不支持中文）

## 常见错误
- ❌ 用 `np.linspace(45, 80, 20)` 生成 x 点然后代入线性公式 → 每条线从 K₂O=0 出发，严重偏离标准
- ❌ 图上显示网格线 → 分类图不需要网格线，只干扰分区界线判断
