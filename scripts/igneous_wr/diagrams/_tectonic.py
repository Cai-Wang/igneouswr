import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

import igneous_wr.report.style as _style
from igneous_wr.core.chem import feot_calc
from igneous_wr.core.ternary import (
    SQRT3_2, ternary_to_xy, ternary_corners,
    draw_ternary_frame, draw_ternary_grid,
    draw_ternary_ticks, label_ternary_vertices,
)
from igneous_wr.boundaries.core import load_boundary

"""
_tectonic.py — 构造判别图：Meschede, Wood, Pearce-Cann, 四联, Shervais Ti-V
"""

# ────────────────────────────────────────────────────────────
# 🌍 构造环境判别
# ────────────────────────────────────────────────────────────

def plot_meschede(gd, out_dir=None, save=True):
    """
    Meschede (1986) Nb×2–Zr/4–Y 三角图 🔥火山岩
    所需元素: Nb, Zr, Y
    """
    missing = gd.check_elements('Nb', 'Zr', 'Y', strict=True)
    if missing:
        return None, None
    nb_arr = gd.get('Nb'); zr_arr = gd.get('Zr'); yi_arr = gd.get('Y')
    labels = gd.labels

    PTS_M = {
        'a':(0,50,50),'b':(3,53,44),'c':(12,60,28),'d':(34,52.5,13.5),
        'e':(79,14,7),'f':(56.5,16.5,27),'g':(50,17,33),'h':(22,21,57),
        'i':(0,23,77),'k':(24,33.5,42.5),'l':(22,37,41),'m':(31,36,33),
        'n':(35,37.5,27.5),'o':(50,33,17),
    }
    cart_m = {k: ternary_to_xy(*v) for k, v in PTS_M.items()}

    FIELDS_M = {
        'A1':{'keys':['d','e','f','o','c'],'fill':'#FFE0B2','edge':'#E65100','label':'A1','sub':'WPA'},
        'A2':{'keys':['c','o','f','g','n'],'fill':'#FDF6E3','edge':'#E65100','label':'A2','sub':'WPA/WPT'},
        'B': {'keys':['n','g','h','k','l'],'fill':'#BBDEFB','edge':'#1565C0','label':'B', 'sub':'P-MORB'},
        'C': {'keys':['b','c','n','m','l'],'fill':'#C8E6C9','edge':'#2E7D32','label':'C', 'sub':'WPT/VAB'},
        'D': {'keys':['a','i','h','k','l','b'],'fill':'#E1BEE7','edge':'#6A1B9A','label':'D', 'sub':'N-MORB'},
    }

    x_d, y_d = ternary_to_xy(2.0*nb_arr, zr_arr/4.0, yi_arr)

    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    label_ternary_vertices(ax, '2Nb', 'Zr/4', 'Y', corners=corners)

    for fd in FIELDS_M.values():
        keys = fd['keys'] + [fd['keys'][0]]
        ax.fill([cart_m[k][0] for k in keys], [cart_m[k][1] for k in keys],
                color=fd['fill'], edgecolor=fd['edge'], lw=1.5, zorder=1)

    for name, fd in FIELDS_M.items():
        cx = np.mean([cart_m[k][0] for k in fd['keys']])
        cy = np.mean([cart_m[k][1] for k in fd['keys']])
        ax.text(cx, cy+0.02, fd['label'], fontsize=20, fontweight='bold',
                ha='center', va='center', color=fd['edge'], alpha=0.8, zorder=5)
        ax.text(cx, cy-0.03, fd['sub'], fontsize=9,
                ha='center', va='center', color=fd['edge'], alpha=0.7, zorder=5)

    _style.plot_samples_ternary(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.1, 1.1); ax.set_ylim(-0.1, SQRT3_2+0.1)
    ax.set_aspect('equal'); ax.axis('off')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Meschede1986_ternary.png', out_dir)
    return fig, ax


