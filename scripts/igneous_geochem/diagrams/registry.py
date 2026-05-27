"""
registry.py — 图件注册表

集中管理所有图件的元信息：绘图函数、输出文件名、描述、元素依赖、岩性适用。

DiagramSpec 支持 6 参写法（向后兼容）：
    DiagramSpec(fn, filename, desc, needed, any_of, rock_types)

新增 3 个可选字段（人工校正管理）：
    review_status: "needs_review" / "verified" / "experimental"
    source_ref:    参考来源（如 "Winchester & Floyd 1977"）
    review_note:   校正说明
"""

from dataclasses import dataclass, field
from typing import Optional

# ── import 所有绘图函数（避免循环依赖：registry 不 import whole_rock_core） ──
# 旧模块仍在 whole_rock/diagrams/ 中，使用绝对导入（scripts 在 sys.path 中）
from whole_rock.diagrams._classification import (
    plot_tas, plot_k2o_sio2, plot_afm, plot_shand, plot_winchester_floyd,
    plot_cabanis, plot_mullen, plot_jensen, plot_oconnor_volc, plot_ohta_arai,
    plot_pearce1977, plot_co_th, plot_an_ab_or, plot_qapf,
)
from whole_rock.diagrams._source import (
    plot_ree, plot_spider, plot_pearce_2008,
    plot_u_th_zr_nb, plot_pearce_1983, plot_sm_yb_la_sm,
    plot_sc_v, plot_ba_th_la_sm, plot_zr_y_zr,
    plot_gdyb_dydystar, plot_dyyb_layb, plot_nb_la_th_la,
)
from whole_rock.diagrams._evolution import (
    plot_harker, plot_miyashiro, plot_mgno, plot_zr_covariance,
)
from whole_rock.diagrams._tectonic import (
    plot_meschede, plot_wood, plot_pearce_cann, plot_4panel, plot_shervais,
    plot_saccani_2015, plot_harris, plot_muller_kternary,
)
from whole_rock.diagrams._xy_diagrams import (
    plot_tasmiddlemostplut, plot_tasmiddlemostvolc, plot_coxplut, plot_coxvolc,
    plot_pearcenorry, plot_pearce1982,
    plot_pearcegranite, plot_pearcenbthyb, plot_pearcenbtiyb,
    plot_frost, plot_whalen1, plot_whalen2, plot_whalen3, plot_sylvester,
    plot_villaseca, plot_debonba, plot_debonpq, plot_schandl, plot_batchelor,
    plot_mullerkbinary, plot_hollocher1, plot_hollocher2,
    plot_hastie, plot_maniar, plot_agrawal, plot_verma,
    plot_larocheplut, plot_larochevolc, plot_middlemostplut,
    plot_pecetaylor, plot_layb, plot_ross,
)


@dataclass
class DiagramSpec:
    """图件规格。支持 6 参写法；新增 review 字段带默认值，不破旧语法。"""
    fn: object
    filename: str
    desc: str
    needed: tuple
    any_of: Optional[tuple] = None
    rock_types: tuple = ("mafic",)
    # ── 人工校正状态（可选，默认 needs_review） ──
    review_status: str = "needs_review"
    source_ref: str = ""
    review_note: str = ""


