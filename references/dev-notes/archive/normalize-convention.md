# 标准化常量模块 `_normalize.py` 使用约定

## 位置

`scripts/_normalize.py`

## 用途

存放所有标准化参考值常量（球粒陨石、原始地幔、后续可能加入的 N-MORB、E-MORB、OIB、CI 不同版本等）以及 `normalize(data_dict, ref)` 纯函数。

## 关键约束：0 图形依赖

`_normalize.py` 只依赖 `numpy`，不依赖 `matplotlib`、`pyplot` 或任何图形库。

### 为什么重要

`_source.py`（REE / 蛛网图绘图模块）需要 `CHONDRITE` 和 `normalize()`。在 `_normalize.py` 独立之前，这些常量定义在 `whole_rock_core.py` 中，`_source.py` 通过 `from whole_rock_core import ...` 获取。这造成了两个问题：

1. `_source.py` import `whole_rock_core` 会触发所有模块的加载（包括 `_style` 的 matplotlib 设置）
2. 其他纯计算模块（如 `_evolution.py` 未来可能加入的 REE 协变图）也需要 `CHONDRITE`，但不想因为 import 一个常量就拉入 matplotlib

### 规范

```python
# ✅ 正确：从 _normalize 直接导入，无副作用
from _normalize import CHONDRITE, REE_ORDER, normalize

# ❌ 错误：绕道 geochem_core（虽然向后兼容，但不必要）
from whole_rock_core import CHONDRITE
```

## 何时在此模块新增常量

- 新增的标准化方案属于**全局通用**标准（如 McDonough & Sun 1995 CI chondrite、N-MORB、E-MORB、OIB）
- 仅单张图使用的参考线（如某论文特有的判别域边界值）应定义在该图的绘图函数中，不放进 `_normalize.py`

## 导出链路

```
_normalize.py  (定义)
     ↓
whole_rock_core.py  (from _normalize import ...，保持向后兼容)
     ↓
用户 / agent：from whole_rock_core import * 仍可访问 CHONDRITE、normalize 等
```

新建的 diagram 子模块应直接 `from _normalize import ...`，而非绕道 `whole_rock_core`。
