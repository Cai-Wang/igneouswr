# 自动计算比值参考 (merge_excel.py compute_ratios)

## 总览

`merge_excel.py` 的 `compute_ratios()` 函数在合并主量/微量后，自动计算并追加 40 个常用地球化学比值到输出 Excel。

球粒陨石标准化值采用 **Sun & McDonough (1989)**。

## 稀土相关 (16 项)

| 比值 | 公式 | 说明 |
|------|------|------|
| ΣREE | La+Ce+Pr+Nd+Sm+Eu+Gd+Tb+Dy+Ho+Er+Tm+Yb+Lu | 稀土总量 |
| LREE | La+Ce+Pr+Nd+Sm+Eu | 轻稀土和 |
| HREE | Gd+Tb+Dy+Ho+Er+Tm+Yb+Lu | 重稀土和 |
| LREE/HREE | LREE / HREE | 轻重稀土分异 |
| Eu/Eu* | EuN / [(SmN+GdN)/2] | Eu 异常 |
| Ce/Ce* | CeN / [(LaN+PrN)/2] | Ce 异常 |
| (La/Yb)N | (La/CI) / (Yb/CI) | 轻重稀土分异程度 |
| (La/Sm)N | (La/CI) / (Sm/CI) | 轻稀土分馏 |
| (Gd/Yb)N | (Gd/CI) / (Yb/CI) | 重稀土分馏 |
| (Dy/Yb)N | (Dy/CI) / (Yb/CI) | 中重稀土分馏 |
| (Sm/Yb)N | (Sm/CI) / (Yb/CI) | 中稀土 vs 重稀土 |
| (Tb/Yb)N | (Tb/CI) / (Yb/CI) | 重稀土细微分馏 |
| (Ce/Yb)N | (Ce/CI) / (Yb/CI) | |
| (Pr/Yb)N | (Pr/CI) / (Yb/CI) | |
| (Nd/Yb)N | (Nd/CI) / (Yb/CI) | |
| (La/Nd)N | (La/CI) / (Nd/CI) | 轻稀土内部 |

*CI = 球粒陨石标准化值*

## 微量元素比值 (24 项)

| 比值 | 公式 | 地质意义 |
|------|------|----------|
| Zr/Hf | Zr / Hf | 岩浆分异程度 |
| Nb/Ta | Nb / Ta | 俯冲/地幔源区 |
| Zr/Nb | Zr / Nb | 源区亏损程度 |
| Th/Nb | Th / Nb | 地壳混染 |
| Th/La | Th / La | 沉积物俯冲 |
| La/Nb | La / Nb | 源区特征 |
| La/Ta | La / Ta | 地幔源区类型 |
| Ba/Th | Ba / Th | 俯冲流体 |
| Ba/Nb | Ba / Nb | 俯冲流体印记 |
| Rb/Sr | Rb / Sr | 部分熔融程度 |
| Sr/Y | Sr / Y | 榴辉岩相残留 |
| Zr/Y | Zr / Y | 地幔熔融程度 |
| Ti/Y | Ti / Y | 源区深度 |
| Ti/Zr | Ti / Zr | 钛矿物分异 |
| Ni/Co | Ni / Co | 镁铁质来源 |
| Cr/Ni | Cr / Ni | 超镁铁质来源 |
| V/Cr | V / Cr | 氧逸度（定性） |
| V/Sc | V / Sc | 氧逸度指标 |
| Ce/Pb | Ce / Pb | 地壳混染 |
| Nb/U | Nb / U | 地幔/地壳区分 |
| Sm/Nd | Sm / Nd | 稀土分馏 |
| Rb/Ba | Rb / Ba | 流体活动性 |
| Ba/Sr | Ba / Sr | 流体活动性 |
| Sr/Nd | Sr / Nd | 源区特征 |

## 实现注意事项

- `compute_ratios()` 接收 `(sample_count, data_dict)`，data_dict 的键是元素名、值是长度=sample_count 的列表
- 返回 `[(name, [values]), ...]`，仅保留至少有一个非 None 值的比值
- 依赖元素缺失的比值自动跳过（不会报错，不输出该行）
- 标准化比值和 Eu/Eu* 精确到 3 位小数，简单比值精确到 2 位
- 内部用 `_get_val()` 安全取数，不依赖 pandas

## 开发者备注

如需添加新比值：
1. 在 `for i in range(sample_count)` 循环内用 `normalized_ratio()` 或 `simple_ratio()` 计算
2. 加入 `ratios.append()` 的字典中
3. `ratio_names` 会自动提取并按字典插入顺序排列
