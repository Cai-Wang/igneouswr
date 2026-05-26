# 模块重构 + 更名记录

> ⚠️ **注意**：`rename-history.md` 已合并至此文件。此文件现同时包含重构和更名记录。

## 更名历史（原 rename-history.md）

### 第一次更名 — 2026-05-08
**原因**：Skill 范围从广义"地球化学绘图"收窄为"全岩地球化学"。旧名称太宽——矿物、流体、同位素等地化图件理论上也可归入。

**变更：**

| 层 | 之前 | 之后 |
|---|---|---|
| Skill 目录名 | `geochemical-plotting/` | `whole-rock-geochemistry/` |
| SKILL.md YAML name | `geochemical-plotting` | `whole-rock-geochemistry` |
| Core Python 模块 | `geochem_core.py` | `whole_rock_core.py` |
| Python 包 | `geochem/` | `whole_rock/` |
| Print 前缀 | `[geochem_core]` | `[whole_rock]` |
| 默认输出目录 | `geochem_output/` | `whole_rock_output/` |
| SKILL.md 标题 | `# 地球化学绘图技能` | `# 全岩地球化学技能（Whole-rock Geochemistry）` |
| Memory 记录 | `geochemical-plotting: 14种图件/...` | `whole-rock-geochemistry: 全岩地化 skill` |
| Cross-ref (merge_excel.py) | `供 geochemical-plotting 直接读取` | `供 whole-rock-geochemistry skill 直接读取` |

### 第二次更名 — 2026-05-08（同一天）
**原因**："全岩地球化学"仍然太宽——涵盖变质岩、陨石、月球样品、沉积物等。此技能专门针对**岩浆岩**全岩地球化学。

**变更：**

| 层 | 之前 | 之后 |
|---|---|---|
| Skill 目录名 | `whole-rock-geochemistry/` | `igneous-geochemistry/` |
| SKILL.md YAML name | `whole-rock-geochemistry` | `igneous-geochemistry` |
| SKILL.md 标题 | `# 全岩地球化学技能（Whole-rock Geochemistry）` | `# 岩浆岩全岩地球化学技能（Igneous Geochemistry）` |
| Python 内部 | `whole_rock_core.py`, `whole_rock/`, `[whole_rock]`, `whole_rock_output` | **不变** — 仅表层名称变更 |
| Memory 记录 | `whole-rock-geochemistry: 全岩地化 skill` | `igneous-geochemistry: 岩浆岩地化 skill` |

### Import 迁移

旧 import（顺序版本）：
```python
# V1（geochemical-plotting 时代）：
from geochem_core import GeochemData, plot_tas, ...
# V2（whole-rock-geochemistry 时代）：
from whole_rock_core import GeochemData, plot_tas, ...
```

当前 import：
```python
from whole_rock_core import GeochemData, plot_tas, ...
```

> 注：Python 内部模块名 (`whole_rock_core.py`, `whole_rock/` 包) 从第一次更名到第二次都保持不变。

### 给未来 Agent 的备忘

- 如果遇到脚本或参考文档引用 `geochemical-plotting` 或 `whole-rock-geochemistry`，说明已过期 — 应重定向到 `igneous-geochemistry`
- `geochemical-excel-merge` skill 已于 2026-05-08 删除 — 其唯一的脚本 `merge_excel.py` 现在位于 `igneous-geochemistry/scripts/`
- 更名前 skill 树的备份在 `../geochemical-plotting.bak.20260508/`，但不应用作真实信息来源

---

# 模块重构记录（原 refactoring-history.md）

## 回顾

whole_rock_core.py 原本是 1328 行/55KB 的单一文件。经过多阶段重构：

### 阶段一（2026-05-06）：P2/P3 问题修复
- 删除了未使用的 `import pandas`（消除了 numpy 版本冲突的根源）
- `set_out_dir()` 改为持久化全局变量
- FeO/TFe2O3 至少其一即可出图
- 筛选保留全量视图 (`_all_elem_data`)
- Zr 协变图常量保护
- log 图 0/负值掩码修复
- Windows GBK 编码保护

