"""
_classification.py — 岩石系列 / 分类图（15 个绘图函数）
  原有: TAS, K2O-SiO2, AFM, Shand, W&F, Co-Th, An-Ab-Or, QAPF
  新增 RockPlot SVG: Cabanis, Mullen, Jensen, OConnorVolc, OhtaArai, Pearce1977
"""

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


# ────────────────────────────────────────────────────────────
# Co vs Th 岩浆系列判别图（Hastie et al., 2007）
# ────────────────────────────────────────────────────────────

def plot_co_th(gd, out_dir=None, save=True):
    """Co vs Th 岩浆系列判别图（Hastie et al., 2007）
    所需元素: Co, Th
    """
    missing = gd.check_elements('Co', 'Th', strict=True)
    if missing:
        return None, None
    co = gd.get('Co'); th = gd.get('Th')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.plot([0.5, 10], [25, 25], 'k-', lw=1.0)
    ax.plot([2, 2], [2, 200], 'k-', lw=1.0)
    ax.plot([0.5, 5], [80, 80], 'k-', lw=1.0)
    _style.scatter_samples(ax, th, co, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(0.1, 50); ax.set_ylim(1, 500)
    _style.style_ax(ax, 'Th (ppm)', 'Co (ppm)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Co_Th_Hastie2007.png', out_dir)
    return fig, ax

# ────────────────────────────────────────────────────────────
# An-Ab-Or 长石分类三元图（O'Connor, 1965）
# ────────────────────────────────────────────────────────────

def plot_an_ab_or(gd, out_dir=None, save=True):
    """An-Ab-Or 长石分类三元图（O'Connor, 1965）
    所需元素: Na2O, K2O, CaO, Al2O3, SiO2
    """
    missing = gd.check_elements('Na2O', 'K2O', 'CaO', 'Al2O3', 'SiO2', strict=True)
    if missing:
        return None, None
    na2o = gd.get('Na2O'); k2o = gd.get('K2O'); cao = gd.get('CaO')
    al2o3 = gd.get('Al2O3'); sio2 = gd.get('SiO2')
    labels = gd.labels
    # 简化标准矿物计算
    an = cao; ab = na2o; or_ = k2o
    total = an + ab + or_
    mask = total == 0
    an_n = np.where(mask, 0, an/total*100)
    ab_n = np.where(mask, 0, ab/total*100)
    or_n = np.where(mask, 0, or_/total*100)
    x_d, y_d = ternary_to_xy(an_n, ab_n, or_n)
    valid = ~np.isnan(x_d) & ~np.isnan(y_d)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)
    label_ternary_vertices(ax, 'An', 'Ab', 'Or')
    _style.scatter_samples(ax, x_d[valid], y_d[valid], labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'An_Ab_Or_OConnor1965.png', out_dir)
    return fig, ax

# ────────────────────────────────────────────────────────────
# Q-A-PF 深成岩分类三元图（Streckeisen, 1976）
# ────────────────────────────────────────────────────────────

def plot_qapf(gd, out_dir=None, save=True):
    """Q-A-PF 深成岩分类三元图（Streckeisen, 1976）
    所需元素: SiO2, Na2O, K2O, CaO, Al2O3
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', 'CaO', 'Al2O3', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    cao = gd.get('CaO'); al2o3 = gd.get('Al2O3')
    labels = gd.labels
    # 简化 Q-A-PF
    q = np.maximum(sio2 - 50, 0); a = na2o + k2o; pf = cao + al2o3 - a - q
    pf = np.maximum(pf, 0)
    total = q + a + pf
    mask = total == 0
    q_n = np.where(mask, 0, q/total*100)
    a_n = np.where(mask, 0, a/total*100)
    pf_n = np.where(mask, 0, pf/total*100)
    x_d, y_d = ternary_to_xy(q_n, a_n, pf_n)
    valid = ~np.isnan(x_d) & ~np.isnan(y_d)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)
    label_ternary_vertices(ax, 'Q', 'A', 'P+F')
    _style.scatter_samples(ax, x_d[valid], y_d[valid], labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'QAPF_Streckeisen1976.png', out_dir)
    return fig, ax

# ────────────────────────────────────────────────────────────
# TAS 全碱-硅分类图（Le Bas et al., 1992）
# ────────────────────────────────────────────────────────────

def plot_tas(gd, out_dir=None, save=True):
    """TAS 全碱-硅分类图（Le Bas et al., 1992）
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    alk = na2o + k2o
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))
    xs = np.array([41, 45, 48, 52, 57, 63, 69, 71, 75, 78])
    ys = np.array([0, 3, 4, 5, 7, 9, 11, 12, 13, 14])
    ax.plot(xs, ys, 'k-', lw=1.2, zorder=1)
    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(38, 82); ax.set_ylim(0, 18)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# K₂O–SiO₂ 钾系列分类图（Peccerillo & Taylor, 1976）
