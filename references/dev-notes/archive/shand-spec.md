# Shand A/CNK–A/NK 铝质分类图规范

## 来源
GCDkit Shand.r (xlim=0.5~1.5, ylim=0~7)，2026-06-07 替换原自校准版。

## 坐标轴
- X 轴: A/CNK = Al₂O₃/(CaO+Na₂O+K₂O) (mol 比)
- Y 轴: A/NK = Al₂O₃/(Na₂O+K₂O) (mol 比)
- 范围: X=(0.5, 1.5), Y=(0, 7) — 对应 GCDkit Shand.r 原始范围

## 三条分界线
| 类型 | 定义 | 线型 | 含义 |
|------|------|------|------|
| 垂直线 | A/CNK = 1.0 | 黑色虚线 | 区分过铝质/偏铝质 |
| 水平线 | A/NK = 1.0 | 黑色虚线 | 区分过碱性 |
| 对角线 | A/CNK = A/NK (1:1) | 黑色点线 | 附加参考线 |

## 四个区域（新增 Undefined 区，对齐 GCDkit）
| 区域 | 条件 | 颜色 | 名称 |
|------|------|------|------|
| 左上 (Metaluminous) | A/CNK < 1, A/NK > 1 | 淡绿 #a8e6cf | Metaluminous (偏铝质/亚铝质) |
| 右上 (Peraluminous) | A/CNK > 1, A/NK > 1 | 淡蓝 #90caf9 | Peraluminous (过铝质) |
| 左下 (Peralkaline) | A/CNK < 1, A/NK < 1 | 淡粉 #f48fb1 | Peralkaline (过碱性) |
| 右下 (Undefined) | A/CNK > 1, A/NK < 1 | 淡灰 #e0e0e0 | Undefined (未定义) |

## GCDkit 矩形外框
四段独立线段构成闭合矩形，对应 GCDkit Shand.r 的 lines1~lines4：
- lines1：左上矩形 (Metaluminous 区域外框)
- lines2：右上矩形 (Peraluminous 区域外框)
- lines3：左下矩形 (Peralkaline 区域外框)
- lines4：右下矩形 (Undefined 区域外框)

## 标注
全部使用英文（WSL 环境 matplotlib 不支持中文）