def plot_wood(gd, out_dir=None, save=True):
    """
    Wood (1980) Hf/3–Th–Ta 三角图 🔥火山岩
    所需元素: Hf, Th, Ta
    """
    missing = gd.check_elements('Hf', 'Th', 'Ta', strict=True)
    if missing:
        return None, None
    hf_arr = gd.get('Hf'); th_arr = gd.get('Th'); ta_arr = gd.get('Ta')
    labels = gd.labels

    PTS_W = {
        'a':(87.5,3.0,9.5),'b':(85,15.0,0.0),'c':(77,15.0,8.0),'d':(69,20.0,11.0),
        'e':(65.0,7.0,28.0),'f':(55.0,5.0,40.0),'g':(45.5,35.0,19.5),'h':(42.5,13.5,44.0),
        'l':(24.5,56.5,19.0),'n':(20,56.0,24.0),'o':(20.0,32.0,48.0),'p':(12.0,40.0,48.0),
        'q':(8,62.0,29.0),'r':(0,95.0,5.0),'t':(50,50.0,0.0),'w':(0.0,100,0),
        's':(42.1,42.1,15.8),'k':(33.0,27.0,40.0),'m':(24.5,55.5,20.0),
    }
    cart_w = {k: ternary_to_xy(*v) for k, v in PTS_W.items()}

    FIELDS_W = {
        'A':{'keys':['a','c','d','g','e'],'fill':'#E1F5FE','edge':'#0277BD','label':'A','sub':'N-MORB'},
        'B':{'keys':['g','m','n','k','h','f','e'],'fill':'#FFF8E1','edge':'#F9A825','label':'B','sub':'E-MORB/WPT'},
        'C':{'keys':['n','q','p','o','k'],'fill':'#E8F5E9','edge':'#388E3C','label':'C','sub':'WPA'},
        'D':{'keys':['r','l','s','t','w'],'fill':'#FCE4EC','edge':'#C62828','label':'D','sub':'CAB'},
        'E':{'keys':['b','t','s','d','c'],'fill':'#F3E5F5','edge':'#7B1FA2','label':'E','sub':'IAT'},
    }

    def make_ratio_line_hf_th(ratio_val, n=100):
        pts = []
        for t in np.linspace(0.1, 99.9, n):
            th = t; hf3 = ratio_val * th / 3.0; ta = 100 - hf3 - th
            if ta > 0.1 and hf3 > 0.1: pts.append((hf3, th, ta))
        return pts

    def make_ratio_line_hf_ta(ratio_val, n=200):
        pts = []
        for t in np.linspace(0.5, 99.5, n):
            ta = t; hf3 = ratio_val * ta / 3.0; th = 100 - hf3 - ta
            if th > 0.1 and hf3 > 0.1: pts.append((hf3, th, ta))
        return pts

    x_d, y_d = ternary_to_xy(hf_arr/3.0, th_arr, ta_arr)

    fig, ax = plt.subplots(figsize=(11, 10))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    label_ternary_vertices(ax, 'Hf/3', 'Th', 'Ta', corners=corners)

    for name in ['C','A','B','D','E']:
        fd = FIELDS_W[name]
        keys = fd['keys'] + [fd['keys'][0]]
        ax.fill([cart_w[k][0] for k in keys], [cart_w[k][1] for k in keys],
                color=fd['fill'], edgecolor=fd['edge'], lw=1.8, zorder=2,
                label=f"{name}: {fd['sub']}")

    for ratio_val, color, label_txt in [(3.0,'#FF5722','Hf/Th=3'),(7.0,'#7B1FA2','Hf/Ta=7'),(2.5,'#00897B','Hf/Ta=2.5')]:
        if 'Th' in label_txt:
            line = make_ratio_line_hf_th(ratio_val)
        else:
            line = make_ratio_line_hf_ta(ratio_val)
        if len(line) > 1:
            xs_pts, ys_pts = zip(*[ternary_to_xy(*pt) for pt in line])
            ax.plot(xs_pts, ys_pts, color=color, ls='--', lw=1.0, alpha=0.6, zorder=1)
            idx = len(xs_pts) // 2
            ax.text(xs_pts[idx], ys_pts[idx]-0.02, label_txt, fontsize=9, color=color,
                    rotation=-40, ha='left', va='top', style='italic', zorder=5)

    for name, fd in FIELDS_W.items():
        cx = np.mean([cart_w[k][0] for k in fd['keys']])
        cy = np.mean([cart_w[k][1] for k in fd['keys']])
        ax.text(cx, cy+0.025, fd['label'], fontsize=26, fontweight='bold',
                ha='center', va='center', color=fd['edge'], alpha=0.85, zorder=5)
        ax.text(cx, cy-0.02, fd['sub'], fontsize=10,
                ha='center', va='center', color=fd['edge'], alpha=0.7, zorder=5)

    _style.plot_samples_ternary(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.12, 1.12); ax.set_ylim(-0.12, SQRT3_2+0.12)
    ax.set_aspect('equal'); ax.axis('off')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Wood1980_Hf3_Th_Ta.png', out_dir)
    return fig, ax


