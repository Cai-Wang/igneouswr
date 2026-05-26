# RockPlot SVG 图解目录

来源：RockPlot Electron 应用，位于 `D:\RockPlot`，SVG 提取自 app.asar -> dist/svg/diagrams/。

总计 55 张地球化学图解 SVG（排除 Spider、Scatter、Ternary、DoubleTernary 等展示用图）。

## 与 skill 重叠图（29 张）

已匹配 skill `igneous-geochemistry` 的 `DIAGRAM_REGISTRY`。

| SVG 文件名 | 中文描述 | 坐标类型 | skill 函数 | 备注 |
|---|---|---|---|---|
| TAS | TAS 全碱-硅分类 | 线性-线性 | plot_tas | fill:none，区域由轮廓围成 |
| AFM | AFM 三角分类 | 等边三角 | plot_afm | 无数值轴，A/F/M 顶点文本 |
| K2O_SiO2 | K2O-SiO2 分类 | 线性-线性 | plot_k2o_sio2 | Peccerillo & Taylor 1976 |
| Shand | Shand A/CNK-A/NK | 线性-线性 | plot_shand | Y 轴仅 1 刻度 |
| WinFloyd1 | Winchester-Floyd Zr/TiO2-Nb/Y | 对数-对数 | plot_winchester_floyd | |
| Miyashiro | Miyashiro FeOt/MgO-SiO2 | 线性-线性 | plot_miyashiro | Y 轴仅 1 刻度 |
| Harker | Harker 氧化物协变 | 线性-线性（多面板） | plot_harker | RockPlot 版本稍不同 |
| Zr_Covariance | Zr 协变 | 线性-线性（多面板） | plot_zr_covariance | |
| Meschede | Meschede Nb-Zr-Y 三元 | 三元图 | plot_meschede | 3 clipPath |
| Wood | Wood Hf/3-Th-Ta 三元 | 三元图 | plot_wood | 3 clipPath |
| PearceCann | Pearce & Cann Ti-Zr-Y 三元 | 三元图 | plot_pearce_cann | 3 clipPath |
| Shervais | Shervais Ti-V | 线性-线性 | plot_shervais | |
| Co_Th | Co vs Th (Hastie 2007) | 线性-线性 | plot_co_th | |
| PearceNorry | Pearce & Norry Zr/Y-Zr | 对数-对数 | plot_pearce_1983（不对应） | skill 中无此函数 |
| Pearce1996 | Pearce Th/Yb-Nb/Yb | 对数-对数 | plot_pearce_2008 | |
| PearceThYb_TaYb | Pearce Th/Yb-Ta/Yb 1983 | 对数-对数 | plot_pearce_1983 | |
| NbLa_ThLa | Nb/La vs Th/La | 线性-线性 | plot_nb_la_th_la | |
| BaTh_LaSm | Ba/Th vs La/Sm | 线性-线性 | plot_ba_th_la_sm | |
| SmYb_LaSm | (Sm/Yb)-(La/Sm) 部分熔融 | 线性-线性 | plot_sm_yb_la_sm | |
| Sc_V | Sc vs V | 线性-线性 | plot_sc_v | |
| GdYb_DyDy | Gd/Yb vs Dy/Dy* | 线性-线性 | plot_gdyb_dydystar | |
| DyYb_LaYb | Dy/Yb vs La/Yb | 线性-线性 | plot_dyyb_layb | |
| UTh_ZrNb | U/Th vs Zr/Nb | 线性-线性 | plot_u_th_zr_nb | |
| MgNo_SiO2 | Mg# vs SiO2 | 线性-线性 | plot_mgno | |
| An_Ab_Or | An-Ab-Or 三元（O'Connor） | 三元图 | plot_an_ab_or | |
| QAPF | Q-A-PF 分类（Streckeisen） | 三元图 | plot_qapf | |
| 4panel | 四联比值判别 | 线性-线性（4 面板） | plot_4panel | |
| Saccani | NbN-ThN (Saccani 2015) | 线性-线性 | plot_saccani_2015 | |
| ZrY_Zr_Xia | Zr/Y vs Zr (Xia 2014) | 对数-对数 | plot_zr_y_zr | |

