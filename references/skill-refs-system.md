# 参考文献库系统（References Subsystem）

## 目录结构

```
igneous_wr/references/
├── __init__.py      # 包标记（空）
├── refs.json        # 文献数据（62条记录）
└── loader.py        # 加载/查询模块
```

## 数据格式：refs.json

每条记录格式：
```json
{
  "key": {
    "short": "短名（图上显示）",
    "full": "完整引用（报告参考文献列表）",
    "type": "article | book | other",
    "note": "可选，备注说明"
  }
}
```

### 字段说明

| 字段 | 用途 | 显示位置 |
|------|------|---------|
| `short` | 灰色斜体印在图右下角 | 每张出图的右下角 `ax.text()` |
| `full` | 在 HTML 报告末尾参考文献列表 | `report_YYYYMMDD.html` 的 `<ol>` |
| `type` | 仅供归类参考 | 无显示 |
| `note` | 临时备注，什么时候需要校正的提示 | 无显示 |

### key 命名规则

- 小写字母 + 下划线
- 格式：`<第一作者姓氏><年份>` 或 `<第一作者>_<第二作者><年份>`
- 示例：`lebas1992`, `irvine_baragar1971`, `sun_mcdonough1989`

### 临时/占位 key

当前有图但 full 信息待补充时，用带 note 的临时条目：
```json
"svgboundary": {
  "short": "RockPlot SVG 坐标 (未核实)",
  "full": "",
  "type": "other",
  "note": "从 RockPlot SVG 提取的边界坐标，未与原文逐点核对"
}
```

这类条目在报告里会显示"完整引用信息待补充"。用户校正时只需往 `full` 字段填完整内容即可。

## API：loader.py

### 核心函数

| 函数 | 用途 |
|------|------|
| `load_refs()` | 加载 refs.json，返回 {key: record} dict |
| `get_ref(key)` | 按 key 获取单条记录，找不到返回 None |
| `get_short(key)` | 获取 short 字段（印图用） |
| `get_full(key)` | 获取 full 字段（报告用），fallback 到 short |
| `resolve_source_ref(source_ref, fallback_desc)` | 解析注册表的 source_ref → 有限匹配 |
| `get_references_for_report(used_keys)` | 生成报告参考文献列表 [(key, short, full), ...] |
| `get_all_used_keys()` | 遍历注册表，去重提取所有引用 key |

### resolve_source_ref 支持两种输入

1. **精确 key**：`"lebas1992"` → 直接查 refs.json
2. **模糊匹配**：尝试匹配 refs.json 中任意条目的 `short` 字段（大小写不敏感、部分包含）

返回：(key, short, full, is_verified)
- is_verified=True 表示 full 字段非空

## 自动引用功能

### 图上自动印引用

位置：`igneous_wr/report/style.py` → `save_fig()`

流程：
1. `save_fig(fig, 'ShortName.png')` 收到短文件名
2. 通过 `_SHORT_TO_LONG` 映射找出长名（如 `CLS-01_TAS.png`）
3. 遍历 `DIAGRAM_REGISTRY` 匹配 `d.filename`
4. 用 `d.source_ref` key 查 `get_short(key)`
5. 在图右下角 `ax.text(0.99, 0.01, ..., ha='right', va='bottom')` 印灰色斜体引用

当前仅印在第一个 axes 上。多子图图（如 4panel、Harker 6panel）只印在左下角。

### HTML 报告参考文献列表

位置：`igneous_wr/report/style.py` → `generate_report_html()`

流程：
1. 调用 `get_references_for_report()` 遍历注册表所有 source_ref key
2. 去重后按 key 顺序列出
3. 有 full 字段 → 显示完整引用；无 full → 显示"完整引用信息待补充"

## 新增图件时需要同步的两处引用相关

1. **registry.py**：设置 `source_ref="key"`，key 必须在 refs.json 中已存在
2. **style.py 顶部的 `_SHORT_TO_LONG` 映射表**：必须新增短名→长名映射

如果新增的图引用了一篇 refs.json 中没有的文献，先加 refs.json 条目再加注册表。

## 维护/校正流程

当用户校正某张图时：

1. 改图的函数/坐标/风格 ← 这是主要工作
2. **顺便查 refs.json 中对应的 key，把 `full` 字段填完整** ← 这是顺手的事
   - 如校正 TAS → 找 `key="lebas1992"` → 往 `full` 填入完整引用

标准引用格式（apa-like）：
```
作者姓, 名首字母. (年份). 标题. 期刊名, 卷(期), 页码.
```

示例：
```json
"irvine_baragar1971": {
  "short": "Irvine & Baragar (1971)",
  "full": "Irvine, T.N. & Baragar, W.R.A. (1971). A guide to the chemical classification of the common volcanic rocks. Canadian Journal of Earth Sciences, 8(5), 523-548.",
  "type": "article"
}
```

## 验证

```bash
cd ~/.hermes/skills/data-science/IgneousWR/scripts
python3 -c "
from igneous_wr.references.loader import load_refs, resolve_source_ref, get_references_for_report
from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY

# 验证所有 source_ref 可解析
for d in DIAGRAM_REGISTRY:
    if d.source_ref:
        key, short, full, verified = resolve_source_ref(d.source_ref, d.desc)
        assert key, f'未匹配: {d.filename} → {d.source_ref}'
print('✅ 全部可解析')
"
```