def plot_pearce_cann(gd, out_dir=None, save=True):
    """
    Pearce & Cann (1973) Ti/100–Zr–Y 三角图 🔥火山岩
    所需元素: Ti (ppm), Zr, Y

    标准分区（Pearce & Cann, 1973, EPSL）:
      A = IAT (岛弧拉斑玄武岩)
      B = MORB (洋中脊玄武岩)
      C = CAB (钙碱性玄武岩)
      D = WPB (板内玄武岩)

    ⚠️ 场界坐标与场区标注的对应关系在原始 PTS_PC 数据中存在几何不匹配
       （场区 B 多边形自交，面积仅 ~0.001），需要原始 Fig.2 数字化数据才能彻底修正。
       当前标注已按 Pearce & Cann (1973) 标准配置，但场界位置仍待校准。

    顶点: Ti/100 (顶), Zr (左下), Y (右下)
    Ti 从微量 ppm 列直接读取（即 Ti 毫克/千克，非氧化物 TiO₂）。
    """
    missing = gd.check_elements('Ti', 'Zr', 'Y', strict=True)
    if missing:
        return None, None
    ti_arr = gd.get('Ti'); zr_arr = gd.get('Zr'); yi_arr = gd.get('Y')
    if np.all(np.isnan(ti_arr)):
        print("[PearceCann] ❌ Ti 数据全为 NaN，无法出图")
        return None, None
    labels = gd.labels

    # 场界顶点（继承自 GCDkit Ti/1000 约定 → 当前 Ti/100 体系下近似坐标）
    PTS_PC = {
        'a':(73.8,12.8,13.4), 'b':(73.8,18.5, 7.7), 'c':(68.7,24.8, 6.5),
        'd':(65.6,24.6, 9.8), 'e':(42.9,42.9,14.1), 'f':(42.9,54.0, 3.1),
        'g':(23.6,69.3, 7.1), 'h':(29.4,44.1,26.5), 'i':(29.4,16.2,54.4),
    }
    cart_pc = {k: ternary_to_xy(*v) for k, v in PTS_PC.items()}

    # 四个判别场区 — Pearce & Cann (1973) Fig.2 标准分区
    # 注意：原始 GCDkit 场界多边形在此体系下几何不完全准确
    FIELDS_PC = {
        'A': {'keys':['a','i','h','d','e'],
              'fill':'#FFE0B2', 'edge':'#E65100',
              'label':'A', 'sub':'IAT'},
        'B': {'keys':['a','b','d','e','f'],
              'fill':'#BBDEFB', 'edge':'#1565C0',
              'label':'B', 'sub':'MORB'},
        'C': {'keys':['b','f','g','h','d'],
              'fill':'#C8E6C9', 'edge':'#2E7D32',
              'label':'C', 'sub':'CAB'},
        'D': {'keys':['a','b','c','d','h','i'],
              'fill':'#E1BEE7', 'edge':'#6A1B9A',
              'label':'D', 'sub':'WPB'},
    }

    x_d, y_d = ternary_to_xy(ti_arr/100.0, zr_arr, yi_arr)

    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    label_ternary_vertices(ax, 'Ti/100', 'Zr', 'Y', corners=corners)

    # 填充场区
    for fd in FIELDS_PC.values():
        keys = fd['keys'] + [fd['keys'][0]]
        ax.fill([cart_pc[k][0] for k in keys], [cart_pc[k][1] for k in keys],
                color=fd['fill'], edgecolor=fd['edge'], lw=1.5, zorder=1)

    # 场区标注
    for name, fd in FIELDS_PC.items():
        cx = np.mean([cart_pc[k][0] for k in fd['keys']])
        cy = np.mean([cart_pc[k][1] for k in fd['keys']])
        ax.text(cx, cy+0.02, fd['label'], fontsize=20, fontweight='bold',
                ha='center', va='center', color=fd['edge'], alpha=0.8, zorder=5)
        ax.text(cx, cy-0.03, fd['sub'], fontsize=9,
                ha='center', va='center', color=fd['edge'], alpha=0.7, zorder=5)

    # 图底文献引用
    ax.text(0.5, -0.08, 'After Pearce & Cann (1973)',
            fontsize=8, fontstyle='italic', ha='center', va='top',
            transform=ax.transAxes, color='#666666')

    _style.plot_samples_ternary(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.1, 1.1); ax.set_ylim(-0.1, SQRT3_2+0.1)
    ax.set_aspect('equal'); ax.axis('off')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'PearceCann1973_TiZrY.png', out_dir)
    return fig, ax


def plot_4panel(gd, out_dir=None, save=True):
    """
    四联比值图（V-Ti / Sc-V / Th/Yb-Nb/Yb / Ba/Th-La/Sm）🔥火山岩
    所需元素: Ti, V, Sc, Nb, Yb, Th, La, Sm, Ba
    Ti 从微量 ppm 列直接读取，不需转换。
    """
    missing = gd.check_elements('Ti', 'V', 'Sc', 'Nb', 'Yb', 'Th', 'La', 'Sm', 'Ba', strict=True)
    if missing:
        return None, None
    v_arr = gd.get('V'); sc_arr = gd.get('Sc'); ti_arr = gd.get('Ti')
    if np.all(np.isnan(ti_arr)):
        print("[4panel] ❌ Ti 数据全为 NaN，无法出图")
        return None, None
    nb_arr = gd.get('Nb'); yb_arr = gd.get('Yb'); th_arr = gd.get('Th')
    la_arr = gd.get('La'); sm_arr = gd.get('Sm'); ba_arr = gd.get('Ba')
    labels = gd.labels

    ti_1000 = ti_arr / 1000.0
    nb_yb = np.where(yb_arr != 0, nb_arr / yb_arr, np.nan)
    th_yb = np.where(yb_arr != 0, th_arr / yb_arr, np.nan)
    la_sm = np.where(sm_arr != 0, la_arr / sm_arr, np.nan)
    ba_th = np.where(th_arr != 0, ba_arr / th_arr, np.nan)
    labels = gd.labels
    groups = gd.groups

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    (ax_a, ax_b), (ax_c, ax_d) = axes

    _style.scatter_samples(ax_a, ti_1000, v_arr, labels, groups=groups)
    _style.style_ax(ax_a, 'Ti/1000', 'V (ppm)', xlabel_size=10, ylabel_size=10)
    ax_a.set_xlim(0.1,None); ax_a.set_ylim(0,None)
    ax_a.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax_a.yaxis.set_major_locator(ticker.MultipleLocator(50))

    _style.scatter_samples(ax_b, v_arr, sc_arr, labels, groups=groups)
    _style.style_ax(ax_b, 'V (ppm)', 'Sc (ppm)', xlabel_size=10, ylabel_size=10)
    ax_b.set_xlim(0,None); ax_b.set_ylim(0,None)

    _style.scatter_samples(ax_c, nb_yb, th_yb, labels, groups=groups)
    _style.style_ax(ax_c, 'Nb/Yb', 'Th/Yb', xlabel_size=10, ylabel_size=10)
    ax_c.set_xlim(0.1,None); ax_c.set_ylim(0.01,None)

    _style.scatter_samples(ax_d, la_sm, ba_th, labels, groups=groups)
    _style.style_ax(ax_d, 'La/Sm', 'Ba/Th', xlabel_size=10, ylabel_size=10)
    ax_d.set_xscale('log'); ax_d.set_yscale('log')
    ax_d.xaxis.set_major_locator(ticker.LogLocator(numticks=6))
    ax_d.yaxis.set_major_locator(ticker.LogLocator(numticks=6))
    ax_d.xaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2,10)*0.1))
    ax_d.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2,10)*0.1))
    ax_d.grid(True, which='both', color='#CCCCCC', linewidth=_style.GRID_LW, alpha=0.6, linestyle='--')

    handles, labels_legend = ax_a.get_legend_handles_labels()
    fig.legend(handles, labels_legend, loc='upper right', bbox_to_anchor=(0.99,0.98),
               fontsize=7, framealpha=0.9, edgecolor='#CCCCCC',
               handlelength=1.5, handleheight=1.0)

    plt.tight_layout(rect=[0,0,1,0.96], pad=0.5)
    if save:
        _style.save_fig(fig, 'V_Ti_Sc_ThNb_BaTh_4panel.png', out_dir)
    return fig, axes


