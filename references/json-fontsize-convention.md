# JSON fontsize 约定

IgneousWR 的 JSON 边界数据文件（`boundaries/*/`）中 `fontsize` 字段的语义：

## 设计意图

JSON 中的 fontsize 值为**裸图基准**——即 `figsize=(8, 6)`、ax 宽度约 203mm 时的合适字号。

运行时，所有 `ax.text(fontsize=...)` 的实际值由 `_style.base_fs(ax)` 动态缩放：

```
实际字号 = JSON中的fontsize × base_fs(ax)
```

- 裸图 ax 宽度 203mm → base_fs ≈ 1.0 → JSON 的字号就是最终字号
- 拼版 cell 宽度 75mm → base_fs ≈ 0.37 → 自动缩小

## 为什么 JSON 不改

JSON 里的 `"fontsize": 10` 和代码里硬编码的 `fontsize=10` 意义完全相同——都是针对裸图 203mm 基准的设计值。Python 中 `json_value * base_fs(ax)` 在一个表达式里完成缩放，JSON 文件不需要任何修改。

## 多字号场景（如 Shervais）

Shervais (`boundaries/tec/shervais.json`) 中 `ray_labels` 用 `fontsize: 8`（注释文字）、`region_labels` 用 `fontsize: 10`（分区主标注）。两个值差 2pt——这是有意义的视觉层级。因为两者都乘同一个 `base_fs(ax)`，比例恒为 8:10 = 0.8，不管裸图还是拼版都保持这个比例。

## 非统一字号场景（已修复）

Winchester-Floyd (`boundaries/cls/winchester_floyd.json`) 原本 labels 数组中有 11/10/9/8 四个不同的 fontsize 值。这是建图时的遗留问题（非视觉微调），已全部统一为 10（v2.3）。
