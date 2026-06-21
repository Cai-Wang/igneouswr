import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator

import igneous_wr.report.style as _style
from igneous_wr.core.ternary import ternary_to_xy, ternary_corners, draw_ternary_frame, draw_ternary_ticks, label_ternary_vertices
from igneous_wr.core.normalize import REE_ORDER, CHONDRITE, SPIDER_ORDER, PRIMITIVE_MANTLE, normalize
from igneous_wr.boundaries.core import load_boundary


def plot_ree(gd, ax=None, *, linewidth=1.2, markersize=8,
             marker_edge_color=None, marker_edge_width=0, **kwargs):
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
        raise ValueError("plot_ree 需要 ax 参数。请调用方先建好画布。")
    fig = ax.figure
    x_pos = np.arange(len(REE_ORDER))
    seen_groups = set()

    # 收集所有 Y 值用于自动范围计算
    all_y = []
    for i in range(len(labels)):
        raw = {e: gd.get(e)[i] for e in REE_ORDER}
        normed = normalize(raw, CHONDRITE)
        y_vals = np.array([normed[e] if not np.isnan(normed[e]) else np.nan for e in REE_ORDER])
        valid = np.isfinite(y_vals) & (y_vals > 0)
        all_y.extend(y_vals[valid].tolist())
        g = groups[i] if i < len(groups) else labels[i]
        c = group_colors.get(g, plt.cm.tab10(i))
        label_g = g if g not in seen_groups else None
        seen_groups.add(g)
        ax.plot(x_pos[valid], y_vals[valid], color=c, lw=linewidth, zorder=2, label=label_g)
        ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=markersize,
                   edgecolors=marker_edge_color, linewidths=marker_edge_width, zorder=3)

    # Y 轴自适应范围（内容级）
    if all_y:
        ymin = 10 ** np.floor(np.log10(min(all_y) * 0.8))
        ymax = 10 ** np.ceil(np.log10(max(all_y) * 1.2))
    else:
        ymin, ymax = 0.001, 1000
    ax.set_ylim(ymin, ymax)

    # 统一轴风格（内容级）
    _style.style_ax(ax)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(REE_ORDER)
    ax.set_xlim(x_pos[0] - 0.3, x_pos[-1] + 0.3)
    ax.set_yscale('log')
    ax.set_yticks([0.001, 0.01, 0.1, 1, 10, 100, 1000])
    ax.set_yticklabels(['0.001', '0.01', '0.1', '1', '10', '100', '1000'])

    # Y 参考线 + 网格（内容级）
    ax.axhline(y=1, color='black', linewidth=0.6, zorder=1)
    yticks = ax.get_yticks()
    for tv in yticks[1:-1]:
        if not np.isclose(tv, 1.0):
            ax.axhline(y=tv, color='gray', linewidth=0.4,
                       linestyle=(0, (4, 2)), zorder=0.5)

    ax.set_xlabel('Rare Earth Elements')
    ax.set_ylabel('Chondrite-normalized')
    return (fig, ax)


def plot_spider(gd, ax=None, *, linewidth=1.2, markersize=8,
                marker_edge_color=None, marker_edge_width=0, **kwargs):
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
        raise ValueError("plot_spider 需要 ax 参数。请调用方先建好画布。")
    fig = ax.figure
    x_pos = np.arange(len(SPIDER_ORDER))
    seen_groups = set()

    # 收集所有 Y 值用于自动范围计算
    all_y = []
    for i in range(len(labels)):
        raw = {e: gd.get(e)[i] for e in SPIDER_ORDER}
        normed = normalize(raw, PRIMITIVE_MANTLE)
        y_vals = np.array([normed[e] if not np.isnan(normed[e]) else np.nan for e in SPIDER_ORDER])
        valid = np.isfinite(y_vals) & (y_vals > 0)
        all_y.extend(y_vals[valid].tolist())
        g = groups[i] if i < len(groups) else labels[i]
        c = group_colors.get(g, plt.cm.tab10(i))
        label_g = g if g not in seen_groups else None
        seen_groups.add(g)
        ax.plot(x_pos[valid], y_vals[valid], color=c, lw=linewidth, zorder=2, label=label_g)
        ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=markersize,
                   edgecolors=marker_edge_color, linewidths=marker_edge_width, zorder=3)

    # Y 轴自适应范围（内容级）
    if all_y:
        ymin = 10 ** np.floor(np.log10(min(all_y) * 0.8))
        ymax = 10 ** np.ceil(np.log10(max(all_y) * 1.2))
    else:
        ymin, ymax = 0.001, 1000
    ax.set_ylim(ymin, ymax)

    # 统一轴风格（内容级）
    _style.style_ax(ax)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(SPIDER_ORDER)
    ax.set_xlim(x_pos[0] - 0.3, x_pos[-1] + 0.3)
    ax.set_yscale('log')
    ax.set_yticks([0.001, 0.01, 0.1, 1, 10, 100, 1000])
    ax.set_yticklabels(['0.001', '0.01', '0.1', '1', '10', '100', '1000'])

    # Y 参考线 + 网格（内容级）
    ax.axhline(y=1, color='black', linewidth=0.6, zorder=1)
    yticks = ax.get_yticks()
    for tv in yticks[1:-1]:
        if not np.isclose(tv, 1.0):
            ax.axhline(y=tv, color='gray', linewidth=0.4,
                       linestyle=(0, (4, 2)), zorder=0.5)

    ax.set_xlabel('Trace Elements')
    ax.set_ylabel('Primitive-mantle normalized')
    return (fig, ax)


