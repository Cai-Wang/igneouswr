# 参考数据事实性审查与修复工作流

从 2026-06-10 地球化学事实性审查修复经验中提炼。

## 适用场景

当收到外部审查 agent 对 IgneousWR 参考数据（`references/normalization.json`）的报告时，按此流程处理。

## 审查验收 — 先验证审查结论，再动手

不要假设审查 agent 的报告 100% 正确。关键结论必须独立验算后再执行。

### 1. εNd 自洽性验算

CHUR 的 `¹⁴³Nd/¹⁴⁴Nd` = **0.512638**（目前最广泛采用的参考值）。

```python
CHUR = 0.512638
def calc_epsNd(ratio):
    return round((ratio / CHUR - 1) * 10000, 2)
```

对每个地幔端元（DMM/EM1/EM2/HIMU），用 `143Nd/144Nd` 计算 εNd 并与存储值对比：
- 偏差 < 0.1ε：一致（保留）
- 偏差 ≥ 0.5ε：存储值与同位素比值来自不同文献源，需删除其一避免自相矛盾

**2026-06-10 实例**：EM1(-5.62 vs 计算-6.59, +0.97ε)、EM2(0.039 vs -0.74, +0.78ε)、HIMU(4.135 vs 5.11, -0.98ε) 均偏差约1ε，删除 EpsNd。DMM(12.91 vs 12.91, 0.00ε) 保留。

### 2. 元素合理性检查

钷（Pm, Z=61）**没有稳定同位素**，不存在天然丰度：
- 任何标准化数据集中出现 `"Pm": <任何非零值>` 都是占位符遗留（GCDkit 的 `spider.data` 用 Pm=1.0 在 REE 配分图上占空位）
- 修复：直接删除该键，`normalize()` 遇到缺失元素时会返回 NaN
- REE_ORDER 也不应包含 Pm

**已确认正确的数据集**（不含 Pm）：REE_CHONDRITE_MS95、REE_CHONDRITE_Palme2014、REE_CHONDRITE_ONeill2016

**2026-06-10 实例**：5 个数据集含 `"Pm": 1.0`（REE_PM_MS95、REE_UCC_TM95、REE_AG89、REE_Boynton84、REE_Nakamura74），全部删除。

### 3. 跨数据集值一致性检查

当同一元素的参考值出现在多个数据集中（如 PM 全元素版和 REE 子集版），值必须完全一致。

| 检查项 | 主数据集 | 子数据集 | 问题 | 修复 |
|--------|---------|---------|------|------|
| Lu | PRIMITIVE_MANTLE=0.0675 | REE_PRIMITIVE_MANTLE=0.068 | 四舍五入偏差 0.75% | 子集改为 0.0675 |

修复原则：子数据集同步到主数据集的值，因为主数据集是源头。

## 修复实施 — execute_code 批量编辑 JSON

不要用 patch 逐行修改 JSON（行号不直观）。用 `execute_code` 脚本一次性完成所有修改：

```python
import json

path = "scripts/igneous_wr/core/references/normalization.json"
with open(path, 'r') as f:
    data = json.load(f)

# 1. 删除 Pm
del data["REE_PRIMITIVE_MANTLE_MS_AND_SUN_1995"]["Pm"]
# ... 继续

# 2. 修正 Lu
data["REE_PRIMITIVE_MANTLE_MS_AND_SUN_1995"]["Lu"] = 0.0675

# 3. 删除 EpsNd
del data["EM1_COMPONENT"]["EpsNd"]

# 写入前做完整性验证
assert "Pm" not in data["REE_PRIMITIVE_MANTLE_MS_AND_SUN_1995"]

with open(path, 'w') as f:
    json.dump(data, f, indent=2)
```

完整性验证检查清单：
- [ ] Pm 在 5 个问题数据集中全部消失（grep 检查）
- [ ] REE_PM 的 Lu == PRIMITIVE_MANTLE 的 Lu
- [ ] EM1/EM2/HIMU 不含 EpsNd
- [ ] JSON 格式有效（`python3 -c "import json; json.load(open('...'))"`）

## 后修复验证链

```bash
# 1. JSON 语法有效
python3 -c "import json; json.load(open('igneous_wr/core/references/normalization.json'))"

# 2. 模块级导入正常（normalize.py 在 __init__ 时加载 JSON → 绑定全局变量）
cd scripts
python3 -c "from igneous_wr.core.normalize import *; print('OK: normalize imports')"

# 3. 所有图件烟雾测试
python3 quick_validate.py

# 4. 端到端测试（如果存在）
python3 run_test.py
```

## 文档同步

修复完成后，在 `normalize.py` 的模块级 docstring 底部添加修复记录：

```python
"""
  - 2025-06-10 fix: 删除5数据集中 Pm=1.0 伪值
  - 2025-06-10 fix: REE_PRIMITIVE_MANTLE Lu=0.068→0.0675
  - 2025-06-10 fix: 删除EM1/EM2/HIMU自相矛盾的EpsNd
"""
```

为每个修复记录标注日期和操作摘要，方便后续审查者追溯变更历史。
