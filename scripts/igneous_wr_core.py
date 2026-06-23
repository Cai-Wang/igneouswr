"""
igneous_wr_core.py — IgneousWR 绘图引擎门面（兼容入口）

此文件为 re-export 入口。实际功能在 igneous_wr/ 包中：
  - igneous_wr.io.excel        — Excel 读取、检测限解析
  - igneous_wr.core.data       — GeochemData 数据容器
  - igneous_wr.batch.recommend — recommended_diagrams / plot_recommended
  - igneous_wr.diagrams.registry — 注册表 + 绘图函数

用户仍可 from igneous_wr_core import * 正常使用。
"""

# ── re-export 子模块 ──────────────────────────────────────────
from igneous_wr.core.chem import feot_calc
from igneous_wr.core.ternary import (SQRT3_2, ternary_to_xy, ternary_corners,
                       draw_ternary_frame, draw_ternary_grid,
                       draw_ternary_ticks, label_ternary_vertices)
from igneous_wr.report.style import (times_prop, get_color, set_palette, set_style_preset, set_style,
                     scatter_samples, plot_samples_ternary, scatter_groups,
                     style_ax, save_fig, add_legend, set_out_dir,
                     generate_report_html,
                     MK_SIZE_SINGLE, MK_SIZE_TERNARY, MK_EDGE_COLOR,
                     MK_EDGE_WIDTH, MK_EDGE_WIDTH_T, ANNOTATE_OFFSET,
                     ANNOTATE_FONTSIZE, LEGEND_LOC,
                     TICK_LENGTH, TICK_LENGTH_M, TICK_WIDTH, SPINE_WIDTH, GRID_LW,
                     STYLE_PRESETS, COLOR_PALETTES, get_group_colors,
                     set_font_scale,
                     DEFAULT_OUT_DIR)

# ── 从新结构 re-export ────────────────────────────────────────
from igneous_wr.io.excel import (
    ELEM_ALIAS, KNOWN_ELEMENTS,
    DL_STRATEGY_HALF, DL_STRATEGY_ZERO, DL_STRATEGY_NAN,
    parse_value, find_excel,
)
from igneous_wr.core.data import GeochemData

from igneous_wr.core.normalize import (CHONDRITE, REE_ORDER,
                         PRIMITIVE_MANTLE, SPIDER_ORDER,
                         normalize)

from igneous_wr.diagrams.registry import (
    DiagramSpec,
    DIAGRAM_REGISTRY,
    MAFIC_DIAGRAMS,
    FELSIC_DIAGRAMS,
    # 所有绘图函数
    plot_tas, plot_k2o_sio2, plot_afm, plot_winchester_floyd,
    plot_mullen, plot_co_th,
    plot_tasmiddlemostplut,
    plot_frost_fenr, plot_frost_mali, plot_frost_asi_ank, plot_pearce1996,
    plot_k2o_sio2_peccerillo,
    plot_shand_acnk_ank,
    plot_whalen_ga_al,
    plot_ree, plot_spider, plot_pearce_2008,
    plot_miyashiro, plot_mgo_sio2, plot_p2o5_sio2,
    plot_meschede, plot_wood, plot_shervais,
)

# ── 后置轴样式函数（时序敏感：figkit finalize 之后调用） ──
from igneous_wr.diagrams._source import (
    apply_spider_axis_style, apply_ree_axis_style, auto_xlim_padding,
)

from igneous_wr.batch.recommend import (
    recommended_diagrams,
    plot_recommended,
)
