# 分组推断调试指南 (Group Inference Debug)

## 问题现象

用户反馈：数据加载后出图，所有样品点颜色全是不同的，没有按同一组同色显示。

## 原因

分组着色依赖于 `GeochemData.infer_groups()` 从样品名推断组别。推断规则是：

```python
m = re.match(r'^([A-Za-z0-9]+)-', lbl_str)
if m:
    groups.append(m.group(1))  # 字母数字前缀→组名
else:
    groups.append(lbl_str)     # 单独一组
```

即：**提取连字符前连续的字母+数字串作为组名**（旧版仅提取纯字母串，2026-05-09 修复）。

## 常见失败模式

| 样品名模式 | 示例 | 推断结果 | 问题 |
|-----------|------|---------|------|
| 字母前缀-数字 | `SGT-1`, `SGT-2` | 统一组 `SGT` | ✅ 正确 |
| 数字字母前缀-数字 | `24TJ02-1`, `24TJ02-2` | 统一组 `24TJ02` | ✅ 正确（2026-05-09 修复） |
| 纯数字-数字 | `01-001`, `02-002` | 各组不同 | ❌ 连字符前无字母 |
| 字母前缀-字母-数字 | `SGT-A1`, `SGT-B2` | 统一组 `SGT` | ✅ 正确（正则捕获 `SGT`） |
| 无连字符 | `D353-1`, `D353-2` | 各组不同 | ❌ 同赘余说明 |
| 连字符前有空格或下划线 | `SGT_01`, `SGT 01` | 各组不同 | ❌ 正则不匹配非连字符分隔符 |
| 带地点的样品名 | `HLJ-玄武岩-1`, `HLJ-玄武岩-2` | 组前缀为 `HLJ` | 注意连字符前段是第一段 |

## 快速诊断方法

### 方法 1：直接检查 `gd.groups`

```python
gd = GeochemData(EXCEL)
print(gd.groups)
# 输出示例（失败情况）：
# ['24TJ02-1', '24TJ02-2', '24TJ02-3', ...]
# 输出示例（成功情况）：
# ['SGT', 'SGT', 'SGT', 'YK', 'YK', ...]
```

### 方法 2：检查重复组数

```python
from collections import Counter
groups = gd.groups
print(f"共 {len(set(groups))} 个组，数据 {len(groups)} 个样品")
print(Counter(groups))
# 失败时：每个组只在自身中出现（count=1 的组数 = 样品数）
# 成功时：有大于 1 的 count
```

## 修复方案

### 方案 A：手动指定 groups（推荐，立即生效）

不依赖自动推断，手动给组标签：

```python
gd = GeochemData(EXCEL)

# 手动指定：例如 24TJ02-1 ~ 24TJ02-5 是组 A，D353-1 ~ D353-3 是组 B
# 方法 1：按样品列表顺序写
groups = ['Sikhote-Alin'] * paragraph_count + ['Alps'] * another_count

# 方法 2：用字典映射
group_map = {
    '24TJ02-1': 'Sikhote-Alin',
    '24TJ02-2': 'Sikhote-Alin',
    'D353-1': 'Alps',
    'D353-2': 'Alps',
}
groups = [group_map[lbl] for lbl in gd.labels]

# 应用到出图
plot_tas(gd)  # 内部自动用 gd.groups，但这里 gd.groups 是自动推断的
# 所以需要手动覆盖：
import _style
from whole_rock.diagrams._classification import plot_tas_inner
# 或者直接修改 gd.groups
gd.groups = groups
plot_tas(gd)  # 现在会用手动指定的组
```

### 方案 B：扩展 infer_groups 适配更多模式（需改代码）

如果样品名有 `infer_groups()` 不支持的统一模式（如纯数字 `01-001` 或下划线 `SGT_01`），可以修改正则。当前实现（2026-05-09）已支持数字字母前缀，示例：

```python
# 当前正则（匹配连字符前任意字母数字段）：
m = re.match(r'^([A-Za-z0-9]+)-', lbl_str)

# 如果要支持下划线分隔（如 SGT_01 → 组 SGT）：
m = re.match(r'^([A-Za-z0-9]+)[-_]', lbl_str)

### 方案 C：基于前 N 个字符分组

```python
# 取样品名前 6 个字符作为组
groups = [str(lbl)[:6] for lbl in gd.labels]
gd.groups = groups
```

## 验证

```python
gd.groups = groups  # 手动覆盖后
fig, ax = plot_tas(gd)  # 观察图例是否合并
```

图例应该显示组的数量（而不是样品数量）即为成功。

## 长期方案

如果用户的样品命名仍有 `infer_groups()` 无法识别的模式（如纯数字 `01-001`、下划线分隔 `SGT_01`），且有固定分组意图，可在正则中增加对应规则。但用户在本 session 已表态："这个分组逻辑大家每个人的都不一样"——因此**不在此自动推断上堆叠更多规则**。推荐手动指定 `gd.groups` 作为最终方案。
