# La/Sm 比值 — 地球化学意义与图解应用

> 适用于：Ba/Th vs La/Sm 图、(Sm/Yb)PM vs (La/Sm)PM 图、REE 配分图解读
> 关联函数：`plot_ba_th_la_sm()`, `plot_sm_yb_la_sm()`, `plot_ree()`

---

## 核心含义

La/Sm 是岩浆岩源区性质和熔融过程的核心参数：

| 参数 | 含义 |
|------|------|
| **高 La/Sm** | 低程度熔融 / 富集源区 / 地壳混染 / 沉积物加入 |
| **低 La/Sm** | 高程度熔融 / 亏损源区（如 DMM） |

**原理**：La 比 Sm 更不相容，低程度熔融时优先提取 La → 熔体 La/Sm 极高。二者都是 REE，结晶分异影响小 → 主要反映源头信息。

## 图件判读

### Ba/Th vs La/Sm（Pearce & Robinson 2010）
- 俯冲流体 → Ba/Th 极高，La/Sm 几乎不变
- 沉积物熔融 → Ba/Th 高，La/Sm 也高

### (Sm/Yb)PM vs (La/Sm)PM（Li et al. 2016）
- 尖晶石橄榄岩源区：La/Sm 中低、Sm/Yb < 2
- 石榴石橄榄岩源区：La/Sm 中高、Sm/Yb > 5

### REE 配分图
- (La/Sm)N > 1 → 右倾 LREE 富集（大陆玄武岩/岛弧安山岩）
- (La/Sm)N ≈ 1 → 平坦型（高熔融 MORB/OIB）
- (La/Sm)N < 1 → 左倾亏损型（罕见）

## 标准化参考值（Sun & McDonough 1989）
- CI 球粒陨石：La = 0.687 ppm, Sm = 0.444 ppm
- 原始地幔：La = 0.687 ppm, Sm = 0.444 ppm（注意：代码中 `_normalize.py` 的 PRIMITIVE_MANTLE 对 La/Sm 的取值）
