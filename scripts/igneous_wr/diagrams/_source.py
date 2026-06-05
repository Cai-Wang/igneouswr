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
from igneous_wr.core.normalize import REE_ORDER, CHONDRITE, SPIDER_ORDER, PRIMITIVE_MANTLE, normalize
from igneous_wr.boundaries.core import load_boundary

"""
_source.py — 源区图：REE, Spider, Pearce 系列, U/Th, Th/Yb-Ta/Yb, (Sm/Yb)-(La/Sm), Sc-V, Ba/Th-La/Sm, Nb/La-Th/La, Zr/Y-Zr, Gd/Yb-Dy/Dy*, Dy/Yb-La/Yb
"""

# ────────────────────────────────────────────────────────────
# 🔬 源区性质
# ────────────────────────────────────────────────────────────

def plot_ree(gd, out_dir=None, save=True):
    """
    REE 球粒陨石标准化配分模式图 📊通用
    所需元素: La,Ce,Pr,Nd,Sm,Eu,Gd,Tb,Dy,Ho,Er,Tm,Yb,Lu
    """
    # 核心元素缺了就没法画 REE 模式
    missing = gd.check_elements('La', 'Ce', 'Nd', 'Sm', 'Yb', strict=True)
    if missing:
        return None, None
    # 次要元素缺失仅 warning
    gd.check_elements(*REE_ORDER)
    labels = gd.labels
    groups = gd.groups
    group_colors = _style.get_group_colors(groups)

    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(REE_ORDER))
    seen_groups = set()
    for i in range(len(labels)):
        raw = {e: gd.get(e)[i] for e in REE_ORDER}
        normed = normalize(raw, CHONDRITE)
        y_vals = np.array([normed[e] if not np.isnan(normed[e]) else np.nan for e in REE_ORDER])
        valid = np.isfinite(y_vals) & (y_vals > 0)
        g = groups[i] if i < len(groups) else labels[i]
        c = group_colors.get(g, _style.get_color(i))
        label_g = g if g not in seen_groups else None
        seen_groups.add(g)
        ax.plot(x_pos[valid], y_vals[valid], color=c, lw=1.2, zorder=2, label=label_g)
        ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=_style.MK_SIZE_SINGLE,
                   edgecolors=_style.MK_EDGE_COLOR, linewidths=_style.MK_EDGE_WIDTH, zorder=3)

    ax.set_xticks(x_pos); ax.set_xticklabels(REE_ORDER, fontsize=8)
    ax.set_xlim(x_pos[0]-0.3, x_pos[-1]+0.3)
    ax.set_yscale('log')
    _style.style_ax(ax, 'Rare Earth Elements', 'Chondrite-normalized')
    ax.axhline(y=1, color='gray', ls='--', lw=0.6, alpha=0.7)
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2,10)*0.1))
    _style.add_legend(ax)

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'REE_chondrite.png', out_dir)
    return fig, ax


def plot_spider(gd, out_dir=None, save=True):
    """
    原始地幔标准化蛛网图 📊通用
    所需元素: Rb,Ba,Th,U,Nb,Ta,La,Ce,Pb,Pr,Nd,Sr,Sm,Zr,Hf,Eu,Ti,Gd,Tb,Dy,Ho,Y,Er,Tm,Yb,Lu
    """
    # 核心元素缺了就没法画蛛网模式
    missing = gd.check_elements('Th', 'Nb', 'La', 'Ce', 'Nd', 'Sm', 'Yb', strict=True)
    if missing:
        return None, None
    # 次要元素缺失仅 warning
    gd.check_elements(*SPIDER_ORDER)
    labels = gd.labels
    groups = gd.groups
    group_colors = _style.get_group_colors(groups)

    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(SPIDER_ORDER))
    seen_groups = set()
    for i in range(len(labels)):
        raw = {e: gd.get(e)[i] for e in SPIDER_ORDER}
        normed = normalize(raw, PRIMITIVE_MANTLE)
        y_vals = np.array([normed[e] if not np.isnan(normed[e]) else np.nan for e in SPIDER_ORDER])
        valid = np.isfinite(y_vals) & (y_vals > 0)
        g = groups[i] if i < len(groups) else labels[i]
        c = group_colors.get(g, _style.get_color(i))
        label_g = g if g not in seen_groups else None
        seen_groups.add(g)
        ax.plot(x_pos[valid], y_vals[valid], color=c, lw=1.2, zorder=2, label=label_g)
        ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=_style.MK_SIZE_SINGLE,
                   edgecolors=_style.MK_EDGE_COLOR, linewidths=_style.MK_EDGE_WIDTH, zorder=3)

    ax.set_xticks(x_pos); ax.set_xticklabels(SPIDER_ORDER, fontsize=7, rotation=45, ha='right')
    ax.set_xlim(x_pos[0]-0.3, x_pos[-1]+0.3)
    ax.set_yscale('log')
    _style.style_ax(ax, 'Trace Elements', 'Primitive-mantle normalized')
    ax.axhline(y=1, color='gray', ls='--', lw=0.6, alpha=0.7)
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2,10)*0.1))
    _style.add_legend(ax)

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Spider_PM.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：Pearce (2008) Th/Yb vs Nb/Yb
# ────────────────────────────────────────────────────────────

