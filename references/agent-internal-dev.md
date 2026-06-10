# IgneousWR — Hermes Agent 内部开发参考

本文件记录了 Hermes Agent 专属的内部开发文档，供 Hermes 会话中加载技能时使用。
主仓库的 `SKILL.md` 已改造为 agentskills.io 跨 agent 通用格式。

---

## 删除图件流程

1. 删注册表条目（`registry.py` `DIAGRAM_REGISTRY` 中移除对应 `DiagramSpec`）
2. 删 import（`registry.py` 顶部、`igneous_wr_core.py` re-export）
3. 删函数体（`_classification.py` / `_source.py` / `_evolution.py` / `_tectonic.py` 中对应 `def`）
4. 清理残留引用 + 无用 import（`grep -rn deleted_fn_name scripts/`）
5. 清理无用 import（如删图后无新 scipy 调用，删除 diagrams 三文件中的 `from scipy import stats`，再从 `requirements.txt` 和 `pyproject.toml` 中移除 scipy 依赖）
6. 更新 SKILL.md 图目录、总数、分组计数、校正状态计数
7. 运行 `python3 quick_validate.py` 验证
8. 删除相关引用文件（如不再引用的 `references/dev-notes/` 中的文件）

## 核心原则汇总（补充 SKILL.md 通用版的额外细节）

### 线段与标签风格

- 主分界线（分类/判别/构造区边界）：实线 `color='#333333'`, **lw=1.5**
- 次分界线（子分区、辅助划分）：虚线 `color='#666666'`, **lw=1.2**
- TAS 类多边形：实线 `color='#333333'`, **lw=0.8**
- 辅助参考线（y=1, ASI-ANK 十字等）：虚线 `color='#666666'`, **lw=0.8**
- 三元图场界线：实线 `color='#333333'`, **lw=1.5**
- Shervais 型射线：主判别线（Ti/V=50）lw=1.5，辅助线虚线 lw=1.0
- 所有 `ax.plot()` 禁用 fmt 字符串颜色（如 `'k-'`），统一使用 `color=` 关键字
- 标签统一使用 `#444444`（深灰），禁用彩色标签
- 二元图区域标签字号统一 **10**，TAS 多边形内标签字号 **8.5**，纯文本说明字号 **8**
- 三元图区域标签字号统一 **11**，顶点标签 **12**
- WF1977 标签字号 **9.5**，Pearce1996 **10**，Shervais 区域 **10** 射线 **8**
- REE 配分图 x 轴标签 **8.5**，蛛网图 **7.5**（45°旋转）

### 三元图与二元图视觉统一

- 三元图外框线宽 = `SPINE_WIDTH`（与二元图一致）
- 无网格（2026-06-09 禁用 `draw_ternary_grid()`）
- 刻度标签字号 `TICK_LENGTH+4`（≈9），字体使用 `times_prop`（Times New Roman）
- 刻度颜色 `#000000`（纯黑，2026-06-09 从 `#666666` 改为纯黑）
- 顶点标签字号 12，与二元图 `xlabel_size=12` 统一
- 三角图标签已替换字母为地质含义（TEC-01 Meschede: WPA, N-MORB, CAB 等；TEC-02 Wood: N-MORB, E-MORB, WPT, WPB 等）
- 所有差异参数集中在 `ternary.py` 的四个函数：`draw_ternary_frame/grid/ticks` 和 `label_ternary_vertices`

### 其他

- 底图默认纯黑白线框风格，除 SRC-03 外不渲染彩色填充
- 对数轴刻度标签必须用真数，不可用科学计数法。显式 `ax.set_xticks([...])` + `ax.set_xticklabels([...])`
- 化学式下标统一用 LaTeX `$_n$` 语法（`FeO$_t$`, `SiO$_2$`, `Na$_2$O`, `TiO$_2$`），禁止 Unicode 下标符号和纯文本。三元图顶点标签例外（用 Unicode 字符通过 `label_ternary_vertices` 传入）
- 标引注统一由 `save_fig()` 自动添加（读取 `registry` 中 `source_ref` 字段），禁用手写 `ax.text()` citation

## 数据格式陷阱

当文件保存为"第1行=元素名、第1列=样品名"的标准格式时，`r1_c2`（如SiO2）在 `KNOWN_ELEMENTS` 中，`_load()` 误判为 `transposed=True`，导致仅读取~16个元素、跳过部分样品。修复方法：再用一次 T 转置让布局变为"第1列=元素名、第1行=样品名"后再保存，或者直接用原始转置格式文件。

## 代码审查清单

批改 IgneousWR 代码时（增删图件、重构后），逐项检查：

### 删除图件后
- 无用 import — `scipy` 的 `from scipy import stats` 是三个 diagrams 文件最常见的残留
- 死代码分支 — `data.py` 的 `get()` 方法中检查有无条件恒真的无用分支
- 私有属性访问 — 所有绘图函数必须通过 `gd.check_elements()` / `gd.get()` 访问数据，禁止直接读 `gd._elem_data`
- FakeGeochemData 兼容性 — 新增或修改图后运行 `quick_validate.py`。如果 `'NoneType' object is not iterable`，则 `FakeGeochemData.__init__` 中 `self.groups = []`（非 None）

### pyproject.toml 配置陷阱
- build-backend 必须用 `"setuptools.build_meta"`，不是 `"setuptools.backends._legacy"`（setuptools 75+ 已移除）

### 验证脚本陷阱
- `plot_recommended()` 返回 `{'success': [...], 'skipped': [...]}`，不是 list。不要用 `sorted(result)` 或 `len(result)`（前者只迭代 key，后者恒为 2）
- Monkey-patch 必须用 try/finally：`batch/backgrounds.py` 中 patch 恢复代码必须放在 `finally` 块中

## 已知陷阱（补充 SKILL.md 通用版）

- 二元图多边形共享边错位：相邻多边形共享边必须走完全相同的顶点序列。排查用 set() 求共享边交集
- 排查顺序：发现坐标问题后，先到 GCDkit 安装目录下找对应 R 源码确认原始定义，再下结论
- TAS 火山岩图坐标来源：当前使用 pyrolite 派生坐标（Le Bas 体系），与 GCDkit TASMiddlemostVolc.r 不完全一致
- Frost ASI-ANK 没有对角线（只有 h=1 + v=1 两条虚线），Shand 图才有 y=x 对角线
- R 源码的 `\n` 在 IgneousWR 中必须用真换行符（`'text\nnewlines'`），不可用 `'text\\nnewlines'`（双反斜杠显示为字面文本不换行）。验证：`cat -A <file> | grep "Low-K"` 应显示 `Low-K\nTholeiitic`（单反斜杠 n）
- `refs.json` 不可含 `#` 前缀键，Python json.load 能解析但 Rust/Go 会报错

## 相关技能

- `gcdkit-translator` — GCDkit R → Python 翻译规范
