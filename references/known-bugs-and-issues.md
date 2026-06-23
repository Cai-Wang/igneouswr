# Known Bugs & Issues (IgneousWR)

Documented from real session failures, not speculative.

## 1. HTML report: silent failure

`generate_report_html()` fails with `cannot access local variable 'html' where it is not associated with a value`. The `html` variable is referenced before assignment in certain code paths. The plots themselves still generate fine; only the report.html is missing.

**Status:** unfixed as of v1.0.0  
**Impact:** low — all PNG figures generate correctly  
**Workaround:** ignore the warning, check the output PNGs directly

## 2. `plot_recommended()` result dict

The SKILL.md documents keys `output_dir` and `html_report` in the return dict, but these may not actually be present. The only reliable keys are `figures`, `total`, `generated`, `failed`.

## 3. `plot_recommended()` / `plot_diagram()` parameter name

The parameter is `out_dir`, not `output_dir`. Passing `output_dir=` causes a TypeError.
Use `set_out_dir(path)` BEFORE calling plot functions as the reliable alternative.

## 4. `check_elements()` call signature

`gd.check_elements(["SiO2", "Na2O", "K2O"])` fails with `TypeError: unhashable type: 'list'` because `check_elements` expects `*args`, not a list. Use:
```python
gd.check_elements("SiO2", "Na2O", "K2O")  # ✅ correct
```

## 5. `plot_diagram` / `plot_diagram_ids` not exported

These functions are listed in SKILL.md's `from igneous_wr_core import` block but are **not actually exported** from `igneous_wr_core`. They may exist deeper in the package but cannot be imported from the public API.

**Workaround:** use the individual diagram functions directly by their name (`plot_ree`, `plot_spider`, `plot_tas`, etc.) instead of the generic `plot_diagram` wrapper. All available exports can be checked with `dir(igneous_wr_core)`.

## 6. AI agents: don't bypass IgneousWR for REE/spider

When asked for REE or spider diagrams, the correct first step is to load IgneousWR skill and call `plot_ree(gd, save=False)` / `plot_spider(gd, save=False)`. Do NOT write matplotlib code from scratch (manual normalization with pandas, custom color mapping, etc.) — the skill already handles grouping, normalization, legend, and styling conventions. Compose the returned axes into a combined figure as described in `references/panel-composing-workflow.md`.

## 7. ✅ FIXED: `infer_groups()` grouped MT01A and MT01B together

**Bug:** The SKILL.md documented pattern 2 (`^([A-Za-z]+[0-9]+)` → e.g. `MT01A1` → prefix `MT01`), but this pattern was NOT in the actual code. Only pattern 1 (hyphen prefix) was implemented; everything else fell through to fallback (full sample name as group).

**Fix (2026-06-21):** Added actual pattern 2 in `data.py:infer_groups()`:
```python
# 2) 字母+数字+字母核心，去掉末尾点号数字: MT01A1 → MT01A
m = re.match(r'^([A-Za-z]+[0-9]+[A-Za-z]+)\d*$', lbl_str)
```
Also updated SKILL.md to match the actual regex.

## 8. ✅ FIXED: plot_ree/plot_spider missing `ax=` parameter

**Bug:** `plot_ree()` and `plot_spider()` in `_source.py` did not accept an `ax` parameter, making them incompatible with figkit's A4Grid panel mode. Also had hardcoded `fontsize=8.5` / `fontsize=7.5` that should be controlled by figkit's `apply_format()`.

**Fix (2026-06-21):** Added `ax=None` parameter, split auto-figure vs provided-ax paths, removed `save` side-effect when ax is provided, and removed `fontsize=` from `set_xticklabels()`. IgneousWR handles content; figkit's `apply_format()` handles font size.

**Requirement for future diagram functions:** ALL plot functions must accept `ax=None` and behave correctly in both standalone and panel modes.

## 9. ✅ FIXED: spider X-axis tick alternating in/out with `_direction` and `set_ydata` both failed