def plot_pearce_2008(gd, out_dir=None, save=True):
    """
    Th/Yb vs Nb/Yb 源区判别图（Pearce, 2008）🔥基性岩

    核心原理：Th-Nb 地壳输入替代指标。
    - 大洋玄武岩（MORB、OIB、大洋高原）几乎全部落于 MORB-OIB 阵列内
    - 受地壳混染或俯冲影响的样品会偏离阵列向上（高 Th/Yb）
    - N-MORB/E-MORB/OIB 三个参考点标记典型大洋端元
    - 火山弧及地壳混染玄武岩位于阵列上方

    底图参数来自 GCDkit 6.3.0 Diaries/Geotectonic/PearceNbThYb.r
    N-MORB, E-MORB, OIB 来自 Sun & McDonough 1989 (GCDkit reservoirs.data)

    关键参考：Pearce (2008) Lithos Fig. 2a; Pearce (2014) Elements Fig. 5a

    所需元素: Th, Nb, Yb
    """
    missing = gd.check_elements('Th', 'Nb', 'Yb', strict=True)
    if missing:
        return None, None
    th = gd.get('Th'); nb = gd.get('Nb'); yb = gd.get('Yb')
    labels = gd.labels

    th_yb = np.full_like(th, np.nan, dtype=float)
    nb_yb = np.full_like(nb, np.nan, dtype=float)
    mask = (yb > 0) & ~np.isnan(yb)
    th_yb[mask] = th[mask] / yb[mask]
    nb_yb[mask] = nb[mask] / yb[mask]

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 坐标范围 (from GCDkit) ──
    xlim = (0.1, 100)
    ylim = (0.01, 10)

    # ── MORB-OIB 阵列（来自 GCDkit PearceNbThYb.r）──
    # 斜率: b = (log10(10)-log10(1.2)) / (log10(0.8)-log10(0.1))
    b = (np.log10(10) - np.log10(1.2)) / (np.log10(0.8) - np.log10(0.1))
    # 截距(log空间): a = log10(10) - b * log10(0.8)
    a_intercept = np.log10(10) - b * np.log10(0.8)
    # y = 10^a * x^b
    x_line = np.logspace(np.log10(0.1), np.log10(100), 500)
    y_line = 10 ** a_intercept * (x_line ** b)

    # 背景多边形 (from GCDkit polygon1)
    fill_x = [0.1, 0.3, 100, 100, 80, 0.1]
    fill_y = [0.01, 0.01, 4.8, 10, 10, 0.01]
    ax.fill(fill_x, fill_y, color='#B0D4F1', alpha=0.35, zorder=1)

    # MORB-OIB 阵列虚线
    ax.plot(x_line, y_line, '--', color='gray', linewidth=1.5, zorder=3)

    # ── 标签 ──
    ax.text(0.15, 1, 'Volcanic arc array', fontsize=10, color='gray',
            rotation=42, ha='left', va='bottom', rotation_mode='anchor', zorder=5)
    ax.text(7, 0.5, 'MORB-OIB array', fontsize=10, color='gray',
            rotation=42, ha='left', va='bottom', rotation_mode='anchor', zorder=5)

    # ── 参考点（Sun & McDonough 1989，ppm 原始值来自 GCDkit reservoirs.data）──
    # N-MORB: Nb=2.33, Th=0.12, Yb=3.05 → Nb/Yb=0.764, Th/Yb=0.0393
    # E-MORB: Nb=8.3,  Th=0.6,  Yb=2.37 → Nb/Yb=3.502, Th/Yb=0.2532
    # OIB:    Nb=48,   Th=4,    Yb=2.16 → Nb/Yb=22.222, Th/Yb=1.852

    reservoirs = {
        'N-MORB':  {'nb_yb': 2.33 / 3.05,   'th_yb': 0.12 / 3.05,   'color': '#2196F3'},
        'E-MORB':  {'nb_yb': 8.3  / 2.37,   'th_yb': 0.6  / 2.37,   'color': '#FF9800'},
        'OIB':     {'nb_yb': 48   / 2.16,   'th_yb': 4    / 2.16,   'color': '#F44336'},
    }

    for name, v in reservoirs.items():
        ax.scatter([v['nb_yb']], [v['th_yb']], marker='s', s=80,
                   color=v['color'], edgecolors='black', linewidths=0.8,
                   zorder=10)
        offset_x, offset_y = 1.2, 1.2
        if name == 'N-MORB':
            offset_x, offset_y = 0.65, 1.35
        ax.text(v['nb_yb'] * offset_x, v['th_yb'] * offset_y, name,
                fontsize=9, fontweight='bold', color=v['color'],
                va='bottom', ha='left', zorder=11)

    # ── 投点 ──
    _style.scatter_samples(ax, nb_yb, th_yb, labels, groups=gd.groups)
    _style.add_legend(ax)

    # ── 坐标轴 ──
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xticks([0.1, 1, 10, 100])
    ax.set_xticklabels(['0.1', '1', '10', '100'])
    ax.set_yticks([0.01, 0.1, 1, 10])
    ax.set_yticklabels(['0.01', '0.1', '1', '10'])

    _style.style_ax(ax, 'Nb/Yb', 'Th/Yb')

    # 去除网格线（源区图不要网格）
    ax.grid(False)

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce2008_ThYb_NbYb.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：U/Th vs Zr/Nb (Stern et al., 2006)
# ────────────────────────────────────────────────────────────

