import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

import _style
from _chem import feot_calc
from _ternary import (
    SQRT3_2, ternary_to_xy, ternary_corners,
    draw_ternary_frame, draw_ternary_grid,
    draw_ternary_ticks, label_ternary_vertices,
)

"""
_evolution.py — 演化图：Harker, Miyashiro, Mg#, Zr协变
"""

# ────────────────────────────────────────────────────────────
# 🧬 岩浆演化过程
# ────────────────────────────────────────────────────────────

def plot_harker(gd, out_dir=None, save=True, only_oxides=None, trendline=True):
    """
    Harker 图（SiO₂ vs 主量氧化物，六合一）📊通用
    所需元素: SiO2, MgO, FeO, TFe2O3, Al2O3, CaO, Na2O, TiO2

    Args:
        only_oxides: 可选，指定显示的氧化物列表，如 ['MgO', 'FeOt', 'CaO']
        trendline: 是否画线性回归线和标注 R²（默认 True）
    """
    missing = gd.check_elements('SiO2', strict=True)
    if missing:
        return None, None
    gd.check_elements('MgO', 'FeO', 'TFe2O3', 'Al2O3', 'CaO', 'Na2O', 'TiO2')
    sio2 = gd.get('SiO2'); mgo = gd.get('MgO')
    feo = gd.get('FeO'); tfe2 = gd.get('TFe2O3')
    al2o3 = gd.get('Al2O3'); cao = gd.get('CaO')
    na2o = gd.get('Na2O'); tio2 = gd.get('TiO2')
    feot = feot_calc(feo, tfe2)
    labels = gd.labels
    groups = gd.groups

    harkerOxides = [
        ('MgO', mgo), ('FeOt', feot),
        (r'Al$_2$O$_3$', al2o3), ('CaO', cao),
        (r'Na$_2$O', na2o), (r'TiO$_2$', tio2),
    ]

    # 如果指定了子集，过滤
    if only_oxides is not None:
        harkerOxides = [(lbl, d) for lbl, d in harkerOxides
                        if lbl in only_oxides or
                        lbl.replace(r'\$_2$', '2').replace(r'\$_3$', '3') in only_oxides]
        if not harkerOxides:
            print("[Harker] ⚠️ only_oxides 未匹配任何氧化物，使用全部")
            harkerOxides = [
                ('MgO', mgo), ('FeOt', feot),
                (r'Al$_2$O$_3$', al2o3), ('CaO', cao),
                (r'Na$_2$O', na2o), (r'TiO$_2$', tio2),
            ]

    # 动态计算网格：氧化物个数决定
    n_plots = len(harkerOxides)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols
    figsize_dynamic = (12, 2.5 * n_rows + 0.5)

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize_dynamic)
    axes = axes.flatten()

    for idx, (ylabel, ydata) in enumerate(harkerOxides):
        ax = axes[idx]
        _style.scatter_samples(ax, sio2, ydata, labels, groups=groups)

        # 线性回归 + R²（当 trendline=True 且数据点≥3 时）
        if trendline:
            mask = ~(np.isnan(sio2) | np.isnan(ydata))
            if mask.sum() >= 3 and np.unique(sio2[mask]).size > 1:
                slope, intercept, r_val, p_val, se = stats.linregress(
                    sio2[mask], ydata[mask])
                r2 = r_val ** 2
                x_fit = np.array([sio2[mask].min(), sio2[mask].max()])
                ax.plot(x_fit, slope * x_fit + intercept,
                       color='#555555', lw=0.8, ls='--', zorder=4)
                # R² 标注在左下角
                ax.text(0.05, 0.05, f'R² = {r2:.3f}',
                       transform=ax.transAxes,
                       fontsize=8, va='bottom', ha='left',
                       color='#555555', fontstyle='italic',
                       fontproperties=_style.times_prop)

        _style.style_ax(ax, r'SiO$_2$ (wt.%)', ylabel, xlabel_size=9, ylabel_size=9)
        ax.set_xlim(left=0); ax.set_ylim(bottom=0)

    # 隐藏多余的 subplot
    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)

    handles, labels_legend = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_legend, loc='upper right', bbox_to_anchor=(0.99,0.98),
               fontsize=7, framealpha=0.9, edgecolor='#CCCCCC',
               handlelength=1.5, handleheight=1.0)

    plt.tight_layout(rect=[0,0,1,0.96], pad=0.5)
    if save:
        # 文件名根据氧化物子集动态设定
        if only_oxides:
            suffix = '_'.join(o.replace('$', '') for o in only_oxides)
            fname = f'Harker_{suffix}.png'
        else:
            fname = 'Harker_6panel.png'
        _style.save_fig(fig, fname, out_dir)
    return fig, axes


