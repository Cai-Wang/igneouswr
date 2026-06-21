"""registry.py — 图件注册表

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

# ── import 所有绘图函数（从新包 igneous_wr.diagrams 导入） ──
from igneous_wr.diagrams._classification import (
    plot_tas, plot_k2o_sio2, plot_afm, plot_winchester_floyd,
    plot_mullen, plot_co_th,
    plot_tasmiddlemostplut,
    plot_frost_fenr, plot_frost_mali, plot_frost_asi_ank,
    plot_pearce1996, plot_k2o_sio2_peccerillo,
    plot_shand_acnk_ank,
    plot_whalen_ga_al,
)
from igneous_wr.diagrams._source import (
    plot_ree, plot_spider, plot_pearce_2008,
)
from igneous_wr.diagrams._evolution import (
    plot_miyashiro,
)
from igneous_wr.diagrams._tectonic import (
    plot_meschede, plot_wood, plot_shervais,
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
# DIAGRAM_REGISTRY — 19 张精选图件注册表
# ════════════════════════════════════════════════════════════════
DIAGRAM_REGISTRY = [
    # ── 📋 岩石系列 / 分类 ─────────────────────────────
    DiagramSpec(plot_tas,      "CLS-01_TAS_Middlemost1994_Volcanic.png",            "TAS 全碱-硅分类图（火山岩，Middlemost 1994）", ('SiO2', 'Na2O', 'K2O'), None,                        ("mafic",),
                review_status="verified", source_ref="middlemost1994",
                review_note="16 个分类区多边形，源自 GCDkit TASMiddlemostVolc.r；纯文本区：Sodalitite/Nephelinolith/Leucitolith, Silexite"
                ),
    DiagramSpec(plot_k2o_sio2, "CLS-02_Middlemost1985_K2O_SiO2.png",  "K₂O–SiO₂ 钾系列分类图 (Middlemost 1985)",    ('SiO2', 'K2O'),        None,                        ("mafic", "felsic"),
                review_status="verified", source_ref="middlemost1985",
                review_note="已校正: 端点坐标法, 四色填充+去网格"
                ),
    DiagramSpec(plot_k2o_sio2_peccerillo, "CLS-04_PeccerilloTaylor1976_K2O_SiO2.png",
                "K₂O–SiO₂ 钾系列分类图 (Peccerillo & Taylor 1976)",
                ('SiO2', 'K2O'), None, ("mafic", "felsic"),
                review_status="needs_review", source_ref="peccerillo_taylor1976",
                review_note="全新图, 多段折线分界线, 源自 GCDkit PeceTaylor.r extrapolated=TRUE"
                ),
    DiagramSpec(plot_afm,      "CLS-03_AFM_IB1971.png",      "AFM 钙碱性-拉斑系列判别",                    ('Na2O', 'K2O', 'MgO'), ('FeO', 'TFe2O3'),           ("mafic",),
                review_status="verified", source_ref="irvine_baragar1971"
                ),
    DiagramSpec(plot_winchester_floyd, "CLS-05_Winchester_Floyd1977_NbY_ZrTiO2.png",
                "Winchester & Floyd Zr/TiO2–Nb/Y 分类图", ('Zr', 'TiO2', 'Nb', 'Y'), None,      ("mafic", "felsic"),
                review_status="verified", source_ref="winchester_floyd1977"
                ),
    DiagramSpec(plot_pearce1996, "CLS-29_Pearce1996_NbY_ZrTi.png",
                "Pearce (1996) Zr/Ti–Nb/Y 火山岩分类图", ('Zr', 'Ti', 'Nb', 'Y'), None, ("mafic", "felsic"),
                review_status="verified", source_ref="pearce1996",
                review_note="GCDkit 精确坐标, 对数值直填 plot, log-log 双轴, 10 区域彩色填充"
                ),
    DiagramSpec(plot_co_th,      "CLS-06_Co_Th_Hastie2007.png",          "Co-Th (Hastie) 系列+岩性判别图",          ('Co', 'Th'),       None,                           ("mafic",),
                review_status="verified", source_ref="hastie2007",
                review_note="已校正: X=Co,Y=Th, 四直线分界线, 背景色填充, 系列+岩性双标注"
                ),
    DiagramSpec(plot_mullen,     "CLS-10_Mullen1983_TiO2_MnO_P2O5.png",
                "Mullen TiO2-MnO-P2O5 基性岩三角图",                ('TiO2', 'MnO', 'P2O5'),         None,  ("mafic",),
                review_status="experimental", source_ref=""
                ),
    DiagramSpec(plot_tasmiddlemostplut, "CLS-13_TAS_Middlemost1994_Plutonic.png",
                "TAS 全碱-硅分类图（深成岩，Middlemost 1994）",         ('SiO2', 'Na2O', 'K2O'),           None,  ("felsic",),
                review_status="verified", source_ref="middlemost1994"
                ),

    DiagramSpec(plot_frost_fenr,      "CLS-17_Frost2001_Fenum_SiO2.png",
                "Frost Fe# vs SiO₂ 铁质-镁质分类",          ('SiO2', 'MgO'),                   ('FeO', 'TFe2O3'), ("felsic",),
                review_status="verified", source_ref="frost2001", review_note="已校正: GCDkit坐标 y=0.486+0.0046x, 无色填充"
                ),
    DiagramSpec(plot_frost_mali,      "CLS-30_Frost2001_MALI_SiO2.png",
                "Frost MALI vs SiO₂ 碱-钙分类",          ('SiO2', 'Na2O', 'K2O', 'CaO'),        None, ("felsic",),
                review_status="verified", source_ref="frost2001"
                ),
    DiagramSpec(plot_frost_asi_ank,   "CLS-31_Frost2001_ASI_ANK.png",
                "Frost ASI vs A/NK 铝饱和分类",               ('Al2O3', 'CaO', 'Na2O', 'K2O'),  ('P2O5',), ("felsic",),
                review_status="verified", source_ref="frost2001"
                ),
    DiagramSpec(plot_shand_acnk_ank, "CLS-32_Shand_ACNK_ANK.png",
                "Shand A/CNK vs A/NK 铝饱和分类", ('Al2O3', 'CaO', 'Na2O', 'K2O'), None, ("felsic",),
                review_status="verified", source_ref="shand1943",
                review_note="源自 GCDkit Shand.r: A/CNK vs A/NK, h=1/v=1/diagonal 三条分界线"
                ),
    DiagramSpec(plot_whalen_ga_al, "CLS-33_Whalen_GaAl_NK.png",
                "Whalen 10000*Ga/Al vs Na2O+K2O A型花岗岩判别", ('Ga', 'Al2O3', 'Na2O', 'K2O'), None, ("felsic",),
                review_status="verified", source_ref="whalen1987",
                review_note="源自 GCDkit Whalen.r Fig.1A: log-log, L形分界线 10000Ga/Al=2.6"
                ),

    # ── 🔬 源区性质 ──────────────────────────────────
    DiagramSpec(plot_ree,      "SRC-01_SunMcDonough1989_REE.png",   "REE 球粒陨石标准化配分图",
                ('La','Ce','Pr','Nd','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu'), None,    ("mafic", "felsic"),
                review_status="verified", source_ref="sun_mcdonough1989"
                ),
    DiagramSpec(plot_spider,   "SRC-02_SunMcDonough1989_Spider.png",       "原始地幔标准化蛛网图",
                ('Rb','Ba','Th','U','Nb','Ta','La','Ce','Pb','Pr','Nd','Sr','Sm','Zr','Hf','Eu','Ti','Gd','Tb','Dy','Ho','Y','Er','Tm','Yb','Lu'), None, ("mafic", "felsic"),
                review_status="verified", source_ref="sun_mcdonough1989"
                ),
    DiagramSpec(plot_pearce_2008, "SRC-03_Pearce2008_ThYb_NbYb.png",
                "Pearce Th/Yb-Nb/Yb 源区判别图",                  ('Th', 'Nb', 'Yb'),                None,  ("mafic",),
                review_status="verified", source_ref="pearce2008",
                review_note="2026-06-25 用户校准"
                ),

    # ── 🗺️ 演化 / 协变
    DiagramSpec(plot_miyashiro, "EVO-02_Miyashiro1974_FeOtMgO_SiO2.png", "Miyashiro FeOt/MgO–SiO₂ 构造判别", ('SiO2', 'MgO'), ('FeO', 'TFe2O3'),                    ("mafic",),
                review_status="verified", source_ref="miyashiro1974"
                ),

    # ── 🌍 构造环境判别 ──────────────────────────────
    DiagramSpec(plot_meschede,   "TEC-01_Meschede1986_ternary.png",      "Meschede Nb–Zr–Y 构造判别",        ('Nb', 'Zr', 'Y'),  None,                           ("mafic",),
                review_status="experimental", source_ref=""
                ),
    DiagramSpec(plot_wood,       "TEC-02_Wood1980_Hf3_Th_Ta.png",         "Wood Hf/3–Th–Ta 构造判别",          ('Hf', 'Th', 'Ta'), None,                           ("mafic",),
                review_status="experimental", source_ref=""
                ),
    DiagramSpec(plot_shervais,   "TEC-05_Shervais1982_Ti_V.png",         "Shervais Ti-V 构造判别图",           ('Ti', 'V'),        None,                           ("mafic",),
                review_status="verified", source_ref="shervais1982"
                ),
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
