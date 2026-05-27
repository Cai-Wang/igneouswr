# Batch Background 出图工作流

生成所有 70 张图件的纯底图（无样品投点），用于底图校正/配色审查/预览。

## 脚本

`scripts/batch_backgrounds_main.py` — 统一整合版，替代旧的 batch_backgrounds.py + batch_backgrounds_fix.py

## 用法

```bash
cd scripts/

# full 模式（推荐）：伪造 5 样品的全元素数据 + patch scatter 为空操作
# 覆盖全部 70 张图
python batch_backgrounds_main.py --mode full [--out-dir path/to/output]

# minimal 模式：纯全 NaN 数组，0 样品
# 仅测试不需要实际数据的图
python batch_backgrounds_main.py --mode minimal [--out-dir path/to/output]
```

默认输出目录：`/mnt/c/Users/opcry/Desktop/igenous实验0527/`

## 实现原理

- `FakeGeochemData` 类完全 mock 了 `GeochemData` 的全部接口
  - `mode='minimal'`：所有 `get()` 返回全 NaN 空数组，`groups=None`
  - `mode='full'`：提供 5 个假样品的全元素数据，`groups=['G1',...]`，Ti=6000 ppm
- `mode='full'` 时 patch `igneous_geochem.report.style.scatter_samples` 为空操作
- 同时 patch `save_fig` 用 `spec.filename`（前缀名）输出，不受各绘图函数内部 hardcode 的旧文件名影响
- 所有图无需修改核心代码即可生成纯底图

## 关键要点（历史教训）

1. **groups 不能为 None**：REE/蛛网图调用 `get_group_colors(groups)`，传 None 会报 `TypeError`
2. **Ti vs TiO₂**：PearceCann、Shervais、4panel 等图需要 ppm 级的 'Ti' 元素（从微量列读），不是氧化物 TiO₂
3. **check_elements 不能太宽松**：FakeGeochemData 的 `check_elements` 需要正确返回缺素元素名，否则某些函数在后续 `np.all(np.isnan(arr))` 检查中退出
4. **Ti 值量级**：需要 6000 ppm 级别，不是 6000 wt%