### 阶段二（2026-05-06）：公共能力拆分
从 whole_rock_core.py 中拆出 3 个独立模块：
- `_chem.py` — feot_calc
- `_ternary.py` — 三元图坐标变换全套（SQRT3_2, ternary_to_xy, draw_ternary_*, label_ternary_vertices）
- `_style.py` — 字体/配色/COLORS/风格常量/set_style/scatter_samples/style_ax/save_fig/add_legend

### 阶段三（2026-05-06）：按功能拆图
从 whole_rock_core.py 的 L356~L1097 拆出 4 个 diagram 子模块：
- `geochem/diagrams/_classification.py` — TAS, K₂O-SiO₂, AFM, Shand
- `geochem/diagrams/_source.py` — REE, 蛛网图
- `geochem/diagrams/_evolution.py` — Harker, Miyashiro, Mg#, Zr协变
- `geochem/diagrams/_tectonic.py` — Meschede, Wood, Pearce-Cann, 四联

### 阶段四（2026-05-07）：推荐入口调度 + 样式排查

**在 `whole_rock_core.py` 尾部新增两个智能调度函数：**

- `recommended_diagrams(gd, rock_type='auto')` — 自动判断岩性，返回可用图件列表
- `plot_recommended(gd, out_dir=None)` — 一键出所有推荐图
- `MAFIC_DIAGRAMS` / `FELSIC_DIAGRAMS` — 两张预编码的推荐图列表（13张/7张）

设计原则：推荐列表只是数据，不按岩性硬拆代码。函数内部自动从 SiO₂ 最小值判断岩性，`check_elements` 过滤缺元素图，`(None, None)` 返回值检测兜底。

**同日修复：**
- `_tectonic.py` 缺少 `import matplotlib.ticker as ticker`（拆模块漏项，导致四联图报 `name 'ticker' is not defined`）
- `plot_recommended` 输出目录未尊重 `_OUT_DIR` 持久化设置

**2026-05-07 样式统一收尾（用户反馈"散点不是圆形"）：**

1. 用户反馈 K₂O-SiO₂、Harker、Mg# 等图的散点不是圆形（方片）
2. 全面排查发现：
   - `scatter_samples` 使用 `ax.scatter(x_arr[i], y_arr[i], color=get_color(i), s=60, edgecolors='none', linewidths=0)`，**没有显式 `marker='o'`**
   - 本地 matplotlib `scatter` 默认 marker 为 `'o'`（圆形），Path 分析确认是正圆（24 条 CURVE4 曲线代码，X/Y 范围比 = 1.0）
   - 像素级分析：PIL Image 读取 PNG → 红色连通域 → 33×33 px 正圆
   - 三元图 `plot_samples_ternary` 使用 `ax.plot('o', markersize=15)`，机制不同但也是圆形
   - REE/蜘蛛图 `_source.py` 直接 `ax.scatter(marker='o', s=MK_SIZE_SINGLE)` 而非 `scatter_samples()`，已有 `marker='o'` 所以没问题
3. **实际修复**：在 `_style.py` `scatter_samples` 函数的 `ax.scatter()` 中显式加入 `marker='o'` 参数，不再依赖 matplotlib 默认值
4. 新增 `references/scatter-shape-validation.md` — 像素级散点形状验证脚本

### 阶段六（2026-05-07）：移除 TiO₂→Ti 换算，全部改用微量 ppm

用户指出所有微量元素判别图解中的 Ti 直接从微量数据页的 Ti ppm 列读取，不涉及 TiO₂ wt% 换算。此前旧的 `merge_excel` 脚本曾漏掉 Ti 列，但已修复。

**修改内容：**

