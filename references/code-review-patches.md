# IgneousWR 代码审查修复模式

## 2026-06-26 审查修复记录

### P1-1: O'Neil/O'Neill 双重变量名

**问题**：`normalize.py` 中 `REE_CHONDRITE_PALME_AND_ONEIL_2014`（O'Neil）和 `REE_CHONDRITE_PALME_AND_ONEILL_2014`（O'Neill）内容完全一致，是同一份数据的重复定义。后者静默覆盖前者。

**修复**：
1. 删除 O'Neil 版 REE dict（lines 1263-1279）
2. `NORM_DICT` 中 O'Neil 键指向 O'Neill 变量

```python
# 删除重复定义
- REE_CHONDRITE_PALME_AND_ONEIL_2014 = { ... }  # 删

# NORM_DICT 中单键指向同一对象
"REE chondrite (Palme & O'Neil 2014)": REE_CHONDRITE_PALME_AND_ONEILL_2014,
"REE chondrite (Palme & O'Neill 2014)": REE_CHONDRITE_PALME_AND_ONEILL_2014,  # 同一对象
```

**注意**：`CL_CHONDRITE_PALME_AND_ONEIL_2014`（76元素完整版）和 `CL_CHONDRITE_PALME_AND_ONEILL_2014`（30元素子集）是两个不同数据集，保留不变。

### P1-2: merge_excel.py CHONDRITE 常量重复

**问题**：`merge_excel.py` 复制了一份 CHONDRITE 定义，Tm 值使用了 0.0248 而非 normalize.py 的 0.0247，违反 DRIP 原则。

**修复**：改为 try/except 动态导入，优先从包内加载，fallback 到内联定义且 Tm 修正为 0.0247。

```python
# 优先从包中导入，否则回退到内联定义
try:
    from igneous_wr.core.normalize import CHONDRITE
except ImportError:
    CHONDRITE = { ... 'Tm': 0.0247 ... }
```

### P1-3: 孤立字符串字面量

**问题**：`_source.py:12` 和 `_tectonic.py:12` 各有一个非 docstring 的模块级字符串赋值，Python 不会报错但 lint 工具会标记。

**修复**：直接删除该行。

### P1-4: 无用 import

**问题**：`igneous_wr_core.py` 顶行 `import os, numpy as np` 在纯门面文件中完全未使用。

**修复**：直接删除该行。

### P2-3: FakeGeochemData 跨包 import

**问题**：`backgrounds.py:98` 的 `from igneous_wr_core import ELEM_ALIAS` 绕过包内路径，依赖顶层门面模块，有循环依赖风险。

**修复**：改为 `from igneous_wr.io.excel import ELEM_ALIAS`。

### P2-8: 标准物质排除列表重复

**问题**：`data.py` 中 `_load_wide`（229行）和 `_load_transposed`（353行、369行）各有一份完全相同的 `startswith()` 元组。

**修复**：提取为模块级常量。

```python
_REFERENCE_PREFIXES = ('BCR', 'BHVO', 'AGV', 'GSP', 'G-2', 'JB-', 'JA-',
                       'JG-', 'JP-', 'JR-', 'GSB', 'NIST', 'SRM', 'SY-',
                       'MRG', 'PCC', 'DTS', 'W-2', 'DNC', 'BIR', 'UB-N',
                       'ACE', 'SARM', 'IMA', 'SDC', 'DL-', 'GSR', 'GSS')
```

### P2-4: 三元图右顶点标签对齐

**问题**：`ternary.py:93` 右顶点使用 `ha='right'`，文本从锚点向左延伸，可能覆盖三角区域。与左顶点使用 `ha='right'` 向左伸出三角不对称。

**修复**：改为 `ha='left'`，文本从锚点向右延伸，始终在三角外部。
