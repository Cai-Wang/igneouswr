import numpy as np
import matplotlib.pyplot as plt
import igneous_wr.report.style as _style
from igneous_wr.core.ternary import SQRT3_2, ternary_to_xy, ternary_corners, draw_ternary_frame, draw_ternary_grid, draw_ternary_ticks, label_ternary_vertices
from igneous_wr.boundaries.core import load_boundary

def plot_meschede(gd, out_dir=None, save=True):
    """
    Meschede (1986) Nb×2–Zr/4–Y 三角图 🔥火山岩
    所需元素: Nb, Zr, Y
    """
    missing = gd.check_elements('Nb', 'Zr', 'Y', strict=True)
    if missing:
        return (None, None)
    nb_arr = gd.get('Nb')
    zr_arr = gd.get('Zr')
    yi_arr = gd.get('Y')
    labels = gd.labels
    PTS_M = {'a': (0, 50, 50), 'b': (3, 53, 44), 'c': (12, 60, 28), 'd': (34, 52.5, 13.5), 'e': (79, 14, 7), 'f': (56.5, 16.5, 27), 'g': (50, 17, 33), 'h': (22, 21, 57), 'i': (0, 23, 77), 'k': (24, 33.5, 42.5), 'l': (22, 37, 41), 'm': (31, 36, 33), 'n': (35, 37.5, 27.5), 'o': (50, 33, 17)}
    cart_m = {k: ternary_to_xy(*v) for k, v in PTS_M.items()}
    FIELDS_M = {'A1': {'keys': ['d', 'e', 'f', 'o', 'c'], 'fill': '#FFE0B2', 'edge': '#E65100', 'label': 'A1', 'sub': 'WPA'}, 'A2': {'keys': ['c', 'o', 'f', 'g', 'n'], 'fill': '#FDF6E3', 'edge': '#E65100', 'label': 'A2', 'sub': 'WPA/WPT'}, 'B': {'keys': ['n', 'g', 'h', 'k', 'l', 'm'], 'fill': '#BBDEFB', 'edge': '#1565C0', 'label': 'B', 'sub': 'P-MORB'}, 'C': {'keys': ['b', 'c', 'n', 'm', 'l'], 'fill': '#C8E6C9', 'edge': '#2E7D32', 'label': 'C', 'sub': 'WPT/VAB'}, 'D': {'keys': ['a', 'i', 'h', 'k', 'l', 'b'], 'fill': '#E1BEE7', 'edge': '#6A1B9A', 'label': 'D', 'sub': 'N-MORB'}}
    x_d, y_d = ternary_to_xy(2.0 * nb_arr, zr_arr / 4.0, yi_arr)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    label_ternary_vertices(ax, '2Nb', 'Zr/4', 'Y', corners=corners)
    for fd in FIELDS_M.values():
        keys = fd['keys'] + [fd['keys'][0]]
        ax.plot([cart_m[k][0] for k in keys], [cart_m[k][1] for k in keys], color=_style.LINE_COLOR_MAIN, lw=1.5, zorder=1)
    # GCDkit 精确标签坐标(归一化三角图坐标系)
    MESCHEDE_LABELS = {
        'A1': (0.46, 0.543),      # text4 — WPA
        'A2': (0.456, 0.387),     # text5 — WPA/WPT
        'B':  (0.566, 0.302),     # text6 — P-MORB
        'C':  (0.431, 0.163),     # text7 — WPT/VAB
        'D':  (0.605, 0.092),     # text8 — N-MORB
    }
    for name, fd in FIELDS_M.items():
        lx, ly = MESCHEDE_LABELS.get(name, (0, 0))
        ax.text(lx, ly, fd['sub'], fontsize=11, fontweight='bold',
                ha='center', va='center', color=_style.TEXT_COLOR_LABEL, zorder=5)
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.08, 1.1)
    ax.set_ylim(-0.08, SQRT3_2 + 0.08)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Meschede1986_ternary.png', out_dir)
    return (fig, ax)