def plot_pearce_2008(gd, ax=None, *, linewidth=1.2, markersize=8,
                     marker_edge_color=None, marker_edge_width=0, **kwargs):
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
    if ax is None:
        raise ValueError("plot_pearce_2008 需要 ax 参数。请调用方先建好画布。")
    fig = ax.figure
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
        ax.text(ann['x'], ann['y'], ann['text'], color=ann.get('color', 'gray'), rotation=ann.get('rotation', 0), ha=ann.get('ha', 'left'), va=ann.get('va', 'bottom'), rotation_mode='anchor', zorder=5)
    for rp in bd.get('reference_points', []):
        ax.scatter([rp['x']], [rp['y']], marker=rp.get('marker', 's'), s=rp.get('size', 80), color=rp['color'], edgecolors='black', linewidths=0.8, zorder=10)
        ox = rp.get('offset_x', 1.2)
        oy = rp.get('offset_y', 1.2)
        ax.text(rp['x'] * ox, rp['y'] * oy, rp['name'], fontweight='bold', color=rp['color'], va='bottom', ha='left', zorder=11)
    _style.scatter_samples(ax, nb_yb, th_yb, labels, groups=gd.groups, s=markersize, edgecolors=marker_edge_color, linewidths=marker_edge_width)
    ax.set_xlabel(bd['axes']['xlabel'])
    ax.set_ylabel(bd['axes']['ylabel'])
    return (fig, ax)


def apply_spider_axis_style(ax):
    """蛛网图 X 轴刻度交替内外 + 标签偏移 + Y 竖排。

    位置敏感：必须在 finalize() 和 apply_format() **之后**调用。
    finalize 内部的 fig.canvas.draw() 会重建 Tick 对象，set_marker 会丢失。
    此函数是最后一次碰 Tick 对象的地方。

    用法：
        layout.finalize(pairs=[...])
        apply_format(layout, fmt)
        apply_style(layout, 'ree')
        apply_spider_axis_style(layout.get_ax('sp0'))
        apply_spider_axis_style(layout.get_ax('sp1'))
        layout.save(...)
    """
    fig = ax.figure
    fig.canvas.draw()

    # Y 竖排
    ax.tick_params(axis='y', rotation=90)
    for lbl in ax.get_yticklabels():
        lbl.set_verticalalignment('center')

    # X 轴副刻度关闭
    ax.xaxis.set_minor_locator(NullLocator())

    # X 轴刻度交替内外
    for i, t in enumerate(ax.xaxis.get_major_ticks()):
        t.tick1line.set_marker(3 if i % 2 else 2)

    # X 标签跟随刻度偏移（用 points 绝对单位，不随画布高度变化）
    from matplotlib.transforms import ScaledTranslation
    offset_inner = ScaledTranslation(0, 6/72., fig.dpi_scale_trans)   # 轴内 6pt ≈ 2.1mm
    offset_outer = ScaledTranslation(0, -4/72., fig.dpi_scale_trans)  # 轴外 4pt ≈ 1.4mm
    trans = ax.get_xaxis_transform()
    for i, lbl in enumerate(ax.get_xticklabels()):
        if i % 2:
            lbl.set_transform(trans + offset_outer)
            lbl.set_verticalalignment('top')
        else:
            lbl.set_transform(trans + offset_inner)
            lbl.set_verticalalignment('bottom')


def apply_ree_axis_style(ax):
    """REE 图 Y 竖排。

    Y 网格已放在 plot_ree 主路径（内容级）。
    此处只处理 Tick 对象级：Y 竖排。
    """
    fig = ax.figure
    fig.canvas.draw()

    # Y 竖排
    ax.tick_params(axis='y', rotation=90)
    for lbl in ax.get_yticklabels():
        lbl.set_verticalalignment('center')