1. **`plot_pearce_cann`**：`check_elements` 从 `'TiO2'` 改为 `'Ti'`，删除 `tio2_arr * 10000 * 47.867 / 79.866` 换算
2. **`plot_4panel`**：`check_elements` 从 `'TiO2'` 改为 `'Ti'`，`gd.get('Ti')` 替代 `calc_ti_1000(tio2)`，直接 `ti_arr / 1000.0`
3. **`_chem.py`**：删除 `calc_ti_1000()` 函数
4. **导入清理**：5 个文件移除 `calc_ti_1000` 的死 import
5. **SKILL.md**：图解目录 Pearce Cann/四联 的所需元素改为 `Ti (ppm)`；故障表删除蛛网图缺 Ti 条目

**教训：** Ti 在微量数据中是 ppm 量级，不从主量 TiO₂ 换算。任何从 TiO₂ wt% 换算 Ti ppm 的需求都意味着数据合并不完整，而非代码应承担的逻辑。

### 阶段七（2026-05-08）：工程清理 — 统一 import 模式 + 去死代码 + AFM 三元图重构

**触发**：agent 主动审查发现全部 4 个 diagram 模块存在混合 import 模式和死代码残留。

**修改清单：**

1. **全部 4 个 diagram 模块 import 统一** — `_source.py`、`_classification.py`、`_evolution.py`、`_tectonic.py`
   - 删除全部 `from _style import ...`（各模块重复 import 2-3 次，含死 `MK_SIZE_TERNARY`、`MK_SIZE_PANEL` 等）
   - 统一为 `import _style` + `_style.xxx` 动态读取模式
   - 修复 `_source.py` 中同一行 scatter 同时用 `s=_style.MK_SIZE_SINGLE`（动态）+ `edgecolors=MK_EDGE_COLOR`（快照）的不一致
   - `get_color(i)` → `_style.get_color(i)`、`style_ax(...)` → `_style.style_ax(...)` 等批量转换

2. **`_style.py` 死代码清理** — 删除 `MK_SIZE_PANEL = 60`（重构阶段六已废弃，全代码库无引用）、同步清理 `set_style` valid_keys 和 `style-guide.md`

3. **AFM 三元图重构** — `_classification.py` 的 `plot_afm()` 删除 ~50 行手动三元图代码（含私有 `afm_to_xy` 函数、手动网格绘制、手动顶点标签），改用 `_ternary.py` 通用函数：
   - `ternary_to_xy()` → 坐标计算
   - `draw_ternary_frame()` → 三角边框
   - `draw_ternary_grid()` → 网格线
   - `label_ternary_vertices()` → 顶点标签
   - 保留场界分界线（Irvine & Baragar 1971）和风格文本标注

4. **NaN 防护增强** — `plot_pearce_cann()` 和 `plot_4panel()` 新增 Ti 全 NaN 提前返回

**新陷阱记录：**

- **混合 import 模式最危险**：`from _style import MK_EDGE_COLOR` + 同文件中 `_style.MK_SIZE_SINGLE` — 部分变量快照、部分动态，修改者会误以为全部快照或全部动态，改动时顾此失彼。`set_style(MK_EDGE_COLOR='white')` 后散点边框不会被改变但没有任何报错，产生无声错误。
- **三方重复 import 的历史原因**：4 个 diagram 模块在阶段三从 `whole_rock_core.py` 拆出时，每个模块都是用编辑器复制粘贴了同一段 `from _style import ...` 头部（14 行），后续手动修改不同步导致 `_source.py` 残留 3 份不同版本的 import。应在拆模块时把公共 import 抽到一个常量文件。

### 社区审查修复（2026-05-07）

社区审查指出 4 个接口收口问题，全部修复并通过验证（58/58，新增 12 项 any_of/四元组测试）。

**修复清单：**