def plot_wood(gd, out_dir=None, save=True):
    """
    Wood (1980) Hf/3–Th–Ta 三角图 🔥火山岩
    所需元素: Hf, Th, Ta
    """
    missing = gd.check_elements('Hf', 'Th', 'Ta', strict=True)
    if missing:
        return (None, None)
    hf_arr = gd.get('Hf')
    th_arr = gd.get('Th')
    ta_arr = gd.get('Ta')
    labels = gd.labels
    PTS_W = {'a': (87.5, 3.0, 9.5), 'b': (85, 15.0, 0.0), 'c': (77, 15.0, 8.0), 'd': (69, 20.0, 11.0), 'e': (65.0, 7.0, 28.0), 'f': (55.0, 5.0, 40.0), 'g': (45.5, 35.0, 19.5), 'h': (42.5, 13.5, 44.0), 'l': (24.5, 56.5, 19.0), 'n': (20, 56.0, 24.0), 'o': (20.0, 32.0, 48.0), 'p': (12.0, 40.0, 48.0), 'q': (8, 62.0, 29.0), 'r': (0, 95.0, 5.0), 't': (50, 50.0, 0.0), 'w': (0.0, 100, 0), 's': (42.1, 42.1, 15.8), 'k': (33.0, 27.0, 40.0), 'm': (24.5, 55.5, 20.0)}
    cart_w = {k: ternary_to_xy(*v) for k, v in PTS_W.items()}
    FIELDS_W = {'A': {'keys': ['a', 'c', 'd', 'g', 'e'], 'fill': '#E1F5FE', 'edge': '#0277BD', 'label': 'A', 'sub': 'N-MORB'}, 'B': {'keys': ['g', 'm', 'n', 'k', 'h', 'f', 'e'], 'fill': '#FFF8E1', 'edge': '#F9A825', 'label': 'B', 'sub': 'E-MORB/WPT'}, 'C': {'keys': ['n', 'q', 'p', 'o', 'k'], 'fill': '#E8F5E9', 'edge': '#388E3C', 'label': 'C', 'sub': 'WPA'}, 'D': {'keys': ['r', 'l', 's', 't', 'w'], 'fill': '#FCE4EC', 'edge': '#C62828', 'label': 'D', 'sub': 'CAB'}, 'E': {'keys': ['b', 't', 's', 'd', 'c'], 'fill': '#F3E5F5', 'edge': '#7B1FA2', 'label': 'E', 'sub': 'IAT'}}
    x_d, y_d = ternary_to_xy(hf_arr / 3.0, th_arr, ta_arr)
    fig, ax = plt.subplots(figsize=(11, 10))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    label_ternary_vertices(ax, 'Hf/3', 'Th', 'Ta', corners=corners)
    for name in ['C', 'A', 'B', 'D', 'E']:
        fd = FIELDS_W[name]
        keys = fd['keys'] + [fd['keys'][0]]
        ax.plot([cart_w[k][0] for k in keys], [cart_w[k][1] for k in keys], color=_style.LINE_COLOR_MAIN, lw=1.5, zorder=2)
    # GCDkit 精确标签坐标（归一化三角图坐标系）
    WOOD_LABELS = {
        'A': (0.525, 0.615),   # N-MORB  — text5
        'B': (0.52, 0.35),     # E-MORB/WPT — text7
        'C': (0.45, 0.15),     # WPA    — text4
        'D': (0.2, 0.22),      # CAB    — text8
        'E': (0.35, 0.5),      # IAT    — text6
    }
    for name, fd in FIELDS_W.items():
        lx, ly = WOOD_LABELS.get(name, (0, 0))
        ax.text(lx, ly, fd['sub'], fontsize=11, fontweight='bold',
                ha='center', va='center', color=_style.TEXT_COLOR_LABEL, zorder=5)
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.08, 1.1)
    ax.set_ylim(-0.08, SQRT3_2 + 0.08)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Wood1980_Hf3_Th_Ta.png', out_dir)
    return (fig, ax)

def plot_shervais(gd, out_dir=None, save=True):
    """Ti vs V 构造判别图（Shervais, 1982）🔥基性岩
    底图数据来自 boundaries/tec/shervais.json
    分区: ARC (Ti/V < 20), OFB (Ti/V 20~50), WPB/OIB (Ti/V > 50)
    所需元素: Ti, V
    """
    missing = gd.check_elements('Ti', 'V', strict=True)
    if missing:
        return (None, None)
    ti_arr = gd.get('Ti')
    v_arr = gd.get('V')
    if np.all(np.isnan(ti_arr)):
        print('[Shervais] ❌ Ti 数据全为 NaN，无法出图')
        return (None, None)
    labels = gd.labels
    ti_1000 = ti_arr / 1000.0
    fig, ax = plt.subplots(figsize=(9, 7))
    bd = load_boundary('tec', 'shervais')
    ax.set_xlim(bd['axes']['xlim'])
    ax.set_ylim(bd['axes']['ylim'])
    _xt = np.array([0.0, bd['axes']['xlim'][1]])
    for ray in bd.get('rays', []):
        ax.plot(_xt, ray['slope'] * _xt, ray['ls'], color=ray['color'], lw=ray['lw'], zorder=3)
    for rl in bd.get('ray_labels', []):
        ax.text(rl['x'], rl['y'], rl['text'], fontsize=rl.get('fontsize', 7.5), ha=rl.get('ha', 'center'), va=rl.get('va', 'center'), color=rl['color'], fontstyle=rl.get('fontstyle', 'italic'))
    for rgl in bd.get('region_labels', []):
        ax.text(rgl['x'], rgl['y'], rgl['text'], fontsize=rgl.get('fontsize', 11), ha=rgl.get('ha', 'center'), va=rgl.get('va', 'center'), fontweight=rgl.get('fontweight', 'bold'), color=rgl['color'], zorder=5)
    _style.scatter_samples(ax, ti_1000, v_arr, labels, groups=gd.groups)
    _style.add_legend(ax)
    _style.style_ax(ax, bd['axes']['xlabel'], bd['axes']['ylabel'])
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Shervais1982_Ti_V.png', out_dir)
    return (fig, ax)
