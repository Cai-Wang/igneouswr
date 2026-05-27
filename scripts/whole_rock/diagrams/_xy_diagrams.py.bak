import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

import _style
from _chem import feot_calc

"""
_xy_diagrams.py — 新增 XY 二元图（22 张）

包含：TAS 变体、Pearce 系列、Frost、Whalen、Debon 等经典二元判别图。
全部绘图函数遵循统一的 (gd, out_dir=None, save=True) 签名，
返回 (fig, ax) 或 (None, None)（缺元素时）。

安装：在 whole_rock_core.py 的 DIAGRAM_REGISTRY 中注册即可自动纳入推荐。
"""

# ════════════════════════════════════════════════════════════
# 1. TAS 变体系列（分类图）
# ════════════════════════════════════════════════════════════

# ── TAS Plutonic (Middlemost 1994) ────────────────────────

def plot_tasmiddlemostplut(gd, out_dir=None, save=True):
    """TAS Plutonic (Middlemost 1994) — 深成岩全碱-硅分类图
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))

    # Middlemost (1994) 深成岩系列分界线
    # 平行的斜线群：石英二长岩/二长岩/二长闪长岩等之间的边界
    xs = np.linspace(42, 80, 20)
    ax.plot(xs, 0.07*xs - 1.8, 'k-', lw=0.8)   # 碱性/亚碱性分界
    ax.plot([45, 95], [5, 5], 'k--', lw=0.8)     # 低碱/中碱
    ax.plot([45, 95], [9.5, 17], 'k--', lw=0.8)  # 中碱/高碱

    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(35, 82); ax.set_ylim(0, 18)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS_Middlemost1994_Plutonic.png', out_dir)
    return fig, ax


# ── TAS Volcanic (Middlemost 1994) ─────────────────────────

def plot_tasmiddlemostvolc(gd, out_dir=None, save=True):
    """TAS Volcanic (Middlemost 1994) — 火山岩全碱-硅分类图
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))

    # Middlemost (1994) 火山岩边界线 — 与 Le Bas 相似但略有偏移
    xs = np.linspace(41, 82, 20)
    ax.plot(xs, 0.095*xs - 2.8, 'k-', lw=1.0)  # Irvine 分界线
    ax.plot(xs, 0.06*xs - 1.0, 'k--', lw=0.8)   # 辅助分界
    ax.plot([41, 77], [4, 4], 'k--', lw=0.8)
    ax.plot([41, 82], [8, 14], 'k--', lw=0.8)

    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(35, 82); ax.set_ylim(0, 18)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS_Middlemost1994_Volcanic.png', out_dir)
    return fig, ax


# ── Cox Plutonic (1979) ───────────────────────────────────

def plot_coxplut(gd, out_dir=None, save=True):
    """TAS for plutonic rocks (Cox et al. 1979)
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))

    # Cox (1979) TAS 分界线
    xs = np.linspace(42, 78, 20)
    ax.plot(xs, 0.08*xs - 1.6, 'k-', lw=1.0)   # 碱性/亚碱性
    ax.plot([42, 80], [2.5, 2.5], 'k--', lw=0.8)
    ax.plot([52, 76], [5.5, 10], 'k--', lw=0.8)

    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(35, 82); ax.set_ylim(0, 18)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS_Cox1979_Plutonic.png', out_dir)
    return fig, ax


# ── Cox Volcanic (1979) ───────────────────────────────────

def plot_coxvolc(gd, out_dir=None, save=True):
    """TAS for volcanic rocks (Cox et al. 1979)
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))

    xs = np.linspace(35, 89, 20)
    ax.plot(xs, 0.09*xs - 2.6, 'k-', lw=1.0)
    ax.plot([35, 68], [2, 6.5], 'k--', lw=0.8)
    ax.plot([42, 82], [7, 14], 'k--', lw=0.8)

    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(35, 82); ax.set_ylim(0, 18)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS_Cox1979_Volcanic.png', out_dir)
    return fig, ax



# ════════════════════════════════════════════════════════════
# 2. 判别/源区图（Pearce 系列）
# ════════════════════════════════════════════════════════════

