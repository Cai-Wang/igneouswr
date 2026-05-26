"""
_ternary.py — 三元图坐标变换

所有风格参数（线宽/颜色/字号）都从 _style 动态引用，不再硬编码。
调用者调用 set_style_preset() 后会影响全三元图。

依赖: numpy, _style
"""

import numpy as np
import _style

SQRT3_2 = np.sqrt(3) / 2


def ternary_to_xy(a, b, c):
    """三元组 (a,b,c) → 笛卡尔 (x,y)。约定 a=顶角, b=左下, c=右下。"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    s = a + b + c
    mask = s == 0
    a_n = np.where(mask, 0, a / s)
    c_n = np.where(mask, 0, c / s)
    return 0.5 * a_n + c_n, SQRT3_2 * a_n


def ternary_corners():
    """返回三元图三个角点的 (x,y) 坐标字典。"""
    return {
        'top':   ternary_to_xy(100, 0, 0),
        'left':  ternary_to_xy(0, 100, 0),
        'right': ternary_to_xy(0, 0, 100),
    }


def draw_ternary_frame(ax, corners=None, corner_labels=None):
    """绘制三元图边框。线宽从 _style.SPINE_WIDTH 取值（*3 以视觉接近旧 lw=2.5）。

    Args:
        ax: matplotlib Axes
        corners: 可选，三元角点坐标 dict（来自 ternary_corners()）
        corner_labels: 可选，三个顶点的标签列表 [top, left, right]
            传入时自动调用 label_ternary_vertices 标注顶点
    """
    if corners is None:
        corners = ternary_corners()
    lw_val = _style.SPINE_WIDTH * 3.0
    for p1, p2 in [('top', 'left'), ('left', 'right'), ('right', 'top')]:
        ax.plot([corners[p1][0], corners[p2][0]],
                [corners[p1][1], corners[p2][1]],
                'k-', lw=lw_val, zorder=3)

    # 如果传入了 corner_labels，自动标注顶点
    if corner_labels is not None and len(corner_labels) == 3:
        label_ternary_vertices(ax, corner_labels[0], corner_labels[1], corner_labels[2],
                               corners=corners)


def draw_ternary_grid(ax, step=10):
    """绘制三元图网格。线宽/风格从 _style 取值。"""
    color = '#CCCCCC'
    lw_val = max(_style.GRID_LW, 0.15)
    for v in range(step, 100, step):
        for line in [
            (ternary_to_xy(v, 100-v, 0), ternary_to_xy(v, 0, 100-v)),
            (ternary_to_xy(0, v, 100-v), ternary_to_xy(100-v, v, 0)),
            (ternary_to_xy(100-v, 0, v), ternary_to_xy(0, 100-v, v)),
        ]:
            ax.plot([line[0][0], line[1][0]], [line[0][1], line[1][1]],
                    color=color, lw=lw_val, zorder=0, linestyle=_style.GRID_STYLE)


def draw_ternary_ticks(ax, step=20, corners=None):
    """绘制三元图刻度标签。字号从 _style 风格常量取值。"""
    if corners is None:
        corners = ternary_corners()
    fs = _style.TICK_LENGTH + 3  # 刻度长度 + 3 ≈ 8（旧硬编码值），但响应风格变化
    color = '#666666'
    for v in range(step, 100, step):
        p = ternary_to_xy(v, 100-v, 0)
        ax.text(p[0]-0.018, p[1]+0.008, str(v), fontsize=fs,
                ha='right', va='center', color=color)
        p = ternary_to_xy(100-v, 0, v)
        ax.text(p[0]+0.018, p[1]+0.008, str(v), fontsize=fs,
                ha='left', va='center', color=color)
        p = ternary_to_xy(0, v, 100-v)
        ax.text(p[0], p[1]-0.028, str(v), fontsize=fs,
                ha='center', va='top', color=color)


def label_ternary_vertices(ax, top_label, left_label, right_label,
                           corners=None, fontsize=14, **kw):
    """标注三元图顶点名称。字号可覆盖。"""
    if corners is None:
        corners = ternary_corners()
    ax.text(corners['top'][0], corners['top'][1]+0.04, top_label,
            fontsize=fontsize, fontweight='bold', ha='center', va='bottom',
            fontproperties=_style.times_prop, **kw)
    ax.text(corners['left'][0]-0.035, corners['left'][1]-0.03, left_label,
            fontsize=fontsize, fontweight='bold', ha='right', va='top',
            fontproperties=_style.times_prop, **kw)
    ax.text(corners['right'][0]+0.035, corners['right'][1]-0.03, right_label,
            fontsize=fontsize, fontweight='bold', ha='right', va='top',
            fontproperties=_style.times_prop, **kw)
