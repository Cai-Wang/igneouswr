# IgneousWR 代码审查 & 修复工作流

从本会话（2026-06-10）的审查修复经验中提炼的模式。

## 审查报告优先级处理链

当收到一个外部审查 agent 的报告时，按此顺序处理：

### P1 — 必须修复（影响正确性或开源可用性）
先修这些，不商量。包括：
- 数据不一致（如 CHONDRITE Tm 0.0248 vs 0.0247）
- 无效代码（孤立字符串字面量、无用 import）
- 重复定义/变量覆盖（O'Neil/O'Neill 同名赋值）
- 修复后跑 `pytest tests/ -v` 验证

### P2 — 建议修复（质量/可维护性）
P1 完成后在同一批处理：
- DRY 违规（重复常量、重复排除列表）
- import 倒挂（跨包导入门面模块）
- 文档过长、单文件过巨
- 缺少单元测试
- 修复后跑 `pytest tests/ -v` + `quick_validate.py --quick`

### N — 新发现（审查 agent 二次扫描发现）
修完 P1/P2 后处理：
- 命名歧义（CL_ONEIL → CL_FULL/SHORT）
- 数据冗余（LONG 版本与原始版完全一致 → alias）
- IDE 友好度（缺 `__all__`）
- 补充测试覆盖新发现

## 硬编码字典 → JSON 外置两步法

当 Python 文件中存在大量硬编码 dict（如 normalize.py 47 个 dict，1490 行）：

### 第一步：提取脚本
```python
# tools/extract_{name}.py
import ast, json, os
# 1. parse source 为 AST
# 2. 遍历所有 ast.Assign，筛选 dict 赋值
# 3. 写入 JSON（含 _NORM_DICT 映射、_aliases、_REE_ORDER 等元数据）
# 4. 验证 JSON 完整性
```

### 第二步：重写源文件
```python
# 原文件 → 82 行加载器
# - 从 JSON 加载
# - globals() 动态注入保持向后兼容
# - NORM_DICT 通过 _NORM_DICT 映射重建
# - 别名通过 _aliases 映射重建
# - __all__ 列表（IDE 类型提示友好）
```

### 验证列表
```bash
# 1. 语法检查
python3 -c "import ast; ast.parse(open('xxx.py').read())"

# 2. 模块级功能测试
python3 -c "
from xxx import NORM_DICT, CHONDRITE, ...
# 验证关键常量值正确
# 验证别名指向同一对象（is 检查）
# 验证 NORM_DICT 所有条目可解析
"

# 3. 现有关键字引用方测试
pytest tests/ -v
python3 quick_validate.py --quick
```

## 数据处理类常量的注意事项

1. **O'Neil/O'Neill 拼写问题**：GCDkit 原始数据源两者混用。修复原则——保留正确拼写（双 L），所有引用点统一指向同一变量。`NORM_DICT` 中两个外部键都映射到同一个 Python 对象。
2. **LONG 后缀的 GCDkit 语义**：GCDkit 中 `_LONG` 表示扩展元素列表（含主量元素）。如果数据与非 LONG 版完全一致，转为 alias 而非独立复制。
3. **FULL vs SHORT 命名**：当存在完整版（76 元素）和子集版（30 元素）时，用 `_FULL` / `_SHORT` 后缀命名，不保留原拼写差异命名的历史遗留。
