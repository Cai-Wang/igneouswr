# 坐标外置模式（Boundary Extraction Pattern）

2026-06-10 完成了 `_classification.py` 和 `_tectonic.py` 的坐标外置，以及 `_xy_diagrams.py` 的拆散。

## 数据结构

坐标数据存放于 `scripts/whole_rock/boundaries/`，按图件类别分 4 个子目录：
- `cls/` — 分类图（13 个 JSON）
- `tec/` — 构造图（harris.json）
- `src/` — 源区图（暂无）
- `evo/` — 演化图（暂无）

## JSON 格式规范

每个 JSON 文件用 `load_boundary(category, name)` 加载（来自 `boundaries/core.py`）。

### 三元图曲线格式

```json
{
    "_meta": {"name": "...", "type": "ternary_boundary", "components": ["A", "B", "C"]},
    "curves": {
        "curve0": {"a": [...], "b": [...], "c": [...]},
        "curve1": ...
    }
}
```

加载后，函数体内用 `ternary_to_xy(np.array(c['a']), ...)` 转换。

### 三元图多边形格式（Cabanis 式）

```json
{
    "_meta": {"name": "...", "type": "ternary_polygon"},
    "polygon": [
        {"a": 0.0, "b": 0.0, "c": 100.0},
        ...
    ]
}
```

### XY 图多边形/节点格式（W&F 式）

```json
{
    "_meta": {"name": "...", "type": "XY_log_nodes"},
    "nodes": {"1": [x, y], "2": [x, y], ...},
    "edges": [[1, 2, 3, ...], ...],
    "labels": [{"x": x, "y": y, "text": "...", "fontsize": n}, ...]
}
```

### XY 图分界线格式（AFM 式）

```json
{
    "_meta": {"name": "...", "type": "ternary_boundary"},
    "boundary": [
        {"a": 32.9, "b": 62.1, "c": 5.0},
        ...
    ]
}
```

## 提取流程

1. 在原始文件 `grep -n '^_'` 找模块级变量定义
2. 确认每个数组的来源（函数名对应）
3. 写入对应的 JSON 文件
4. 在函数体内加 `load_boundary()` 调用
5. 删除模块级变量定义
6. 语法检查 + import 验证

## Pitfalls

### JSON 解析为 list 而非 tuple → 不可 hash

`json.load()` 始终将 `[x, y]` 数组解析为 Python `list`，而非 `tuple`。这导致：

```python
seg = tuple(sorted([poly[i], poly[(i+1) % n]]))  # ← poly[i] 是 [x, y] list
segments.add(seg)
# TypeError: unhashable type: 'list'  ← sorted() 返回 list
```

**修复**：在 `load_boundary()` 返回值的外层把 list 转 tuple：

```python
_TAS_FIELDS = {k: [tuple(p) for p in v] for k, v in _tas_data['fields'].items()}
```

或者改 `sorted()` 为 `tuple(sorted(tuple(...)))`。推荐前者，因为数据进入 `ax.fill()` 和 `ax.plot()` 后都能接受 list。

**检查清单**：使用 `load_boundary()` 加载任何包含坐标对的数据时，检查该数据是否会进入：
1. `set()` / 集合运算 → 需转 `tuple`
2. `dict` 的 `keys()` → 需转 `tuple`
3. `hash()` → 需转 `tuple`

### sys.path 需包含 `whole_rock/`

`boundaries/` 包位于 `scripts/whole_rock/boundaries/`，需要 `scripts/whole_rock/` 在 sys.path 上才能被 `from boundaries.core import load_boundary` 解析。以下入口脚本必须在启动时添加：

```python
wr_path = os.path.join(SCRIPT_DIR, 'whole_rock')
if os.path.isdir(wr_path) and wr_path not in sys.path:
    sys.path.insert(0, wr_path)
```

已知受影响入口：
- `quick_validate.py`（bootstrap 区）
- `batch_backgrounds_main.py`（启动区）
- 任何直接 `python3 xxx.py` 运行的脚本

`quick_validate.py --quick` 和 `batch_backgrounds_main.py --mode minimal` 是验证 sys.path 是否正确的回归标准。

## 已提取的文件

| 原始文件 | 类别 | JSON 文件 | 函数 | 状态 |
|---------|------|-----------|------|------|
| `_classification.py` | cls | afm.json | plot_afm | ✅ |
| | | cabanis.json | plot_cabanis | ✅ |
| | | jensen.json | plot_jensen | ✅ |
| | | k2o_sio2.json | plot_k2o_sio2 | ✅ |
| | | mullen.json | plot_mullen | ✅ |
| | | oconnor_volc.json | plot_oconnor_volc | ✅ |
| | | ohta_arai.json | plot_ohta_arai | ✅ |
| | | pearce1977.json | plot_pearce1977 | ✅ |
| | | qap.json | plot_qapf | ✅ |
| | | shand.json | plot_shand | ✅ |
| | | tas.json | plot_tas | ✅ |
| | | winchester_floyd.json | plot_winchester_floyd | ✅ |
| | | oconnor_intrusive.json | plot_an_ab_or | ✅ |
| | | co_th_hastie.json | plot_co_th | ✅ |
| `_tectonic.py` | tec | harris.json | plot_harris | ✅ |

## 35 个 XY 函数的坐标情况

`_xy_diagrams.py` 的 32 个函数和 `_classification.py` 原有的 3 个 XY 函数（k2o_sio2, shand, winchester_floyd）中，坐标直接写在函数体内部（如 `ax.axhline(1, ...)`、`ax.plot(xs, ...)` 等单线坐标），没有大块的 `np.array` 定义。这些单线坐标因为量小、与绘图逻辑紧密耦合，保持原位（不抽离 JSON 是合理设计决定）。
