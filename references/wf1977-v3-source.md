# wf1977_v3.py — Winchester & Floyd (1977) 72 点系统原始母版

> **来源**：用户提供的独立脚本，位于 WorkBuddy 目录
> `/mnt/c/Users/opcry/WorkBuddy/2026-05-25-08-24-41/wf1977_v3.py`
>
> **更新日期**：2026-05-25

## 与本 skill 的关系

`wf1977_v3.py` 是 `_classification.py::plot_winchester_floyd()` 中底图数据的**原始母版**。
代码中的 72 个 POINTS、12 条 LINES、6 个 JUNCTIONS 以及 ROCK_LABELS 全部来自此脚本。

## 与 skill 中实现的差异

`wf1977_v3.py` 是自包含的独立脚本，实现与原文献图版 1:1 对应的完整底图，包含：
- 所有 72 个原始数据点（红色散点 + 编号标签）
- Junction 交叉点蓝色圆圈高亮
- 右上角线段速查框
- 点级标签偏移量系统（防止标签重叠）

而 skill 中的 `plot_winchester_floyd()` 仅提取��：
- POINTS 坐标、LINES 分段、JUNCTIONS 标注、ROCK_LABELS
- 省略了红色数据点编号标签（这些是底图绘制辅助标记，不是图的一部分）
- 省略了点级标签偏移（skill 中不标注点号）
- 省略了右上角速查框

## 参考

- 对应的分界线坐标详细文档：`references/winchester-floyd-boundary-data.md`
- WF 公式说明：`references/winchester-floyd-formula.md`
- 旧版 GeoPlotters 提取记录（已废弃）：`references/geo-plotters-xls-extraction.md`