1. **`plot_recommended` 缺 `rock_type` 参数**（P2）
   - 签名从 `(gd, out_dir=None)` → `(gd, out_dir=None, rock_type='auto')`
   - 内部复用 `recommended_diagrams` 做岩性判定和元素过滤，消除冗余 SiO₂ ��断

2. **推荐列表支持 `any_of` OR 条件**（P2）
   - 数据表从三元组 `(fn, desc, needed)` 升级为四元组 `(fn, desc, needed, any_of)`
   - AFM/Miyashiro/Mg# 设 `any_of=('FeO', 'TFe2O3')`，至少一个存在即可推荐
   - 消除了之前把 Fe 系从 needed 里拿掉的 workaround
   - `recommended_diagrams` 和 `plot_recommended` 中相应更新了解包逻辑

3. **`_source.py` 导入时快照冻结 `MK_SIZE_SINGLE`**（P2）
   - `from _style import MK_SIZE_SINGLE` 在导入时复制了变量值
   - `set_style` 修改的是 `_style.MK_SIZE_SINGLE`，但 `_source.py` 用的是自己的模块命名空间副本
   - 修复：改为 `import _style` + `s=_style.MK_SIZE_SINGLE`（调用时动态读取）
   - 其他子模块（`_classification.py`, `_evolution.py`, `_tectonic.py`）通过 `scatter_samples` 画散点，`scatter_samples` 内部每次调用时读 `_style.MK_SIZE_SINGLE`，不受此问题影响

4. **`quick_validate.py` `sys.reconfigure` 写错**（P3）
   - `sys.reconfigure()` 不存在，应调用 `sys.stdout.reconfigure(encoding='utf-8')`

## 永久留存陷阱记录

- **导入时快照陷阱**：`from module import variable` 在导入瞬间复制了变量的值。后续 `module.variable = new_value` 不影响当前模块中的副本。必须用 `import module; module.variable` 才能动态读取。此模式影响所有风格常量（`MK_SIZE_SINGLE`, `MK_SIZE_TERNARY` 等）。
- **`any_of` 设计模式**：数据驱动的过滤逻辑中，`any_of` 组内的元素构成 OR 关系（至少一个存在即可，不必全部存在）。比在运行时做 `feot_calc` 兜底更语义清晰，适合 agent 预览推荐列表。
- **patch 截断风险**：`patch` 操作目标文件被外部编辑后，可能产生内容截断。操作关键文件前建议先确认文件未被其他进程占用，或做备份。`_style.py` 的 `was modified since you last read it on disk` 警告是有效信号，必须 re-read 后再 patch。
- **混合 import 模式禁止**：`import _style; _style.xxx` 是唯一允许的模式。`from _style import ...`（包括混合使用两者）产生无声的运行时不一致。

## 当前约定

- 所有 diagram 文件使用绝对 import（`import _style` 而不是相对导入），因为 scripts/ 目录不是 pip 安装包
- **推荐模式**：`import _style; _style.MK_SIZE_SINGLE`、`_style.scatter_samples(...)`、`_style.save_fig(...)`
- **禁止模式**：任何 `from _style import ...`，包括混合 `from _style import ...` + `import _style`
- `whole_rock_core.py` 作为门面 API 保留，用户/agent 的 `from whole_rock_core import *` 代码零改动
- 添加新图件：在对应的 `_xxx.py` 中添加函数，然后在 `whole_rock_core.py` 中 import + re-export
- 任何 `ax.scatter()` 调用都必须显式写 `marker='o'`，不可依赖 matplotlib 默认值
- 数据表 tuple 更新时记得同步解包逻辑（`recommended_diagrams` 和 `plot_recommended` 中的 `for fn, desc, needed, any_of in pool`）
- **已废弃**：`MK_SIZE_PANEL`（阶段六用 `MK_SIZE_SINGLE` 统一后未清理）
- **已废弃**：`calc_ti_1000()`（阶段六 Ti 全部改用微量 ppm 后删除）
