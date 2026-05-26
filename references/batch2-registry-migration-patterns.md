# Batch 2.5 补充 — 渐进迁移收口

## 应补充到 Batch 2 的核心教训

### 1. `whole_rock_core.py` 内联注册表残留问题

Batch 2 的 patch（替换行 462-475 的 import 语句）**只替换了顶部 import，没有删除行 499-667 的旧内联 `class DiagramSpec` + `DIAGRAM_REGISTRY` 列表 + 派生代码**。导致：
```python
# 文件顶部
from igneous_geochem.diagrams.registry import DIAGRAM_REGISTRY  # OK

# 200 行后
DIAGRAM_REGISTRY = [...]  # 覆盖了 import 版本！
```

`from whole_rock_core import DIAGRAM_REGISTRY` 拿到的是内联旧版本（无 review_status 字段），尽管 `from igneous_geochem.diagrams.registry import DIAGRAM_REGISTRY` 拿到的是新版本。

**教训**：渐进迁移中，旧文件的内联定义必须先删除，否则 import 先执行然后被覆盖。简单 patch 行 462-475 是不够的。

### 2. 兼容门面的 sys.modules 接管模式

`from X import *` 作为门面时有变量隔离问题：`set_style()` 修改新包模块的全局变量，但门面模块的 `MK_SIZE_SINGLE` 是 import-time 的旧拷贝。

**正确方案**（已验证 202/0/0 通过）：
```python
"""_style.py — 兼容门面"""
import sys
_mod = sys.modules.get('igneous_geochem.report.style')
if _mod is None:
    import igneous_geochem.report.style as _mod
_mod.__dict__['__name__'] = __name__
sys.modules[__name__] = _mod
```

### 3. 每次迁移收口标准

Batch 2.5 用户明确了每次架构迁移的收口清单：
- [ ] 工作区干净（`git status --short` 无意外文件）
- [ ] SKILL.md 的"中期待办"更新为正确打勾状态
- [ ] `quick_validate.py --quick` 通过
- [ ] `quick_validate.py`（完整模式）通过
- [ ] registry 总数不变（70）
- [ ] mafic/felsic 计数不变（49/32）
- [ ] 文件名无重复
