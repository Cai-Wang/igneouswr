# CLS-11 Jensen (1976) 阳离子分类三角图 — 校正记录

## 状态
✅ 已完成（2026-05-27 第二期校正）

## 修正内容

### 端元修正（最重要）
**原错误**：使用氧化物重量百分比作为三角图端元坐标（Al₂O₃ vs FeOt+TiO₂ vs MgO）
- 这实际上只是做了 FeOt 换算（FeO+0.9×Fe₂O₃），但三个角仍然是 wt% 值
- 结果：不同元素因为摩尔质量不同，不能在同一三角空间正确比例

**修正后**：严格按 Jensen (1976) 原文，使用**阳离子数比例**
- 先将 Fe₂O₃ 按 85:15 分裂为 Fe³⁺ 和 FeO（Jensen 默认）

### 阳离子数计算公式

**元素 → 摩尔 × 价态**：

```
# 顶角 (Al + Fe³⁺ + Ti)
top = (Al₂O₃ / 101.96 × 2) + (Fe₂O₃ / 159.69 × 2) + (TiO₂ / 79.866 × 1)

# 左下 (Mg + Fe²⁺ + Mn)
left = (FeO / 71.844 × 1) + (MgO / 40.304 × 1) + (MnO / 70.937 × 1)

# 右下 (Ca + Na + K)
right = (CaO / 56.08 × 1) + (Na₂O / 61.98 × 2) + (K₂O / 94.20 × 2)
```

### Fe 的分配

```python
# 从 TFe₂O₃ 得到 FeO (total)
feot = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))

# 85:15 分配
feo_m = feot * 0.85         # Fe²⁺ (进入 left 角)
fe2o3_m = feot * 0.15 * 71.844/71.844 * 159.69/71.844
# 简化: fe2o3_m = feot * 0.15 * 159.69/71.844
# 但直接用 fe2o3 的质量而非 FeO 的质量: fe2o3_m = feot * 0.15 * (159.69/71.844)
```

**实际代码**（`_classification.py` `plot_jensen` 函数）：
```python
# Fe²⁺/Fe³⁺ 85:15
feo = feot * 0.85
fe2o3 = feot * 0.15 * 2.222  # 159.69/71.844 ≈ 2.222

# 阳离子数
top = (gd.get('Al2O3') / 101.96 * 2 +
       fe2o3 / 159.69 * 2 +
       gd.get('TiO2') / 79.866 * 1)
left = (feo / 71.844 * 1 +
        gd.get('MgO') / 40.304 * 1 +
        gd.get('MnO') / 70.937 * 1)
right = (gd.get('CaO') / 56.08 * 1 +
         gd.get('Na2O') / 61.98 * 2 +
         gd.get('K2O') / 94.20 * 2)
```

### 所需元素
所有 8 个元素全部必需：Al₂O₃, FeO/TFe₂O₃, TiO₂, MgO, MnO, CaO, Na₂O, K₂O

### 分界线坐标
使用 SVG 提取的 19 条 `jensen_all` 边界路径，定义在函数体内。分界线将三角图分为 4 个区域：
1. **Komatiitic** — 高 Mg 区
2. **Tholeiitic** — 高 Fe 区
3. **Calc-alkaline** — 中间过渡区
4. **High-Al calc-alkaline** — 高 Al 区

### 遗留问题
- Fe²⁺/Fe³⁺ 比例 85:15 是 Jensen 默认值，实际可根据岩石氧化状态调整
- 分界线坐标来自 SVG 提取（WSL 环境下），尚未与文献原文逐一比对
- 场域标签位置基于经验放置（不压在分界线上），用户可能调整