def plot_miyashiro(gd, out_dir=None, save=True):
    """
    Miyashiro (1974) FeOt/MgO vs SiO₂ 🔥火山岩
    所需元素: SiO2, FeO, TFe2O3, MgO
    """
    missing = gd.check_elements('SiO2', 'MgO', strict=True)
    if missing:
        return None, None
    # FeO/TFe2O3 至少其一即可
    feo_ok = not gd.check_elements('FeO')
    tfe2_ok = not gd.check_elements('TFe2O3')
    if not (feo_ok or tfe2_ok):
        print("[whole_rock] ❌ 缺少 FeO 和 TFe2O3，无法计算 FeOt/MgO")
        return None, None
    sio2 = gd.get('SiO2'); feo = gd.get('FeO')
    tfe2 = gd.get('TFe2O3'); mgo = gd.get('MgO')
    feot = feot_calc(feo, tfe2)
    feot_mgo = np.where(mgo > 0, feot / mgo, np.nan)
    labels = gd.labels

    fig, ax = plt.subplots(figsize=(8, 6))
    x_line = np.array([40, 80])
    y_line = 0.1578 * x_line - 6.016
    ax.plot(x_line, y_line, 'k-', lw=1.0)
    ax.fill_between(x_line, y_line, 0, alpha=0.06, color='#1565C0')
    ax.fill_between(x_line, y_line, 20, alpha=0.06, color='#D62728')

    ax.text(50, 0.8, 'Calc-alkaline', fontsize=10, fontstyle='italic',
            ha='center', va='center', color='#1565C0', fontproperties=_style.times_prop)
    ax.text(65, 6.0, 'Tholeiitic', fontsize=10, fontstyle='italic',
            ha='center', va='center', color='#D62728', fontproperties=_style.times_prop)

    ax.set_xlim(38, 80); ax.set_ylim(0, 10)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', 'FeOt/MgO')

    _style.scatter_samples(ax, sio2, feot_mgo, labels, groups=gd.groups)
    _style.add_legend(ax)

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Miyashiro1974_FeOtMgO_SiO2.png', out_dir)
    return fig, ax


def plot_mgno(gd, out_dir=None, save=True):
    """
    Mg# vs SiO₂ 📊通用
    所需元素: SiO2, FeO, TFe2O3, MgO
    """
    missing = gd.check_elements('SiO2', 'MgO', strict=True)
    if missing:
        return None, None
    # FeO/TFe2O3 至少其一即可
    feo_ok = not gd.check_elements('FeO')
    tfe2_ok = not gd.check_elements('TFe2O3')
    if not (feo_ok or tfe2_ok):
        print("[whole_rock] ❌ 缺少 FeO 和 TFe2O3，无法计算 Mg#")
        return None, None
    sio2 = gd.get('SiO2'); feo = gd.get('FeO')
    tfe2 = gd.get('TFe2O3'); mgo = gd.get('MgO')
    feot = feot_calc(feo, tfe2)
    mg_mol = mgo / 40.304
    feot_mol = feot / 71.844
    mg_no = np.where((mg_mol + feot_mol) > 0, mg_mol / (mg_mol + feot_mol) * 100, np.nan)
    labels = gd.labels

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axhline(y=50, color='#555555', ls=':', lw=0.8, alpha=0.7)
    ax.text(76, 51, 'Mg# = 50', fontsize=8, ha='right', va='bottom',
            color='#555555', fontproperties=_style.times_prop)

    ax.set_xlim(38, 80); ax.set_ylim(0, 100)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', 'Mg#')

    _style.scatter_samples(ax, sio2, mg_no, labels, groups=gd.groups)
    _style.add_legend(ax)

    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'MgNo_vs_SiO2.png', out_dir)
    return fig, ax


def plot_zr_covariance(gd, out_dir=None, save=True):
    """
    Zr 微量元素协变图（3×3 网格）📊通用
    所需元素: Zr, Nb, Hf, Th, Y, Yb, La, Sm, Ba, Sr
    """
    missing = gd.check_elements('Zr', strict=True)
    if missing:
        return None, None
    gd.check_elements('Nb', 'Hf', 'Th', 'Y', 'Yb', 'La', 'Sm', 'Ba', 'Sr')
    Zr = gd.get('Zr')
    pairs = [
        ('Nb', gd.get('Nb')), ('Hf', gd.get('Hf')),
        ('Th', gd.get('Th')), ('Y', gd.get('Y')),
        ('Yb', gd.get('Yb')), ('La', gd.get('La')),
        ('Sm', gd.get('Sm')), ('Ba', gd.get('Ba')),
        ('Sr', gd.get('Sr')),
    ]
    labels = gd.labels
    groups = gd.groups

    fig, axes = plt.subplots(3, 3, figsize=(10, 9))
    axes = axes.flatten()

    for idx, (ylabel, ydata) in enumerate(pairs):
        ax = axes[idx]
        _style.scatter_samples(ax, Zr, ydata, labels, groups=groups)
        mask = ~(np.isnan(Zr) | np.isnan(ydata))
        if mask.sum() > 2 and np.unique(Zr[mask]).size > 1:
            slope, intercept, r, p, se = stats.linregress(Zr[mask], ydata[mask])
            x_fit = np.array([Zr[mask].min(), Zr[mask].max()])
            ax.plot(x_fit, slope*x_fit+intercept, color='#555555', lw=0.8, ls='--', zorder=4)
            ax.text(0.05, 0.95, f'$R^2$ = {r**2:.3f}', transform=ax.transAxes,
                    fontsize=8, va='top', ha='left', color='#333333')
        _style.style_ax(ax, 'Zr (ppm)', f'{ylabel} (ppm)', xlabel_size=9, ylabel_size=9)

    handles, labels_legend = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_legend, loc='upper right', bbox_to_anchor=(0.99,0.98),
               fontsize=7, framealpha=0.9, edgecolor='#CCCCCC',
               handlelength=1.5, handleheight=1.0)

    plt.tight_layout(rect=[0,0,1,0.96], pad=0.5)
    if save:
        _style.save_fig(fig, 'Zr_covariance.png', out_dir)
    return fig, axes
