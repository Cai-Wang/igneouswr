"""
_style.py — 样式、字体、配色、投点辅助、坐标轴风格、保存

提供统一风格管理和分组着色功能：
- 风格预设系统：set_style_preset(name) 一键切换整套风格
- 分组着色：scatter_groups() 按组同色 + 合并图例
- 所有绘图函数通过 import igneous_wr.report.style as _style; _style.XXX 动态引用

用法：
    import igneous_wr.report.style as _style
    _style.set_style_preset('nature')    # 切换 Nature 期刊风格
    _style.scatter_groups(ax, x, y, labels, groups=['玄武岩','玄武岩','安山岩',...])
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


# ── 注册表短名→长名映射（由 _build_short_to_long_index() 自动从 registry 构建） ───
# 这不是硬编码表。每次首次调用 save_fig 时从 DIAGRAM_REGISTRY 自动生成。
# 避免 _SHORT_TO_LONG 与 FILENAME_MAP 双源不同步问题。
_SHORT_TO_LONG = None  # lazy init

def _build_short_to_long_index():
    """从 DIAGRAM_REGISTRY 构建短名→长名映射。"""
    from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY
    index = {}
    for d in DIAGRAM_REGISTRY:
        # d.filename 如 'CLS-01_TAS.png' → 短名 'TAS.png'
        short = d.filename.split('_', 1)[1] if '_' in d.filename else d.filename
        index[short] = d.filename
    return index


def _get_long_name(short_name):
    """由 DIAGRAM_REGISTRY 自动反查长名。找不到则返回原文件名。"""
    global _SHORT_TO_LONG
    if _SHORT_TO_LONG is None:
        _SHORT_TO_LONG = _build_short_to_long_index()
    return _SHORT_TO_LONG.get(short_name, short_name)


# ── Times New Roman 字体查找 ───────────────────────────────
def _find_times_font():
    candidates = [
        '/mnt/c/Windows/Fonts/times.ttf',
        '/mnt/c/Windows/Fonts/TIMES.TTF',
        '/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf',
        os.path.expanduser('~/.fonts/times.ttf'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

_TIMES_TTF = _find_times_font()
if _TIMES_TTF:
    fm.fontManager.addfont(_TIMES_TTF)
    times_prop = fm.FontProperties(fname=_TIMES_TTF)
    plt.rcParams.update({
        'font.family': times_prop.get_name(),
        'axes.unicode_minus': False,
    })
else:
    plt.rcParams.update({
        'font.family': 'serif',
        'axes.unicode_minus': False,
    })
    times_prop = fm.FontProperties(family='serif')


# ════════════════════════════════════════════════════════════
# 配色系统
# ════════════════════════════════════════════════════════════

# ── 调色板 ─────────────────────────────────────────────────
COLOR_PALETTES = {
    # SciencePlots 科学期刊颜色循环（Science 2018 6色推荐）
    'scienceplots': [
        '#0C5DA5', '#00B945', '#FF9500', '#FF2C00', '#845B97', '#474747',
    ],
    # 默认 10 色（Tableau 风格，当前系统默认）
    'default': [
        '#D62728', '#1F77B4', '#2CA02C', '#FF7F0E', '#9467BD',
        '#17BECF', '#8C564B', '#E377C2', '#0D4F8B', '#DAA520',
    ],
    # Nature 期刊风格（柔和、学术、低饱和度）
    'nature': [
        '#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F',
        '#8491B4', '#91D1C2', '#DC0000', '#7E6148', '#B09C85',
    ],
    # ColorBrewer 色盲友好（Set2 + Dark2 混编）
    'colorbrewer': [
        '#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854',
        '#FFD92F', '#E5C494', '#B3B3B3', '#1B9E77', '#D95F02',
    ],
    # 高对比度（黑白打印友好）
    'high_contrast': [
        '#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442',
        '#0072B2', '#D55E00', '#CC79A7', '#333333', '#999999',
    ],
    # 灰色渐变（黑白打印专用）
    'grayscale': [
        '#000000', '#333333', '#555555', '#777777', '#999999',
        '#BBBBBB', '#444444', '#666666', '#888888', '#AAAAAA',
    ],
}

# 当前活跃的调色板名
_ACTIVE_PALETTE = 'default'
_COLORS = list(COLOR_PALETTES[_ACTIVE_PALETTE])


def get_color(i):
    """按索引获取颜色（轮询当前活跃调色板）。"""
    return _COLORS[i % len(_COLORS)]


def set_palette(name):
    """切换调色板。name: 'default' | 'nature' | 'colorbrewer' | 'high_contrast' | 'grayscale'"""
    global _ACTIVE_PALETTE, _COLORS
    if name in COLOR_PALETTES:
        _ACTIVE_PALETTE = name
        _COLORS = list(COLOR_PALETTES[name])
        print(f"[_style] 调色板 → {name}")
    else:
        valid = ', '.join(COLOR_PALETTES.keys())
        print(f"[_style] ⚠️ 未知调色板: {name}，可用: {valid}")


def get_group_colors(groups):
    """
    为分组列表分配一致的颜色。

    Args:
        groups: 分组标签列表，如 ['玄武岩', '安山岩', '流纹岩', '玄武岩', ...]

    Returns:
        dict: {group_name: hex_color, ...}
    """
    unique = sorted(set(groups))
    return {g: get_color(i) for i, g in enumerate(unique)}


# ── 输出路径 ───────────────────────────────────────────────
DEFAULT_OUT_DIR = '../runs/default'      # 项目化后输出到项目 runs/
_OUT_DIR = None


def set_out_dir(path=None):
    """设置输出目录，持久化到全局变量。所有绘图函数自动使用此路径。"""
    global _OUT_DIR
    out = path or DEFAULT_OUT_DIR
    os.makedirs(out, exist_ok=True)
    _OUT_DIR = out
    return out


# ── SciencePlots 可选集成 ───────────────────────────────────
try:
    import scienceplots
    _HAS_SCIENCEPLOTS = True
except ImportError:
    _HAS_SCIENCEPLOTS = False


# ── 风格常量 ───────────────────────────────────────────────
MK_SIZE_SINGLE  = 60
MK_SIZE_TERNARY = 15
MK_MARKER       = 'o'
MK_EDGE_COLOR   = 'none'
MK_EDGE_WIDTH   = 0.0
MK_EDGE_WIDTH_T = 0.0
ANNOTATE_OFFSET = (6, 4)
ANNOTATE_FONTSIZE = 7
LEGEND_LOC      = 'upper right'
TICK_LENGTH    = 5
TICK_LENGTH_M  = 3
TICK_WIDTH     = 0.8
SPINE_WIDTH    = 0.8
GRID_LW        = 0.4
GRID_STYLE     = '--'
GRID_ALPHA     = 0.6


def set_style(**kwargs):
    """运行时覆盖风格常量。"""
    valid_keys = {
        'MK_SIZE_SINGLE', 'MK_SIZE_TERNARY',
        'MK_MARKER',
        'MK_EDGE_COLOR', 'MK_EDGE_WIDTH', 'MK_EDGE_WIDTH_T',
        'ANNOTATE_OFFSET', 'ANNOTATE_FONTSIZE', 'LEGEND_LOC',
        'TICK_LENGTH', 'TICK_LENGTH_M', 'TICK_WIDTH', 'SPINE_WIDTH', 'GRID_LW',
        'GRID_STYLE', 'GRID_ALPHA',
    }
    for k, v in kwargs.items():
        if k in valid_keys:
            globals()[k] = v
        else:
            print(f"[_style] ⚠️ 未知风格常量: {k}")


# ════════════════════════════════════════════════════════════
# 风格预设系统
# ════════════════════════════════════════════════════════════

# 预设 = {预设名: {变量名: 值, ...}}
# 变量名是字符串键，对应模块全局变量的名字
STYLE_PRESETS = {
    'science': {
        'palette': 'scienceplots',
        'MK_SIZE_SINGLE': 55,
        'MK_SIZE_TERNARY': 14,
        'MK_EDGE_COLOR': '#333333',
        'MK_EDGE_WIDTH': 0.3,
        'MK_EDGE_WIDTH_T': 0.3,
        'ANNOTATE_OFFSET': (6, 4),
        'LEGEND_LOC': 'upper right',
        'TICK_LENGTH': 3,
        'TICK_LENGTH_M': 1.5,
        'GRID_LW': 0.4,
        'GRID_STYLE': '--',
        'GRID_ALPHA': 0.5,
        'SPINE_WIDTH': 0.5,
        'use_scienceplots': True,
    },
    'nature_journal': {
        'palette': 'nature',
        'MK_SIZE_SINGLE': 55,
        'MK_SIZE_TERNARY': 13,
        'MK_EDGE_COLOR': '#333333',
        'MK_EDGE_WIDTH': 0.3,
        'ANNOTATE_OFFSET': (6, 4),
        'LEGEND_LOC': 'upper left',
        'TICK_LENGTH': 3,
        'TICK_LENGTH_M': 1.5,
        'GRID_LW': 0.2,
        'GRID_STYLE': ':',
        'GRID_ALPHA': 0.4,
        'SPINE_WIDTH': 0.5,
        'use_scienceplots': True,
        'scienceplots_style': 'nature',
    },
    'default': {
        'palette': 'default',
        'MK_SIZE_SINGLE': 60,
        'MK_SIZE_TERNARY': 15,
        'MK_EDGE_COLOR': 'none',
        'MK_EDGE_WIDTH': 0.0,
        'ANNOTATE_OFFSET': (6, 4),
        'LEGEND_LOC': 'upper right',
        'TICK_LENGTH': 5,
        'TICK_LENGTH_M': 3,
        'GRID_LW': 0.4,
        'GRID_STYLE': '--',
        'GRID_ALPHA': 0.6,
        'SPINE_WIDTH': 0.8,
    },
    'nature': {
        'palette': 'nature',
        'MK_SIZE_SINGLE': 50,
        'MK_SIZE_TERNARY': 12,
        'MK_EDGE_COLOR': '#333333',
        'MK_EDGE_WIDTH': 0.3,
        'ANNOTATE_OFFSET': (6, 4),
        'LEGEND_LOC': 'upper left',
        'TICK_LENGTH': 4,
        'TICK_LENGTH_M': 2,
        'GRID_LW': 0.2,
        'GRID_STYLE': ':',
        'GRID_ALPHA': 0.4,
        'SPINE_WIDTH': 0.6,
    },
    'lithos': {
        'palette': 'colorbrewer',
        'MK_SIZE_SINGLE': 55,
        'MK_SIZE_TERNARY': 14,
        'MK_EDGE_COLOR': 'none',
        'MK_EDGE_WIDTH': 0.0,
        'ANNOTATE_OFFSET': (5, 3),
        'LEGEND_LOC': 'lower right',
        'TICK_LENGTH': 4,
        'TICK_LENGTH_M': 2,
        'GRID_LW': 0.0,
        'GRID_STYLE': '--',
        'GRID_ALPHA': 0.0,
        'SPINE_WIDTH': 0.6,
    },
    'journal_chinese': {
        'palette': 'default',
        'MK_SIZE_SINGLE': 70,
        'MK_SIZE_TERNARY': 18,
        'MK_EDGE_COLOR': 'none',
        'MK_EDGE_WIDTH': 0.0,
        'ANNOTATE_OFFSET': (6, 4),
        'LEGEND_LOC': 'upper right',
        'TICK_LENGTH': 5,
        'TICK_LENGTH_M': 3,
        'GRID_LW': 0.3,
        'GRID_STYLE': '--',
        'GRID_ALPHA': 0.5,
        'SPINE_WIDTH': 1.0,
    },
    'high_contrast': {
        'palette': 'high_contrast',
        'MK_SIZE_SINGLE': 70,
        'MK_SIZE_TERNARY': 18,
        'MK_EDGE_COLOR': 'none',
        'MK_EDGE_WIDTH': 0.0,
        'ANNOTATE_OFFSET': (6, 4),
        'LEGEND_LOC': 'upper right',
        'TICK_LENGTH': 6,
        'TICK_LENGTH_M': 4,
        'GRID_LW': 0.5,
        'GRID_STYLE': '-',
        'GRID_ALPHA': 0.3,
        'SPINE_WIDTH': 1.2,
    },
}


def set_style_preset(name):
    """
    一键切换整套风格预设。

    可用的预设：'default', 'nature', 'lithos', 'journal_chinese', 'high_contrast'

    用法：
        import igneous_wr.report.style as _style
        _style.set_style_preset('nature')
        plot_tas(gd)  # 自动使用 nature 风格
    """
    if name not in STYLE_PRESETS:
        valid = ', '.join(STYLE_PRESETS.keys())
        print(f"[_style] ⚠️ 未知风格预设: {name}，可用: {valid}")
        return

    preset = dict(STYLE_PRESETS[name])

    # 是否启用 SciencePlots
    use_sp = preset.pop('use_scienceplots', False)
    sp_style = preset.pop('scienceplots_style', 'science')

    # 先切换调色板
    set_palette(preset.pop('palette'))

    # 再应用所有风格常量（通过 globals() 直接修改模块变量）
    for key, val in preset.items():
        globals()[key] = val

    print(f"[_style] 风格预设 → {name} ({len(STYLE_PRESETS[name])} 项)")

    # 如果要求 SciencePlots 且可用，应用之
    if use_sp and _HAS_SCIENCEPLOTS:
        try:
            plt.style.use([sp_style, 'no-latex'] if sp_style == 'science' else [sp_style])
            print(f"[_style] SciencePlots 样式已应用: {sp_style}")
        except Exception:
            pass  # scienceplots 出错不中断
    elif use_sp and not _HAS_SCIENCEPLOTS:
        print(f"[_style] ⚠️ SciencePlots 未安装，跳过（pip install SciencePlots）")


# ════════════════════════════════════════════════════════════
# 投点辅助
# ════════════════════════════════════════════════════════════

def scatter_samples(ax, x_arr, y_arr, labels, s=None, edgecolors=None, lw=None,
                    groups=None, group_colors=None, **kw):
    """
    按样品逐个 scatter，自动分色 + label。

    若传了 groups，则按分组着色，图例按组合并而非逐样品显示。
    若未传 groups（向后兼容），行为保持不变。

    Args:
        groups: 可选，每个样品所属组的标签列表
        group_colors: 可选，{group: color} 映射，None 则自动分配
    """
    if s is None: s = MK_SIZE_SINGLE
    if edgecolors is None: edgecolors = MK_EDGE_COLOR
    if lw is None: lw = MK_EDGE_WIDTH

    if groups is not None:
        # 分组模式：按组着色，合并图例
        if group_colors is None:
            group_colors = get_group_colors(groups)
        seen_groups = set()
        n = len(labels)
        do_annotate = n <= 25
        for i in range(n):
            if np.isnan(x_arr[i]) or np.isnan(y_arr[i]) or np.isinf(x_arr[i]) or np.isinf(y_arr[i]):
                continue
            g = groups[i] if i < len(groups) else '其他'
            c = group_colors.get(g, '#999999')
            label = g if g not in seen_groups else None
            seen_groups.add(g)
            ax.scatter(x_arr[i], y_arr[i], marker=MK_MARKER, color=c, s=s,
                       edgecolors=edgecolors, linewidths=lw, zorder=6,
                       label=label, **kw)
            if do_annotate:
                ax.annotate(labels[i], (x_arr[i], y_arr[i]),
                            textcoords='offset points', xytext=ANNOTATE_OFFSET,
                            fontsize=ANNOTATE_FONTSIZE, color='#333333')
    else:
        # 原始模式：每个样品单独颜色 + label
        n = len(labels)
        do_annotate = n <= 25
        for i in range(n):
            if np.isnan(x_arr[i]) or np.isnan(y_arr[i]) or np.isinf(x_arr[i]) or np.isinf(y_arr[i]):
                continue
            ax.scatter(x_arr[i], y_arr[i], marker=MK_MARKER, color=get_color(i), s=s,
                       edgecolors=edgecolors, linewidths=lw, zorder=6,
                       label=labels[i], **kw)
            if do_annotate:
                ax.annotate(labels[i], (x_arr[i], y_arr[i]),
                            textcoords='offset points', xytext=ANNOTATE_OFFSET,
                            fontsize=ANNOTATE_FONTSIZE, color='#333333')


def scatter_groups(ax, x_arr, y_arr, labels, groups, s=None, edgecolors=None, lw=None,
                   group_colors=None, **kw):
    """
    按分组着色 + 合并图例。是 scatter_samples 的分组封装。

    等价于 scatter_samples(ax, x_arr, y_arr, labels, groups=groups, ...)。

    Args:
        groups: 每个样品所属组的标���列表
        group_colors: 可选，{group: color}，None 则自动分配
    """
    scatter_samples(ax, x_arr, y_arr, labels, s=s, edgecolors=edgecolors, lw=lw,
                    groups=groups, group_colors=group_colors, **kw)


def plot_samples_ternary(ax, x_arr, y_arr, labels, ms=None,
                         groups=None, group_colors=None, **kw):
    """
    在三元图上按样品逐个 plot，自动分色 + label。

    若传了 groups，则按分组着色，图例按组合并。
    若未传 groups（向后兼容），行为保持不变。
    """
    if ms is None: ms = MK_SIZE_TERNARY

    if groups is not None:
        # 分组模式
        if group_colors is None:
            group_colors = get_group_colors(groups)
        seen_groups = set()
        n = len(labels)
        do_annotate = n <= 25
        for i in range(n):
            if np.isnan(x_arr[i]) or np.isnan(y_arr[i]) or np.isinf(x_arr[i]) or np.isinf(y_arr[i]):
                continue
            g = groups[i] if i < len(groups) else '其他'
            c = group_colors.get(g, '#999999')
            label = g if g not in seen_groups else None
            seen_groups.add(g)
            ax.plot(x_arr[i], y_arr[i], marker=MK_MARKER, markersize=ms,
                    markerfacecolor=c, markeredgecolor=MK_EDGE_COLOR,
                    markeredgewidth=MK_EDGE_WIDTH_T, zorder=8, label=label, **kw)
            if do_annotate:
                ax.annotate(labels[i], (x_arr[i], y_arr[i]),
                            textcoords='offset points', xytext=ANNOTATE_OFFSET,
                            fontsize=ANNOTATE_FONTSIZE, color='#333333')
    else:
        # 原始模式
        n = len(labels)
        do_annotate = n <= 25
        for i in range(n):
            if np.isnan(x_arr[i]) or np.isnan(y_arr[i]) or np.isinf(x_arr[i]) or np.isinf(y_arr[i]):
                continue
            ax.plot(x_arr[i], y_arr[i], marker=MK_MARKER, markersize=ms,
                    markerfacecolor=get_color(i), markeredgecolor=MK_EDGE_COLOR,
                    markeredgewidth=MK_EDGE_WIDTH_T, zorder=8, label=labels[i], **kw)
            if do_annotate:
                ax.annotate(labels[i], (x_arr[i], y_arr[i]),
                            textcoords='offset points', xytext=ANNOTATE_OFFSET,
                            fontsize=ANNOTATE_FONTSIZE, color='#333333')


# ── 坐标轴风格 ─────────────────────────────────────────────
def style_ax(ax, xlabel='', ylabel='', xlabel_size=12, ylabel_size=12):
    """统一坐标轴风格：刻度向内、边框、网格。"""
    ax.tick_params(direction='in', length=TICK_LENGTH, width=TICK_WIDTH, top=True, right=True, labelsize=9)
    ax.grid(color='#CCCCCC', linewidth=GRID_LW, alpha=GRID_ALPHA, linestyle=GRID_STYLE)
    ax.minorticks_on()
    ax.tick_params(direction='in', which='minor', length=TICK_LENGTH_M, width=TICK_WIDTH*0.6, top=True, right=True)
    for spine in ax.spines.values():
        spine.set_linewidth(SPINE_WIDTH)
    if xlabel:
        ax.set_xlabel(xlabel, fontproperties=times_prop, fontsize=xlabel_size)
    if ylabel:
        ax.set_ylabel(ylabel, fontproperties=times_prop, fontsize=ylabel_size)


# ── 保存 / 图例 ────────────────────────────────────────────
def save_fig(fig, filename, out_dir=None, dpi=600):
    """保存图片到输出目录。自动查注册表加引用 imprint。不关闭 fig。

    Args:
        fig: matplotlib Figure 对象
        filename: 输出文件名（如 'TAS.png' 或 'CLS-01_TAS.png'）
        out_dir: 输出目录，None 则使用默认输出目录
        dpi: 图片分辨率（默认 600）

    Returns:
        str: 保存文件的绝对路径
    """
    out = out_dir or _OUT_DIR or DEFAULT_OUT_DIR
    os.makedirs(out, exist_ok=True)
    # 自动补注册表编号前缀：短名 → 长名（如 TAS.png → CLS-01_TAS.png）
    long_name = _get_long_name(filename)
    path = os.path.join(out, long_name)

    # ── 自动加引用 imprint ────────────────────────────
    # 从文件名找注册表条目
    ref_text = None
    try:
        from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY
        from igneous_wr.references.loader import get_short
        for d in DIAGRAM_REGISTRY:
            if d.filename == long_name:
                if d.source_ref:
                    ref_text = get_short(d.source_ref)
                break
    except Exception:
        pass

    if ref_text:
        # 取最后一个 axe
        axs = fig.axes
        if axs:
            ax = axs[0]  # 多数单轴图
            ax.text(0.99, 0.01, ref_text,
                    transform=ax.transAxes,
                    fontsize=7, color='gray', style='italic',
                    ha='right', va='bottom',
                    fontfamily='serif')

    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    print(f"[saved] {path}")
    return path


def add_legend(ax, loc=None, fontsize=7):
    """统一图例风格。默认右上角。无数据时静默跳过。"""
    if loc is None: loc = LEGEND_LOC
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc=loc, fontsize=fontsize, framealpha=0.9, edgecolor='#CCCCCC')


# ── HTML 报告生成 ────────────────────────────────────────────

def generate_report_html(success, skipped, gd=None, out_dir=None, rock_type=None):
    """在出图完毕后，自动生成一份自包含的 HTML 图集报告。
    按 4 个方向（分类/源区/演化/构造）分组展示。

    Args:
        success: [(fn_name, fname), ...] — plot_recommended 的 success 列表
        skipped: [(desc, reason), ...] — plot_recommended 的 skipped 列表
        gd: GeochemData 实例（可选），用于显示数据源和样品信息
        out_dir: 输出目录（可选），从 gd 或默认值推断
        rock_type: 岩性判定结果（可选）

    Returns:
        str: HTML 文件的绝对路径
    """
    from datetime import datetime

    out = out_dir or _OUT_DIR or DEFAULT_OUT_DIR
    os.makedirs(out, exist_ok=True)

    n_total = len(success) + len(skipped)
    n_ok = len(success)
    n_skip = len(skipped)

    data_src = getattr(gd, 'path', '未知')
    n_samples = len(getattr(gd, 'labels', [])) if gd else 0
    rock_label = rock_type or ('自动判定' if gd else '未知')

    # 方向前缀映射（从 DIAGRAM_REGISTRY 自动推断）
    def _get_direction(fn_name):
        """从注册表反查图件方向。"""
        from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY
        prefixes = {
            'CLS': '岩石系列 / 分类',
            'SRC': '源区性质',
            'EVO': '岩浆演化过程',
            'TEC': '构造环境判别',
        }
        for d in DIAGRAM_REGISTRY:
            if d.fn.__name__ == fn_name and d.filename:
                prefix = d.filename.split('-')[0]
                return prefixes.get(prefix, '其他')
        # fallback: 从长名前缀猜
        return '其他'

    # 按方向分组
    sections = {
        '岩石系列 / 分类': [],
        '源区性质': [],
        '岩浆演化过程': [],
        '构造环境判别': [],
    }
    for fn_name, fname in success:
        sec = _get_direction(fn_name)
        if sec not in sections:
            sections[sec] = []
        sections[sec].append((fn_name, fname))

    lines = []
    def w(s=""):
        lines.append(s)

    w('<!DOCTYPE html>')
    w('<html lang="zh-CN">')
    w('<head>')
    w('<meta charset="UTF-8">')
    w(f'<title>岩浆岩全岩地球化学图集 — {datetime.now():%Y-%m-%d}</title>')
    w('<style>')
    w('* { margin: 0; padding: 0; box-sizing: border-box; }')
    w('body { font-family: \"Times New Roman\", \"SimSun\", serif; max-width: 1200px; margin: 0 auto; padding: 30px 20px; background: #fafafa; color: #222; }')
    w('h1 { font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 8px; margin-bottom: 15px; color: #111; }')
    w('h2 { font-size: 16px; color: #555; font-weight: normal; margin-bottom: 20px; }')
    w('.meta { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 14px 18px; margin-bottom: 25px; font-size: 13px; line-height: 1.8; }')
    w('.meta strong { display: inline-block; width: 80px; color: #666; }')
    w('.summary { display: flex; gap: 15px; margin-bottom: 25px; }')
    w('.summary-item { flex: 1; background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 14px 18px; text-align: center; }')
    w('.summary-item .num { font-size: 28px; font-weight: bold; display: block; }')
    w('.summary-item .label { font-size: 12px; color: #888; margin-top: 4px; }')
    w('.summary-item.ok .num { color: #2CA02C; }')
    w('.summary-item.skip .num { color: #D62728; }')
    w('.summary-item.total .num { color: #1F77B4; }')
    w('.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 5px; }')
    w('.grid-item { background: #fff; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; transition: box-shadow .2s; }')
    w('.grid-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,.12); }')
    w('.grid-item img { width: 100%; display: block; cursor: pointer; border-bottom: 1px solid #eee; }')
    w('.grid-item .caption { padding: 8px 12px; font-size: 13px; color: #444; }')
    w('.grid-item .caption code { font-size: 11px; color: #999; }')
    w('.lightbox { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,.85); z-index: 999; cursor: zoom-out; justify-content: center; align-items: center; }')
    w('.lightbox img { max-width: 90%; max-height: 90%; border-radius: 4px; box-shadow: 0 0 40px rgba(0,0,0,.5); }')
    w('.lightbox:target { display: flex; }')
    w('.skipped-section { margin-top: 25px; }')
    w('.skipped-section h3 { font-size: 15px; color: #888; margin-bottom: 8px; }')
    w('.skipped-section ul { list-style: none; padding: 0; }')
    w('.skipped-section li { font-size: 13px; color: #999; padding: 3px 0; }')
    w('.skipped-section li::before { content: \"✗ \"; color: #D62728; }')
    w('.footer { margin-top: 30px; padding-top: 12px; border-top: 1px solid #ddd; font-size: 11px; color: #aaa; text-align: center; }')
    w('</style>')
    w('</head>')
    w('<body>')

    w(f'<h1>岩浆岩全岩地球化学图集</h1>')
    w(f'<h2>{datetime.now():%Y-%m-%d}</h2>')

    w('<div class=\"meta\">')
    w(f'<strong>数据源</strong> {data_src}<br>')
    w(f'<strong>样品数</strong> {n_samples}<br>')
    w(f'<strong>岩性</strong> {rock_label}<br>')
    w(f'<strong>输出目录</strong> {out}')
    w('</div>')

    w('<div class=\"summary\">')
    w(f'<div class=\"summary-item total\"><span class=\"num\">{n_total}</span><span class=\"label\">推荐图件数</span></div>')
    w(f'<div class=\"summary-item ok\"><span class=\"num\">{n_ok}</span><span class=\"label\"> 成功</span></div>')
    w(f'<div class=\"summary-item skip\"><span class=\"num\">{n_skip}</span><span class=\"label\"> 跳过</span></div>')
    w('</div>')

    if success:
        # 按方向输出（固定顺序：分类 → 源区 → 演化 → 构造）
        section_order = ['岩石系列 / 分类', '源区性质', '岩浆演化过程', '构造环境判别']
        section_emojis = {
            '岩石系列 / 分类': '📋 岩石系列 / 分类',
            '源区性质': '🔬 源区性质',
            '岩浆演化过程': '🧬 岩浆演化过程',
            '构造环境判别': '🌍 构造环境判别',
        }
        for sec in section_order:
            items = sections.get(sec, [])
            if not items:
                continue
            w(f'<h3 style=\"margin-top:22px; margin-bottom:8px; font-size:16px; color:#333;\">{section_emojis.get(sec, sec)}</h3>')
            w('<div class=\"grid\">')
            for fn_name, fname in items:
                w('<div class=\"grid-item\">')
                w(f'<a href=\"#lightbox-{fn_name}\"><img src=\"{fname}\" alt=\"{fn_name}\"></a>')
                w(f'<div class=\"caption\">{fn_name} <code>{fname}</code></div>')
                w('</div>')
                w(f'<div id=\"lightbox-{fn_name}\" class=\"lightbox\"><img src=\"{fname}\" alt=\"{fn_name}\"></div>')
            w('</div>')

        # 任何不属于 4 个方向的图
        other = sections.get('其他', [])
        if other:
            w('<h3 style=\"margin-top:22px; margin-bottom:8px; font-size:16px; color:#888;\">其他</h3>')
            w('<div class=\"grid\">')
            for fn_name, fname in other:
                w('<div class=\"grid-item\">')
                w(f'<a href=\"#lightbox-{fn_name}\"><img src=\"{fname}\" alt=\"{fn_name}\"></a>')
                w(f'<div class=\"caption\">{fn_name} <code>{fname}</code></div>')
                w('</div>')
                w(f'<div id=\"lightbox-{fn_name}\" class=\"lightbox\"><img src=\"{fname}\" alt=\"{fn_name}\"></div>')
            w('</div>')

    if skipped:
        w('<div class=\"skipped-section\">')
        w(f'<h3> 已跳过 {len(skipped)} 张图</h3>')
        w('<ul>')
        for desc, reason in skipped:
            safe_desc = str(desc).replace('<', '&lt;').replace('>', '&gt;')
            safe_reason = str(reason).replace('<', '&lt;').replace('>', '&gt;')
            w(f'<li>{safe_desc} — {safe_reason}</li>')
        w('</ul>')
        w('</div>')

    # ── 参考文献列表 ──
    try:
        from igneous_wr.references.loader import get_references_for_report, _format_ref_line
        refs = get_references_for_report()
        if refs:
            w('<div class=\"references\">')
            w('<h3 style=\"margin-top:28px; margin-bottom:10px; font-size:16px; color:#333;\">参考文献</h3>')
            w('<ol style=\"font-size:12px; color:#555; line-height:1.9; padding-left:20px;\">')
            for key, short, full in refs:
                if full:
                    w(f'<li>{full}</li>')
                else:
                    w(f'<li><em>{short}</em> (完整引用信息待补充)</li>')
            w('</ol>')
            w('</div>')
    except Exception as e:
        print(f'[报告] ⚠️ 参考文献列表生成跳过: {e}')

    w(f'<div class=\"footer\">由 IgneousWR skill 自动生成 · {datetime.now():%Y-%m-%d %H:%M}</div>')

    w('</body>')
    w('</html>')

    html = '\n'.join(lines)
    fname = f'report_{datetime.now():%Y%m%d}.html'
    path = os.path.join(out, fname)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[报告] {path}")
    return path