def plot_u_th_zr_nb(gd, out_dir=None, save=True):
    """
    U/Th vs Zr/Nb 源区判别图（Stern et al., 2006）

    区分沉积物熔体交代 vs 流体交代的源区。
    高 Zr/Nb + 低 U/Th → 沉积物熔体；低 Zr/Nb + 高 U/Th → 流体交代。

    所需元素: U, Th, Zr, Nb
    """
    missing = gd.check_elements('U', 'Th', 'Zr', 'Nb', strict=True)
    if missing:
        return None, None
    u = gd.get('U'); th = gd.get('Th')
    zr = gd.get('Zr'); nb = gd.get('Nb')
    labels = gd.labels

    u_th = np.full_like(u, np.nan, dtype=float)
    zr_nb = np.full_like(zr, np.nan, dtype=float)
    mask1 = (th > 0) & ~np.isnan(th) & ~np.isnan(u)
    mask2 = (nb > 0) & ~np.isnan(nb) & ~np.isnan(zr)
    u_th[mask1] = u[mask1] / th[mask1]
    zr_nb[mask2] = zr[mask2] / nb[mask2]

    fig, ax = plt.subplots(figsize=(8, 7))

    # 参考线：通常沉积物熔体 vs 流体轨迹
    # 大致分界线：U/Th ≈ 0.25（最简单的划分）
    ax.axhline(y=0.25, color='#888888', lw=0.8, ls='--')
    ax.text(0.3, 0.35, 'Fluid-related\nmetasomatism', fontsize=8, ha='center', va='center',
            fontstyle='italic', color='#888888', fontproperties=_style.times_prop)
    ax.text(20, 0.07, 'Sediment melt\nmetasomatism', fontsize=8, ha='center', va='center',
            fontstyle='italic', color='#888888', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, zr_nb, u_th, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0.1, 50)
    ax.set_ylim(0.02, 1.5)
    _style.style_ax(ax, 'Zr/Nb', 'U/Th')
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'UTh_ZrNb_Stern2006.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：Th/Yb vs Ta/Yb (Pearce, 1983)
# ────────────────────────────────────────────────────────────

