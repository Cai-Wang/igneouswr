# 地球化学数据表格式化输出

当用户需要将全岩数据输出为 "元素在行、样品在列" 的专业排版 Excel 表格时，使用此流程。

## 典型场景

- 用户有 GeochemData 对象（或原始 Excel），需要生成一份可直接用于论文或报告的排版表格
- 需要自动计算常用地球化学比值
- 需要带颜色/边框/冻结窗格等专业格式
- 需要从原始 Excel 中剔除不属于微量元素列的 K(ppm) 和 Al(ppm)

## 完整微量元素比值列表

以下比值按分组的顺序排列（每组间加空行分隔），紧跟在微量元素数据之后：

### 组1：REE参数
- **ΣREE** = La+Ce+Pr+Nd+Sm+Eu+Gd+Tb+Dy+Ho+Er+Tm+Yb+Lu
- **LREE/HREE** = (La+Ce+Pr+Nd+Sm+Eu) / (Gd+Tb+Dy+Ho+Er+Tm+Yb+Lu)
- **(La/Yb)N** = (La/0.237) / (Yb/0.161) — 球粒陨石标准化
- **(La/Sm)N** = (La/0.237) / (Sm/0.148)
- **(Gd/Yb)N** = (Gd/0.207) / (Yb/0.161)
- **Eu/Eu*** = (Eu/0.0563) / sqrt((Sm/0.148) × (Gd/0.207))
- **Ce/Ce*** = (Ce/0.613) / sqrt((La/0.237) × (Pr/0.093))

### 组2：HFSE特征比值
- **Nb/Ta**, **Zr/Hf**, **Th/U**, **Y/Ho**
- **Zr/Y**, **Ti/Y**, **Nb/Y**

### 组3：LILE相关
- **Rb/Sr**, **Rb/Ba**, **Ba/Sr**, **Sr/Y**
- **K/Rb** = K₂O × 8302 / Rb (K₂O wt% → K ppm)
- **Rb/Nb**, **Ba/Nb**, **Ce/Sr**

### 组4：过渡金属
- **Ni/Co**, **Cr/Ni**

### 球粒陨石标准化值 (McDonough & Sun 1995)

```python
chondrite = {
    'La': 0.237, 'Ce': 0.613, 'Pr': 0.093, 'Nd': 0.457,
    'Sm': 0.148, 'Eu': 0.0563, 'Gd': 0.207, 'Tb': 0.038, 'Dy': 0.254,
    'Ho': 0.057, 'Er': 0.167, 'Tm': 0.026, 'Yb': 0.161, 'Lu': 0.0245
}
```

## 用户偏好

- 布局：元素在行，样品在列。第1列=元素名，第2列起=样品编号
- **结构顺序**：主量元素 (wt.%) → **主量参数**（紧跟在主量元素之后）→ 微量元素 (ppm) → **微量元素比值**（紧跟在微量元素之后）
- K (ppm) 和 Al (ppm) 不是微量元素，不应出现在微量元素区域。它们是主量元素含量换算的ppm值。
- 微量元素按标准地化顺序排列：LILE (Rb→Cs→Ba→Sr→Pb→Tl) → HFSE (Nb→Ta→Zr→Hf→Y→Th→U) → REE (La→Lu) → 过渡金属 (Sc→Ti→V→Cr→Mn→Co→Ni→Cu→Zn→Ga) → 其他 (Li→Be→Mo→Sn→W)
- 需要计算的主量参数：Na₂O+K₂O, K₂O/Na₂O, Mg#, A/CNK, A/NK, K₂O/Al₂O₃
- 需要计算的微量元素比值：见下方完整列表

## 数值精度规范

| 列类型 | 小数位数 | 示例 |
|--------|---------|------|
| 主量氧化物 (wt%) | 2 | 73.61 |
| Na₂O+K₂O | 2 | 7.68 |
| K₂O/Na₂O | 3 | 0.080 |
| Mg#（molar） | 1 | 25.3 |
| A/CNK, A/NK | 3 | 1.124 |
| K₂O/Al₂O₃ | 4 | 0.0112 |
| 微量元素 (ppm) | 2（Ti用1位） | 29.94 |
| ΣREE, LREE/HREE, (La/Yb)N等 | 2 | 4.44 |
| Eu/Eu*, Ce/Ce* | 3 | 1.385 |
| Nb/Ta, Zr/Hf等HFSE比值 | 2 | 9.41 |
| Rb/Sr, Rb/Ba等LILE比值 | 4 | 0.3755 |
| K/Rb | 1 | 351.7 |
| Ni/Co, Cr/Ni | 2 | 24.46 |
| Zr/Y, Ti/Y | 2 | 2.89 |
| Nb/Y | 3 | 0.871 |

## 计算用公式

所有比值直接从原始数据（转置后）计算，而非从已格式化版本重算：

