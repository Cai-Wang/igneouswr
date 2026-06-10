# Guan et al. (2025) 文献图解参考

> Guan et al. (2025) Early Paleozoic subduction initiation in the West Proto-Tethys Ocean: Insights from ophiolitic Speik Complex in the Eastern Alps. *Geoscience Frontiers*.
>
> Obsidian 文献笔记：`/mnt/d/Hermes DB/文献笔记/Guan2025_Speik俯冲起始地化论证.md`
> 分析记录：`/mnt/d/Hermes DB/分析记录/2026-05-09 Guan2025 地化图解学习.md`

## 该文献使用的图解在本 skill 中的对应函数

| 文献图号 | 图名 | skill 函数 | 实现状态 |
|---------|------|-----------|---------|
| Fig.5 | Nb/Y vs Zr/Ti (Pearce 1996) | `plot_winchester_floyd()` | ✅ 已有 |
| Fig.6a,c,e | REE 球粒陨石标准化 | `plot_ree()` | ✅ 已有 |
| Fig.6b,d,f | PM 蛛网图 | `plot_spider()` | ✅ 已有 |
| Fig.8 | Zr 协变 | `plot_zr_covariance()` | ✅ 已有 |
| Fig.9a | 2Nb-Zr/4-Y (Meschede 1986) | `plot_meschede()` | ✅ 已有 |
| Fig.9b | Hf/3-Th-Ta (Wood 1980) | `plot_wood()` | ✅ 已有 |
| Fig.10a | Ti vs V (Ishizuka/Shervais) | `plot_shervais()` | ✅ 已有 |
| Fig.10b | **Sc vs V (Hickey-Vargas 2018)** | `plot_sc_v()` | ✅ 2026-05-09 新增 |
| Fig.10c | Th/Yb vs Nb/Yb (Pearce 2008) | `plot_pearce_2008()` | ✅ 已有 |
| Fig.10d | **Ba/Th vs La/Sm (Pearce & Robinson 2010)** | `plot_ba_th_la_sm()` | ✅ 2026-05-09 新增 |
| 讨论 | **Zr/Y vs Zr (Xia 2014)** | `plot_zr_y_zr()` | ✅ 2026-05-09 新增 |

## 论证逻辑（可复用写作结构）

8 层递进论证链，从岩性定名到构造模型：

1. **定名** → Nb/Y-Zr/Ti（分类图）
2. **微量元素模式** → REE + 蛛网图（识别俯冲信号）
3. **排除变质干扰** → Zr 协变图（验证数据可靠性）
4. **构造环境** → 三元构造判别图（MORB vs 弧）
5. **氧化条件/过程** → Ti-V + Sc-V + Th/Yb-Nb/Yb + Ba/Th-La/Sm（核心）
6. **弧类型细化** → Zr/Y vs Zr + Th/Yb-Ta/Yb 比值（岛弧 vs 大陆弧）
7. **特殊岩石成因** → SiO₂ vs La/Yb 等（斜长花岗岩）
8. **归纳为模型** → 结合年代学整合到区域构造演化

## 关键地化指标参考值

| 指标 | FAB | 玻安岩 | 岛弧玄武岩 | MORB |
|------|-----|--------|-----------|------|
| (La/Yb)N | 0.52–1.27 | — | 1.64–3.54 | ~0.6–1.0 |
| Ti/V | ~20–50 | ~10 | ~20–60 | ~50–100 |
| V/Sc | ~5–8 | ~3–6 | ~4–7 | ~6–8 |
| Ba/Th | 50–200 | >200 | 高 | <50 |
| Zr/Y | < 3 | — | < 3 | ~2–3 |

## 数据来源

- Mariana FABs 和玻安岩：Reagan et al. (2010)
- Diyanmiao/Qimanyute FABs：Li et al. (2020), Zhang et al. (2022)
- 玻安岩类角闪岩：Burda et al. (2021)
- ASB 玄武岩：Arculus et al. (2015)