def plot_pearce_1983(gd, out_dir=None, save=True):
    """
    Th/Yb vs Ta/Yb 构造环境判别图（Pearce, 1983）

    区分：MORB / 板内碱性 / 板内拉斑 / 钙碱性玄武岩 / 钾玄岩。
    与 Pearce (2008) Th/Yb-Nb/Yb 互补。

    所需元素: Th, Ta, Yb
    """
    missing = gd.check_elements('Th', 'Ta', 'Yb', strict=True)
    if missing:
        return None, None
    th = gd.get('Th'); ta = gd.get('Ta'); yb = gd.get('Yb')
    labels = gd.labels

    th_yb = np.full_like(th, np.nan, dtype=float)
    ta_yb = np.full_like(ta, np.nan, dtype=float)
    mask = (yb > 0) & ~np.isnan(yb)
    th_yb[mask] = th[mask] / yb[mask]
    ta_yb[mask] = ta[mask] / yb[mask]

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 分区边界（Pearce, 1983 Fig.3）──
    # 坐标从原文 log-log 图读取
    # 板内 vb（碱性）+ 板内 tb（拉斑）/ CAB / SHO / MORB 边界
    # 边界1: 对角线 MORB-CAB-SHO（从下到上）——约 Th/Yb = 1.5 * (Ta/Yb)^1.2
    # 边界2: 板内/ MORB — Th/Yb ≈ 0.2 水平线
    # 边界3: 板内碱性/拉斑 — 垂线 Ta/Yb ≈ 1.5

    # MORB 场（左下半）
    ax.axhline(y=0.2, xmin=0, xmax=0.2, color='#888888', lw=0.8)
    # CAB 斜线（从 MORB 右上边界开始）
    th_vals = np.logspace(np.log10(0.01), np.log10(1.5), 30)
    ta_arr = 0.8 * th_vals**0.85  # 近似 CALB 边界
    ax.loglog(ta_arr, th_vals, color='#888888', lw=1.0)
    # SHO 上界
    th_vals2 = np.logspace(np.log10(0.05), np.log10(5), 30)
    ta_arr2 = 0.3 * th_vals2**0.85
    ax.loglog(ta_arr2, th_vals2, color='#888888', lw=1.0)

    # 场标注
    ax.text(0.04, 0.05, 'MORB', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(0.1, 0.5, 'CAB', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(0.5, 0.3, 'WPB\n(tholeiitic)', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    # WPB (alkaline) 标注 — 用正确坐标
    ax.text(1.5, 1.5, 'WPB\n(alkaline)', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(0.1, 1.8, 'SHO', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, ta_yb, th_yb, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0.01, 5)
    ax.set_ylim(0.01, 10)
    _style.style_ax(ax, 'Ta/Yb', 'Th/Yb')
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'ThYb_TaYb_Pearce1983.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：(Sm/Yb)PM vs (La/Sm)PM (Li et al., 2016)
# ────────────────────────────────────────────────────────────

def plot_sm_yb_la_sm(gd, out_dir=None, save=True):
    """
    (Sm/Yb)PM vs (La/Sm)PM 部分熔融模拟图（Li et al., 2016）

    区分尖晶石 vs 石榴石橄榄岩��区，估算部分熔融程度。
    含尖晶石橄榄岩和石榴石橄榄岩的理论熔融曲线。

    所需元素: La, Sm, Yb
    """
    missing = gd.check_elements('La', 'Sm', 'Yb', strict=True)
    if missing:
        return None, None
    la = gd.get('La'); sm = gd.get('Sm'); yb = gd.get('Yb')
    labels = gd.labels

    from igneous_wr.core.normalize import PRIMITIVE_MANTLE
    pm_la = PRIMITIVE_MANTLE.get('La', 0.687)
    pm_sm = PRIMITIVE_MANTLE.get('Sm', 0.444)
    pm_yb = PRIMITIVE_MANTLE.get('Yb', 0.493)

    la_sm_pm = np.full_like(la, np.nan, dtype=float)
    sm_yb_pm = np.full_like(sm, np.nan, dtype=float)
    mask = (sm > 0) & ~np.isnan(sm) & ~np.isnan(la) & ~np.isnan(yb)
    la_sm_pm[mask] = (la[mask] / pm_la) / (sm[mask] / pm_sm)
    sm_yb_pm[mask] = (sm[mask] / pm_sm) / (yb[mask] / pm_yb)

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 尖晶石橄榄岩熔融曲线 ──
    # 参考 Li et al. (2016) — D 值和模式配分
    # 尖晶石 lherzolite: ol:0.53, opx:0.27, cpx:0.17, sp:0.03
    # 石榴石 lherzolite: ol:0.60, opx:0.20, cpx:0.10, gt:0.10
    # 非模态熔融，平均 D 值
    # 这里用近似曲线：目视坐标从 Li et al. (2016) Fig.6 读取
    # 尖晶石曲线：La/Sm 变化较小，Sm/Yb 较平坦
    F_vals = np.array([0.25, 0.15, 0.10, 0.07, 0.05, 0.03, 0.01, 0.005])
    # 尖晶石橄榄岩熔体 (La/Sm)PM, (Sm/Yb)PM
    sp_la_sm = np.array([0.8, 1.0, 1.2, 1.4, 1.8, 2.6, 5.5, 9.0])
    sp_sm_yb = np.array([0.7, 0.8, 0.9, 1.0, 1.1, 1.3, 1.8, 2.2])
    # 石榴石橄榄岩熔体 (La/Sm)PM, (Sm/Yb)PM
    gt_la_sm = np.array([1.2, 1.5, 1.9, 2.4, 3.0, 4.2, 8.0, 12])
    gt_sm_yb = np.array([0.6, 0.8, 1.0, 1.6, 2.4, 4.0, 18, 35])

    # 用更干净的目视坐标
    ax.loglog(sp_la_sm, sp_sm_yb, 'o-', color='#559955', lw=1.5, ms=3,
              label='Spinel lherzolite')
    ax.loglog(gt_la_sm, gt_sm_yb, 's-', color='#995555', lw=1.5, ms=3,
              label='Garnet lherzolite')

    # F 值标注 — 关键处标注 F 值
    # 只在选定的点标注
    annotate_idx = [0, 3, 6]  # F=25%, 7%, 1%
    for i in annotate_idx:
        ax.annotate(f'F={F_vals[i]:.0%}', (sp_la_sm[i], sp_sm_yb[i]),
                   fontsize=7, color='#559955',
                   textcoords='offset points', xytext=(4, 4),
                   fontproperties=_style.times_prop)
        ax.annotate(f'F={F_vals[i]:.0%}', (gt_la_sm[i], gt_sm_yb[i]),
                   fontsize=7, color='#995555',
                   textcoords='offset points', xytext=(4, 4),
                   fontproperties=_style.times_prop)

    # 标注源区端元
    ax.text(0.2, 0.08, 'PM', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#888888', fontproperties=_style.times_prop)
    ax.scatter([1], [1], marker='+', s=40, color='#888888', zorder=0)

    _style.scatter_samples(ax, la_sm_pm, sm_yb_pm, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0.3, 20)
    ax.set_ylim(0.1, 50)
    _style.style_ax(ax, '(La/Sm)PM', '(Sm/Yb)PM')
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'SmYb_LaSm_partial_melting.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：Sc vs V (Hickey-Vargas et al., 2018)
# ────────────────────────────────────────────────────────────

def plot_sc_v(gd, out_dir=None, save=True):
    """
    Sc vs V 俯冲氧化条件判别图（Hickey-Vargas et al., 2018）

    区分 FAB、玻安岩、MORB 等弧前岩浆系列的氧化条件。
    俯冲起始时板片流体使地幔楔氧化 → V/Sc 和 Ti/V 升高。
    FAB 的 V ≈ 250–450 ppm, Sc ≈ 40–60
    玻安岩的 V ≈ 120–300 ppm, Sc ≈ 20–40
    DMM 的 V ≈ 80 ppm, Sc ≈ 15

    所需元素: Sc, V
    """
    missing = gd.check_elements('Sc', 'V', strict=True)
    if missing:
        return None, None
    sc = gd.get('Sc'); v = gd.get('V')
    labels = gd.labels

    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 参考场 ──
    # DMM 点
    ax.scatter([15], [80], marker='*', s=100, color='#4488CC', zorder=5, label='DMM')
    ax.text(16, 75, 'DMM', fontsize=8, fontstyle='italic', color='#4488CC',
            fontproperties=_style.times_prop)

    # FAB 场（Mariana FABs）
    fab_rect = patches.Rectangle((35, 230), 30, 250,
                                 linewidth=0, facecolor='#CC8844', alpha=0.15, zorder=0)
    ax.add_patch(fab_rect)
    ax.text(45, 260, 'Mariana\nFABs', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#CC8844', fontproperties=_style.times_prop)

    # 玻安岩场
    bon_rect = patches.Rectangle((18, 100), 25, 140,
                                 linewidth=0, facecolor='#CC5555', alpha=0.15, zorder=0)
    ax.add_patch(bon_rect)
    ax.text(30, 170, 'Boninites', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#CC5555', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, sc, v, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0, 80)
    ax.set_ylim(0, 600)
    _style.style_ax(ax, 'Sc (ppm)', 'V (ppm)')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Sc_V_HickeyVargas2018.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：Ba/Th vs La/Sm (Pearce & Robinson, 2010)
# ────────────────────────────────────────────────────────────

def plot_ba_th_la_sm(gd, out_dir=None, save=True):
    """
    Ba/Th vs La/Sm 板片流体 vs 沉积物熔体判别图（Pearce & Robinson, 2010）

    区分俯冲带中板片流体交代 vs 沉积物熔体交代的贡献。
    - 高 Ba/Th + 低 La/Sm → 流体主导（Ba 在流体中高度活动）
    - 低 Ba/Th + 高 La/Sm → 沉积物熔体主导
    - MORB 背景值：Ba/Th ≈ 50, La/Sm ≈ 2

    所需元素: Ba, Th, La, Sm
    """
    missing = gd.check_elements('Ba', 'Th', 'La', 'Sm', strict=True)
    if missing:
        return None, None
    ba = gd.get('Ba'); th = gd.get('Th')
    la = gd.get('La'); sm = gd.get('Sm')
    labels = gd.labels

    ba_th = np.full_like(ba, np.nan, dtype=float)
    la_sm = np.full_like(la, np.nan, dtype=float)
    mask1 = (th > 0) & ~np.isnan(th) & ~np.isnan(ba)
    mask2 = (sm > 0) & ~np.isnan(sm) & ~np.isnan(la)
    ba_th[mask1] = ba[mask1] / th[mask1]
    la_sm[mask2] = la[mask2] / sm[mask2]

    fig, ax = plt.subplots(figsize=(8, 7))

    # MORB 参考点
    ax.scatter([2], [50], marker='*', s=80, color='#4488CC', zorder=5, label='MORB')
    ax.text(2.3, 40, 'MORB', fontsize=8, fontstyle='italic', color='#4488CC',
            fontproperties=_style.times_prop)

    # 流体主导区（高 Ba/Th）
    ax.axhline(y=150, color='#888888', lw=0.8, ls='--')
    ax.text(1, 180, 'Fluid-dominated\nmetasomatism', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#888888', fontproperties=_style.times_prop)

    # 熔体主导区（高 La/Sm）
    ax.axvline(x=5, color='#888888', lw=0.8, ls='--')
    ax.text(7, 60, 'Sediment melt\nmetasomatism', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#888888', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, la_sm, ba_th, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0.5, 15)
    ax.set_ylim(5, 800)
    _style.style_ax(ax, 'La/Sm', 'Ba/Th')
    ax.set_xscale('log')
    ax.set_yscale('log')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'BaTh_LaSm_PearceRobinson2010.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 构造判别：Zr/Y vs Zr 岛弧 vs 大陆弧 (Xia, 2014)
# ────────────────────────────────────────────────────────────

def plot_zr_y_zr(gd, out_dir=None, save=True):
    """
    Zr/Y vs Zr 岛弧 vs 大陆弧判别图（Xia, 2014 汇总）

    区分岛弧玄武岩（IAB）和活动大陆边缘弧玄武岩（ACMAB）：
    - 岛弧（IAB）：Zr < 130 ppm, Zr/Y < 3.3
    - 大陆弧（ACMAB）：Zr > 70 ppm, Zr/Y > 3.4
    简单实用，配合 Th/Yb-Ta/Yb 使用效果更佳。

    所需元素: Zr, Y
    """
    missing = gd.check_elements('Zr', 'Y', strict=True)
    if missing:
        return None, None
    zr = gd.get('Zr'); y = gd.get('Y')
    labels = gd.labels

    zr_y = np.full_like(zr, np.nan, dtype=float)
    mask = (y > 0) & ~np.isnan(y) & ~np.isnan(zr)
    zr_y[mask] = zr[mask] / y[mask]

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 分区边界 ──
    # IAB 区：Zr < 130, Zr/Y < 3.3
    # ACMAB 区：Zr > 70, Zr/Y > 3.4
    # 两者之间存在重叠过渡区

    # 水平边界 Zr/Y = 3.3
    ax.axhline(y=3.3, color='#888888', lw=0.8, ls='--')
    # 垂直边界 Zr = 130
    ax.axvline(x=130, color='#888888', lw=0.8, ls='--')

    # 场标注
    ax.text(30, 1.5, 'IAB\n(Island arc)', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(300, 6, 'ACMAB\n(Active continental\nmargin arc)', fontsize=10, ha='center', va='center',
            fontstyle='italic', color='#666666', fontproperties=_style.times_prop)
    ax.text(80, 4.5, 'Transition', fontsize=9, ha='center', va='center',
            fontstyle='italic', color='#888888', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, zr, zr_y, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0, 300)
    ax.set_ylim(0, 10)
    _style.style_ax(ax, 'Zr (ppm)', 'Zr/Y')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'ZrY_Zr_Xia2014.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区：Gd/Yb vs Dy/Dy* 稀土分馏模式 (Davidson 2013)
# ────────────────────────────────────────────────────────────

def plot_gdyb_dydystar(gd, out_dir=None, save=True):
    """
    Gd/Yb vs Dy/Dy* 稀土分馏模式图 📊通用
    Davidson et al. (2013, Nature Geoscience)

    Dy/Dy* 是 Dy 相对于相邻中稀土（Tb–Ho）的异常指标：
      Dy/Dy* = Dy_N / (La_N^(4/7) * Yb_N^(3/7))  或等价按位置比例
    此处实现 Davidson 原式：
      Dy/Dy* = Dy_N / (Tb_N^(1/3) * Ho_N^(2/3))
    更简单的近似：Dy/Dy* = Dy_N / (Tb_N * Ho_N)^0.5

    解释：
    - 高 Gd/Yb + 高 Dy/Dy* → 平坦配分，浅部源区
    - 低 Gd/Yb + 低 Dy/Dy* → 陡峭HREE配分，深部源区（含石榴石）
    - Dy/Dy* < 1 → 中稀土亏损（角闪石/榍石残留）
      Dy/Dy* > 1 → 中稀土富集（石榴石残留，HREE强烈分馏）

    所需元素: La, Tb, Dy, Ho, Yb
    """
    missing = gd.check_elements('La', 'Tb', 'Dy', 'Ho', 'Yb', strict=True)
    if missing:
        return None, None

    la = gd.get('La'); tb = gd.get('Tb'); dy = gd.get('Dy')
    ho = gd.get('Ho'); yb = gd.get('Yb')
    labels = gd.labels

    # 球粒陨石标准化
    from igneous_wr.core.normalize import CHONDRITE
    la_n = la / CHONDRITE.get('La', 0.237)
    tb_n = tb / CHONDRITE.get('Tb', 0.058)
    dy_n = dy / CHONDRITE.get('Dy', 0.4)
    ho_n = ho / CHONDRITE.get('Ho', 0.088)
    yb_n = yb / CHONDRITE.get('Yb', 0.24)

    # Gd/Yb_N
    gd_norm = gd.get('Gd') / CHONDRITE.get('Gd', 0.25)
    with np.errstate(divide='ignore', invalid='ignore'):
        gdyb = gd_norm / yb_n
        # Dy/Dy* = Dy_N / (Tb_N * Ho_N)^0.5  (Davidson 2013)
        dydystar = dy_n / np.sqrt(tb_n * ho_n)

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 参考线 ──
    # Dy/Dy* = 1 基准线
    ax.axhline(y=1.0, color='#888888', lw=0.6, ls=':', alpha=0.6)
    ax.text(0.35, 0.93, 'MREE depleted\\n(amphibole/titanite residue)', fontsize=8,
            ha='center', va='top', fontstyle='italic', color='#888888',
            fontproperties=_style.times_prop, alpha=0.7)
    ax.text(3.5, 1.07, 'MREE enriched\\n(garnet residue)', fontsize=8,
            ha='center', va='bottom', fontstyle='italic', color='#888888',
            fontproperties=_style.times_prop, alpha=0.7)

    # 等比例混合趋势线（示意）
    trend_x = np.array([0.2, 0.5, 1.0, 2.0, 4.0, 10.0])
    trend_y = 1.0 + 0.15 * np.log(trend_x / 0.5)
    ax.plot(trend_x, trend_y, color='#aaaaaa', lw=0.5, ls='--', alpha=0.5)

    _style.scatter_samples(ax, gdyb, dydystar, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xscale('log')
    ax.set_xlim(0.15, 50)
    ax.set_ylim(0.4, 2.0)
    _style.style_ax(ax, '(Gd/Yb)$_N$', 'Dy/Dy* (Davidson, 2013)')

    import matplotlib.ticker as mticker
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.1f}'))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'GdYb_DyDystar_Davidson2013.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区：Dy/Yb vs La/Yb 石榴石源区深度判别 (Zhang, 2018)
# ────────────────────────────────────────────────────────────

def plot_dyyb_layb(gd, out_dir=None, save=True):
    """
    Dy/Yb vs La/Yb 石榴石源区深度判别图 📊通用
    Zhang et al. (2018, Earth-Science Reviews) / Shaw (1972)

    La/Yb 比值主要受部分熔融程度控制（轻稀土高度不相容，熔融程度越低La/Yb越高）。
    Dy/Yb 比值主要受残留相矿物组合控制：石榴子石强烈富集重稀土，因此含石榴
    子石残留时的熔体拥有低的 Dy/Yb。角闪石/单斜辉石残留时 Dy/Yb 较高。

    解释（Schmidt & Jagoutz, 2017 整理）：
    - Dy/Yb > 2.5: 石榴石残留，深部高压熔融 (>1.5 GPa)
    - Dy/Yb 1.5–2.5: 混合源区（石榴石+尖晶石过渡带）
    - Dy/Yb < 1.5: 尖晶石残留，浅部低压熔融 (<1.0 GPa)

    所需元素: La, Dy, Yb
    """
    missing = gd.check_elements('La', 'Dy', 'Yb', strict=True)
    if missing:
        return None, None

    la = gd.get('La'); dy = gd.get('Dy'); yb = gd.get('Yb')
    labels = gd.labels

    with np.errstate(divide='ignore', invalid='ignore'):
        layb = la / yb
        dyyb = dy / yb

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 分区界限 ──
    # Dy/Yb = 1.5（尖晶石/石榴石过渡下限）
    ax.axhline(y=1.5, color='#888888', lw=0.8, ls='--')
    ax.axhspan(ymin=0, ymax=1.5, alpha=0.04, color='#ddaa00')
    # Dy/Yb = 2.5（石榴岩域上限）
    ax.axhline(y=2.5, color='#888888', lw=0.8, ls='--')
    ax.axhspan(ymin=2.5, ymax=10, alpha=0.04, color='#cc6644')

    # 场标注
    ax.annotate('Spinel lherzolite\\n(<1.0 GPa)', xy=(0.4, 0.08),
                xycoords='axes fraction', fontsize=9, ha='center', va='bottom',
                fontstyle='italic', color='#aa8800', fontproperties=_style.times_prop)
    ax.annotate('Garnet lherzolite\\n(>1.5 GPa)', xy=(0.4, 0.92),
                xycoords='axes fraction', fontsize=9, ha='center', va='top',
                fontstyle='italic', color='#bb5533', fontproperties=_style.times_prop)
    ax.annotate('Garnet+Spinel\\ntransition', xy=(0.5, 0.46),
                xycoords='axes fraction', fontsize=8, ha='center', va='center',
                fontstyle='italic', color='#888888', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, layb, dyyb, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xscale('log')
    max_layb = np.nanmax(layb) * 1.3 if not np.all(np.isnan(layb)) else 10
    min_layb = np.nanmin(layb) * 0.7 if not np.all(np.isnan(layb)) else 1
    ax.set_xlim(min_layb, max_layb)
    ax.set_ylim(0, max(4.0, np.nanmax(dyyb)*1.2))

    import matplotlib.ticker as mticker
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}'))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())

    _style.style_ax(ax, 'La/Yb', 'Dy/Yb')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'DyYb_LaYb_garnet_depth.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# 🔬 源区判别：Nb/La vs Th/La (Cabanis & Lemelle, 1986)
# ────────────────────────────────────────────────────────────

def plot_nb_la_th_la(gd, out_dir=None, save=True):
    """
    Nb/La vs Th/La 构造判别图 🔥基性岩

    用不相容元素比值区分不同构造背景：
    - OIB (洋岛玄武岩): 高 Nb/La (>0.8~1.0), 低-中 Th/La (0.05~0.15)
    - N-MORB (正常洋中脊): 高 Nb/La (>0.8), 低 Th/La (<0.08)
    - E-MORB (富集洋中脊): 中 Nb/La (0.5~1.0), 中 Th/La (0.08~0.15)
    - IAB (岛弧玄武岩): 低 Nb/La (<0.5), 高 Th/La (>0.15)

    参考: Cabanis & Lemelle (1986), Condie (2005), Wang et al. (2015)

    所需元素: Nb, Th, La
    """
    missing = gd.check_elements('Nb', 'Th', 'La', strict=True)
    if missing:
        return None, None
    nb = gd.get('Nb'); th = gd.get('Th'); la = gd.get('La')
    labels = gd.labels

    nb_la = np.full_like(nb, np.nan, dtype=float)
    th_la = np.full_like(th, np.nan, dtype=float)
    mask = (la > 0) & ~np.isnan(la)
    nb_la[mask] = nb[mask] / la[mask]
    th_la[mask] = th[mask] / la[mask]

    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 场界 ──
    # IAB 区: Nb/La < 0.5, Th/La > 0.15
    ax.axvline(x=0.5, color='#888888', lw=0.8, ls='--')
    ax.axhline(y=0.15, color='#888888', lw=0.8, ls='--')
    # MORB-OIB 与地壳混染的分界（大致 Th/La = 0.2）
    ax.axhline(y=0.2, color='#aaaaaa', lw=0.5, ls=':')

    # N-MORB 框
    ax.axvspan(0.8, 1.8, ymin=0, ymax=0.146, alpha=0.06, color='#4488cc')
    # OIB 框
    ax.axvspan(0.8, 2.5, ymin=0.146, ymax=0.26, alpha=0.06, color='#dd8844')
    # E-MORB 框
    ax.axvspan(0.5, 1.2, ymin=0.08/0.3, ymax=0.146, alpha=0.06, color='#88aa44')
    # IAB 框
    ax.axvspan(0, 0.5, ymin=0.146, ymax=1.0, alpha=0.06, color='#cc6644')

    # 场标注
    ax.text(0.08, 0.22, 'IAB (Island Arc\\nBasalt)', fontsize=8, ha='left', va='center',
            fontstyle='italic', color='#bb5544', fontproperties=_style.times_prop)
    ax.text(0.08, 0.06, 'N-MORB', fontsize=8, ha='left', va='center',
            fontstyle='italic', color='#3377bb', fontproperties=_style.times_prop)
    ax.text(1.2, 0.06, 'OIB (Ocean Island\\nBasalt)', fontsize=8, ha='left', va='center',
            fontstyle='italic', color='#cc7733', fontproperties=_style.times_prop)
    ax.text(1.0, 0.11, 'E-MORB', fontsize=8, ha='center', va='center',
            fontstyle='italic', color='#779933', fontproperties=_style.times_prop)
    ax.text(1.0, 0.21, 'Crustal\\nContamination', fontsize=7, ha='center', va='center',
            fontstyle='italic', color='#999999', fontproperties=_style.times_prop)

    _style.scatter_samples(ax, nb_la, th_la, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(0, 3.0)
    ax.set_ylim(0, 0.3)
    _style.style_ax(ax, 'Nb/La', 'Th/La')

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'NbLa_ThLa_Cabanis1986.png', out_dir)
    return fig, ax


def plot_pearcenbthyb(gd, out_dir=None, save=True):
    """Pearce (1995) Nb/Yb vs Th/Yb + Th vs Nb (2in1 panel)
    所需元素: Nb, Th, Yb
    """
    missing = gd.check_elements('Nb', 'Th', 'Yb', strict=True)
    if missing:
        return None, None
    nb = gd.get('Nb'); th = gd.get('Th'); yb = gd.get('Yb')
    labels = gd.labels
    nb_yb = np.where(yb > 0, nb / yb, np.nan)
    th_yb = np.where(yb > 0, th / yb, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.plot([0.01, 50], [0.01*0.1, 50*0.1], 'k-', lw=1.5, label='N-MORB')
    ax.plot([0.01, 50], [0.01*0.4, 50*0.4], 'k--', lw=0.8, label='E-MORB')
    ax.plot([0.01, 50], [0.01*1.0, 50*1.0], 'k:', lw=0.8, label='OIB')

    _style.scatter_samples(ax, nb_yb, th_yb, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(0.01, 50); ax.set_ylim(0.001, 10)
    _style.style_ax(ax, 'Nb/Yb', 'Th/Yb')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1995_NbYb_ThYb.png', out_dir)
    return fig, ax


# ── Pearce Nb-Ti-Yb ──────────────────────────────────────


def plot_pearcenbtiyb(gd, out_dir=None, save=True):
    """Pearce (1995) Ti/Yb vs Nb/Yb 判别图
    所需元素: Ti, Nb, Yb
    """
    missing = gd.check_elements('Ti', 'Nb', 'Yb', strict=True)
    if missing:
        return None, None
    ti = gd.get('Ti'); nb = gd.get('Nb'); yb = gd.get('Yb')
    labels = gd.labels
    ti_yb = np.where(yb > 0, ti / yb, np.nan)
    nb_yb = np.where(yb > 0, nb / yb, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    # MORB-OIB 趋势线
    xs = np.logspace(np.log10(0.01), np.log10(50), 50)
    ax.plot(xs, 800 * xs, 'k-', lw=1.5, label='MORB-OIB array')
    ax.plot(xs, 800 * xs * 0.5, 'k--', lw=0.8, label='×0.5')
    ax.plot(xs, 800 * xs * 2, 'k--', lw=0.8, label='×2')

    # 俯冲带影响标注
    ax.fill_between([0.01, 50], [800*0.01, 800*50], [800*0.01*10, 800*50*10],
                     alpha=0.08, color='brown')

    _style.scatter_samples(ax, nb_yb, ti_yb, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(0.01, 50); ax.set_ylim(10, 100000)
    _style.style_ax(ax, 'Nb/Yb', 'Ti/Yb')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1995_TiYb_NbYb.png', out_dir)
    return fig, ax


# ════════════════════════════════════════════════════════════
# 3. 构造/演化专题图
# ════════════════════════════════════════════════════════════

# ── Frost (2001) FeO/(FeO+MgO) vs SiO₂ ─────────────────


def plot_sylvester(gd, out_dir=None, save=True):
    """Sylvester (1989) CaO/Na2O vs Al2O3 花岗岩源区判别
    所需元素: CaO, Na2O, Al2O3
    """
    missing = gd.check_elements('CaO', 'Na2O', 'Al2O3', strict=True)
    if missing:
        return None, None
    cao = gd.get('CaO'); na2o = gd.get('Na2O'); al2o3 = gd.get('Al2O3')
    labels = gd.labels
    cao_na2o = np.where(na2o > 0, cao / na2o, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    # 分界：泥质源区 vs 砂屑质源区
    ax.axhline(0.3, 0, 1, color='k', ls='--', lw=1.2)
    # 高压熔融 vs 低压熔融
    xs = np.linspace(10, 18, 30)
    ax.plot(xs, 0.05 * xs, 'k:', lw=0.8)

    ax.text(11, 0.8, 'Clay-rich\n(pelitic)', fontsize=9, ha='center', style='italic')
    ax.text(11, 0.08, 'Clay-poor\n(psammitic)', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, al2o3, cao_na2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(10, 18); ax.set_ylim(0.01, 2)
    ax.set_yscale('log')
    _style.style_ax(ax, r'Al$_2$O$_3$ (wt.%)', 'CaO/Na$_2$O')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Sylvester1989_CaONa2O_Al2O3.png', out_dir)
    return fig, ax


# ── Villaseca (1998) ASI vs FMM ───────────────────────────


def plot_layb(gd, out_dir=None, save=True):
    """La/Yb vs Yb 判别图 — 源区部分熔融趋势
    所需元素: La, Yb
    """
    missing = gd.check_elements('La', 'Yb', strict=True)
    if missing:
        return None, None
    la = gd.get('La'); yb = gd.get('Yb')
    labels = gd.labels
    la_yb = np.where(yb > 0, la / yb, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    # 部分熔融曲线示意
    ax.plot([0, 10], [20, 0], 'k-', lw=1.0, alpha=0.5)
    ax.axhline(5, 0, 1, color='k', ls='--', lw=0.8)
    ax.text(4, 8, 'Garnet-bearing\nsource', fontsize=9, ha='center', style='italic')
    ax.text(4, 2, 'Garnet-free\nsource', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, yb, la_yb, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 10); ax.set_ylim(0, 30)
    _style.style_ax(ax, 'Yb (ppm)', 'La/Yb')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'LaYb_vs_Yb.png', out_dir)
    return fig, ax


# ── Ross & Bédard (2009) 判别 ─────────────────────────────


def plot_ross(gd, out_dir=None, save=True):
    """Ross & Bédard (2009) 岩浆过程判别图
    所需元素: La, Sm, Yb
    """
    missing = gd.check_elements('La', 'Sm', 'Yb', strict=True)
    if missing:
        return None, None
    la = gd.get('La'); sm = gd.get('Sm'); yb = gd.get('Yb')
    labels = gd.labels
    la_sm = np.where(sm > 0, la / sm, np.nan)
    la_yb = np.where(yb > 0, la / yb, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.plot([0, 15], [15, 0], 'k-', lw=1.0, alpha=0.5, label='Partial melting')
    ax.text(5, 10, 'Partial\nmelting', fontsize=9, ha='center', style='italic')
    ax.text(5, 3, 'Fractional\ncrystallization', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, la_sm, la_yb, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 12); ax.set_ylim(0, 25)
    _style.style_ax(ax, 'La/Sm', 'La/Yb')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Ross2009_LaSm_LaYb.png', out_dir)
    return fig, ax