```python
# Na₂O+K₂O = Na2O + K2O
nk_vals = [a + b for a, b in zip(na2o_vals, k2o_vals)]

# K₂O/Na₂O = K2O / Na2O
# 需处理 Na2O=0 的除零情况
kn_vals = [k / n if n else 0 for k, n in zip(k2o_vals, na2o_vals)]

# Mg# (molar) = MgO/40.3044 / (MgO/40.3044 + TFe2O3*0.9/71.844) * 100
# 注：分子是 MgO wt% → mol，分母是 MgO + FeOt 的摩尔数
# FeOt = TFe₂O₃ × 0.8998
mg_vals = []
for mgo, tfe in zip(mgo_vals, tfe_vals):
    mg_mol = mgo / 40.3044
    feo = tfe * 0.8998
    fe_mol = feo / 71.844
    mg_vals.append(mg_mol / (mg_mol + fe_mol) * 100 if (mg_mol + fe_mol) > 0 else 0)

# A/CNK = Al₂O₃/(CaO + Na₂O + K₂O) — 摩尔比，需分子量换算
# Al₂O₃/101.96, CaO/56.08, Na₂O/61.98, K₂O/94.20
acnk_vals = []
for al, ca, na, k in zip(al_vals, ca_vals, na2o_vals, k2o_vals):
    al_mol = al / 101.96
    ca_mol = ca / 56.08
    na_mol = na / 61.98
    k_mol = k / 94.20
    denom = ca_mol + na_mol + k_mol
    acnk_vals.append(al_mol / denom if denom else 0)

# A/NK = Al₂O₃/(Na₂O + K₂O) — 摩尔比
# Al₂O₃/101.96, Na₂O/61.98, K₂O/94.20
ank_vals = []
for al, na, k in zip(al_vals, na2o_vals, k2o_vals):
    al_mol = al / 101.96
    na_mol = na / 61.98
    k_mol = k / 94.20
    denom = na_mol + k_mol
    ank_vals.append(al_mol / denom if denom else 0)

# K₂O/Al₂O₃ = K₂O(重量)/Al₂O₃(重量) — 重量比
ka_vals = [k / a if a else 0 for k, a in zip(k2o_vals, al_vals)]

# 注意：K₂O/Al₂O₃ 用的是主量氧化物重量百分比，不是ppm换算值

# Total = 主量氧化物之和（含TFe₂O₃，不含比值/K/Al列）
```

## Python 实现概要

使用 openpyxl 的 Workbook 从头构建，而非修改已有 Excel：

```python
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()
ws = wb.active

# 样式定义
header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
header_font = Font(name='微软雅黑', bold=True, color='FFFFFF', size=10)
section_fill = PatternFill(start_color='D6E4F0', end_color='D6E4F0', fill_type='solid')
section_font = Font(name='微软雅黑', bold=True, size=10)
data_font = Font(name='微软雅黑', size=9)
thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)

# 交替行颜色（偶数行用淡蓝色背景）
alt_fill = PatternFill(start_color='D9E2F3', end_color='D9E2F3', fill_type='solid')

# 写入标题头（第1行）
# A1="元素", B1=第一个样品名, C1=第二个样品名...
ws.cell(1, 1, '元素').font = header_font
for c, sid in enumerate(sample_ids, start=2):
    cell = ws.cell(1, c, sid)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal='center')

# 分节写入...
# freeze_panes = 'A2'  # 冻结表头
# 设置列宽和行高
```

## 已知陷阱

1. **Excel 格式陷阱**：原始文件如果是 "第1行=元素名、第1列=样品名" 这种标准宽表，GeochemData 的 `_load()` 判断逻辑可能误判为 transposed 格式。最好先读取验证布局再取数。

2. **数据在原始文件中有时带前后空格**（如 `"V "` 而不是 `"V"`）：读取元素名时必须 `.strip()`，否则微量元素会因名称不匹配而全部跳过。

3. **主量总和检查**：如果数据已经去LOI归一化（各氧化物总和≈100%），Total行应显示总和。如果是原始数据，Total行可加LOI列。

4. **Fe₂O₃ vs FeO 的 Mg# 计算**：用户数据中可能只有 TFe₂O₃（总铁转换为Fe₂O₃），没有单独的 FeO。Mg# 的 molar 公式需要 `FeOt = TFe₂O₃ × 0.8998`。

5. **微量元素中 K 和 Al**：部分数据文件的主量氧化物中已有 K₂O 和 Al₂O₃，微量元素列中还有 K(ppm) 和 Al(ppm)。两者同时存在时，氧化物体积（高精度4-5位小数）和微量元素值（低精度整数/1位小数）取主量版的氧化物值。表格中将 K₂O 和 Al₂O₃ 放在主量区域，**K(ppm) 和 Al(ppm) 不属于微量元素，不应出现在微量元素区域**。它们是从主量元素换算出来的，如果保留会误导分析。

6. **低于检出限的微量元素处理**：用户数据中低于检出限的值显示为字符串（如 `"<0.00"`）或空值。处理建议：
   - **推荐方案（用户已确认）**：保持原样写入，不替换为数值。即 `<0.00` 写为 `<0.00`，空值写为空。
   - **替代方案A（填0）**：V含量会偏低，如果V是重要判别元素会误导。
   - **替代方案B（填½ DL）**：地球化学标准做法，比0更接近真实分布。需要知道检出限值。
   - **用户最终选择**：V低于检出限用 `<0.00` 文本表达，不填0。
   - 写入Excel时，字符串值（如 `"<0.00"`）直接用openpyxl写入，不试图转为数值。