## RockPlot 独有图（26 张）

skill 中尚未实现的图。按地球化学分组整理：

### 构造环境（10 张）

| SVG 文件名 | 文献 | 坐标轴 | 说明 |
|---|---|---|---|
| PearceGranite | Pearce et al. 1984 | log-log: Rb vs Y+Nb | 花岗岩构造判别 |
| TaYb_Yb | Pearce 1982? | log-log: Ta/Yb vs Yb | 俯冲带判别 |
| Th_Hf_Ta | Wood 1980 变体 | 三元 | Hf-Th-Ta 三元变体 |
| Th_Ta_Hf |  | 三元 | Ta 在顶点的变体 |
| Zr_Y_Ti |  | 三元 | Zr-Y-Ti 三元判别 |
| Ti_Zr_Sr | Pearce & Cann 1973 变体 | 三元 | Ti-Zr-Sr 三元 |
| Zr_Nb_Y |  | 三元 | Zr-Nb-Y 三元 |
| Hf_Zr_Nb |  | 三元 | Hf-Zr-Nb 三元 |
| Cr_Y |  | log-linear | Cr vs Y 判别 |
| Zr_Nb_Ce_Y |  | 三元/四元 | 组合路径 |

### 地幔源区（8 张）

| SVG 文件名 | 文献 | 坐标轴 | 说明 |
|---|---|---|---|
| PearceNbTiYb | Pearce (变体) | log-log: Ti/Yb vs Nb/Yb | |
| La_Nb |  | log-linear | La vs Nb |
| Nb_Zr |  | log-log? | Nb vs Zr |
| La_Sm_Nd |  | 三元 | La-Sm-Nd 三元 |
| Th_Nb_Ce |  | 三元 | Th-Nb-Ce 三元 |
| Zr_Yb_Nb |  | 三元/二元 | Zr/Yb vs Nb |
| Hf_Sm_Nd |  | 三元 | Hf-Sm-Nd 三元 |
| La_Y_Nb |  | 三元 | La-Y-Nb 三元 |

### 分类与演化（5 张）

| SVG 文件名 | 文献 | 坐标轴 | 说明 |
|---|---|---|---|
| K2O_Na2O | Middlemost? | linear-linear | K2O vs Na2O |
| FeO_MgO |  | linear-linear | FeO vs MgO |
| Al2O3_SiO2 |  | linear-linear | Al2O3 vs SiO2 |
| CaO_SiO2 |  | linear-linear | CaO vs SiO2（炭���岩分类） |
| Co_Ni |  | linear-linear | Cu-Ni 判别 |

### 稀有（3 张，待确认）

| SVG 文件名 | 文献 | 坐标轴 | 说明 |
|---|---|---|---|
| Carbonatite | 碳酸岩分类 | 三元? | 碳��岩专属分类图 |
| TTG |  | 三元/二元 | TTG 岩石分类 |
| Jensen | Jensen 1976 | 等边三角 | MgO-FeOt+TiO2-Al2O3 三角 |

## 批量提取参数

| 参数 | 值 |
|---|---|
| 映射公式模板 | `px = slope * (value or log10(value)) + intercept` |
| tick chunk size | 1200 字符 |
| X/Y 分类阈值 | `py < 0.1` 为 X tick，`px < 0.1` 为 Y tick |
| 对数判定比值范围 | 2.5 到 15 |
| 线性拟合验证 | R2 > 0.99 确认 |
| SVG 区域 translate | (100, 50) |
| SVG 有效宽度 | 约 700 px（x: 0.5~700.08） |
| SVG 有效高度 | 约 526 px（y: 0.5~526.5） |
