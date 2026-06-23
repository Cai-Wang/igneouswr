"""build_2x2_geochem.py — 四图 A4 拼版 (手动 add_axes 定位)

每个图 80mm 宽，在 A4 上独立定位，不裁剪。
全部字体 12pt。

用法:
    python3 build_2x2_geochem.py <xlsx_path> [-o PREFIX]
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 全局字体
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'  # 数学符号也能匹配 TNR 风格

from igneous_wr_core import GeochemData

DPI = 300
TEXT_COLOR = '#333333'
LINE_COLOR_MAIN = '#333333'
LINE_COLOR_SEC = '#666666'
FS = 12            # 全局字号

# ── A4 尺寸 ──
A4_W, A4_H = 210, 297  # mm

# ── 布局参数 ──
PANEL_W = 80            # 每个图 80mm 宽
COL_GAP = 10            # 列间距 10mm
ROW_GAP = 12            # 行间距 12mm（12pt 字体需要更多空间）
LEFT_M = (A4_W - (2 * PANEL_W + COL_GAP)) / 2

# 面板高度（保持原比例）
H_ROW1 = 75   # TAS y:0-19
H_ROW2 = 68   # Shand y:0-7, Whalen log

# 垂直居中
CONTENT_H = H_ROW1 + ROW_GAP + H_ROW2
TOP_M = (A4_H - CONTENT_H) / 2

POS = {}
POS['a'] = [LEFT_M / A4_W, (TOP_M + H_ROW2 + ROW_GAP) / A4_H, PANEL_W / A4_W, H_ROW1 / A4_H]
POS['b'] = [(LEFT_M + PANEL_W + COL_GAP) / A4_W, (TOP_M + H_ROW2 + ROW_GAP) / A4_H, PANEL_W / A4_W, H_ROW1 / A4_H]
POS['c'] = [LEFT_M / A4_W, TOP_M / A4_H, PANEL_W / A4_W, H_ROW2 / A4_H]
POS['d'] = [(LEFT_M + PANEL_W + COL_GAP) / A4_W, TOP_M / A4_H, PANEL_W / A4_W, H_ROW2 / A4_H]


def style_ax(ax, xlabel='', ylabel=''):
    ax.tick_params(direction='in', length=4.5, width=0.5, top=True, right=True, labelsize=FS)
    ax.minorticks_on()
    ax.tick_params(direction='in', which='minor', length=2.5, width=0.3, top=True, right=True)
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=FS, fontfamily='Times New Roman')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=FS, fontfamily='Times New Roman')


def add_L_label(ax, label_text):
    ax.plot([0.92, 0.92], [0.92, 1.0], transform=ax.transAxes,
            color='#333', lw=0.5, zorder=20)
    ax.plot([0.92, 1.0], [0.92, 0.92], transform=ax.transAxes,
            color='#333', lw=0.5, zorder=20)
    r = plt.Rectangle((0.921, 0.921), 0.077, 0.077,
                      facecolor='white', edgecolor='none',
                      transform=ax.transAxes, zorder=19)
    ax.add_patch(r)
    ax.text(0.96, 0.96, label_text, fontsize=FS, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes, zorder=21)


# ═══════════════════════════════════════════════
# 面板绘制
# ═══════════════════════════════════════════════

def draw_tas(ax, gd):
    sio2 = gd.get('SiO2')
    alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    from igneous_wr.boundaries.core import load_boundary
    td = load_boundary('cls', 'tas')
    fields = {k: [tuple(p) for p in v] for k, v in td['fields'].items()}
    lm = td['labels']
    to = td.get('text_only', {})
    for name, poly in fields.items():
        n = len(poly)
        for i in range(n):
            seg = tuple(sorted([poly[i], poly[(i + 1) % n]]))
            ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                    color=LINE_COLOR_MAIN, lw=0.7, zorder=2)
    for label, (tx, ty) in to.items():
        ax.text(tx, ty, label, ha='center', va='center', fontsize=FS,
                fontweight='normal', color=LINE_COLOR_SEC, style='italic', zorder=5)
    for name, poly in fields.items():
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        ax.text(cx, cy, lm.get(name, name), ha='center', va='center',
                fontsize=FS, fontweight='bold', color=TEXT_COLOR, zorder=5)
    ax.scatter(sio2, alk, c='#e74c3c', s=24, edgecolors='#c0392b',
               linewidths=0.5, zorder=10, alpha=0.85)
    for i, lbl in enumerate(labels):
        ax.annotate(lbl, (sio2[i], alk[i]),
                    textcoords='offset points', xytext=(4, 5),
                    fontsize=FS, color='#555', zorder=11)
    ax.set_xlim(34, 90)
    ax.set_ylim(0, 19)
    ax.set_xticks(range(35, 95, 5))
    style_ax(ax, 'SiO$_2$ (wt.%)', 'Na$_2$O+K$_2$O (wt.%)')


def draw_k2o_sio2(ax, gd):
    sio2 = gd.get('SiO2')
    k2o = gd.get('K2O')
    labels = gd.labels
    ax.plot([45, 75], [0.5, 2.5], color=LINE_COLOR_MAIN, lw=1.5, zorder=3)
    ax.plot([50, 75], [1.5, 4.0], color=LINE_COLOR_SEC, lw=1.2, ls='--', zorder=3)
    ax.plot([55, 75], [2.5, 6.0], color=LINE_COLOR_SEC, lw=1.2, ls='-.', zorder=3)
    ax.text(80, 1.4, 'Low-K\nTholeiitic', fontsize=FS, ha='right', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=4)
    ax.text(80, 3.7, 'Medium-K\nCalc-alkaline', fontsize=FS, ha='right', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=4)
    ax.text(80, 5.7, 'High-K\nCalc-alkaline', fontsize=FS, ha='right', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=4)
    ax.text(43, 7.4, 'Shoshonitic', fontsize=FS, ha='left', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=4)
    ax.scatter(sio2, k2o, c='#e74c3c', s=24, edgecolors='#c0392b',
               linewidths=0.5, zorder=10, alpha=0.85)
    for i, lbl in enumerate(labels):
        ax.annotate(lbl, (sio2[i], k2o[i]),
                    textcoords='offset points', xytext=(4, 5),
                    fontsize=FS, color='#555', zorder=11)
    ax.set_xlim(42, 82)
    ax.set_ylim(0, 8)
    style_ax(ax, 'SiO$_2$ (wt.%)', 'K$_2$O (wt.%)')


def draw_shand(ax, gd):
    al2o3 = gd.get('Al2O3')
    cao = gd.get('CaO')
    na2o = gd.get('Na2O')
    k2o = gd.get('K2O')
    labels = gd.labels
    MW = {'Al2O3': 101.96, 'CaO': 56.08, 'Na2O': 61.98, 'K2O': 94.20}
    al_m = al2o3 / MW['Al2O3']
    ca_m = cao / MW['CaO']
    na_m = na2o / MW['Na2O']
    k_m = k2o / MW['K2O']
    acnk = al_m / (ca_m + na_m + k_m)
    a_nk = al_m / (na_m + k_m)
    ax.set_xlim(0.5, 2.0)
    ax.set_ylim(0, 7)
    ax.axhline(y=1.0, color=LINE_COLOR_SEC, ls='--', lw=0.8, zorder=2)
    ax.axvline(x=1.0, color=LINE_COLOR_SEC, ls='--', lw=0.8, zorder=2)
    ax.plot([0, 7], [0, 7], color=LINE_COLOR_SEC, ls=':', lw=0.8, zorder=2)
    ax.text(0.72, 5.5, 'Metaluminous', fontsize=FS, ha='center', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=3)
    ax.text(1.5, 5.5, 'Peraluminous', fontsize=FS, ha='center', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=3)
    ax.text(0.72, 0.5, 'Peralkaline', fontsize=FS, ha='center', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=3)
    ax.scatter(acnk, a_nk, c='#e74c3c', s=24, edgecolors='#c0392b',
               linewidths=0.5, zorder=10, alpha=0.85)
    for i, lbl in enumerate(labels):
        ax.annotate(lbl, (acnk[i], a_nk[i]),
                    textcoords='offset points', xytext=(4, 5),
                    fontsize=FS, color='#555', zorder=11)
    style_ax(ax, 'A/CNK', 'A/NK')


def draw_whalen(ax, gd):
    ga = gd.get('Ga')
    al2o3 = gd.get('Al2O3')
    na2o = gd.get('Na2O')
    k2o = gd.get('K2O')
    labels = gd.labels
    ga_al = ga / (al2o3 * 0.52913)
    alk = na2o + k2o
    ax.set_xscale('log', base=10)
    ax.set_yscale('log', base=10)
    ax.set_xlim(1, 20)
    ax.set_ylim(1, 20)
    ax.set_xticks([1, 3, 10, 20])
    ax.set_yticks([1, 3, 10, 20])
    ax.set_xticklabels(['1', '3', '10', '20'])
    ax.set_yticklabels(['1', '3', '10', '20'])
    ax.plot([1, 2.6], [8.5, 8.5], color=LINE_COLOR_MAIN, lw=1.5, zorder=3)
    ax.plot([2.6, 2.6], [8.5, 1], color=LINE_COLOR_MAIN, lw=1.5, zorder=3)
    ax.text(3.5, 12, 'A-type', fontsize=FS, ha='left', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=4)
    ax.text(1.6, 3.2, 'I & S-type', fontsize=FS, ha='center', va='center',
            color=TEXT_COLOR, fontweight='bold', zorder=4)
    ax.scatter(ga_al, alk, c='#e74c3c', s=24, edgecolors='#c0392b',
               linewidths=0.5, zorder=10, alpha=0.85)
    for i, lbl in enumerate(labels):
        ax.annotate(lbl, (ga_al[i], alk[i]),
                    textcoords='offset points', xytext=(4, 5),
                    fontsize=FS, color='#555', zorder=11)
    style_ax(ax, '10000×Ga/Al', 'Na$_2$O+K$_2$O (wt.%)')
    ax.tick_params(axis='both', which='major', labelsize=FS)


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

def main():
    xlsx_path = None
    out_prefix = 'geochem_2x2'
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == '-o' and i+1 < len(args):
            out_prefix = args[i+1]
        elif a.endswith('.xlsx'):
            xlsx_path = a
    if xlsx_path is None:
        print('Usage: python3 build_2x2_geochem.py <xlsx_path> [-o PREFIX]')
        sys.exit(1)

    gd = GeochemData(xlsx_path)
    print(f'Loaded {len(gd.labels)} samples')

    fig = plt.figure(figsize=(A4_W / 25.4, A4_H / 25.4), dpi=DPI)
    fig.patch.set_facecolor('white')

    panels = [
        ('a', draw_tas),
        ('b', draw_k2o_sio2),
        ('c', draw_shand),
        ('d', draw_whalen),
    ]

    for key, draw_fn in panels:
        ax = fig.add_axes(POS[key])
        print(f'  Drawing ({key}) at {POS[key]}')
        draw_fn(ax, gd)
        add_L_label(ax, f'({key})')

    out = f'{out_prefix}_a4.png'
    fig.savefig(out, dpi=DPI, facecolor='white', edgecolor='none')
    print(f'\n  Saved: {out}')
    plt.close(fig)


if __name__ == '__main__':
    main()