# ────────────────────────────────────────────────────────────
# 🌍 构造判别：Shervais (1982) Ti vs V
# ────────────────────────────────────────────────────────────

def plot_shervais(gd, out_dir=None, save=True):
    """
    Ti vs V 构造判别图（Shervais, 1982）🔥基性岩

    用 Ti/V 比值区分弧/ MORB / OIB 玄武岩。
    Ti 从微量 ppm 列直接读取，不需转换。
    V 是对氧化还原敏感的元素，Ti 是不活动元素。

    底图按 Shervais (1982) 原始线性坐标（改自 GCDkit 版）：
      X 轴: Ti/1000 (范围 0~25)
      Y 轴: V (ppm) (范围 0~600)
      Ti/V 比射线: 10(虚线), 20(虚线), 50(实线), 100(虚线)

    分区: ARC (Ti/V < 20), OFB (Ti/V 20~50), WPB/OIB (Ti/V > 50)

    所需元素: Ti, V
    """
    missing = gd.check_elements('Ti', 'V', strict=True)
    if missing:
        return None, None
    ti_arr = gd.get('Ti'); v_arr = gd.get('V')
    if np.all(np.isnan(ti_arr)):
        print("[Shervais] ❌ Ti 数据全为 NaN，无法出图")
        return None, None
    labels = gd.labels

    # Shervais (1982) 横轴为 Ti/1000，原始 Ti(ppm) 要除以 1000
    ti_1000 = ti_arr / 1000.0

    # ── 版面设置 ──
    fig, ax = plt.subplots(figsize=(9, 7))

    # ── Ti/V 比值射线 ──
    # Shervais (1982) Figure 2 四根 Ti/V 比射线，从原点出发
    # 在 Ti/1000 (x) vs V (y) 坐标系下，V = (Ti/1000 * 1000) / ratio
    # Ti/V = 10 -> y = 100*x  (虚线)
    # Ti/V = 20 -> y =  50*x  (虚线)
    # Ti/V = 50 -> y =  20*x  (实线)
    # Ti/V = 100 -> y = 10*x  (虚线)
    _xt = np.array([0.0, 25.0])
    ax.plot(_xt, 100.0 * _xt, 'k--', lw=0.8, zorder=3)
    ax.plot(_xt, 50.0 * _xt,  'k--', lw=0.8, zorder=3)
    ax.plot(_xt, 20.0 * _xt,  'k-',  lw=1.0, zorder=3)
    ax.plot(_xt, 10.0 * _xt,  'k--', lw=0.8, zorder=3)

    # ── Ti/V 比标注 ──
    ax.text(2.0,  265,  'Ti/V=10', fontsize=7.5, ha='center', va='center',
            color='#333', fontstyle='italic')
    ax.text(4.5,  270,  'Ti/V=20', fontsize=7.5, ha='center', va='center',
            color='#333', fontstyle='italic')
    ax.text(12.0, 275,  'Ti/V=50', fontsize=7.5, ha='center', va='center',
            color='#333', fontstyle='italic')
    ax.text(21.0, 285,  'Ti/V=100', fontsize=7.5, ha='center', va='center',
            color='#333', fontstyle='italic')

    # ── 构造环境标签 ──
    ax.text(4.0,  560,  'ARC', fontsize=11, ha='center', va='center',
            fontweight='bold', color='#2979FF', zorder=5)
    ax.text(15.0, 560,  'OFB', fontsize=11, ha='center', va='center',
            fontweight='bold', color='#558B2F', zorder=5)
    ax.text(12.0, 80,   'WPB', fontsize=11, ha='center', va='center',
            fontweight='bold', color='#E65100', zorder=5)

    # ── 数据投点 ──
    _style.scatter_samples(ax, ti_1000, v_arr, labels, groups=gd.groups)
    _style.add_legend(ax)

    # ── 坐标轴（线性，非 log）──
    ax.set_xlabel('Ti/1000', fontsize=12)
    ax.set_ylabel('V (ppm)', fontsize=12)
    ax.set_xlim(0.0, 25.0)
    ax.set_ylim(0.0, 600.0)
    ax.set_xticks(range(0, 26, 5))
    ax.set_yticks(range(0, 601, 100))
    _style.style_ax(ax, 'Ti/1000', 'V (ppm)')

    # ── 文献引用 ──
    ax.text(0.5, -0.10, 'After Shervais (1982)', fontsize=8,
            fontstyle='italic', ha='center', va='top',
            transform=ax.transAxes, color='#666666')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Shervais1982_Ti_V.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🌍 构造判别：NbN vs ThN (Saccani, 2015)
