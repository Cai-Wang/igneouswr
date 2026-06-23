import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import igneous_wr.report.style as _style
from igneous_wr.core.ternary import ternary_to_xy, ternary_corners, draw_ternary_frame, draw_ternary_grid, draw_ternary_ticks, label_ternary_vertices
from igneous_wr.core.normalize import REE_ORDER, CHONDRITE, SPIDER_ORDER, PRIMITIVE_MANTLE, normalize
from igneous_wr.boundaries.core import load_boundary

def plot_ree(gd, ax=None, **kwargs):
    """
    REE 球粒陨石标准化配分模式图 📊通用
    所需元素: La,Ce,Pr,Nd,Sm,Eu,Gd,Tb,Dy,Ho,Er,Tm,Yb,Lu
    """
    missing = gd.check_elements('La', 'Ce', 'Nd', 'Sm', 'Yb', strict=True)
    if missing:
        return (None, None)
    gd.check_elements(*REE_ORDER)
    labels = gd.labels
    groups = gd.groups
    group_colors = _style.get_group_colors(groups)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    else:
        fig = ax.figure
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
        ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=_style.MK_SIZE_SINGLE, edgecolors=_style.MK_EDGE_COLOR, linewidths=_style.MK_EDGE_WIDTH, zorder=3)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(REE_ORDER)
    ax.set_xlim(x_pos[0] - 0.3, x_pos[-1] + 0.3)
    ax.set_yscale('log')
    # Y 轴范围根据数据自动适配
    all_valid = []
    for i in range(len(labels)):
        raw = {e: gd.get(e)[i] for e in REE_ORDER}
        normed = normalize(raw, CHONDRITE)
        all_valid.extend([normed[e] for e in REE_ORDER if not np.isnan(normed[e]) and normed[e] > 0])
    if all_valid:
        ymin = 10 ** np.floor(np.log10(min(all_valid) * 0.8))
        ymax = 10 ** np.ceil(np.log10(max(all_valid) * 1.2))
        decades = np.arange(np.log10(ymin), np.log10(ymax) + 1)
        ticks = [10 ** d for d in decades]
    else:
        ticks = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{v:g}' if v == int(v) else f'{v}' for v in ticks])
    _style.style_ax(ax, '', 'Sample/Chondrite')
    ax.axhline(y=1, color='gray', ls='-', lw=0.8, alpha=0.7)
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2, 10) * 0.1))
    # 以下设置独立出图和 figkit 拼版共用
    ax.xaxis.set_minor_locator(ticker.NullLocator())
    ax.tick_params(axis='y', rotation=90)
    for lbl in ax.get_yticklabels():
        lbl.set_verticalalignment('center')
    for tv in ticks[1:-1]:
        if abs(tv - 1.0) > 1e-10:
            ax.axhline(y=tv, color='gray', ls=(0, (4, 2)), lw=0.5, alpha=0.5)
    fmt_ticks = [f'{v:g}' if v == int(v) else f'{v}' for v in ticks]
    ax.set_yticklabels(fmt_ticks)
    fig.canvas.draw()
    return (fig, ax)


def plot_spider(gd, ax=None, **kwargs):
    """
    原始地幔标准化蛛网图 📊通用
    所需元素: Rb,Ba,Th,U,Nb,Ta,La,Ce,Pb,Pr,Nd,Sr,Sm,Zr,Hf,Eu,Ti,Gd,Tb,Dy,Ho,Y,Er,Tm,Yb,Lu
    """
    missing = gd.check_elements('Th', 'Nb', 'La', 'Ce', 'Nd', 'Sm', 'Yb', strict=True)
    if missing:
        return (None, None)
    gd.check_elements(*SPIDER_ORDER)
    labels = gd.labels
    groups = gd.groups
    group_colors = _style.get_group_colors(groups)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    else:
        fig = ax.figure
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
        ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=_style.MK_SIZE_SINGLE, edgecolors=_style.MK_EDGE_COLOR, linewidths=_style.MK_EDGE_WIDTH, zorder=3)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(SPIDER_ORDER)
    ax.set_xlim(x_pos[0] - 0.3, x_pos[-1] + 0.3)
    ax.set_yscale('log')
    # Y 轴范围根据数据自动适配
    all_valid = []
    for i in range(len(labels)):
        raw = {e: gd.get(e)[i] for e in SPIDER_ORDER}
        normed = normalize(raw, PRIMITIVE_MANTLE)
        all_valid.extend([normed[e] for e in SPIDER_ORDER if not np.isnan(normed[e]) and normed[e] > 0])
    if all_valid:
        ymin = 10 ** np.floor(np.log10(min(all_valid) * 0.8))
        ymax = 10 ** np.ceil(np.log10(max(all_valid) * 1.2))
        decades = np.arange(np.log10(ymin), np.log10(ymax) + 1)
        ticks = [10 ** d for d in decades]
    else:
        ticks = [0.001, 0.01, 0.1, 1, 10, 100, 1000]
    ax.set_yticks(ticks)
    ax.set_yticklabels([f'{v:g}' if v == int(v) else f'{v}' for v in ticks])
    _style.style_ax(ax, '', 'Sample/Primitive Mantle')
    ax.axhline(y=1, color='gray', ls='-', lw=0.8, alpha=0.7)
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2, 10) * 0.1))
    # 以下设置部分独立出图和 figkit 拼版共用
    ax.xaxis.set_minor_locator(ticker.NullLocator())
    ax.tick_params(axis='y', rotation=90)
    for lbl in ax.get_yticklabels():
        lbl.set_verticalalignment('center')
    for tv in ticks[1:-1]:
        if abs(tv - 1.0) > 1e-10:
            ax.axhline(y=tv, color='gray', ls=(0, (4, 2)), lw=0.5, alpha=0.5)
    fmt_ticks = [f'{v:g}' if v == int(v) else f'{v}' for v in ticks]
    ax.set_yticklabels(fmt_ticks)
    # X 轴刻度交替内外 + 标签偏移（两种模式都执行，需先 draw 初始化 tick）
    fig.canvas.draw()
    for i, t in enumerate(ax.xaxis.get_major_ticks()):
        t.tick1line.set_marker(3 if i % 2 else 2)
    for i, lbl in enumerate(ax.get_xticklabels()):
        if i % 2:
            lbl.set_y(-0.025)
            lbl.set_verticalalignment('top')
        else:
            lbl.set_y(0.04)
            lbl.set_verticalalignment('bottom')
    return (fig, ax)

