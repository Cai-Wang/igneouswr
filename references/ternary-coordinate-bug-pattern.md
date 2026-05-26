# 三元图坐标传递 Bug 模式

## 背景

2026-05-17 审计中发现 `_classification.py` 中两个三元图函数存在相同 bug：传给 `plot_samples_ternary()` 的是原始三元百分比值而非笛卡尔坐标，导致样品投点位置完全错误。

## Bug 模式

```python
# ❌ 错误模式：传三元百分比值
_style.plot_samples_ternary(ax, an_norm, ab_norm, or_norm, labels, ...)
# an_norm + ab_norm + or_norm ≈ 100 (三元百分比)

# ✅ 正确模式：转换到笛卡尔坐标再传
xy_pairs = [an_ab_ternary_to_xy(a, ab, o) for a, ab, o in zip(an_norm, ab_norm, or_norm)]
x_vals = [p[0] for p in xy_pairs if not np.isnan(p[0])]
y_vals = [p[1] for p in xy_pairs if not np.isnan(p[1])]
_style.plot_samples_ternary(ax, x_vals, y_vals, labels, ...)
```

## 关键函数签名

```python
# _style.py:416
def plot_samples_ternary(ax, x_arr, y_arr, labels, ...):
    # x_arr, y_arr = 笛卡尔坐标 (不是三元百分比)
```

## 检查标准

- 场界多边形用转换后坐标画的 → 样品点也必须用转换后坐标
- 每个三元图内部都有自己的转换函数（`an_ab_ternary_to_xy`、`qapf_to_xy`）或共用的 `ternary_to_xy`
- 转换函数定义的位置不重要，重要的是**调用处是否用了转换**

## 受影响的函数（已修复）

1. `plot_an_ab_or()` — 第 533 行 → 用 `an_ab_ternary_to_xy()`
2. `plot_qapf()` — 第 671 行 → 用 `qapf_to_xy()`

## 未受影响（已验证）

`_tectonic.py` 中所有三个三元图（Meschede, Wood, Pearce-Cann）在传给 `plot_samples_ternary` 前已经过 `ternary_to_xy()` 转换，数据流正确。

## 新增三元图时的检查要点

新增三元图时，代码审查必须逐行验证：

1. 样品点数据流：原始三元值 → 转换函数 → `plot_samples_ternary(x, y, ...)`
2. 场界多边形：也是用同一转换函数画的（一致性检查）
3. 参考线/等值线：是否也用了转换
4. 确保传给 `plot_samples_ternary` 的 `x` / `y` 不是原始三元值
