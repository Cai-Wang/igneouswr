# Batch 2 注册表迁移 — 关键模式记录

## 模式1：用 `sys.modules` 接管做兼容门面

旧文件需要改成兼容门面但又要保持全局变量同步（`set_style()` 修改后读 `_style.MK_SIZE_SINGLE` 必须一致），方案：

```python
"""_style.py — 兼容门面，直接引用 igneous_geochem.report.style 模块"""
import sys
_mod = sys.modules.get('igneous_geochem.report.style')
if _mod is None:
    import igneous_geochem.report.style as _mod
_mod.__dict__['__name__'] = __name__
sys.modules[__name__] = _mod
```

原理：让 sys.modules 中旧模块名指向新模块对象。`from _style import MK_SIZE_SINGLE` 和 `_style.MK_SIZE_SINGLE` 读写的是同一个模块对象的同一份变量，`set_style()` 修改新包变量时旧名引用自动同步。

反模式：`from X import *` 做门面 — import 时拷贝标量值，后续修改不生效。

## 模式2：registry 不 import whole_rock_core

registry.py 绝对不能 import whole_rock_core（循环依赖）。正确方向：
- registry.py -> import 各 plot_* 函数（从 `whole_rock.diagrams._xxx`）
- whole_rock_core.py -> from registry import 再 re-export

## 模式3：New DiagramSpec review_status 字段

```python
@dataclass
class DiagramSpec:
    fn: object
    filename: str
    desc: str
    needed: tuple
    any_of: Optional[tuple] = None
    rock_types: tuple = ("mafic",)
    # 新增校正状态字段（可选，默认值不破旧 6 参语法）
    review_status: str = "needs_review"  # verified / needs_review / experimental
    source_ref: str = ""
    review_note: str = ""
```

旧 6 参写法 `DiagramSpec(fn, fn, desc, need, any_of, types)` 不受影响（默认值兜底）。新增字段提供质量管理入口。

## 模式4：import 来源与函数实际所在模块核对

旧代码中 import 声明与实际定义模块不一��（如 `plot_co_th` 在 _classification.py 但被从 _tectonic import）。核对方法：
```python
import re, os
for fname in sorted(os.listdir('whole_rock/diagrams/')):
    with open(f'whole_rock/diagrams/{fname}') as f:
        content = f.read()
    for fn in funcs_to_find:
        if f'def {fn}(' in content:
            print(f"  {fn} -> {fname}")
```

这个不一致在旧 whole_rock_core.py 中就存在（运行时恰好因为名字冲突少而没报错），搬到 registry.py 的清晰 import 时才暴露出来。修复：按实际模块分配 import。

## Registry 验收清单

每次搬注册表后确认以下自动检查和手动核对：
- `DIAGRAM_REGISTRY` 总数 70（不变）
- `MAFIC_DIAGRAMS` 49（不变）
- `FELSIC_DIAGRAMS` 32（不变）
- 文件名无重复
- 每个 fn 有 `__name__`
- MAFIC/FELSIC 四元组兼容
- `from whole_rock_core import *` 通过
- `from whole_rock_core import DIAGRAM_REGISTRY, MAFIC_DIAGRAMS, FELSIC_DIAGRAMS` 通过
- `--quick`: 202/0/0 | full: 211/0/0
- 元素依赖检查全部一致（`test_element_dependency_integrity()`）