# ── Pearce 1996 (Th/Yb vs Nb/Yb) ──────────────────────────

# ── Pearce & Norry (1979) Zr/Y vs Zr ─────────────────────

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

def plot_frost(gd, out_dir=None, save=True):
    """Frost et al. (2001) Fe-number vs SiO₂ 铁质-镁质花岗岩分类
    所需元素: SiO2, MgO, FeO(T) 或 TFe2O3
    """
    missing = gd.check_elements('SiO2', 'MgO', strict=True)
    if 'FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data:
        return None, None
    sio2 = gd.get('SiO2'); mgo = gd.get('MgO')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels
    denom = feo_t + mgo
    fe_num = np.where(denom > 0, feo_t / denom, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    # Frost (2001) 分界: Fe* = 0.8 (铁质/镁质分界)
    ax.axhline(0.8, 0, 1, color='k', ls='--', lw=1.5)
    ax.axhline(0.6, 0, 1, color='k', ls=':', lw=0.8)
    ax.axvline(56, 0, 1, color='grey', ls=':', lw=0.8)
    ax.axvline(71, 0, 1, color='grey', ls=':', lw=0.8)

    ax.text(40, 0.9, 'Ferroan', fontsize=11, ha='left', style='italic')
    ax.text(40, 0.65, 'Magnesian', fontsize=11, ha='left', style='italic')

    _style.scatter_samples(ax, sio2, fe_num, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(40, 80); ax.set_ylim(0.3, 1.0)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'FeO$_t$/(FeO$_t$+MgO)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Frost2001_Fenum_SiO2.png', out_dir)
    return fig, ax


# ── Whalen (1987) Ga/Al A-type 判别图（三张）────────────

# Whalen 1: 10000*Ga/Al vs Zr

def plot_whalen1(gd, out_dir=None, save=True):
    """Whalen et al. (1987) 10000*Ga/Al vs Zr A型花岗岩判别
    所需元素: Ga, Al (or Al2O3), Zr
    """
    missing = gd.check_elements('Ga', 'Al2O3', 'Zr', strict=True)
    if missing:
        return None, None
    ga = gd.get('Ga'); al2o3 = gd.get('Al2O3'); zr = gd.get('Zr')
    labels = gd.labels
    # Ga/Al = Ga / (Al2O3 * 2*26.98/101.96) ≈ Ga / (Al2O3 * 0.529)
    # 10000*Ga/Al
    ga_al = ga / (al2o3 * 0.529)
    ga_al_10k = ga_al * 10000
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.axhline(2.6, 0, 1, color='k', ls='--', lw=1.2, label='A-type boundary')
    ax.axhline(4.0, 0, 1, color='grey', ls=':', lw=0.8)

    ax.text(5, 4.5, 'A-type', fontsize=10, ha='left', style='italic')
    ax.text(5, 1.5, 'I, S, M-type', fontsize=10, ha='left', style='italic')

    _style.scatter_samples(ax, zr, ga_al_10k, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log')
    ax.set_xlim(10, 2000); ax.set_ylim(0.5, 20)
    _style.style_ax(ax, 'Zr (ppm)', r'10000$\times$Ga/Al')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Whalen1987_GaAl_Zr.png', out_dir)
    return fig, ax


# Whalen 2: 10000*Ga/Al vs Nb

def plot_whalen2(gd, out_dir=None, save=True):
    """Whalen et al. (1987) 10000*Ga/Al vs Nb A型花岗岩判别
    所需元素: Ga, Al2O3, Nb
    """
    missing = gd.check_elements('Ga', 'Al2O3', 'Nb', strict=True)
    if missing:
        return None, None
    ga = gd.get('Ga'); al2o3 = gd.get('Al2O3'); nb = gd.get('Nb')
    labels = gd.labels
    ga_al = ga / (al2o3 * 0.529)
    ga_al_10k = ga_al * 10000
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.axhline(2.6, 0, 1, color='k', ls='--', lw=1.2, label='A-type boundary')

    ax.text(0.5, 4.5, 'A-type', fontsize=10, ha='left', style='italic')
    ax.text(0.5, 1.5, 'I, S, M-type', fontsize=10, ha='left', style='italic')

    _style.scatter_samples(ax, nb, ga_al_10k, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log')
    ax.set_xlim(1, 500); ax.set_ylim(0.5, 20)
    _style.style_ax(ax, 'Nb (ppm)', r'10000$\times$Ga/Al')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Whalen1987_GaAl_Nb.png', out_dir)
    return fig, ax


# Whalen 3: 10000*Ga/Al vs Ce

def plot_whalen3(gd, out_dir=None, save=True):
    """Whalen et al. (1987) 10000*Ga/Al vs Ce+Y+Zr A型花岗岩判别
    所需元素: Ga, Al2O3, Ce, Y, Zr
    """
    missing = gd.check_elements('Ga', 'Al2O3', 'Ce', 'Y', 'Zr', strict=True)
    if missing:
        return None, None
    ga = gd.get('Ga'); al2o3 = gd.get('Al2O3')
    ce = gd.get('Ce'); y = gd.get('Y'); zr = gd.get('Zr')
    labels = gd.labels
    ga_al = ga / (al2o3 * 0.529)
    ga_al_10k = ga_al * 10000
    ce_y_zr = ce + y + zr
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.axhline(2.6, 0, 1, color='k', ls='--', lw=1.2, label='A-type boundary')
    ax.axhline(4.0, 0, 1, color='grey', ls=':', lw=0.8)

    ax.text(10, 4.5, 'A-type', fontsize=10, ha='left', style='italic')
    ax.text(10, 1.5, 'I, S, M-type', fontsize=10, ha='left', style='italic')

    _style.scatter_samples(ax, ce_y_zr, ga_al_10k, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log')
    ax.set_xlim(10, 5000); ax.set_ylim(0.5, 20)
    _style.style_ax(ax, 'Ce+Y+Zr (ppm)', r'10000$\times$Ga/Al')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Whalen1987_GaAl_CeYZr.png', out_dir)
    return fig, ax


# ── Sylvester (1989) CaO/Na2O vs Al2O3 ────────────────────

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

def plot_villaseca(gd, out_dir=None, save=True):
    """Villaseca et al. (1998) ASI vs FMM 花岗岩源区分类
    ASI = Al2O3/(CaO+Na2O+K2O) 摩尔比
    FMM = (FeOt+MgO)/(TiO2+Al2O3) × 100
    所需元素: Al2O3, CaO, Na2O, K2O, MgO, TiO2, FeO(T) 或 TFe2O3
    """
    missing = gd.check_elements('Al2O3', 'CaO', 'Na2O', 'K2O', 'MgO', 'TiO2', strict=True)
    if missing:
        return None, None
    if 'FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data:
        return None, None
    al2o3 = gd.get('Al2O3'); cao = gd.get('CaO')
    na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    mgo = gd.get('MgO'); tio2 = gd.get('TiO2')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels

    # 摩尔比 ASI = Al2O3 / (CaO + Na2O + K2O)
    asi = (al2o3 / 101.96) / ((cao / 56.08) + (na2o / 61.98) + (k2o / 94.20))
    # FMM = (FeOt + MgO) / (TiO2 + Al2O3) × 100 (wt%)
    fmm = (feo_t + mgo) / (tio2 + al2o3) * 100
    fig, ax = plt.subplots(figsize=(9, 7))

    # Villaseca (1998) 分界
    ax.axhline(1.0, 0, 1, color='k', ls='--', lw=1.2)
    ax.axvline(2.0, 0, 1, color='k', ls='--', lw=0.8)
    ax.axvline(10, 0, 1, color='k', ls=':', lw=0.8)

    ax.text(0.5, 1.4, 'Peraluminous', fontsize=9, ha='center', style='italic')
    ax.text(0.5, 0.8, 'Metaluminous', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, fmm, asi, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 50); ax.set_ylim(0.5, 2.0)
    _style.style_ax(ax, 'FMM (FeO$_t$+MgO)/(TiO$_2$+Al$_2$O$_3$)×100', 'ASI')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Villaseca1998_ASI_FMM.png', out_dir)
    return fig, ax


# ════════════════════════════════════════════════════════════
# 4. 花岗岩专题图
# ════════════════════════════════════════════════════════════

# ── Debon & Le Fort (1983) B-A 图 ────────────────────────

def plot_debonba(gd, out_dir=None, save=True):
    """Debon & Le Fort (1983) B-A 花岗岩矿物分类图
    B = Fe+Mg+Ti, A = Al-(K+Na+2Ca)
    所需元素: Al2O3, K2O, Na2O, CaO, FeO(T), MgO, TiO2
    """
    needed = ('Al2O3', 'K2O', 'Na2O', 'CaO', 'MgO', 'TiO2')
    missing = gd.check_elements(*needed, strict=True)
    if missing or ('FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data):
        return None, None
    al2o3 = gd.get('Al2O3'); k2o = gd.get('K2O')
    na2o = gd.get('Na2O'); cao = gd.get('CaO')
    mgo = gd.get('MgO'); tio2 = gd.get('TiO2')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels

    # 原子数 (milliatoms/100g): Al = Al2O3*2000/101.96, K = K2O*2000/94.20, ...
    al = al2o3 * 2000 / 101.96
    k = k2o * 2000 / 94.20
    na = na2o * 2000 / 61.98
    ca = cao * 2000 / 56.08
    fe = feo_t * 2000 / 71.84
    mg = mgo * 2000 / 40.30
    ti = tio2 * 2000 / 79.87
    b = (fe + mg + ti) / 100  # 除以100使数值范围合理
    a = (al - (k + na + 2*ca)) / 100
    fig, ax = plt.subplots(figsize=(10, 8))

    # Debon B-A 分界线（经验值）
    ax.axvline(0, 0, 1, color='k', lw=0.5)
    ax.axhline(0, 0, 1, color='k', lw=0.5)
    # 分区标注
    ax.fill_between([-100, 0], 0, 100, alpha=0.05, color='blue')
    ax.fill_between([0, 50], 0, 100, alpha=0.05, color='red')
    ax.text(-30, 50, 'Per.\n domain', fontsize=10, ha='center', style='italic')
    ax.text(20, 50, 'Metal.\n domain', fontsize=10, ha='center', style='italic')

    _style.scatter_samples(ax, a, b, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-60, 40); ax.set_ylim(0, 80)
    _style.style_ax(ax, 'A = Al-(K+Na+2Ca) (×10$^{-2}$)', 'B = Fe+Mg+Ti (×10$^{-2}$)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Debon1983_BA_diagram.png', out_dir)
    return fig, ax


# ── Debon & Le Fort (1983) P-Q 图 ─────────────────────────

def plot_debonpq(gd, out_dir=None, save=True):
    """Debon & Le Fort (1983) P-Q 花岗岩分类图
    P = K-(Na+Ca), Q = Si/3-(K+Na+2Ca/3), 原子数
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
    p = (k - (na + ca)) / 100
    q = (si/3 - (k + na + 2*ca/3)) / 100
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.axhline(0, 0, 1, color='k', lw=0.5)
    ax.axvline(0, 0, 1, color='k', lw=0.5)

    # 标注典型矿物区
    ax.text(-20, 50, 'Ksp\n domain', fontsize=9, ha='center', style='italic', alpha=0.5)
    ax.text(20, 50, 'Plag\n domain', fontsize=9, ha='center', style='italic', alpha=0.5)

    _style.scatter_samples(ax, p, q, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-40, 30); ax.set_ylim(-20, 80)
    _style.style_ax(ax, 'P = K-(Na+Ca) (×10$^{-2}$)', 'Q = Si/3-(K+Na+2Ca/3) (×10$^{-2}$)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Debon1983_PQ_diagram.png', out_dir)
    return fig, ax


# ── Schandl (2004) Y vs Zr ────────────────────────────────

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

def plot_mullerkbinary(gd, out_dir=None, save=True):
    """Muller et al. (1992) K₂O vs SiO₂ 岩浆系列判别
    所需元素: SiO2, K2O
    """
    missing = gd.check_elements('SiO2', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); k2o = gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(9, 7))

    # Muller (1992) 分界: 低K/中K/高K
    xs = np.linspace(45, 65, 30)
    ax.plot(xs, 0.02*xs + 0.1, 'k-', lw=1.2, label='Low-K / Medium-K')
    ax.plot(xs, 0.08*xs - 2.2, 'k--', lw=1.2, label='Medium-K / High-K')
    ax.plot(xs, 0.12*xs - 3.8, 'k:', lw=1.0, label='High-K / Shoshonite')

    ax.text(48, 0.3, 'Low-K\n(tholeiitic)', fontsize=8, ha='center')
    ax.text(48, 0.9, 'Medium-K\n(calc-alkaline)', fontsize=8, ha='center')
    ax.text(48, 1.8, 'High-K', fontsize=8, ha='center')
    ax.text(48, 3.0, 'Shoshonite', fontsize=8, ha='center', rotation=10)

    _style.scatter_samples(ax, sio2, k2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(45, 65); ax.set_ylim(0, 5)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Muller1992_K2O_SiO2.png', out_dir)
    return fig, ax


# ── Hollocher (2012) V/Sc vs V+Sc ─────────────────────────

def plot_hollocher1(gd, out_dir=None, save=True):
    """Hollocher et al. (2012) V/Sc vs V+Sc 弧岩浆氧化条件判别
    所需元素: V, Sc
    """
    missing = gd.check_elements('V', 'Sc', strict=True)
    if missing:
        return None, None
    v = gd.get('V'); sc = gd.get('Sc')
    labels = gd.labels
    v_sc = np.where(sc > 0, v / sc, np.nan)
    v_plus_sc = v + sc
    fig, ax = plt.subplots(figsize=(9, 7))

    ax.axhline(10, 0, 1, color='k', ls='--', lw=1.0, label='oxidized / reduced')
    ax.text(200, 15, 'Oxidized arc', fontsize=9, ha='center', style='italic')
    ax.text(200, 5, 'Reduced arc', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, v_plus_sc, v_sc, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(50, 1000); ax.set_ylim(0, 40)
    _style.style_ax(ax, 'V+Sc (ppm)', 'V/Sc')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Hollocher2012_VSc.png', out_dir)
    return fig, ax


# ── Hollocher (2012) V/Sc vs Zr/Ce ─────────────────────────

def plot_hollocher2(gd, out_dir=None, save=True):
    """Hollocher et al. (2012) Zr/Ce vs V/Sc 弧岩浆分类
    所需元素: V, Sc, Zr, Ce
    """
    missing = gd.check_elements('V', 'Sc', 'Zr', 'Ce', strict=True)
    if missing:
        return None, None
    v = gd.get('V'); sc = gd.get('Sc')
    zr = gd.get('Zr'); ce = gd.get('Ce')
    labels = gd.labels
    v_sc = np.where(sc > 0, v / sc, np.nan)
    zr_ce = np.where(ce > 0, zr / ce, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))

    _style.scatter_samples(ax, zr_ce, v_sc, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 20); ax.set_ylim(0, 40)
    _style.style_ax(ax, 'Zr/Ce', 'V/Sc')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Hollocher2012_VSc_ZrCe.png', out_dir)
    return fig, ax


# ════════════════════════════════════════════════════════════
# 5. 其他专题图 — 分类 / 判别
# ════════════════════════════════════════════════════════════

# ── Hastie et al. (2007) Co-Th 系列判别（已有Co-Th参考）───

def plot_hastie(gd, out_dir=None, save=True):
    """Hastie et al. (2007) Th-Co 弧岩浆系列判别图
    所需元素: Th, Co
    """
    missing = gd.check_elements('Th', 'Co', strict=True)
    if missing:
        return None, None
    th = gd.get('Th'); co = gd.get('Co')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(9, 7))

    xs = np.linspace(0, 100, 50)
    # 分界线: 拉斑/钙碱, 钙碱/高K钙碱
    ax.plot(xs, -0.5*xs + 30, 'k-', lw=1.2, label='Tholeiitic / Calc-alkaline')
    ax.plot(xs, -0.3*xs + 35, 'k--', lw=0.8, label='CA / High-K CA')

    ax.text(10, 5, 'Tholeiitic', fontsize=9, ha='center', style='italic')
    ax.text(30, 15, 'Calc-alkaline', fontsize=9, ha='center', style='italic')
    ax.text(10, 25, 'High-K CA', fontsize=9, ha='center', style='italic')

    _style.scatter_samples(ax, th, co, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 30); ax.set_ylim(0, 50)
    _style.style_ax(ax, 'Th (ppm)', 'Co (ppm)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Hastie2007_Th_Co.png', out_dir)
    return fig, ax


# ── Maniar & Piccoli (1989) 判别图 ────────────────────────

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

def plot_larocheplut(gd, out_dir=None, save=True):
    """La Roche et al. (1980) R1-R2 侵入岩分类图
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
    r1 = (4*si - 11*(na+k) - 2*(fe+ti)) / 100
    r2 = (al + 2*mg + 6*ca) / 100
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.axhline(0, 0, 1, color='k', lw=0.5)
    ax.axvline(0, 0, 1, color='k', lw=0.5)

    _style.scatter_samples(ax, r1, r2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-30, 40); ax.set_ylim(-20, 30)
    _style.style_ax(ax, 'R1', 'R2')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'LaRoche1980_R1_R2_plutonic.png', out_dir)
    return fig, ax


# ── La Roche (1980) 火山岩 R1-R2 ──────────────────────────

def plot_larochevolc(gd, out_dir=None, save=True):
    """La Roche et al. (1980) R1-R2 火山岩分类图
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
    r1 = (4*si - 11*(na+k) - 2*(fe+ti)) / 100
    r2 = (al + 2*mg + 6*ca) / 100
    fig, ax = plt.subplots(figsize=(10, 8))

    ax.axhline(0, 0, 1, color='k', lw=0.5)
    ax.axvline(0, 0, 1, color='k', lw=0.5)

    _style.scatter_samples(ax, r1, r2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-30, 40); ax.set_ylim(-20, 30)
    _style.style_ax(ax, 'R1', 'R2')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'LaRoche1980_R1_R2_volcanic.png', out_dir)
    return fig, ax


# ── Middlemost (1991) 侵入岩分类 ──────────────────────────

def plot_middlemostplut(gd, out_dir=None, save=True):
    """Middlemost (1991) Na2O+K2O vs SiO2 侵入岩分类图
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))

    xs = np.linspace(42, 80, 20)
    ax.plot(xs, 0.07*xs - 1.8, 'k-', lw=0.8)
    ax.plot([45, 95], [5, 5], 'k--', lw=0.8)
    ax.plot([45, 95], [9.5, 17], 'k--', lw=0.8)

    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(35, 82); ax.set_ylim(0, 18)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Middlemost1991_Plutonic.png', out_dir)
    return fig, ax


# ── Peccerillo & Taylor (1976) K2O-SiO2 ──────────────────

def plot_pecetaylor(gd, out_dir=None, save=True):
    """Peccerillo & Taylor (1976) K₂O vs SiO₂ 系列判别图
    所需元素: SiO2, K2O
    """
    missing = gd.check_elements('SiO2', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); k2o = gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(9, 7))

    xs = np.linspace(45, 78, 50)
    # Peccerillo & Taylor (1976) 分界
    ax.plot([45, 78], [0.4, 1.9], 'k-', lw=1.2, label='Low-K / Medium-K')
    ax.plot([45, 78], [1.8, 3.8], 'k--', lw=1.0, label='Medium-K / High-K')
    ax.plot([45, 61], [2.8, 4.7], 'k:', lw=0.8, label='High-K / Shoshonite')

    _style.scatter_samples(ax, sio2, k2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(45, 78); ax.set_ylim(0, 6)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Peccerillo_Taylor1976_K2O_SiO2.png', out_dir)
    return fig, ax


# ── La/Yb vs Yb 判别图 ────────────────────────────────────

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
