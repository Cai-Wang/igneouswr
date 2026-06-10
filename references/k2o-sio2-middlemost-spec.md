# K₂O–SiO₂ Middlemost (1985) 分类图规范

## 来源
用户审查（2026-05-27），基于 Middlemost (1985) "Magmas and Magmatic Rocks" 图9。
标签布局参考 GCDkit Peccerillo & Taylor (1976) `PeceTaylor.r` `temp3` 块风格（2026-06-09 修正）。

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
| 区域 | 标签位置 | 说明 |
|------|---------|------|
| Low-K Tholeiitic | x=80, y=1.4, ha='right', va='center' | 右边缘，Low-K与Medium-K界线之间中点 |
| Medium-K Calc-alkaline | x=80, y=3.7, ha='right', va='center' | 右边缘，Medium-K与High-K界线之间中点 |
| High-K Calc-alkaline | x=80, y=5.7, ha='right', va='center' | 右边缘，High-K与Shoshonitic界线之间中点 |
| Shoshonitic | x=44, y=7.4, ha='left', va='center' | 左边缘，Shoshonitic区 |

**标签布局逻辑**（参考 GCDkit Peccerillo & Taylor 1976 `PeceTaylor.r` `temp3`）：
- 前3个区域标签沿 x=80 右边缘右对齐（`adj=c(1,0.5)` → `ha='right', va='center'`）
- Shoshonitic 在 x=44 左边缘左对齐（`adj=c(0,0.5)` → `ha='left', va='center'`）
- 所有标签统一颜色 `#444444`，不分区着色

## 排版规范
- **去除网格**：`ax.grid(False)` 在 `style_ax()` **之后**（现 style_ax 已不添加网格）
- **刻度向内**：`style_ax()` 已自动设置 `tick_params(direction='in')`
- **区域标注用英文**（WSL 不支持中文）

## 常见错误
- ❌ 用 `np.linspace(45, 80, 20)` 生成 x 点然后代入线性公式 → 每条线从 K₂O=0 出发，严重偏离标准
- ❌ 图上显示网格线 → 分类图不需要网格线，只干扰分区界线判断
- ❌ 标签放在图中间区域用 `ha='center'` → 用户要求 GCDkit P&T 风格（右侧右对齐 + 左侧左对齐）
- ❌ 双换行符 `\\n` 在 Python 字符串中变成字面反斜杠 → 使用 `\n`（真换行符），patch 后必须用 `cat -A` 验证
