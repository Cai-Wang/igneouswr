import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

import _style
from _chem import feot_calc
from _ternary import (
    SQRT3_2, ternary_to_xy, ternary_corners,
    draw_ternary_frame, draw_ternary_grid,
    draw_ternary_ticks, label_ternary_vertices,
)

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
    Ti 从微量 ppm 列直接读取，不需转换。
    """
    missing = gd.check_elements('Ti', 'Zr', 'Y', strict=True)
    if missing:
        return None, None
    ti_arr = gd.get('Ti'); zr_arr = gd.get('Zr'); yi_arr = gd.get('Y')
    if np.all(np.isnan(ti_arr)):
        print("[PearceCann] ❌ Ti 数据全为 NaN，无法出图")
        return None, None
    labels = gd.labels

    PTS_PC = {
        'a':(22,38,40),'b':(22,55,23),'c':(18,65,17),'d':(16,60,24),
        'e':(7,70,23),'f':(7,88,5),'g':(3,88,9),'h':(4,60,36),'i':(4,22,74),
    }
    cart_pc = {k: ternary_to_xy(*v) for k, v in PTS_PC.items()}

    FIELDS_PC = {
        'D': {'keys':['a','b','c','d','h','i'],'fill':'#E1BEE7','edge':'#6A1B9A','label':'D','sub':'MORB'},
        'C': {'keys':['b','f','g','h','d'],'fill':'#C8E6C9','edge':'#2E7D32','label':'C','sub':'WPB'},
        'B': {'keys':['a','b','d','e','f'],'fill':'#BBDEFB','edge':'#1565C0','label':'B','sub':'MORB+IAT+CAB'},
        'A': {'keys':['a','i','h','d','e'],'fill':'#FFE0B2','edge':'#E65100','label':'A','sub':'IAT+CAB'},
    }

    # Ti/100-Zr-Y: Ti除以100使量级与Zr匹配，Y不额外缩放
    # ⚠️ 场界多边形坐标(PTS_PC)基于Ti/1000约定设计，
    #    在Ti/100体系下位置可能不准确，需确认后调整
    x_d, y_d = ternary_to_xy(ti_arr/100.0, zr_arr, yi_arr)

    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    label_ternary_vertices(ax, 'Ti/100', 'Zr', 'Y', corners=corners)

    for fd in FIELDS_PC.values():
        keys = fd['keys'] + [fd['keys'][0]]
        ax.fill([cart_pc[k][0] for k in keys], [cart_pc[k][1] for k in keys],
                color=fd['fill'], edgecolor=fd['edge'], lw=1.5, zorder=1)

    for name, fd in FIELDS_PC.items():
        cx = np.mean([cart_pc[k][0] for k in fd['keys']])
        cy = np.mean([cart_pc[k][1] for k in fd['keys']])
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

    # Ti/V 比值线（划分构造环境）
    # Shervais (1982): Ti/V = 10, 20, 50, 100 为边界
    # 注意：横轴 Ti/1000 下的 Ti/V 比值线，物理上等价但数值要对应
    fig, ax = plt.subplots(figsize=(8, 7))

    # ── Ti/V 比值线 ──
    # 横轴是 Ti/1000，比值线 y = V = (Ti/1000)*1000 / ratio
    ratio_lines = {
        10: ('Ti/V = 10', '#990000'),
        20: ('Ti/V = 20', '#CC6600'),
        50: ('Ti/V = 50', '#009933'),
        100: ('Ti/V = 100', '#3366CC'),
    }
    x_range_ti1000 = np.array([0.01, 50])  # 对应原始 Ti 10~50000 ppm
    for ratio, (label_txt, color) in ratio_lines.items():
        # 因为散点 = ti_arr/1000，要维持 Ti/V = ratio，V = ti_arr / ratio = ti_1000 * 1000 / ratio
        # 但在 ti_1000 坐标系下，V 值不变（ppm 不变）
        # 所以线：在 log(ti_1000) vs log(V) 空间，V = (ti_1000 * 1000) / ratio
        y_vals = (x_range_ti1000 * 1000) / ratio
        ax.loglog(x_range_ti1000, y_vals, color=color, lw=0.8, ls='--', alpha=0.7)
        # 标注
        mid_x = 2.0  # Ti/1000 = 2，对应原始 Ti = 2000 ppm
        mid_y = (mid_x * 1000) / ratio
        ax.text(mid_x * 1.3, mid_y * 1.3, label_txt, fontsize=7,
                color=color, fontstyle='italic', fontproperties=_style.times_prop)

    # ── 构造环境标签 ──
    # Shervais 的原始分区（横轴为 Ti/1000 刻度时的标注位置）
    ax.text(0.05, 0.5, 'Arc\n(IAT,\nboninite)', fontsize=8, ha='left', va='bottom',
            fontstyle='italic', color='#990000', fontproperties=_style.times_prop)
    ax.text(0.5, 50, 'Arc\ntholeiite', fontsize=8, ha='center', va='bottom',
            fontstyle='italic', color='#CC6600', fontproperties=_style.times_prop)
    ax.text(3, 100, 'MORB', fontsize=9, ha='center', va='bottom',
            fontstyle='italic', color='#009933', fontproperties=_style.times_prop)
    ax.text(8, 120, 'WPB / OIB', fontsize=9, ha='center', va='bottom',
            fontstyle='italic', color='#3366CC', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, ti_1000, v_arr, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlabel('Ti/1000', fontsize=12)
    ax.set_ylabel('V (ppm)', fontsize=12)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.03, 60)
    ax.set_ylim(0.3, 3000)
    _style.style_ax(ax, 'Ti/1000', 'V (ppm)')

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

    from _normalize import N_MORB
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

harr_0_a = np.array([76.7, 72.1, 50.8, 22.4, 19.5])
harr_0_b = np.array([-0.0, 14.0, 26.7, 43.5, -0.2])
harr_0_c = np.array([23.4, 14.0, 22.5, 34.1, 80.6])
harr_0_xy = ternary_to_xy(harr_0_a, harr_0_b, harr_0_c)
harr_1_a = np.array([50.8, 30.1]); harr_1_b = np.array([26.7, -0.1]); harr_1_c = np.array([22.5, 69.9])
harr_1_xy = ternary_to_xy(harr_1_a, harr_1_b, harr_1_c)
harr_2_a = np.array([6.2, 7.8, 15.2, 21.9, 25.6, 26.2])
harr_2_b = np.array([71.4, 69.5, 60.1, 50.0, 42.7, 41.3])
harr_2_c = np.array([22.4, 22.7, 24.6, 28.1, 31.7, 32.5])
harr_2_xy = ternary_to_xy(harr_2_a, harr_2_b, harr_2_c)

_harr_all = [harr_0_xy, harr_1_xy, harr_2_xy]


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