**Bug:** Two approaches were tried and both failed:
- `t._direction = 'out' if i % 2 else 'in'` — attribute is stored but not used by matplotlib ≥3.8 renderer
- `t.tick1line.set_ydata([0, -length if i % 2 else length])` — ydata is modified but tick direction is controlled by marker symbol, not line data

**最终方案 (2026-06-21):** matplotlib 渲染 tick 方向靠的是 `tick1line` 的 **marker 标记值**，不是 ydata 也不是 `_direction`：

```python
t.tick1line.set_marker(2)  # tickup → 向上指 → 对于底部X轴 = 向内（进入图区）
t.tick1line.set_marker(3)  # tickdown → 向下指 → 对于底部X轴 = 向外（离开图区）
```

**关键时序：** 必须 `fig.canvas.draw()` 之后才能改 marker（tick1line 对象在 draw 后才真正创建）。

**预防：** 
- 如果后面调了 `ax.tick_params(direction=...)`，它会重置所有 tick 的 marker 值
- 详见 IgneousWR skill 的 `references/matplotlib-tick-workarounds.md`

## 10. ✅ FIXED: `_standalone` Python scoping bug

**Bug:** In `plot_ree()` and `plot_spider()`, the function parameter `ax=None` was reassigned by `fig, ax = plt.subplots()` inside the first `if ax is None:` block. The second `if ax is None:` block (containing tight_layout, tick settings, etc.) was **never entered** because `ax` was no longer None after the reassignment.

**Pattern (WRONG):**
```python
def plot_xxx(gd, ..., ax=None):
    if ax is None:
        fig, ax = plt.subplots()  # ← ax is reassigned HERE
    ...
    if ax is None:                # ← NEVER True! ax is now an Axes object
        plt.tight_layout()        # ← NEVER executes
```

**Fix:** Save the original state BEFORE reassignment:
```python
def plot_xxx(gd, ..., ax=None):
    _standalone = ax is None       # ← save BEFORE reassignment
    if ax is None:
        fig, ax = plt.subplots()
    ...
    if _standalone:                # ← correct!
        plt.tight_layout()
```

**Applies to:** Any function that conditionally creates a Figure/Axes and later needs to check whether it was standalone mode. This is a Python scope trap, not specific to matplotlib.

## 11. ✅ FIXED: plot_ree Y 轴 set_yticks 在 set_yscale 之前

**Bug:** `plot_ree` 第54-56行 `set_yticks` + `set_yticklabels`，第64行 `set_yscale('log')`。后者会调用 `set_default_locators_and_formatters()` 重置 major locator 为 `LogLocator`，覆盖前者的 `FixedLocator`。在数据范围小的场景（如 0.5-50），LogLocator 会插入 0.2、0.5 等非预期标签。

**Fix (2026-06-26):** 改成和 `plot_spider` 一致的写法：`set_yscale('log')` → `FixedLocator` → `FuncFormatter` → `NullLocator`。Y 轴处理顺序统一。

## 12. ✅ FIXED: plot_ree X 轴次要刻度未关闭

**Bug:** `style_ax()` 调 `minorticks_on()` 后 REE X 轴出现 13 根次要刻度线（14 个元素位之间）。`apply_ree_axis_style` 只处理 Y 竖排，没有 `xaxis.set_minor_locator(NullLocator())`。

**Fix (2026-06-26):** `plot_ree` 主路径加 `ax.xaxis.set_minor_locator(NullLocator())`，和 Y 轴同步关闭次要刻度。

## 13. ✅ FIXED: 蛛网图 X 轴首尾标签与边框重叠（拼版模式）

**Bug:** `plot_spider` 的 `xlim` padding 固定 ±0.3 数据单位。裸图（~200mm 宽）下 OK，A4 拼版 cell（~75mm）下 0.3 数据单位 = 0.8mm，标签字宽 ~2mm，Cs 和 Lu 顶破边框。

**Fix (2026-06-26):** 新增 `auto_xlim_padding(ax)` — 实测首尾 xticklabel bbox，超出多少扩多少。内容级独立函数，时序 `finalize → auto_xlim_padding → apply_*_axis_style → save`。