# ════════════════════════════════════════════════════════════════
# DIAGRAM_REGISTRY — 70 张图件注册表
# ════════════════════════════════════════════════════════════════
DIAGRAM_REGISTRY = [
    # ── 📋 岩石系列 / 分类 ─────────────────────────────
    DiagramSpec(plot_tas,      "CLS-01_TAS.png",            "TAS 全碱-硅分类图",                         ('SiO2', 'Na2O', 'K2O'), None,                        ("mafic",),
                review_status="verified", source_ref="Le Bas et al. 1992 (pyrolite coordinates)",
                review_note="17 个分类区多边形+碱性/亚碱性虚线, 无 pyrolite 依赖"),
    DiagramSpec(plot_k2o_sio2, "CLS-02_K2O_SiO2_PT76.png",  "K₂O–SiO₂ 钾系列分类图",                      ('SiO2', 'K2O'),        None,                        ("mafic", "felsic"),
                review_status="verified", source_ref="Peccerillo & Taylor 1976"),
    DiagramSpec(plot_afm,      "CLS-03_AFM_IB1971.png",      "AFM 钙碱性-拉斑系列判别",                    ('Na2O', 'K2O', 'MgO'), ('FeO', 'TFe2O3'),           ("mafic",),
                review_status="verified", source_ref="Irvine & Baragar 1971"),
    DiagramSpec(plot_shand,    "CLS-04_Shand_ACNK_ANK.png",  "Shand A/CNK–A/NK 铝质分类图",               ('Al2O3', 'CaO', 'Na2O', 'K2O'), None,                ("felsic",),
                review_status="verified", source_ref="Shand 1947; Frost & Kelsey 2013"),
    DiagramSpec(plot_winchester_floyd, "CLS-05_Winchester_Floyd1977_NbY_ZrTiO2.png",
                "Winchester & Floyd Zr/TiO2–Nb/Y 分类图", ('Zr', 'TiO2', 'Nb', 'Y'), None,      ("mafic", "felsic"),
                review_status="verified", source_ref="Winchester & Floyd 1977; v11 精细校正"),

    # ── 🔬 源区性质 ──────────────────────────────────
    DiagramSpec(plot_ree,      "SRC-01_REE_chondrite.png",   "REE 球粒陨石标准化配分图",
                ('La','Ce','Pr','Nd','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu'), None,    ("mafic", "felsic"),
                review_status="verified", source_ref="Sun & McDonough 1989"),
    DiagramSpec(plot_spider,   "SRC-02_Spider_PM.png",       "原始地幔标准化蛛网图",
                ('Rb','Ba','Th','U','Nb','Ta','La','Ce','Pb','Pr','Nd','Sr','Sm','Zr','Hf','Eu','Ti','Gd','Tb','Dy','Ho','Y','Er','Tm','Yb','Lu'), None, ("mafic", "felsic"),
                review_status="verified", source_ref="Sun & McDonough 1989"),
    DiagramSpec(plot_pearce_2008, "SRC-03_Pearce2008_ThYb_NbYb.png",
                "Pearce Th/Yb–Nb/Yb 源区判���图",                  ('Th', 'Nb', 'Yb'),                None,  ("mafic",),
                review_status="verified", source_ref="Pearce 2008"),

    # ── 🗺️ 演化 / 协变 ─────────────────────────────
    DiagramSpec(plot_harker,   "EVO-01_Harker_6panel.png",    "Harker 六合一协变图",                       ('SiO2','MgO','Al2O3','CaO','Na2O','TiO2'), ('FeO', 'TFe2O3'),      ("mafic", "felsic"),
                review_status="verified", source_ref="Harker 1909; 标准协变散点图"),
    DiagramSpec(plot_miyashiro,"EVO-02_Miyashiro1974_FeOtMgO_SiO2.png", "Miyashiro FeOt/MgO–SiO₂ 构造判别", ('SiO2', 'MgO'), ('FeO', 'TFe2O3'),                    ("mafic",),
                review_status="verified", source_ref="Miyashiro 1974"),
    DiagramSpec(plot_mgno,     "EVO-03_MgNo_vs_SiO2.png",    "Mg# vs SiO₂ 演化图",                        ('SiO2', 'MgO'),        ('FeO', 'TFe2O3'),          ("mafic", "felsic"),
                review_status="verified", source_ref="通用 Mg#-SiO₂ 演化图"),
    DiagramSpec(plot_zr_covariance, "EVO-04_Zr_covariance.png", "Zr 协变 3×3 图",                        ('Zr', 'Nb', 'Hf', 'Th', 'Y', 'Yb', 'La', 'Sm', 'Ba', 'Sr'),                None,                        ("mafic", "felsic"),
                review_status="experimental", source_ref="3×3 协变矩阵，无文献边界"),

    # ── 🌍 构造环境判别 ──────────────────────────────
    DiagramSpec(plot_meschede,   "TEC-01_Meschede1986_ternary.png",      "Meschede Nb–Zr–Y 构造判别",        ('Nb', 'Zr', 'Y'),  None,                           ("mafic",),
                review_status="experimental", source_ref="Nb-Zr-Y 三角图边界未逐点核对"),
    DiagramSpec(plot_wood,       "TEC-02_Wood1980_Hf3_Th_Ta.png",         "Wood Hf/3–Th–Ta 构造判别",          ('Hf', 'Th', 'Ta'), None,                           ("mafic",),
                review_status="experimental", source_ref="Hf/3-Th-Ta 三角图边界未逐点核对"),
    DiagramSpec(plot_pearce_cann,"TEC-03_PearceCann1973_TiZrY.png",       "Pearce & Cann Ti–Zr–Y 构造判别",    ('Ti', 'Zr', 'Y'),  None,                           ("mafic",),
                review_status="experimental", source_ref="Ti-Zr-Y 三角图边界未逐点核对"),
    DiagramSpec(plot_4panel,     "TEC-04_V_Ti_Sc_ThNb_BaTh_4panel.png",  "四联比值构造判别图",                 ('Ti', 'V', 'Sc', 'Th', 'Nb', 'Ba', 'La', 'Sm', 'Yb'),  None,           ("mafic",),
                review_status="experimental", source_ref="四联图多子图，交叉引用边界复杂"),
    DiagramSpec(plot_shervais,   "TEC-05_Shervais1982_Ti_V.png",         "Shervais Ti-V 构造判别图",           ('Ti', 'V'),        None,                           ("mafic",),
                review_status="verified", source_ref="Shervais 1982"),
    DiagramSpec(plot_co_th,      "CLS-06_Co_Th_Hastie2007.png",          "Co-Th (Hastie) 系列判别图",          ('Co', 'Th'),       None,                           ("mafic",)),
    DiagramSpec(plot_u_th_zr_nb, "SRC-04_UTh_ZrNb_Stern2006.png",        "U/Th-Zr/Nb (Stern) 源区判别",        ('U', 'Th', 'Zr', 'Nb'),  None,                      ("mafic",)),
    DiagramSpec(plot_pearce_1983, "TEC-06_ThYb_TaYb_Pearce1983.png",     "Th/Yb-Ta/Yb (Pearce 1983) 构造判别", ('Th', 'Ta', 'Yb'), None,                             ("mafic",)),
    DiagramSpec(plot_sm_yb_la_sm, "SRC-05_SmYb_LaSm_partial_melting.png","(Sm/Yb)PM-(La/Sm)PM 部分熔融图",    ('Sm', 'Yb', 'La'), None,                            ("mafic",),
                review_status="experimental", source_ref="部分熔融模拟轨迹线"),
    DiagramSpec(plot_saccani_2015,"TEC-07_NbN_ThN_Saccani2015.png",      "NbN-ThN (Saccani) 构造判别",         ('Nb', 'Th'),       None,                           ("mafic",)),
    DiagramSpec(plot_sc_v,     "SRC-06_Sc_V_HickeyVargas2018.png",    "Sc-V (Hickey-Vargas) 氧化条件判别",  ('Sc', 'V'),            None,                           ("mafic",)),
    DiagramSpec(plot_ba_th_la_sm, "SRC-07_BaTh_LaSm_PearceRobinson2010.png", "Ba/Th-La/Sm 流体vs熔体判别",('Ba', 'Th', 'La', 'Sm'), None,                         ("mafic",)),
    DiagramSpec(plot_zr_y_zr,  "TEC-08_ZrY_Zr_Xia2014.png",           "Zr/Y vs Zr 岛弧vs大陆弧判别",        ('Zr', 'Y'),            None,                           ("mafic",)),
    DiagramSpec(plot_gdyb_dydystar, "SRC-08_GdYb_DyDystar_Davidson2013.png",
                "Gd/Yb vs Dy/Dy* 稀土分馏模式 (Davidson 2013)",   ('La', 'Gd', 'Tb', 'Dy', 'Ho', 'Yb'),  None,  ("mafic", "felsic"),
                review_status="experimental", source_ref="特殊比值计算逻辑"),
    DiagramSpec(plot_dyyb_layb,  "SRC-09_DyYb_LaYb_garnet_depth.png",
                "Dy/Yb vs La/Yb 石榴石深度判别",                  ('Dy', 'Yb', 'La'),                 None,  ("mafic", "felsic"),
                review_status="experimental", source_ref="特殊比值计算逻辑"),

    # ── 🧮 分类 / 三角图 + 判别函数（分类+构造混合） ─────────
    DiagramSpec(plot_an_ab_or,   "CLS-07_An_Ab_Or_OConnor1965.png",
                "An-Ab-Or 斜长石三元图 (O'Connor 1965)",          ('Na2O', 'K2O', 'CaO', 'Al2O3', 'SiO2'),               None,  ("felsic",),
                review_status="experimental", source_ref="斜长石三元（非标准地化图件）"),
    DiagramSpec(plot_qapf,       "CLS-08_QAPF_Streckeisen1976.png",
                "Q-A-PF 深成岩分类三元图 (Streckeisen 1976)",     ('SiO2', 'Na2O', 'K2O', 'CaO', 'Al2O3'), None, ("felsic",)),
    DiagramSpec(plot_nb_la_th_la,"TEC-09_NbLa_ThLa_Cabanis1986.png",
                "Nb/La vs Th/La 构造判别 (Cabanis & Lemelle 1986)", ('Nb', 'Th', 'La'),               None,  ("mafic",)),

    # -- RockPlot SVG 三角图 (2026-05-25) ---------------------
    DiagramSpec(plot_cabanis,    "CLS-09_Cabanis1986_LaY_Nb_ternary.png",
                "Cabanis La/10-Y/15-Nb/8 基性岩三角图",             ('La', 'Y', 'Nb'),                None,  ("mafic",),
                review_status="experimental", source_ref="RockPlot SVG 三角图边界未逐点核对"),
    DiagramSpec(plot_mullen,     "CLS-10_Mullen1983_TiO2_MnO_P2O5.png",
                "Mullen TiO2-MnO-P2O5 基性岩三角图",                ('TiO2', 'MnO', 'P2O5'),         None,  ("mafic",),
                review_status="experimental", source_ref="RockPlot SVG 三角图边界未逐点核对"),
    DiagramSpec(plot_jensen,     "CLS-11_Jensen1976_cation_ternary.png",
                "Jensen FeOt+TiO2-Al2O3-MgO 阳离子三角图",          ('MgO', 'Al2O3', 'TiO2'),                 ('FeO', 'TFe2O3'), ("mafic",),
                review_status="experimental", source_ref="RockPlot SVG 三角图边界未逐点核对"),
    DiagramSpec(plot_oconnor_volc,"CLS-12_OConnor_Volc_An_Ab_Or.png",
                "O'Connor An-Ab-Or 火山岩三角图",                   ('Na2O', 'K2O', 'CaO'),          None,  ("felsic",),
                review_status="experimental", source_ref="RockPlot SVG 三角图边界未逐点核对"),
    DiagramSpec(plot_ohta_arai,  "SRC-10_Ohta_Arai2007_MFW.png",
                "Ohta & Arai M-F-W 俯冲带源区三角图",               ('La', 'Sm', 'Nb', 'Ce', 'Zr', 'Y'),   None,  ("mafic",),
                review_status="experimental", source_ref="RockPlot SVG 三角图边界未逐点核对"),
    DiagramSpec(plot_pearce1977, "TEC-10_Pearce1977_FeOt_MgO_Al2O3.png",
                "Pearce FeOt-MgO-Al2O3 基性岩构造三角图",           ('MgO', 'Al2O3'),                 ('FeO', 'TFe2O3'), ("mafic",),
                review_status="experimental", source_ref="RockPlot SVG 三角图边界未逐点核对"),
    DiagramSpec(plot_harris,     "TEC-11_Harris1986_Rb30_Hf_3Ta.png",
                "Harris Rb/30-Hf-3Ta 花岗岩构造判别三角图",         ('Rb', 'Hf', 'Ta'),               None,  ("felsic",),
                review_status="experimental", source_ref="Rb/30-Hf-3Ta 三角图未逐点核对"),
    DiagramSpec(plot_muller_kternary, "TEC-12_Muller2000_Kternary.png",
                "Muller Th-Ta-Hf 三子图等边三元构造判别图",         ('Th', 'Ta', 'Hf'),              None,  ("mafic",),
                review_status="experimental", source_ref="子图逻辑复杂，边界未逐点核对"),

    # -- XY 二元图 (2026-05-26) ---------------------------------
    DiagramSpec(plot_tasmiddlemostplut, "CLS-13_TAS_Middlemost1994_Plutonic.png",
                "TAS 深成岩全碱-硅分类 (Middlemost 1994)",         ('SiO2', 'Na2O', 'K2O'),           None,  ("felsic",),
                review_status="verified", source_ref="Middlemost 1994"),
    DiagramSpec(plot_tasmiddlemostvolc, "CLS-14_TAS_Middlemost1994_Volcanic.png",
                "TAS 火山岩全碱-硅分类 (Middlemost 1994)",         ('SiO2', 'Na2O', 'K2O'),           None,  ("mafic",),
                review_status="verified", source_ref="Middlemost 1994"),
    DiagramSpec(plot_coxplut,    "CLS-15_TAS_Cox1979_Plutonic.png",
                "TAS 深成岩分类 (Cox 1979)",                      ('SiO2', 'Na2O', 'K2O'),           None,  ("felsic",),
                review_status="verified", source_ref="Cox et al. 1979"),
    DiagramSpec(plot_coxvolc,    "CLS-16_TAS_Cox1979_Volcanic.png",
                "TAS 火山岩分类 (Cox 1979)",                      ('SiO2', 'Na2O', 'K2O'),           None,  ("mafic",),
                review_status="verified", source_ref="Cox et al. 1979"),
    DiagramSpec(plot_pearcenorry,"TEC-13_Pearce_Norry1979_ZrY_Zr.png",
                "Pearce & Norry Zr/Y–Zr WPB/MORB/IAB 构造判别",               ('Zr', 'Y'),                       None,  ("mafic",),
                review_status="verified", source_ref="Pearce & Norry 1979"),
    DiagramSpec(plot_pearce1982, "TEC-14_Pearce1982_ZrY_Zr.png",
                "Pearce (1982) Zr/Y–Zr + Ti/Nb/Sr 多元素判别",                  ('Zr', 'Y', 'Ti', 'Nb', 'Sr'),                       None,  ("mafic",),
                review_status="verified", source_ref="Pearce 1982"),
    DiagramSpec(plot_pearcegranite, "TEC-15_Pearce1984_Granite_Rb_YNb.png",
                "Pearce Rb–Y+Nb 花岗岩构造判别",                  ('Rb', 'Y', 'Nb'),                 None,  ("felsic",)),
    DiagramSpec(plot_pearcenbthyb, "SRC-11_Pearce1995_NbYb_ThYb.png",
                "Pearce Nb/Yb–Th/Yb 源区判别",                   ('Nb', 'Th', 'Yb'),                None,  ("mafic",),
                review_status="verified", source_ref="Pearce 1995"),
    DiagramSpec(plot_pearcenbtiyb, "SRC-12_Pearce1995_TiYb_NbYb.png",
                "Pearce Ti/Yb–Nb/Yb 源区判别",                   ('Ti', 'Nb', 'Yb'),                None,  ("mafic",),
                review_status="verified", source_ref="Pearce 1995"),
    DiagramSpec(plot_frost,      "CLS-17_Frost2001_Fenum_SiO2.png",
                "Frost Fe-number vs SiO₂ 铁质-镁质分类",          ('SiO2', 'MgO'),                   ('FeO', 'TFe2O3'), ("felsic",),
                review_status="verified", source_ref="Frost et al. 2001"),
    DiagramSpec(plot_whalen1,    "CLS-18_Whalen1987_GaAl_Zr.png",
                "Whalen 10000×Ga/Al–Zr A型花岗岩判别",           ('Ga', 'Al2O3', 'Zr'),             None,  ("felsic",)),
    DiagramSpec(plot_whalen2,    "CLS-19_Whalen1987_GaAl_Nb.png",
                "Whalen 10000×Ga/Al–Nb A型花岗岩判别",           ('Ga', 'Al2O3', 'Nb'),             None,  ("felsic",)),
    DiagramSpec(plot_whalen3,    "CLS-20_Whalen1987_GaAl_CeYZr.png",
                "Whalen 10000×Ga/Al–Ce+Y+Zr A型花岗岩判别",      ('Ga', 'Al2O3', 'Ce', 'Y', 'Zr'),  None,  ("felsic",)),
    DiagramSpec(plot_sylvester,  "SRC-13_Sylvester1989_CaONa2O_Al2O3.png",
                "Sylvester CaO/Na₂O–Al₂O₃ 花岗岩源区判别",       ('CaO', 'Na2O', 'Al2O3'),           None,  ("felsic",)),
    DiagramSpec(plot_villaseca,  "CLS-21_Villaseca1998_ASI_FMM.png",
                "Villaseca ASI–FMM 花岗岩源区分类",              ('Al2O3', 'CaO', 'Na2O', 'K2O', 'MgO', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("felsic",),
                review_status="experimental", source_ref="ASI-FMM 较新分类未核实"),
    DiagramSpec(plot_debonba,    "CLS-22_Debon1983_BA_diagram.png",
                "Debon B-A 花岗岩矿物分类图",                    ('Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("felsic",),
                review_status="experimental", source_ref="矿物参数计算逻辑未核实"),
    DiagramSpec(plot_debonpq,    "CLS-23_Debon1983_PQ_diagram.png",
                "Debon P-Q 花岗岩矿物分类图",                    ('SiO2', 'Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("felsic",),
                review_status="experimental", source_ref="矿物参数计算逻辑未核实"),
    DiagramSpec(plot_schandl,    "TEC-16_Schandl2004_Y_Zr.png",
                "Schandl Y–Zr 花岗岩构造判别图",                 ('Y', 'Zr'),                        None,  ("felsic",),
                review_status="verified", source_ref="Schandl et al. 2004"),
    DiagramSpec(plot_batchelor,  "TEC-17_Batchelor1985_R1_R2.png",
                "Batchelor & Bowden R1-R2 花岗岩构造判别",       ('SiO2', 'Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("felsic",),
                review_status="experimental", source_ref="R1-R2 计算公式需核实"),
    DiagramSpec(plot_mullerkbinary, "CLS-24_Muller1992_K2O_SiO2.png",
                "Muller K₂O–SiO₂ 岩浆系列判别",                 ('SiO2', 'K2O'),                    None,  ("mafic",)),
    DiagramSpec(plot_hollocher1, "EVO-05_Hollocher2012_VSc.png",
                "Hollocher V/Sc–V+Sc 弧岩浆氧化条件判别",        ('V', 'Sc'),                        None,  ("mafic",)),
    DiagramSpec(plot_hollocher2, "EVO-06_Hollocher2012_VSc_ZrCe.png",
                "Hollocher Zr/Ce–V/Sc 弧岩浆分类",              ('V', 'Sc', 'Zr', 'Ce'),            None,  ("mafic",)),
    DiagramSpec(plot_hastie,     "CLS-25_Hastie2007_Th_Co.png",
                "Hastie Th–Co 弧岩浆系列分类",                   ('Th', 'Co'),                       None,  ("mafic",)),
    DiagramSpec(plot_maniar,     "TEC-18_Maniar1989_Granite_disc.png",
                "Maniar & Piccoli 花岗岩构造判别",               ('SiO2', 'Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("felsic",),
                review_status="experimental", source_ref="花岗岩判别逻辑较新"),
    DiagramSpec(plot_agrawal,    "TEC-19_Agrawal2004_DF1_DF2.png",
                "Agrawal DF1-DF2 基性岩构造判别",               ('TiO2', 'Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'MnO', 'P2O5', 'SiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("mafic",),
                review_status="experimental", source_ref="判别函数公式未核对原文献"),
    DiagramSpec(plot_verma,      "TEC-20_Verma_discriminant_DF1_DF2.png",
                "Verma 判别函数 基性岩构造判别",                 ('TiO2', 'Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'MnO', 'P2O5', 'SiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("mafic",),
                review_status="experimental", source_ref="判别函数公式未核对原文献"),
    DiagramSpec(plot_larocheplut,"CLS-26_LaRoche1980_R1_R2_plutonic.png",
                "La Roche R1-R2 侵入岩分类图",                  ('SiO2', 'Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("felsic",),
                review_status="experimental", source_ref="R1-R2 分类计算公式需核实"),
    DiagramSpec(plot_larochevolc,"CLS-27_LaRoche1980_R1_R2_volcanic.png",
                "La Roche R1-R2 火山岩分类图",                  ('SiO2', 'Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2'),
                                                                  ('FeO', 'TFe2O3'),                       ("mafic",),
                review_status="experimental", source_ref="R1-R2 分类计算公式需核实"),
    DiagramSpec(plot_middlemostplut, "CLS-28_Middlemost1991_Plutonic.png",
                "Middlemost Na₂O+K₂O–SiO₂ 深成岩分类",           ('SiO2', 'Na2O', 'K2O'),            None,  ("felsic",),
                review_status="verified", source_ref="Middlemost 1991"),
    DiagramSpec(plot_pecetaylor,  "CLS-29_Peccerillo_Taylor1976_K2O_SiO2.png",
                "Peccerillo & Taylor K₂O–SiO₂ 岩浆系列判别",     ('SiO2', 'K2O'),                    None,  ("mafic",),
                review_status="verified", source_ref="Peccerillo & Taylor 1976"),
    DiagramSpec(plot_layb,       "SRC-14_LaYb_vs_Yb.png",
                "La/Yb vs Yb 源区部分熔融判别",                 ('La', 'Yb'),                        None,  ("mafic", "felsic")),
    DiagramSpec(plot_ross,       "SRC-15_Ross2009_LaSm_LaYb.png",
                "Ross & Bédard La/Sm–La/Yb 岩浆过程判别",        ('La', 'Sm', 'Yb'),                  None,  ("mafic", "felsic")),
]

# =====================================================================
# 派生列表（保持向后兼容）
# =====================================================================

def _is_mafic(d: DiagramSpec) -> bool:
    return "mafic" in d.rock_types

def _is_felsic(d: DiagramSpec) -> bool:
    return "felsic" in d.rock_types

# MAFIC_DIAGRAMS / FELSIC_DIAGRAMS — 四元组 (fn, desc, needed, any_of)，兼容旧代码
MAFIC_DIAGRAMS = [(d.fn, d.desc, d.needed, d.any_of) for d in DIAGRAM_REGISTRY if _is_mafic(d)]
FELSIC_DIAGRAMS = [(d.fn, d.desc, d.needed, d.any_of) for d in DIAGRAM_REGISTRY if _is_felsic(d)]

# 文件名映射：fn.__name__ → 输出文件名
FILENAME_MAP = {d.fn.__name__: d.filename for d in DIAGRAM_REGISTRY}
