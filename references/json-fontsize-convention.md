# IgneousWR JSON 边界数据中的 fontsize 字段约定

## 设计意图

JSON 文件中 `fontsize` 字段的值是**裸图基准字号**（裸图宽度 203mm，即 matplotlib `figsize=(8,6)` 的物理宽度）。

运行时，代码中 `ax.text(fontsize=json_val * _style.base_fs(ax))` 自动按实际 ax 物理宽度等比缩放。

- 裸图 203mm → `base_fs(ax) ≈ 1.0` → 字号不变
- 拼版 cell 75mm → `base_fs(ax) ≈ 0.37` → 字号自动缩小
- 下限 0.25（极小 cell 也不丢标签）

## JSON fontsize 值的实际情况

不同图、甚至同一张图的不同标注，fontsize 值并不统一。原因有两类：

### 有规律的设计差异

如 Shervais：
- `ray_labels[].fontsize: 8` — 射线旁边的小字注释（斜体）
- `region_labels[].fontsize: 10` — 分区名（粗体）

这是设计意图：注释 < 主标注。`base_fs(ax)` 缩放后层级关系保持不变。

### 视觉微调

如 Winchester-Floyd labels 中：
- `Phonolite: 11` — 分区较窄，需要大字显眼
- `Andesite Basalt: 8` — 分区空间小，文字容易溢出，被迫缩小

这些是当年针对裸图 203mm 逐字微调的结果，现在通过 `base_fs(ax)` 缩放后仍保持裸图时的相对比例。

## 不要做的事

- 不要试图把 JSON 的 fontsize 统一成相同值——微调信息会丢失
- 不要在 JSON 中用 `"fontsize": "label"` 等语义标签——改动成本大且丢掉微调
- 不需要在新建 JSON 边界文件时精确计算字号——用倒数第二接近的值即可，出图后微调

## 代码路径

所有 JSON fontsize 到 ax.text 的路径都经过 `base_fs(ax)`：

```
_source.py:   ann.get('fontsize', 10) * _style.base_fs(ax)
_evolution.py: ann.get('fontsize', 10) * _style.base_fs(ax)
_tectonic.py:  rl.get('fontsize', 7.5) * _style.base_fs(ax)
_tectonic.py:  rgl.get('fontsize', 11) * _style.base_fs(ax)
_classification.py: 硬编码 fontsize=N * _style.base_fs(ax)
```

`base_fs(ax)` 定义在 `igneous_wr/report/style.py`，基准宽度 `_REF_WIDTH_MM = 203.0`。