## 14. ✅ FIXED: apply_ree_axis_style 缺少 X 轴交替格式

**问题:** `apply_ree_axis_style` 只处理 Y 竖排，REE 和 Spider 的 X 轴视觉不对齐。

**Fix (2026-06-26):** `apply_ree_axis_style` 扩展为和 `apply_spider_axis_style` 相同的 X 轴处理：`set_marker(2/3)` 刻度交替 + `ScaledTranslation(±7pt)` 标签偏移 + `NullLocator` 次要刻度关闭。

## 15. ✅ FIXED: X 轴标签偏移不对称（6pt / -4pt）

**Bug:** `apply_spider_axis_style` 偶数位标签向内 +6pt，奇数位向外 -4pt。`TICK_LENGTH=5pt`，奇数位标签距刻度尖仅 1pt（5pt 外 + 4pt 外），且偶数位距轴线 6pt、奇数位距轴线仅 4pt——不称。

**Fix (2026-06-26):** 统一为 ±7pt。标签与刻度尖始终保持 2pt 间隙，内外对称。`apply_ree_axis_style` 和 `apply_spider_axis_style` 共用相同值。

## 16. ✅ FIXED: Spider Y 轴多延一个 decade 导致标签拥挤

**Bug:** `plot_spider` 的 `ymin` 额外 `- 1` decade，比 REE 多延伸一个数量级。数据跨度 +1 decade 后容易 >7 个 label，在 42mm 高 cell 里重叠。

**Fix (2026-06-26):** 去掉额外延伸，和 REE 统一。同时加防御：>7 decade 时稀疏标签（按 decade 指数奇偶跳显），防止极端数据标签拥挤。MT01-04 数据 6 decade 全显正常。

## 17. ✅ FIXED: 稀疏标签 formatter 浮点精度 + 索引跳显错误

**Bug(1):** `FuncFormatter` 用 `ticks.index(v)` 精确匹配——`10**0` 和 `FixedLocator` 传回的 `1.0` 浮点不精确相等，`ValueError` 返回空字符串，导致 "1" 标签消失。

**Bug(2):** 初始 stride=2 按数组索引取偶数位——8 个 tick `[0.001,...,10000]` 取索引 0,2,4,6 → 跳过了 "1"（索引3）和 "100"（索引5）。

**Fix (2026-06-26):** 改用 `round(np.log10(v)) % 2 == 0` 按 decade 指数判断——`10^0=1` 指数偶数→标，`10^2=100` 指数偶数→标。不依赖索引或浮点精确匹配。

**What happened (2026-06-21):** All 15 `_style.add_legend(ax)` calls across 4 diagram files were removed. Legend creation is now handled by figkit's `apply_style()`, which:
  - Collects line labels from all subplots
  - Creates a single shared legend on the first subplot
  - Uses `Line2D(linewidth=0, marker='o')` for dots-only handles (no line swatch)

**Impact on standalone mode:** When IgneousWR functions are called without figkit (standalone), no legend is auto-generated. Users must manually call `ax.legend()` or use workaround:
```python
fig, ax = plot_ree(gd, save=False)
ax.legend()  # manually add legend in standalone mode
```

## 11. ✅ FIXED: plot_ree Y-axis tick order inconsistent with plot_spider

**Bug (2026-06-27):** `plot_ree` called `set_yticks()` / `set_yticklabels()` **before** `set_yscale('log')`, causing matplotlib's LogLocator to potentially override the manually-set ticks. Also lacked `NullLocator()` for minor ticks, which could produce dense sub-decade tick marks.

`plot_spider` had the correct order (`set_yscale('log')` → `FixedLocator` → `NullLocator`), but REE did not match.

**Fix:** Brought `plot_ree` inline with `plot_spider`: moved `set_yscale('log')` before the tick setup, replaced `set_yticks`/`set_yticklabels` with `FixedLocator` + `FuncFormatter`, and added `NullLocator()` for minor ticks. Both functions now share identical Y-axis tick logic.

**Prevention:** When editing `plot_ree` or `plot_spider`, verify they stay in sync on Y-axis setup. If one changes, check the other.
