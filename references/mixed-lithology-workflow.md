# 混合岩性出图工作流记录

> 当样品同时包含中基性（SiO₂ 55-62%）和酸性（SiO₂ 70-75%）成分时，`plot_recommended()` 按 SiO₂ 最小值判定岩性，会跳过镁铁质专用图。本文件记录补跑方案。

## 场景描述

- 样品：25SMH14 (SiO₂ 55-59%, 中基性) + 25SMH17 (SiO₂ 74-75%, 酸性)
- 自动判定：长英质（SiO₂ min = 54.8 ≥ 52）
- 推荐入口出图：8 张（K₂O-SiO₂, Shand, Winchester-Floyd, REE, 蛛网图, Harker, Mg#, Zr 协变）
- 实际共出图：25 张

## 补跑策略

`plot_recommended()` 执行完毕后，额外调用被跳过的镁铁质图件：

```python
# 镁铁质分类+构造
for fn in [plot_tas, plot_afm, plot_miyashiro, plot_meschede, 
           plot_wood, plot_pearce_cann, plot_4panel, plot_shervais,
           plot_saccani_2015, plot_zr_y_zr]:
    fn(gd)

# 镁铁质源区
for fn in [plot_pearce_2008, plot_u_th_zr_nb, plot_pearce_1983,
           plot_sm_yb_la_sm, plot_sc_v, plot_ba_th_la_sm, plot_co_th]:
    fn(gd)
```

## 注意事项

- 缺关键元素时函数返回 `(None, None)`，不会崩溃
- Ti 在微量数据中已存在（ppm 值），构造判别图（Meschede, Wood, Pearce-Cann, Shervais）均正常出图
- 含 TFe2O3 + FeO 时，Miyashiro/AFM/Mg# 会自动计算 FeOt
- 补跑的图不会自动进入原始 report_*.html，需要单独生成完整版 HTML

## 数据特征

| 样品 | SiO₂ | MgO | K₂O | Na₂O | TFe₂O₃ | 岩性 |
|------|------|-----|-----|------|---------|------|
| 25SMH14-1 | 57.0 | 1.88 | 1.45 | 5.53 | 8.38 | 中基性 |
| 25SMH14-2 | 54.8 | 2.21 | 1.29 | 5.56 | 8.92 | 中基性 |
| 25SMH14-3 | 58.9 | 1.82 | 1.30 | 5.17 | 7.94 | 中基性 |
| 25SMH17-1 | 74.9 | 0.09 | 5.21 | 3.82 | 3.52 | 酸性 |
| 25SMH17-2 | 75.2 | 0.08 | 4.18 | 4.62 | 3.48 | 酸性 |
| 25SMH17-3 | 74.5 | 0.09 | 3.61 | 5.33 | 3.52 | 酸性 |