def plot_pearce_2008(gd, out_dir=None, save=True):
    """Th/Yb vs Nb/Yb 源区判别图（Pearce, 2008）🔥基性岩
    底图数据来自 boundaries/src/pearce_2008.json
    所需元素: Th, Nb, Yb
    """
    missing = gd.check_elements('Th', 'Nb', 'Yb', strict=True)
    if missing:
        return (None, None)
    th = gd.get('Th')
    nb = gd.get('Nb')
    yb = gd.get('Yb')
    labels = gd.labels
    th_yb = np.full_like(th, np.nan, dtype=float)
    nb_yb = np.full_like(nb, np.nan, dtype=float)
    mask = (yb > 0) & ~np.isnan(yb)
    th_yb[mask] = th[mask] / yb[mask]
    nb_yb[mask] = nb[mask] / yb[mask]
    fig, ax = plt.subplots(figsize=(8, 7))
    bd = load_boundary('src', 'pearce_2008')
    ax.set_xlim(bd['axes']['xlim'])
    ax.set_ylim(bd['axes']['ylim'])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xticks(bd['axes']['xticks'])
    ax.set_xticklabels(['0.1', '1', '10', '100'])
    ax.set_yticks(bd['axes']['yticks'])
    ax.set_yticklabels(['0.01', '0.1', '1', '10'])
    for p in bd.get('polygon_fills', []):
        ax.fill(p['fill_x'], p['fill_y'], color=p['color'], alpha=p['alpha'], zorder=p.get('zorder', 1))
    arr = bd['line_annotations'][0]
    f = arr['formula']
    x_line = np.logspace(np.log10(arr['x_range'][0]), np.log10(arr['x_range'][1]), 500)
    y_line = 10 ** f['a_intercept'] * x_line ** f['b']
    ax.plot(x_line, y_line, arr['line_style'], color=arr['color'], linewidth=arr['linewidth'], zorder=arr.get('zorder', 3))
    for ann in bd.get('annotations', []):
        ax.text(ann['x'], ann['y'], ann['text'], fontsize=ann.get('fontsize', 10) * _style.base_fs(ax), color=ann.get('color', 'gray'), rotation=ann.get('rotation', 0), ha=ann.get('ha', 'left'), va=ann.get('va', 'bottom'), rotation_mode='anchor', zorder=5)
    for rp in bd.get('reference_points', []):
        ax.scatter([rp['x']], [rp['y']], marker=rp.get('marker', 's'), s=rp.get('size', 80), color=rp['color'], edgecolors='black', linewidths=0.8, zorder=10)
        ox = rp.get('offset_x', 1.2)
        oy = rp.get('offset_y', 1.2)
        ax.text(rp['x'] * ox, rp['y'] * oy, rp['name'], fontsize=9.5 * _style.base_fs(ax), fontweight='bold', color=rp['color'], va='bottom', ha='left', zorder=11)
    _style.scatter_samples(ax, nb_yb, th_yb, labels, groups=gd.groups)
    _style.style_ax(ax, bd['axes']['xlabel'], bd['axes']['ylabel'])
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce2008_ThYb_NbYb.png', out_dir)
    return (fig, ax)