# ────────────────────────────────────────────────────────────

def plot_k2o_sio2(gd, out_dir=None, save=True):
    """K₂O–SiO₂ 钾系列分类图（Peccerillo & Taylor, 1976）
    所需元素: SiO2, K2O
    """
    missing = gd.check_elements('SiO2', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); k2o = gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))
    xs = np.linspace(45, 80, 20)
    ax.plot(xs, 0.025*xs-2.0, 'k-', lw=1.0)
    ax.plot(xs, 0.05*xs-3.0, 'k-', lw=1.0)
    ax.plot(xs, 0.1*xs-5.0, 'k-', lw=1.0)
    ax.plot(xs, 0.2*xs-9.0, 'k-', lw=1.0)
    _style.scatter_samples(ax, sio2, k2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(42, 82); ax.set_ylim(0, 8)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'K2O_SiO2_PT76.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# AFM 三角图（Irvine & Baragar, 1971）
# ────────────────────────────────────────────────────────────

def plot_afm(gd, out_dir=None, save=True):
    """AFM 三角图（Irvine & Baragar, 1971）
    A=Na₂O+K₂O, F=FeO*, M=MgO
    所需元素: Na2O, K2O, MgO, (FeO / TFe2O3)
    """
    missing = gd.check_elements('Na2O', 'K2O', 'MgO', strict=True)
    if missing:
        return None, None
    na2o = gd.get('Na2O'); k2o = gd.get('K2O'); mgo = gd.get('MgO')
    feo = gd.get('FeO'); tfe2 = gd.get('TFe2O3')
    labels = gd.labels
    a = na2o + k2o; f = feot_calc(feo, tfe2); m = mgo
    total = a + f + m
    valid = (total > 0) & ~np.isnan(total)
    a_p = np.where(valid, a/total*100, 0)
    f_p = np.where(valid, f/total*100, 0)
    m_p = np.where(valid, m/total*100, 0)
    x_d = np.where(valid, ternary_to_xy(a_p, f_p, m_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(a_p, f_p, m_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)
    ib_x = np.array([20, 32, 41, 56, 75])
    ib_y = np.array([80, 68, 59, 44, 25])
    th_x, th_y = ternary_to_xy(ib_x, ib_y, 100-ib_x-ib_y)
    ax.plot(th_x, th_y, 'k-', lw=1.5, zorder=4)
    label_ternary_vertices(ax, r'Na$_2$O+K$_2$O', 'FeO*', 'MgO')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'AFM_IB1971.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# Shand A/CNK–A/NK 铝质分类图
# ────────────────────────────────────────────────────────────

def plot_shand(gd, out_dir=None, save=True):
    """Shand A/CNK–A/NK 铝质分类图
    所需元素: Al2O3, CaO, Na2O, K2O
    """
    missing = gd.check_elements('Al2O3', 'CaO', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    al2o3 = gd.get('Al2O3'); cao = gd.get('CaO')
    na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    labels = gd.labels
    a_cnk = al2o3 / (cao + na2o + k2o)
    a_nk = al2o3 / (na2o + k2o)
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.axhline(y=1, color='#888888', ls='--', lw=1.0)
    ax.axvline(x=1, color='#888888', ls='--', lw=1.0)
    _style.scatter_samples(ax, a_cnk, a_nk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 3); ax.set_ylim(0, 3)
    _style.style_ax(ax, 'A/CNK', 'A/NK')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Shand_ACNK_ANK.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# Winchester & Floyd Zr/TiO₂–Nb/Y 分类图
# ────────────────────────────────────────────────────────────

def plot_winchester_floyd(gd, out_dir=None, save=True):
    """Winchester & Floyd (1977) Zr/TiO2-Nb/Y 岩石分类图
    所需元素: Zr, TiO2, Nb, Y
    """
    missing = gd.check_elements('Zr', 'TiO2', 'Nb', 'Y', strict=True)
    if missing:
        return None, None
    zr = gd.get('Zr'); tio2 = gd.get('TiO2')
    nb = gd.get('Nb'); yi = gd.get('Y')
    labels = gd.labels
    zr_tio2 = np.where(tio2 > 0, zr / tio2, np.nan)
    nb_yi = np.where(yi > 0, nb / yi, np.nan)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.plot([0.001, 0.008, 0.03, 0.1, 0.5, 2, 10], [0.04]*7, 'k-', lw=1.0)
    ax.plot([0.001, 0.01, 0.1], [0.6, 0.6, 0.5], 'k-', lw=1.0)
    ax.plot([0.01, 0.1, 0.3, 1.0], [0.01, 0.008, 0.008, 0.01], 'k-', lw=1.0)
    _style.scatter_samples(ax, nb_yi, zr_tio2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(0.01, 15); ax.set_ylim(0.001, 2)
    _style.style_ax(ax, 'Nb/Y', 'Zr/TiO2')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Winchester_Floyd1977_NbY_ZrTiO2.png', out_dir)
    return fig, ax

# ════════════════════════════════════════════════════════════
# 📋 RockPlot SVG 新增三角图
# ════════════════════════════════════════════════════════════

# ── Cabanis (1989) La/10–Y/15–Nb/8 底部岩分类 ────────────

cabanis_bd_a = np.array([0.0, 47.0, 57.0, 47.0, 54.0, 58.0, 54.0, 59.0, 67.0, 59.0, 80.0, 100.0, 80.0, 68.0, 76.5, 68.0, 27.5, 42.5, 27.5, 0.0])
cabanis_bd_b = np.array([62.0, 32.9, 43.0, 32.9, 28.5, 19.5, 28.5, 25.4, 33.0, 25.4, 12.4, -0.0, 12.4, 16.2, -0.0, 16.2, 29.2, -0.0, 29.2, 38.0])
cabanis_bd_c = np.array([38.0, 20.1, 0.0, 20.1, 17.5, 22.5, 17.5, 15.6, 0.0, 15.6, 7.6, 0.0, 7.6, 15.8, 23.5, 15.8, 43.3, 57.5, 43.3, 62.0])
cabanis_bd_xy = ternary_to_xy(cabanis_bd_a, cabanis_bd_b, cabanis_bd_c)


def plot_cabanis(gd, out_dir=None, save=True):
    """Cabanis (1989) La/10-Y/15-Nb/8 基性岩构造判别三角图
    SVG轴标: 顶=Y/15, 左下=La/10, 右下=Nb/8
    所需元素: La, Y, Nb
    """
    missing = gd.check_elements('La', 'Y', 'Nb', strict=True)
    if missing:
        return None, None
    la = gd.get('La'); yi = gd.get('Y'); nb = gd.get('Nb')
    labels = gd.labels
    # 标准化: 按文献标准化因子
    a = yi / 15.0; b = la / 10.0; c = nb / 8.0
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
    ax.plot(cabanis_bd_xy[0], cabanis_bd_xy[1], 'k-', lw=1.5, zorder=4)
    label_ternary_vertices(ax, 'Y/15', 'La/10', 'Nb/8')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Cabanis1986_LaY_Nb_ternary.png', out_dir)
    return fig, ax


# ── Mullen (1983) TiO2–10MnO–10P2O5 基性岩判别 ───────────

mullen_0_a = np.array([59.0, 27.0, 27.0, 18.0, 0.0])
mullen_0_b = np.array([41.0, 41.0, 28.0, 21.0, 8.0])
mullen_0_c = np.array([0.0, 32.0, 45.0, 61.0, 92.0])
mullen_0_xy = ternary_to_xy(mullen_0_a, mullen_0_b, mullen_0_c)
mullen_1_a = np.array([77.0, 29.0, 27.0])
mullen_1_b = np.array([23.0, 30.0, 28.0])
mullen_1_c = np.array([0.0, 41.0, 45.0])
mullen_1_xy = ternary_to_xy(mullen_1_a, mullen_1_b, mullen_1_c)
mullen_2_a = np.array([39.0, 18.0, 18.0])
mullen_2_b = np.array([61.0, 61.0, 21.0])
mullen_2_c = np.array([0.0, 21.0, 61.0])
mullen_2_xy = ternary_to_xy(mullen_2_a, mullen_2_b, mullen_2_c)
mullen_3_a = np.array([27.0, 45.0])
mullen_3_b = np.array([28.0, -0.0])
mullen_3_c = np.array([45.0, 55.0])
mullen_3_xy = ternary_to_xy(mullen_3_a, mullen_3_b, mullen_3_c)


def plot_mullen(gd, out_dir=None, save=True):
    """Mullen (1983) TiO2-10MnO-10P2O5 基性岩构造判别三角图
    SVG轴标: 顶=TiO2, 左下=10MnO, 右下=10P2O5
    所需元素: TiO2, MnO, P2O5
    """
    missing = gd.check_elements('TiO2', 'MnO', 'P2O5', strict=True)
    if missing:
        return None, None
    tio2 = gd.get('TiO2'); mno = gd.get('MnO'); p2o5 = gd.get('P2O5')
    labels = gd.labels
    a = tio2; b = mno * 10.0; c = p2o5 * 10.0
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
    # 4 条分界线
    for xy in [mullen_0_xy, mullen_1_xy, mullen_2_xy, mullen_3_xy]:
        ax.plot(xy[0], xy[1], 'k-', lw=1.5, zorder=4)
    label_ternary_vertices(ax, 'TiO2', '10MnO', '10P2O5')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Mullen1983_TiO2_MnO_P2O5.png', out_dir)
    return fig, ax


# ── Jensen (1976) FeOt+TiO2–Al2O3–MgO 阳离子判别 ─────────

jensen_0_a = np.array([10.0, 11.7, 19.3, 24.9, 28.0, 28.9, 28.8, 27.3, 24.6, 19.6, 13.7, 12.5])
jensen_0_b = np.array([90.0, 86.7, 71.7, 60.6, 54.4, 52.5, 51.5, 50.6, 50.4, 50.8, 51.4, 51.5])
jensen_0_c = np.array([0.0, 1.6, 9.0, 14.5, 17.5, 18.6, 19.7, 22.0, 25.0, 29.6, 34.9, 36.0])
jensen_0_xy = ternary_to_xy(jensen_0_a, jensen_0_b, jensen_0_c)
jensen_1_a = np.array([0.0, 55.0]); jensen_1_b = np.array([50.0, 22.5]); jensen_1_c = np.array([50.0, 22.5])
jensen_1_xy = ternary_to_xy(jensen_1_a, jensen_1_b, jensen_1_c)
jensen_2_a = np.array([0.0, 40.0]); jensen_2_b = np.array([40.0, -0.0]); jensen_2_c = np.array([60.0, 60.0])
jensen_2_xy = ternary_to_xy(jensen_2_a, jensen_2_b, jensen_2_c)
jensen_3_a = np.array([33.3, 25.0]); jensen_3_b = np.array([33.3, 50.0]); jensen_3_c = np.array([33.4, 25.0])
jensen_3_xy = ternary_to_xy(jensen_3_a, jensen_3_b, jensen_3_c)
jensen_4_a = np.array([50.0, 35.0, 33.5, 29.0]); jensen_4_b = np.array([50.0, 50.0, 50.0, 51.5]); jensen_4_c = np.array([0.0, 15.0, 16.5, 19.5])
jensen_4_xy = ternary_to_xy(jensen_4_a, jensen_4_b, jensen_4_c)
jensen_5_a = np.array([40.0, 10.0]); jensen_5_b = np.array([60.0, 60.0]); jensen_5_c = np.array([0.0, 30.0])
jensen_5_xy = ternary_to_xy(jensen_5_a, jensen_5_b, jensen_5_c)
jensen_6_a = np.array([30.0, 0.0]); jensen_6_b = np.array([70.0, 70.0]); jensen_6_c = np.array([0.0, 30.0])
jensen_6_xy = ternary_to_xy(jensen_6_a, jensen_6_b, jensen_6_c)
jensen_7_a = np.array([20.0, 0.0]); jensen_7_b = np.array([80.0, 80.0]); jensen_7_c = np.array([0.0, 20.0])
jensen_7_xy = ternary_to_xy(jensen_7_a, jensen_7_b, jensen_7_c)
jensen_8_a = np.array([10.0, 20.1, 30.0, 10.0]); jensen_8_b = np.array([90.0, 70.0, 70.0, 90.0]); jensen_8_c = np.array([0.0, 9.9, -0.0, 0.0])
jensen_8_xy = ternary_to_xy(jensen_8_a, jensen_8_b, jensen_8_c)
jensen_9_a = np.array([20.1, 25.2, 40.0, 30.0, 20.1])
jensen_9_b = np.array([70.0, 60.0, 60.0, 70.0, 70.0])
jensen_9_c = np.array([9.9, 14.8, 0.0, -0.0, 9.9])
jensen_9_xy = ternary_to_xy(jensen_9_a, jensen_9_b, jensen_9_c)
jensen_10_a = np.array([25.2, 28.5, 29.0, 29.0, 33.5, 35.0, 50.0, 40.0, 25.2])
jensen_10_b = np.array([60.0, 53.5, 52.5, 51.5, 50.0, 50.0, 50.0, 60.0, 60.0])
jensen_10_c = np.array([14.8, 18.0, 18.5, 19.5, 16.5, 15.0, 0.0, 0.0, 14.8])
jensen_10_xy = ternary_to_xy(jensen_10_a, jensen_10_b, jensen_10_c)
jensen_11_a = np.array([0.0, 15.1, 10.0, 0.0, 0.0]); jensen_11_b = np.array([80.0, 80.0, 90.0, 100.0, 80.0]); jensen_11_c = np.array([20.0, 4.9, 0.0, 0.0, 20.0])
jensen_11_xy = ternary_to_xy(jensen_11_a, jensen_11_b, jensen_11_c)
jensen_12_a = np.array([0.0, 20.1, 15.1, 0.0, 0.0]); jensen_12_b = np.array([70.0, 70.0, 80.0, 80.0, 70.0]); jensen_12_c = np.array([30.0, 9.9, 4.9, 20.0, 30.0])
jensen_12_xy = ternary_to_xy(jensen_12_a, jensen_12_b, jensen_12_c)
jensen_13_a = np.array([0.0, 0.0, 25.2, 20.1, 0.0]); jensen_13_b = np.array([70.0, 60.0, 60.0, 70.0, 70.0]); jensen_13_c = np.array([30.0, 40.0, 14.8, 9.9, 30.0])
jensen_13_xy = ternary_to_xy(jensen_13_a, jensen_13_b, jensen_13_c)
jensen_14_a = np.array([12.5, 20.0, 25.0, 27.5, 29.0, 29.0, 28.5, 25.2, 0.0, 12.5])
jensen_14_b = np.array([51.5, 50.8, 50.3, 50.5, 51.5, 52.5, 53.5, 60.0, 60.0, 51.5])
jensen_14_c = np.array([36.0, 29.2, 24.7, 22.0, 19.5, 18.5, 18.0, 14.8, 40.0, 36.0])
jensen_14_xy = ternary_to_xy(jensen_14_a, jensen_14_b, jensen_14_c)
jensen_15_a = np.array([0.0, 33.3, 25.0, 24.8, 20.0, 12.5, 0.0])
jensen_15_b = np.array([50.0, 33.3, 50.0, 50.3, 50.8, 51.5, 50.0])
jensen_15_c = np.array([50.0, 33.4, 25.0, 24.8, 29.2, 36.0, 50.0])
jensen_15_xy = ternary_to_xy(jensen_15_a, jensen_15_b, jensen_15_c)
jensen_16_a = np.array([0.0, 40.0, 55.0, 0.0, 0.0]); jensen_16_b = np.array([40.0, -0.0, 22.5, 50.0, 40.0]); jensen_16_c = np.array([60.0, 60.0, 22.5, 50.0, 60.0])
jensen_16_xy = ternary_to_xy(jensen_16_a, jensen_16_b, jensen_16_c)
jensen_17_a = np.array([0.0, 40.0, 0.0, 0.0]); jensen_17_b = np.array([-0.0, -0.0, 40.0, -0.0]); jensen_17_c = np.array([100.0, 60.0, 60.0, 100.0])
jensen_17_xy = ternary_to_xy(jensen_17_a, jensen_17_b, jensen_17_c)
jensen_18_a = np.array([24.8, 25.0, 33.3, 55.0, 50.0, 35.0, 33.5, 29.0, 27.5, 25.0, 24.8])
jensen_18_b = np.array([50.3, 50.0, 33.3, 22.5, 50.0, 50.0, 50.0, 51.5, 50.5, 50.3, 50.3])
jensen_18_c = np.array([24.8, 25.0, 33.4, 22.5, 0.0, 15.0, 16.5, 19.5, 22.0, 24.7, 24.8])
jensen_18_xy = ternary_to_xy(jensen_18_a, jensen_18_b, jensen_18_c)

_jensen_all = [jensen_0_xy, jensen_1_xy, jensen_2_xy, jensen_3_xy, jensen_4_xy,
               jensen_5_xy, jensen_6_xy, jensen_7_xy, jensen_8_xy, jensen_9_xy,
               jensen_10_xy, jensen_11_xy, jensen_12_xy, jensen_13_xy, jensen_14_xy,
               jensen_15_xy, jensen_16_xy, jensen_17_xy, jensen_18_xy]


def plot_jensen(gd, out_dir=None, save=True):
    """Jensen (1976) FeOt+TiO2-Al2O3-MgO 阳离子三角图
    所需元素: FeO/TFe2O3, TiO2, Al2O3, MgO
    """
    missing = gd.check_elements('Al2O3', 'MgO', strict=True)
    if missing:
        return None, None
    al2o3 = gd.get('Al2O3'); mgo = gd.get('MgO')
    feo = gd.get('FeO'); tfe2 = gd.get('TFe2O3'); tio2 = gd.get('TiO2')
    labels = gd.labels
    feot = feot_calc(feo, tfe2)
    a = feot + tio2; b = al2o3; c = mgo
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
    for xy in _jensen_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.2, zorder=4)
    label_ternary_vertices(ax, 'FeOt+TiO2', 'Al2O3', 'MgO')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Jensen1976_cation_ternary.png', out_dir)
    return fig, ax


# ── O'Connor (1965) An-Ab-Or 火山岩分类 ──────────────────

ocomorv_0_a = np.array([0.0, 17.5]); ocomorv_0_b = np.array([70.0, 52.5]); ocomorv_0_c = np.array([30.0, 30.0])
ocomorv_0_xy = ternary_to_xy(ocomorv_0_a, ocomorv_0_b, ocomorv_0_c)
ocomorv_1_a = np.array([20.0, 44.0]); ocomorv_1_b = np.array([60.0, 36.0]); ocomorv_1_c = np.array([20.0, 20.0])
ocomorv_1_xy = ternary_to_xy(ocomorv_1_a, ocomorv_1_b, ocomorv_1_c)
ocomorv_2_a = np.array([16.3, 35.8]); ocomorv_2_b = np.array([48.7, 29.2]); ocomorv_2_c = np.array([35.0, 35.0])
ocomorv_2_xy = ternary_to_xy(ocomorv_2_a, ocomorv_2_b, ocomorv_2_c)
ocomorv_3_a = np.array([12.5, 27.5]); ocomorv_3_b = np.array([37.5, 22.5]); ocomorv_3_c = np.array([50.0, 50.0])
ocomorv_3_xy = ternary_to_xy(ocomorv_3_a, ocomorv_3_b, ocomorv_3_c)
ocomorv_4_a = np.array([25.0, 12.5]); ocomorv_4_b = np.array([75.5, 37.5]); ocomorv_4_c = np.array([-0.5, 50.0])
ocomorv_4_xy = ternary_to_xy(ocomorv_4_a, ocomorv_4_b, ocomorv_4_c)
ocomorv_5_a = np.array([12.5, 2.5]); ocomorv_5_b = np.array([37.5, 7.5]); ocomorv_5_c = np.array([50.0, 90.0])
ocomorv_5_xy = ternary_to_xy(ocomorv_5_a, ocomorv_5_b, ocomorv_5_c)
ocomorv_6_a = np.array([2.5, 5.5]); ocomorv_6_b = np.array([7.5, 4.5]); ocomorv_6_c = np.array([90.0, 90.0])
ocomorv_6_xy = ternary_to_xy(ocomorv_6_a, ocomorv_6_b, ocomorv_6_c)

_ocomorv_all = [ocomorv_0_xy, ocomorv_1_xy, ocomorv_2_xy, ocomorv_3_xy,
                ocomorv_4_xy, ocomorv_5_xy, ocomorv_6_xy]


def plot_oconnor_volc(gd, out_dir=None, save=True):
    """O'Connor (1965) An-Ab-Or 火山岩分类三角图
    SVG轴标: 顶=An, 左下=Ab, 右下=Or
    所需元素: Na2O, K2O, CaO, Al2O3, SiO2
    """
    missing = gd.check_elements('Na2O', 'K2O', 'CaO', strict=True)
    if missing:
        return None, None
    na2o = gd.get('Na2O'); k2o = gd.get('K2O'); cao = gd.get('CaO')
    labels = gd.labels
    a = cao; b = na2o; c = k2o
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
    for xy in _ocomorv_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.2, zorder=4)
    label_ternary_vertices(ax, 'An', 'Ab', 'Or')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'OConnor_Volc_An_Ab_Or.png', out_dir)
    return fig, ax


# ── Ohta-Arai (2007) M-F-W 源区判别 ─────────────────────

ohta_0_a = np.array([0.0, 0.6, 3.9, 9.1, 15.2, 21.6, 27.8, 33.7, 40.9, 48.0, 54.9, 62.0, 69.3, 76.4, 83.0, 89.0, 95.6, 97.1])
ohta_0_b = np.array([98.1, 96.8, 90.5, 81.9, 73.1, 65.1, 57.9, 51.6, 43.9, 36.9, 30.3, 23.8, 17.7, 12.2, 7.5, 4.0, 0.7, 0.1])
ohta_0_c = np.array([1.9, 2.6, 5.7, 9.0, 11.7, 13.3, 14.2, 14.8, 15.2, 15.1, 14.8, 14.2, 13.0, 11.4, 9.5, 7.0, 3.6, 2.8])
ohta_0_xy = ternary_to_xy(ohta_0_a, ohta_0_b, ohta_0_c)
ohta_1_a = np.array([11.3, 11.0, 9.4, 7.7, 6.2, 5.2, 4.2, 3.2, 2.3, 1.6, 1.1, 1.0])
ohta_1_b = np.array([78.2, 77.5, 73.5, 66.7, 58.6, 51.4, 44.0, 36.3, 27.7, 18.3, 11.6, 10.3])
ohta_1_c = np.array([10.5, 11.5, 17.1, 25.6, 35.1, 43.4, 51.8, 60.5, 70.0, 80.1, 87.3, 88.7])
ohta_1_xy = ternary_to_xy(ohta_1_a, ohta_1_b, ohta_1_c)
ohta_2_a = np.array([63.9, 63.6, 62.1, 59.5, 55.9, 51.2, 45.3, 37.1, 28.3, 19.5, 12.6, 11.3])
ohta_2_b = np.array([22.5, 21.8, 18.6, 15.9, 13.3, 10.8, 8.7, 6.3, 4.2, 2.3, 1.0, 0.7])
ohta_2_c = np.array([13.6, 14.6, 19.3, 24.5, 30.7, 38.0, 46.1, 56.6, 67.5, 78.2, 86.4, 88.0])
ohta_2_xy = ternary_to_xy(ohta_2_a, ohta_2_b, ohta_2_c)
ohta_3_a = np.array([88.4, 86.5, 77.1, 64.9, 49.0, 33.8, 30.6])
ohta_3_b = np.array([3.6, 3.5, 3.0, 2.2, 1.7, 1.4, 1.3])
ohta_3_c = np.array([8.0, 10.0, 19.9, 32.9, 49.3, 64.8, 68.0])
ohta_3_xy = ternary_to_xy(ohta_3_a, ohta_3_b, ohta_3_c)

_ohta_all = [ohta_0_xy, ohta_1_xy, ohta_2_xy, ohta_3_xy]


def plot_ohta_arai(gd, out_dir=None, save=True):
    """Ohta & Arai (2007) M-F-W 俯冲带源区判别三角图
    SVG轴标: 顶=M, 左下=F, 右下=W
    所需元素: (示踪元素组合)
    """
    missing = gd.check_elements('La', 'Nb', 'Ce', 'Zr', 'Y', 'Sm', strict=True)
    if missing:
        return None, None
    la = gd.get('La'); nb = gd.get('Nb'); ce = gd.get('Ce')
    zr = gd.get('Zr'); yi = gd.get('Y'); sm = gd.get('Sm')
    labels = gd.labels
    # M = FeO*+MgO proxy → 用 Ce+Nb+Zr
    m = ce + nb + zr; f = la + yi; w = sm
    total = m + f + w
    valid = (total > 0) & ~np.isnan(total)
    m_p = np.where(valid, m/total*100, 0)
    f_p = np.where(valid, f/total*100, 0)
    w_p = np.where(valid, w/total*100, 0)
    x_d = np.where(valid, ternary_to_xy(m_p, f_p, w_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(m_p, f_p, w_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)
    for xy in _ohta_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.2, zorder=4)
    label_ternary_vertices(ax, 'M', 'F', 'W')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Ohta_Arai2007_MFW.png', out_dir)
    return fig, ax


# ── Pearce (1977) FeOt-MgO-Al2O3 构造判别 ─────────────

pearce77_0_a = np.array([32.0, 32.0, 51.0]); pearce77_0_b = np.array([38.0, 21.5, 14.0]); pearce77_0_c = np.array([30.0, 46.5, 35.0])
pearce77_0_xy = ternary_to_xy(pearce77_0_a, pearce77_0_b, pearce77_0_c)
pearce77_1_a = np.array([32.0, 27.5, 24.0, 15.0])
pearce77_1_b = np.array([21.5, 21.0, 23.0, 28.0])
pearce77_1_c = np.array([46.5, 51.5, 53.0, 57.0])
pearce77_1_xy = ternary_to_xy(pearce77_1_a, pearce77_1_b, pearce77_1_c)
pearce77_2_a = np.array([27.5, 31.0, 34.0, 34.5, 33.0, 28.5, 21.0])
pearce77_2_b = np.array([21.0, 19.0, 16.0, 14.0, 12.0, 11.5, 10.0])
pearce77_2_c = np.array([51.5, 50.0, 50.0, 51.5, 55.0, 60.0, 69.0])
pearce77_2_xy = ternary_to_xy(pearce77_2_a, pearce77_2_b, pearce77_2_c)
pearce77_3_a = np.array([34.5, 38.0, 43.0, 49.0])
pearce77_3_b = np.array([14.0, 12.4, 10.0, 8.0])
pearce77_3_c = np.array([51.5, 49.6, 47.0, 43.0])
pearce77_3_xy = ternary_to_xy(pearce77_3_a, pearce77_3_b, pearce77_3_c)

_pearce77_all = [pearce77_0_xy, pearce77_1_xy, pearce77_2_xy, pearce77_3_xy]


def plot_pearce1977(gd, out_dir=None, save=True):
    """Pearce (1977) FeOt-MgO-Al2O3 基性岩构造判别三角图
    SVG轴标: 顶=FeOt, 左下=MgO, 右下=Al2O3
    所需元素: FeO/TFe2O3, MgO, Al2O3
    """
    missing = gd.check_elements('MgO', 'Al2O3', strict=True)
    if missing:
        return None, None
    mgo = gd.get('MgO'); al2o3 = gd.get('Al2O3')
    feo = gd.get('FeO'); tfe2 = gd.get('TFe2O3')
    labels = gd.labels
    feot = feot_calc(feo, tfe2)
    a = feot; b = mgo; c = al2o3
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
    for xy in _pearce77_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.2, zorder=4)
    label_ternary_vertices(ax, 'FeOt', 'MgO', 'Al2O3')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1977_FeOt_MgO_Al2O3.png', out_dir)
    return fig, ax
