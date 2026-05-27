# Batch 2/2.5 教训与模式记录

## 核心教训 1：`import → 内联定义覆盖` 陷阱

`whole_rock_core.py` 中先 `from igneous_geochem.diagrams.registry import DIAGRAM_REGISTRY`，但 200 行后有 `DIAGRAM_REGISTRY = [...]` 内联定义覆盖了 import 版本。

**根因**：Python 模块顶层变量定义（即使在后）会覆盖先执行的 import 绑定。`import` 执行了，但被同一模块的同名赋值覆盖。

**验证方法**：检查 `DIAGRAM_REGISTRY[0]` 是否有新增字段（如 `review_status`）。有则来自新包，无则仍在使用旧内联版本。

**修复**：删除内联定义，只保留 import。

## 核心教训 2：门面模块用 sys.modules 接管

`from X import *` 做门面时有变量隔离问题。用 `sys.modules[__name__] = _mod` 接管整个模块。

## 核心教训 3：每次迁移收口标准

- 工作区干净（`git status --short` 无意外文件）
- SKILL.md 的"中期待办"更新为正确打勾状态
- `quick_validate.py --quick` 通过
- `quick_validate.py`（完整模式）通过
- registry 总数不变（70）
- mafic/felsic 计数不变（49/32）
- 文件名无重复
