# IgneousWR 代码审查清单

批改 IgneousWR 代码时（增删图件、重构后），按以下清单逐项检查。

## 删除图件后补充检查

已在 SKILL.md"删除图件流程"中列出基础步骤。之外还要检查：

- **无用 import** — `scipy` 的 `from scipy import stats` 是三个 diagrams 文件（`_classification.py`, `_tectonic.py`, `_source.py`）最常见的残留 import。删图后如果没新增 scipy 调用，直接删除这三处 import，然后从 `requirements.txt` 和 `pyproject.toml` 中移除 `scipy>=1.10`。
- **死代码分支** — `data.py` 的 `get()` 方法中曾经有 `if elem_name == 'Pb' and 'Pb' in self._elem_data` 这种条件恒真的无用分支。检查函数返回值路径中有无自我冗余。
- **私有属性访问** — 所有绘图函数必须通过 `gd.check_elements()` / `gd.get()` 访问数据，禁止直接读 `gd._elem_data`。用 `grep -rn 'gd\._elem_data' scripts/igneous_wr/diagrams/` 排查。
- **FakeGeochemData 兼容性** — 新增或修改图后运行 `quick_validate.py`。如果 minimal mode 报 `'NoneType' object is not iterable`，则是 `FakeGeochemData.__init__` 中 `self.groups = None` 导致 — REE/Spider 的 `get_group_colors(groups)` 需要 `groups` 是列表。改为 `self.groups = []`。
- **三元图标签对齐检查** — `label_ternary_vertices()` 中检查左右顶点的 `ha` 参数：左顶点应为 `ha='right'`（文字向左伸出三角），右顶点应为 `ha='left'`（文字向右伸出三角）。两者必须对称且文字向外延伸。
- **模块级常量去重** — 检查 `data.py` 的 `_load_wide` 和 `_load_transposed` 中是否有重复的数据前缀元组（如参考标准排除列表），提取为模块级 `_REFERENCE_PREFIXES` 常量。
- **跨包 import 路径** — 检查是否通过顶层门面（`igneous_wr_core`）import 子模块内容。应改为直接走包内路径（`igneous_wr.io.excel`），避免循环依赖风险。
- **AGENTS.md 同步** — 如果新增/删除图件或改变验证方式，确保根目录 `AGENTS.md` 中的架构树、命令、计数同步更新。

## 科学正确性检查（2026-06-10 审查新增）

- **Eu/Eu\* 和 Ce/Ce\*** — 必须用几何平均 `√(SmN × GdN)`，不是算术平均 `(SmN + GdN) / 2`。在 `merge_excel.py` 的 `compute_ratios()` 中检查。
- **feot_calc NaN 传播** — `chem.py` 中当 FeO 有效但 TFe2O3 为 NaN 时，`feo + 0.8998 * NaN = NaN` 会丢弃有效值。修复：嵌套 `np.where` 将 NaN TFe2O3 替换为 0 再参与运算。
- **Truthiness 陷阱** — `if ree_vals['Eu']` 在 Eu=0.0 时返回 False，跳过有效数据。检查所有 `if val` 的 float 条件，改为 `if val is not None`。
- **ΣREE 部分求和** — 不要要求 ALL 14 REE 都存在才求和。对缺失部分元素的数据，仅对有效元素求和（`sum(v for v in ree_vals.values() if v is not None)`）。

## 安全加固检查（2026-06-10 审查新增）

- **HTML 报告** — `generate_report_html()` 中所有用户可控制的变量（`data_src`, `rock_label`, `fn_name`, `fname`）必须通过 `html.escape()` 后再写入输出。
- **`open()` encoding** — 所有 `open(path)` 调用必须指定 `encoding='utf-8'`，避免 Windows 中文系统默认编码不一致导致崩溃。
- **`globals()` 注入防护** — 任何通过 `globals()` 从外部数据写模块变量的路径必须有 `valid_keys` 白名单（如 `set_style_preset()` 的 15 个风格常量）。
- **路径遍历防护** — `load_boundary()` 等拼接文件路径的函数必须：category 白名单校验、name 中拒绝 `..` `/` `\\`、`os.path.realpath()` 前缀验证。
- **`matplotlib.use('Agg')`** — 只应在 `style.py` 中设置一次，各 diagrams 模块不应重复调用。

```python
# ❌ 错误 — setuptools >= 75 已移除 setuptools.backends._legacy
build-backend = "setuptools.backends._legacy:_Backend"

# ✅ 正确
build-backend = "setuptools.build_meta"
```

`setuptools.backends._legacy` 在 setuptools 75+ 已被删除，81+ 完全不存在。如果 `pip install -e .` 失败，检查 pyproject.toml 中的 build-backend。

## 测试 / 验证脚本陷阱

- **`plot_recommended()` 返回 dict 而非 list**：返回 `{'success': [(fn_name, fname), ...], 'skipped': [...]}`。不要用 `sorted(result)` 或 `len(result)` — 前者只迭代 dict 的 key（输出 `['skipped', 'success']`），后者恒为 2。
- **monkey-patch 必须用 try/finally**：`batch/backgrounds.py` 的 `run_batch(mode='full')` 中 patch 了 `scatter_samples` 和 `save_fig`。patch 恢复代码必须放在 `finally` 块中，否则异常导致恢复函数不执行，后续调用行为异常。