# ────────────────────────────────────────────────────────────

def plot_saccani_2015(gd, out_dir=None, save=True):
    """
    NbN vs ThN 构造判别图（Saccani, 2015, Geoscience Frontiers）

    使用 N-MORB 标准化的 Nb 和 Th 区分：
    - MORB 阵列（D-MORB, E-MORB, N-MORB）
    - 火山弧阵列（IAT, CAB, BAB）

    所需元素: Nb, Th
    """
    missing = gd.check_elements('Nb', 'Th', strict=True)
    if missing:
        return None, None
    nb = gd.get('Nb'); th = gd.get('Th')
    labels = gd.labels

    from igneous_wr.core.normalize import N_MORB
    nmorb_nb = N_MORB.get('Nb', 2.33)
    nmorb_th = N_MORB.get('Th', 0.12)

    # N-MORB 标准化
    nb_n = np.full_like(nb, np.nan, dtype=float)
    th_n = np.full_like(th, np.nan, dtype=float)
    mask = ~np.isnan(nb) & ~np.isnan(th)
    nb_n[mask] = nb[mask] / nmorb_nb
    th_n[mask] = th[mask] / nmorb_th

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── MORB 阵列 ──
    # Saccani (2015) Fig.2：MORB 阵列和火山弧阵列的边界
    # MORB 阵列大致：ThN ≈ 0.5~3, NbN ≈ 0.3~3
    # 对角线区分 MORB 和弧阵列
    ref_x = np.logspace(np.log10(0.05), np.log10(10), 30)
    # MORB-IAB 边界（近似 ThN/NbN = 1 的对角线）
    # 参考 Saccani (2015) Fig.2：MORB-IAB 边界为一条斜线
    # 边界位置：通过点 (NbN=0.5, ThN=0.5) 和 (NbN=2, ThN=2)
    # 即 ThN/NbN = 1 的对角线
    ax.loglog(ref_x, ref_x, color='#888888', lw=1.0, ls='--')

    # N-MORB 参考点
    ax.scatter([1], [1], marker='*', s=100, color='#4488CC',
               edgecolors='#4488CC', zorder=5, label='N-MORB')
    ax.text(1.1, 0.9, 'N-MORB', fontsize=8,
            fontstyle='italic', color='#4488CC', fontproperties=_style.times_prop)

    # 区分 MORB 和 IAB 的第二个边界：
    # 弧阵列更陡（Th 高，Nb 相对低）
    # 场标注
    ax.text(0.3, 0.15, 'MORB\narray', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(0.3, 2.5, 'Volcanic arc\narray', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(3, 0.4, 'MORB\narray', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, nb_n, th_n, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0.02, 10)
    ax.set_ylim(0.02, 10)
    _style.style_ax(ax, 'NbN', 'ThN')
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'NbN_ThN_Saccani2015.png', out_dir)
    return fig, ax

# ════════════════════════════════════════════════════════════
# 📋 RockPlot SVG 新增
# ════════════════════════════════════════════════════════════

# ── Harris (1986) Rb/30-Hf-3Ta 构造判别 ──────────────────


def plot_harris(gd, out_dir=None, save=True):
    """Harris (1986) Rb/30-Hf-3Ta 花岗岩构造判别三角图
    所需元素: Rb, Hf, Ta
    """
    missing = gd.check_elements('Rb', 'Hf', 'Ta', strict=True)
    if missing:
        return None, None
    rb = gd.get('Rb'); hf = gd.get('Hf'); ta = gd.get('Ta')
    labels = gd.labels
    a = rb / 30.0; b = hf; c = ta * 3.0
    total = a + b + c
    valid = (total > 0) & ~np.isnan(total)
    a_p = np.where(valid, a/total*100, 0)
    b_p = np.where(valid, b/total*100, 0)
    c_p = np.where(valid, c/total*100, 0)
    x_d = np.where(valid, ternary_to_xy(a_p, b_p, c_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(a_p, b_p, c_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)

    # 从 JSON 加载 Harris 边界
    _harr_raw = load_boundary('tec', 'harris')
    _harr_all = []
    for key in sorted(_harr_raw['curves'].keys()):
        c = _harr_raw['curves'][key]
        xy = ternary_to_xy(np.array(c['a']), np.array(c['b']), np.array(c['c']))
        _harr_all.append(xy)

    for xy in _harr_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.5, zorder=4)
    label_ternary_vertices(ax, 'Rb/30', 'Hf', '3Ta')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Harris1986_Rb30_Hf_3Ta.png', out_dir)
    return fig, ax


# ── Muller (2000) Kternary ──────────────────────────────

_muller_labels = [['OI', 'OCI', 'OCA', 'SVO'],  # subplot A
                  ['OFB', 'LKS', 'SSZ', 'WPB'],  # subplot B
                  ['VAB', 'PAP', 'WIP', 'MORB']] # subplot C
_muller_vertices = [
    ('Th', 'Ta', 'Hf'),   # A 的顶点
    ('Th', 'Ta', 'Hf'),   # B 的顶点（相同元素，不同分区）
    ('Th', 'Ta', 'Hf'),   # C 的顶点
]


def plot_muller_kternary(gd, out_dir=None, save=True):
    """Muller (2000) Th-Ta-Hf 三子图等边三元构造判别图
    所需元素: Th, Ta, Hf
    """
    missing = gd.check_elements('Th', 'Ta', 'Hf', strict=True)
    if missing:
        return None, None
    th = gd.get('Th'); ta = gd.get('Ta'); hf = gd.get('Hf')
    labels = gd.labels
    # 标准化
    total = th + ta + hf
    valid = (total > 0) & ~np.isnan(total)
    th_n = np.where(valid, th/total*100, 0)
    ta_n = np.where(valid, ta/total*100, 0)
    hf_n = np.where(valid, hf/total*100, 0)
    x_d = np.where(valid, ternary_to_xy(th_n, ta_n, hf_n)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(th_n, ta_n, hf_n)[1], np.nan)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for i, ax in enumerate(axes):
        corners = ternary_corners()
        draw_ternary_frame(ax, corners)
        draw_ternary_grid(ax, step=20)
        draw_ternary_ticks(ax, step=20)
        label_ternary_vertices(ax, 'Th', 'Ta', 'Hf')
        # 绘制样本点到每个子图
        _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
        ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
        ax.set_aspect('equal'); ax.axis('off')
        ax.set_title(_muller_labels[i][0], fontsize=10, fontweight='bold')
    _style.add_legend(axes[2])
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Muller2000_Kternary.png', out_dir)
    return fig, axes


def plot_pearcenorry(gd, out_dir=None, save=True):
    """Pearce & Norry (1979) Zr/Y vs Zr 构造判别图
    所需元素: Zr, Y
    """
    missing = gd.check_elements('Zr', 'Y', strict=True)
    if missing:
        return None, None
    zr = gd.get('Zr'); y = gd.get('Y')
    labels = gd.labels
    zr_y = np.where(y > 0, zr / y, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    # WPB (板内玄武岩) / MORB (洋中脊) / IAB (岛弧) 分界
    # Zr/Y = 3, Zr/Y = 7
    ax.axhline(3, 0, 1, color='k', ls='--', lw=0.8)
    ax.axhline(7, 0, 1, color='k', ls='--', lw=0.8)
    # Zr = 150 分界
    ax.axvline(150, 0, 1, color='k', ls=':', lw=0.8)

    ax.text(10, 9, 'WPB', fontsize=10, ha='left', style='italic')
    ax.text(10, 5, 'MORB', fontsize=10, ha='left', style='italic')
    ax.text(10, 1.5, 'IAB', fontsize=10, ha='left', style='italic')

    _style.scatter_samples(ax, zr, zr_y, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log')
    ax.set_xlim(5, 2000); ax.set_ylim(0.5, 50)
    _style.style_ax(ax, 'Zr (ppm)', 'Zr/Y')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce_Norry1979_ZrY_Zr.png', out_dir)
    return fig, ax


# ── Pearce (1982) 判别图 ─────────────────────────────────


def plot_pearce1982(gd, out_dir=None, save=True):
    """Pearce (1982) 判别图
    所需元素: Zr, Y, Ti, Nb, Sr
    """
    missing = gd.check_elements('Zr', 'Y', 'Ti', 'Nb', 'Sr', strict=True)
    if missing:
        return None, None
    zr = gd.get('Zr'); y = gd.get('Y')
    ti = gd.get('Ti'); nb = gd.get('Nb'); sr = gd.get('Sr')
    labels = gd.labels
    ti_yb_100 = np.where(y > 0, (ti / 1000) / y * 100, np.nan)
    zr_y = np.where(y > 0, zr / y, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    # 分界 (Pearce 1982 simplified)
    xs = np.linspace(0, 1000, 50)
    ax.axhline(10, 0, 1, color='k', ls='--', lw=0.8)
    ax.axvline(100, 0, 1, color='k', ls='--', lw=0.8)
    # 对角线分界
    ax.plot(xs, xs * 0.1, 'k-', lw=1.0, alpha=0.5)

    _style.scatter_samples(ax, zr, zr_y, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 500); ax.set_ylim(0, 50)
    _style.style_ax(ax, 'Zr (ppm)', 'Zr/Y')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1982_ZrY_Zr.png', out_dir)
    return fig, ax


# ── Pearce Granite (1984) Rb vs Y+Nb ─────────────────────


def plot_pearcegranite(gd, out_dir=None, save=True):
    """Pearce et al. (1984) Rb vs Y+Nb 花岗岩构造判别图
    所需元素: Rb, Y, Nb
    """
    missing = gd.check_elements('Rb', 'Y', 'Nb', strict=True)
    if missing:
        return None, None
    rb = gd.get('Rb'); y = gd.get('Y'); nb = gd.get('Nb')
    labels = gd.labels
    y_nb = y + nb
    fig, ax = plt.subplots(figsize=(9, 7))

    # Pearce (1984) 花岗岩判别边界: VAG, syn-COLG, WPG, ORG
    xs = np.logspace(np.log10(10), np.log10(5000), 100)
    # VAG/syn-COLG 分界: Rb = 48 * exp(-(Y+Nb-30)/200) + 100
    ax.plot(xs, 48 * np.exp(-(xs - 30) / 200) + 100, 'k-', lw=1.5)
    # syn-COLG / WPG 分界: Rb = 100
    ax.axhline(100, 0, 1, color='k', ls='--', lw=0.8)
    # WPG / VAG 分界 (在 Y+Nb 较大端)
    ax.axvline(250, 0, 1, color='k', ls='--', lw=0.8)
    ax.axvline(50, 0, 1, color='k', ls=':', lw=0.8)

    ax.text(15, 300, 'syn-COLG', fontsize=9, ha='left', rotation=35, style='italic')
    ax.text(300, 300, 'WPG', fontsize=9, ha='center', style='italic')
    ax.text(15, 10, 'VAG', fontsize=9, ha='left', style='italic')
    ax.text(300, 10, 'ORG', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, y_nb, rb, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(5, 5000); ax.set_ylim(1, 1000)
    _style.style_ax(ax, 'Y + Nb (ppm)', 'Rb (ppm)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1984_Granite_Rb_YNb.png', out_dir)
    return fig, ax


# ── Pearce Nb-Th-Yb (1995) ───────────────────────────────


def plot_batchelor(gd, out_dir=None, save=True):
    """Batchelor & Bowden (1985) R1-R2 花岗岩构造判别图
    R1 = 4Si - 11(Na+K) - 2(Fe+Ti)
    R2 = Al + 2Mg + 6Ca
    所需元素: SiO2, Al2O3, K2O, Na2O, CaO, FeO(T), MgO, TiO2
    """
    needed = ('SiO2', 'Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2')
    missing = gd.check_elements(*needed, strict=True)
    if missing or ('FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data):
        return None, None
    sio2 = gd.get('SiO2'); al2o3 = gd.get('Al2O3')
    k2o = gd.get('K2O'); na2o = gd.get('Na2O'); cao = gd.get('CaO')
    mgo = gd.get('MgO'); tio2 = gd.get('TiO2')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels

    si = sio2 * 1000 / 60.08
    al = al2o3 * 2000 / 101.96
    k = k2o * 2000 / 94.20
    na = na2o * 2000 / 61.98
    ca = cao * 2000 / 56.08
    fe = feo_t * 2000 / 71.84
    mg = mgo * 2000 / 40.30
    ti = tio2 * 2000 / 79.87
    r1_val = (4*si - 11*(na+k) - 2*(fe+ti)) / 100
    r2_val = (al + 2*mg + 6*ca) / 100
    fig, ax = plt.subplots(figsize=(10, 8))

    # Batchelor 构造分区
    ax.axhline(0, 0, 1, color='k', lw=0.5)
    ax.axvline(0, 0, 1, color='k', lw=0.5)
    # 分区标注
    ax.text(-20, 30, 'Anorogenic', fontsize=9, ha='center', style='italic')
    ax.text(20, 20, 'Syn-collision', fontsize=9, ha='center', style='italic')
    ax.text(-20, -10, 'Late-orogenic', fontsize=9, ha='center', style='italic')
    ax.text(20, -10, 'Post-orogenic', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, r1_val, r2_val, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-40, 40); ax.set_ylim(-20, 40)
    _style.style_ax(ax, 'R1 = 4Si-11(Na+K)-2(Fe+Ti) (×10$^{-2}$)',
                    'R2 = Al+2Mg+6Ca (×10$^{-2}$)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Batchelor1985_R1_R2.png', out_dir)
    return fig, ax


# ── Muller (1992) K2O-SiO2 二元图 ─────────────────────────


def plot_maniar(gd, out_dir=None, save=True):
    """Maniar & Piccoli (1989) 花岗岩构造判别图
    所需元素: SiO2, Al2O3, FeO(T), MgO, CaO, Na2O, K2O, TiO2, MnO, P2O5
    """
    needed = ('SiO2', 'Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'TiO2')
    missing = gd.check_elements(*needed, strict=True)
    if missing or ('FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data):
        return None, None
    sio2 = gd.get('SiO2'); al2o3 = gd.get('Al2O3')
    mgo = gd.get('MgO'); cao = gd.get('CaO')
    na2o = gd.get('Na2O'); k2o = gd.get('K2O'); tio2 = gd.get('TiO2')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels

    # A/CNK vs Na2O+K2O
    acnk = al2o3 / 101.96 / (cao/56.08 + na2o/61.98 + k2o/94.20)
    alk = na2o + k2o
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.axhline(1.0, 0, 1, color='k', ls='--', lw=1.0)
    ax.axvline(5, 0, 1, color='k', ls=':', lw=0.8)

    ax.text(2, 1.4, 'Peraluminous', fontsize=9, ha='left', style='italic')
    ax.text(2, 0.7, 'Metaluminous', fontsize=9, ha='left', style='italic')

    _style.scatter_samples(ax, alk, acnk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 14); ax.set_ylim(0.5, 1.5)
    _style.style_ax(ax, r'Na$_2$O+K$_2$O (wt.%)', 'A/CNK')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Maniar1989_Granite_disc.png', out_dir)
    return fig, ax


# ── Agrawal (2004) 判别函数图 ─────────────────────────────


def plot_agrawal(gd, out_dir=None, save=True):
    """Agrawal (2004) 判别函数 基性岩构造判别图
    需选择三个判别函数之一 (简化版: DF1-DF2)
    所需元素: TiO2, Al2O3, FeO(T), MgO, CaO, Na2O, K2O, MnO, P2O5, SiO2
    """
    needed = ('TiO2', 'Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'MnO', 'P2O5', 'SiO2')
    missing = gd.check_elements(*needed, strict=True)
    if missing or ('FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data):
        return None, None
    tio2 = gd.get('TiO2'); al2o3 = gd.get('Al2O3')
    mgo = gd.get('MgO'); cao = gd.get('CaO')
    na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    mno = gd.get('MnO'); p2o5 = gd.get('P2O5')
    sio2 = gd.get('SiO2')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels

    # DF1 和 DF2 简化公式 (Agrawal 2004)
    df1 = (0.553*tio2 + 0.105*al2o3 - 0.206*feo_t - 0.103*mgo
           + 0.213*cao + 0.142*na2o - 4.382*k2o - 1.277*mno
           + 0.083*p2o5 - 0.410*sio2 - 17.624)
    df2 = (0.188*tio2 + 0.292*al2o3 - 0.293*feo_t + 0.011*mgo
           - 0.153*cao - 0.510*na2o + 2.065*k2o - 3.025*mno
           - 0.024*p2o5 + 0.020*sio2 - 8.532)
    fig, ax = plt.subplots(figsize=(9, 7))

    # 构造分区
    ax.axhline(0, 0, 1, color='k', lw=0.5)
    ax.axvline(0, 0, 1, color='k', lw=0.5)
    ax.text(-2, 2, 'WPB', fontsize=9, ha='center', style='italic')
    ax.text(2, 2, 'IAB', fontsize=9, ha='center', style='italic')
    ax.text(-2, -2, 'MORB', fontsize=9, ha='center', style='italic')
    ax.text(2, -2, 'IAB+MORB', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, df1, df2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-4, 4); ax.set_ylim(-4, 4)
    _style.style_ax(ax, 'DF1', 'DF2')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Agrawal2004_DF1_DF2.png', out_dir)
    return fig, ax


# ── Verma (2002, 2013) 判别图 ─────────────────────────────


def plot_verma(gd, out_dir=None, save=True):
    """Verma et al. 判别函数 基性岩构造判别图
    所需元素: TiO2, Al2O3, FeO(T), MgO, CaO, Na2O, K2O, MnO, P2O5, SiO2
    """
    needed = ('TiO2', 'Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'MnO', 'P2O5', 'SiO2')
    missing = gd.check_elements(*needed, strict=True)
    if missing or ('FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data):
        return None, None
    tio2 = gd.get('TiO2'); al2o3 = gd.get('Al2O3')
    mgo = gd.get('MgO'); cao = gd.get('CaO')
    na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    mno = gd.get('MnO'); p2o5 = gd.get('P2O5'); sio2 = gd.get('SiO2')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels

    df1 = (0.499*tio2 + 0.434*al2o3 - 0.120*feo_t + 0.124*mgo
           - 0.010*cao + 0.212*na2o - 0.904*k2o + 0.077*mno
           + 0.324*p2o5 - 0.783*sio2 + 38.373)
    df2 = (-0.552*tio2 + 0.188*al2o3 - 0.157*feo_t + 0.203*mgo
           + 0.020*cao - 0.213*na2o - 0.472*k2o + 0.312*mno
           + 0.193*p2o5 - 0.044*sio2 + 7.142)
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.axhline(0, 0, 1, color='k', lw=0.5)
    ax.axvline(0, 0, 1, color='k', lw=0.5)
    ax.text(-2, 3, 'IA', fontsize=9, ha='center', style='italic')
    ax.text(3, 2, 'MORB', fontsize=9, ha='center', style='italic')
    ax.text(-2, -2, 'WPB', fontsize=9, ha='center', style='italic')
    ax.text(2, -3, 'CA', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, df1, df2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-4, 5); ax.set_ylim(-4, 4)
    _style.style_ax(ax, 'DF1', 'DF2')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Verma_discriminant_DF1_DF2.png', out_dir)
    return fig, ax


# ── La Roche (1980) 侵入岩 R1-R2 ──────────────────────────


def plot_schandl(gd, out_dir=None, save=True):
    """Schandl et al. (2004) Y vs Zr 花岗岩构造判别图
    所需元素: Y, Zr
    """
    missing = gd.check_elements('Y', 'Zr', strict=True)
    if missing:
        return None, None
    y = gd.get('Y'); zr = gd.get('Zr')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(9, 7))

    # Schandl 分界线
    ax.plot([0, 200], [0, 500], 'k-', lw=1.0)
    ax.axhline(100, 0, 1, color='k', ls='--', lw=0.8)
    ax.axvline(150, 0, 1, color='k', ls=':', lw=0.8)

    _style.scatter_samples(ax, zr, y, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 500); ax.set_ylim(0, 300)
    _style.style_ax(ax, 'Zr (ppm)', 'Y (ppm)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Schandl2004_Y_Zr.png', out_dir)
    return fig, ax


# ── Batchelor & Bowden (1985) R1-R2 ────────────────────────


# ── Maniar & Piccoli (1989) 判别图 ────────────────────────


