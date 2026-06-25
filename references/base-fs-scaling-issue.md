# base_fs 字号架构变更记录

## v2.3（废弃）

- `base_fs` 返回无量纲比例 `ax_w_mm / 203.0`
- 调用：`fontsize=N * base_fs(ax)`，N 是硬编码 pt 值
- 问题：不读 rcParams，无视 figkit 预设的 font.size

## v2.4（当前 — 2026-07-01 重构）

- `base_fs` 返回实际 pt 值
- 调用：`fontsize=base_fs(ax, scale=M)`，M = N/10 即 GCDkit cex 等价
- 读取 `plt.rcParams['font.size']` 做基准
- 下限 `max(raw_fs, target_fs * 0.55)`
- 所有调用站（_classification.py、_evolution.py、_tectonic.py）共 44+ 处替换

## 效果

| 场景 | 旧 (v2.3) | 新 (v2.4) |
|------|-----------|-----------|
| 裸图 203mm, font.size=10 | 10pt (硬编码) | 10pt (读 rcParams) |
| 裸图 203mm, font.size=8 | 10pt (不读 rcParams) | 8pt (读 rcParams) |
| 拼版 75mm, font.size=8 | 3.7pt (无下限) | 4.4pt (下限 55%) |
