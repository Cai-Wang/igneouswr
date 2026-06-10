"""
_classification.py — 岩石系列 / 分类图（10 个绘图函数）
  原有: TAS, K2O-SiO2, AFM, Shand, W&F, Co-Th, An-Ab-Or, QAPF
  新增 RockPlot SVG: Cabanis, Mullen, Jensen, OConnorVolc, OhtaArai, Pearce1977
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import igneous_wr.report.style as _style
from igneous_wr.core.chem import feot_calc
from igneous_wr.core.ternary import ternary_to_xy, ternary_corners, draw_ternary_frame, draw_ternary_grid, draw_ternary_ticks, label_ternary_vertices
from igneous_wr.boundaries.core import load_boundary

def plot_co_th(gd, out_dir=None, save=True):
    """Th–Co 岩浆系列+岩性判别图（Hastie et al., 2007, Fig. 7）
    X=Co (ppm), 反向坐标（70→0 高Co在左）
    Y=Th (ppm), 对数坐标（GCDkit 标准）
    四套分界线均为直线端点坐标：
      系列: IAT/CA/HK-SHO
      岩性: B/BA+A/D+R
    所需元素: Co, Th
    """
    missing = gd.check_elements('Co', 'Th', strict=True)
    if missing:
        return (None, None)
    co = gd.get('Co')
    th = gd.get('Th')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(9, 8))

    # Y轴对数，X轴反向（与 GCDkit Hastie.r 一致）
    ax.set_yscale('log')
    ax.set_xlim(70, 0)
    ax.set_ylim(0.01, 100)

    # 系列分界线（坐标与 GCDkit 一致）
    ax.plot([70, 0], [0.245, 1.35], color='#333333', lw=1.5, zorder=3)          # IAT / CA
    ax.plot([70, 0], [2.2, 9], color='#333333', lw=1.2, linestyle='--', dashes=(6, 3), zorder=3)  # CA / HK-CA+SHO
    # 岩性分界线
    ax.plot([38.4, 24], [0.01, 100], color='#666666', lw=1.2, zorder=3)          # B / BA+A
    ax.plot([23, 7], [0.01, 100], color='#666666', lw=1.2, zorder=3)             # BA+A / D+R*

    # 系列标注
    ax.text(68, 0.1, 'Tholeiite\nSeries', fontsize=10, fontweight='bold',
            color='#444444', ha='left', va='center')
    ax.text(68, 1.0, 'Calc-alkaline\nSeries', fontsize=10, fontweight='bold',
            color='#444444', ha='left', va='center')
    ax.text(68, 60, 'High-K calc-alkaline\nand Shoshonite Series',
            fontsize=10, fontweight='bold', color='#444444', ha='left', va='center')

    # 岩性标注（vs GCDkit adj=0.5 → va='center'）
    ax.text(50, 0.02, 'B', fontsize=10, fontweight='bold', color='#444444',
            ha='center', va='center')
    ax.text(30, 0.02, 'BA/A', fontsize=10, fontweight='bold', color='#444444',
            ha='center', va='center')
    ax.text(10, 0.02, 'D/R*', fontsize=10, fontweight='bold', color='#444444',
            ha='center', va='center')

    _style.scatter_samples(ax, co, th, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xticks(range(0, 71, 10))
    ax.set_yticks([0.01, 0.1, 1, 10, 100])
    ax.set_yticklabels(['0.01', '0.1', '1', '10', '100'])
    _style.style_ax(ax, 'Co (ppm)', 'Th (ppm)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Co_Th_Hastie2007.png', out_dir)
    return (fig, ax)

def plot_tas(gd, out_dir=None, save=True):
    """TAS 全碱-硅分类图（Middlemost 1994，改编自 Le Bas & Streckeisen 1991）
    多边形坐标源自 GCDkit TASMiddlemostVolc.r
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    na2o = gd.get('Na2O')
    k2o = gd.get('K2O')
    alk = na2o + k2o
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7))
    _tas_data = load_boundary('cls', 'tas')
    _TAS_FIELDS = {k: [tuple(p) for p in v] for k, v in _tas_data['fields'].items()}
    _TAS_LABELS = _tas_data['labels']
    for name, poly in _TAS_FIELDS.items():
        n = len(poly)
        for i in range(n):
            seg = tuple(sorted([poly[i], poly[(i + 1) % n]]))
            ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], color='#333333', lw=0.8, zorder=2)
    # 文本标签（纯分类区，无视觉边界）
    _text_only = _tas_data.get('text_only', {})
    for label, (tx, ty) in _text_only.items():
        ax.text(tx, ty, label, ha='center', va='center', fontsize=8, fontweight='normal',
                color='#666666', style='italic', zorder=5)
    for name, poly in _TAS_FIELDS.items():
        cx = sum((p[0] for p in poly)) / len(poly)
        cy = sum((p[1] for p in poly)) / len(poly)
        label = _TAS_LABELS.get(name, name)
        ax.text(cx, cy, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#444444', zorder=5)
    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(34, 90)
    ax.set_ylim(0, 19)
    ax.set_xticks(range(35, 95, 5))
    _style.style_ax(ax, 'SiO$_2$ (wt.%)', 'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'CLS-01_TAS_Middlemost1994_Volcanic.png', out_dir)
    return (fig, ax)

def plot_k2o_sio2(gd, out_dir=None, save=True):
    """K₂O–SiO₂ 钾系列分类图（Middlemost, 1985, 图9）
    所需元素: SiO2, K2O
    分界线: Low-K, Medium-K, High-K, Shoshonitic
    界线端点坐标参考 Middlemost (1985)
    """
    missing = gd.check_elements('SiO2', 'K2O', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    k2o = gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.plot([45, 75], [0.5, 2.5], color='#333333', lw=1.5, zorder=3)
    ax.plot([50, 75], [1.5, 4.0], color='#666666', lw=1.2, linestyle='--', zorder=3)
    ax.plot([55, 75], [2.5, 6.0], color='#666666', lw=1.2, linestyle='-.', zorder=3)
    # 标签位置参考 GCDkit Peccerillo & Taylor 1976 风格：
    # 前 3 个在右边缘右对齐 (adj=c(1,0.5))，Shoshonite 在左边缘左对齐 (adj=c(0,0.5))
    # 垂直位置 = 各区间在 x=80 处的 y 中点
    ax.text(80, 1.4, 'Low-K\nTholeiitic', fontsize=10, ha='right', va='center', color='#444444', fontweight='bold', zorder=4)
    ax.text(80, 3.7, 'Medium-K\nCalc-alkaline', fontsize=10, ha='right', va='center', color='#444444', fontweight='bold', zorder=4)
    ax.text(80, 5.7, 'High-K\nCalc-alkaline', fontsize=10, ha='right', va='center', color='#444444', fontweight='bold', zorder=4)
    ax.text(44, 7.4, 'Shoshonitic', fontsize=10, ha='left', va='center', color='#444444', fontweight='bold', zorder=4)
    _style.scatter_samples(ax, sio2, k2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(42, 82)
    ax.set_ylim(0, 8)
    _style.style_ax(ax, 'SiO$_2$ (wt.%)', 'K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Middlemost1985_K2O_SiO2.png', out_dir)
    return (fig, ax)

def plot_k2o_sio2_peccerillo(gd, out_dir=None, save=True):
    """K₂O–SiO₂ 钾系列分类图（Peccerillo & Taylor, 1976, Fig.2）
    多段折线边界，源自 GCDkit PeceTaylor.r extrapolated=TRUE 坐标
    所需元素: SiO2, K2O
    标签布局参考 GCDkit temp3 风格（右侧右对齐 + Shoshonite 左侧左对齐）
    """
    missing = gd.check_elements('SiO2', 'K2O', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    k2o = gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(8, 7))
    # Tholeiite / Calc-alkaline boundary
    ax.plot([48, 52, 56, 63, 70, 78], [0.3, 0.5, 0.7, 1, 1.3, 1.6],
            color='#333333', lw=1.5, zorder=3)
    # Calc-alkaline / High-K boundary
    ax.plot([48, 52, 56, 63, 70, 75], [1.2, 1.5, 1.8, 2.4, 3, 3.43],
            color='#666666', lw=1.2, linestyle='--', zorder=3)
    # High-K / Shoshonite boundary
    ax.plot([48, 52, 56, 63, 70], [1.6, 2.4, 3.2, 4, 4.8],
            color='#666666', lw=1.2, linestyle='-.', zorder=3)
    # Labels (GCDkit PeceTaylor.r temp3 style)
    ax.text(77, 0.7, 'Tholeiite Series', fontsize=10, ha='right', va='center',
            color='#444444', fontweight='bold', zorder=4)
    ax.text(77, 2.4, 'Calc-alkaline\nSeries', fontsize=10, ha='right', va='center',
            color='#444444', fontweight='bold', zorder=4)
    ax.text(77, 4, 'High-K calc-alkaline\nSeries', fontsize=10, ha='right', va='center',
            color='#444444', fontweight='bold', zorder=4)
    ax.text(47, 4.5, 'Shoshonite Series', fontsize=10, ha='left', va='center',
            color='#444444', fontweight='bold', zorder=4)
    _style.scatter_samples(ax, sio2, k2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(45, 78)
    ax.set_ylim(0, 7)
    _style.style_ax(ax, 'SiO$_2$ (wt.%)', 'K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'CLS-04_PeccerilloTaylor1976_K2O_SiO2.png', out_dir)
    return (fig, ax)

def plot_afm(gd, out_dir=None, save=True):
    """AFM 三角图（Irvine & Baragar, 1971）
    A=Na₂O+K₂O, F=FeO*, M=MgO
    布局：F 顶角，A 左下，M 右下
    分界线 9 点坐标：来自 GCDkit AFM.r (equ=FALSE, Rickwood 1989 引用版)
    所需元素: Na2O, K2O, MgO, (FeO / TFe2O3)
    """
    missing = gd.check_elements('Na2O', 'K2O', 'MgO', strict=True)
    if missing:
        return (None, None)
    na2o = gd.get('Na2O')
    k2o = gd.get('K2O')
    mgo = gd.get('MgO')
    feo = gd.get('FeO')
    tfe2 = gd.get('TFe2O3')
    labels = gd.labels
    a = na2o + k2o
    f = feot_calc(feo, tfe2)
    m = mgo
    total = a + f + m
    valid = (total > 0) & ~np.isnan(total)
    a_p = np.where(valid, a / total * 100, 0)
    f_p = np.where(valid, f / total * 100, 0)
    m_p = np.where(valid, m / total * 100, 0)
    x_d = np.where(valid, ternary_to_xy(f_p, a_p, m_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(f_p, a_p, m_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    _xx = [0.231, 0.312, 0.436, 0.473, 0.513, 0.542, 0.5555, 0.617, 0.675]
    _yy = [0.3135012, 0.3671948, 0.4641896, 0.4728499, 0.4728499, 0.4572614, 0.442539, 0.375855, 0.3031089]
    ax.plot(_xx, _yy, color='#333333', lw=1.5, zorder=5)
    ax.text(0.5, 0.53, 'Tholeiite Series', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=6)
    ax.text(0.5, 0.1, 'Calc-Alkaline Series', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=6)
    label_ternary_vertices(ax, 'FeO*', 'Na$_2$O+K$_2$O', 'MgO')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.08, 1.1)
    ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'AFM_IB1971.png', out_dir)
    return (fig, ax)

def plot_winchester_floyd(gd, out_dir=None, save=True):
    """Winchester & Floyd (1977) Zr/TiO2–Nb/Y 火山岩分类图
    精细底图 v11 — 67 节点 × 9 条校正边界线
    所需元素: Zr, TiO2, Nb, Y
    """
    missing = gd.check_elements('Zr', 'TiO2', 'Nb', 'Y', strict=True)
    if missing:
        return (None, None)
    zr = gd.get('Zr')
    tio2 = gd.get('TiO2')
    nb = gd.get('Nb')
    yi = gd.get('Y')
    labels = gd.labels
    zr_tio2 = np.where(tio2 > 0, zr / tio2, np.nan)
    nb_yi = np.where(yi > 0, nb / yi, np.nan)
    fig, ax = plt.subplots(figsize=(10, 7))
    _wf_data = load_boundary('cls', 'winchester_floyd')
    _WF_NODES = {int(k): v for k, v in _wf_data['nodes'].items()}
    _WF_EDGES = _wf_data['edges']
    _WF_LABELS = _wf_data['labels']
    for edge in _WF_EDGES:
        xs = [_WF_NODES[n][0] for n in edge]
        ys = [_WF_NODES[n][1] for n in edge]
        ax.plot(xs, ys, color='#333333', linewidth=1.5, linestyle='-', solid_capstyle='round', zorder=2)
    for label in _WF_LABELS:
        rx, ry, text = (label['x'], label['y'], label['text'])
        ax.text(rx, ry, text, fontsize=9.5, color='#444444', ha='center', va='center', fontweight='normal', zorder=3)
    _style.scatter_samples(ax, nb_yi, zr_tio2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.01, 15)
    ax.set_ylim(0.001, 10)
    ax.set_xticks([0.01, 0.1, 1, 10])
    ax.set_xticklabels(['0.01', '0.1', '1', '10'])
    ax.set_yticks([0.001, 0.01, 0.1, 1, 10])
    ax.set_yticklabels(['0.001', '0.01', '0.1', '1', '10'])
    _style.style_ax(ax, 'Nb/Y', 'Zr/TiO$_2$')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Winchester_Floyd1977_NbY_ZrTiO2.png', out_dir)
    return (fig, ax)

def plot_mullen(gd, out_dir=None, save=True):
    """Mullen (1983) TiO₂-10×MnO-10×P₂O₅ 基性岩构造判别三角图
    三条实线(L1 L2)+一条虚线(L4)划分6个区:
      OIT / MORB / IAT / CAB / OIA / BON
    对应端点:
      A(77,23,0) B(29,30,41) C(0,8,92)
      D(59,41,0) E(27,41,32) F(26.87,28.36,44.78)
      G(39,61,0) H(18,61,21) I(18,22,60)
      J(45,0,55)
    L1(solid): A→B→C (m0)
    L2(solid): D→E→F (m1)
    L3(dashed): G→H→I (m2)
    L4(dashed): B→J  (m3)
    所需元素: TiO2, MnO, P2O5
    """
    missing = gd.check_elements('TiO2', 'MnO', 'P2O5', strict=True)
    if missing:
        return (None, None)
    tio2 = gd.get('TiO2')
    mno = gd.get('MnO')
    p2o5 = gd.get('P2O5')
    labels = gd.labels
    a = tio2
    b = mno * 10.0
    c = p2o5 * 10.0
    total = a + b + c
    valid = (total > 0) & ~np.isnan(total)
    a_p = np.where(valid, a / total * 100, 0)
    b_p = np.where(valid, b / total * 100, 0)
    c_p = np.where(valid, c / total * 100, 0)
    x_d = np.where(valid, ternary_to_xy(a_p, b_p, c_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(a_p, b_p, c_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)
    _mullen_raw = load_boundary('cls', 'mullen')
    _mullen_curves = _mullen_raw['curves']
    m0_xy = ternary_to_xy(np.array(_mullen_curves['m0']['a']), np.array(_mullen_curves['m0']['b']), np.array(_mullen_curves['m0']['c']))
    m1_xy = ternary_to_xy(np.array(_mullen_curves['m1']['a']), np.array(_mullen_curves['m1']['b']), np.array(_mullen_curves['m1']['c']))
    m2_xy = ternary_to_xy(np.array(_mullen_curves['m2']['a']), np.array(_mullen_curves['m2']['b']), np.array(_mullen_curves['m2']['c']))
    m3_xy = ternary_to_xy(np.array(_mullen_curves['m3']['a']), np.array(_mullen_curves['m3']['b']), np.array(_mullen_curves['m3']['c']))
    ax.plot(m0_xy[0], m0_xy[1], color='#333333', lw=1.5, zorder=4)
    ax.plot(m1_xy[0], m1_xy[1], color='#333333', lw=1.5, zorder=4)
    ax.plot(m2_xy[0], m2_xy[1], color='#666666', lw=1.2, linestyle='--', zorder=4)
    ax.plot(m3_xy[0], m3_xy[1], color='#666666', lw=1.2, linestyle='--', zorder=4)
    lbl_oit = ternary_to_xy(np.array([57.7]), np.array([16.1]), np.array([26.1]))
    ax.text(lbl_oit[0][0], lbl_oit[1][0], 'OIT', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=5)
    lbl_iat = ternary_to_xy(np.array([34.6]), np.array([50.7]), np.array([14.7]))
    ax.text(lbl_iat[0][0], lbl_iat[1][0], 'IAT', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=5)
    lbl_morb = ternary_to_xy(np.array([46.2]), np.array([33.9]), np.array([19.9]))
    ax.text(lbl_morb[0][0], lbl_morb[1][0], 'MORB', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=5)
    lbl_cab = ternary_to_xy(np.array([11.5]), np.array([49.2]), np.array([39.2]))
    ax.text(lbl_cab[0][0], lbl_cab[1][0], 'CAB', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=5)
    lbl_oia = ternary_to_xy(np.array([25.4]), np.array([10.3]), np.array([64.3]))
    ax.text(lbl_oia[0][0], lbl_oia[1][0], 'OIA', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=5)
    lbl_bon = ternary_to_xy(np.array([17.3]), np.array([71.3]), np.array([11.3]))
    ax.text(lbl_bon[0][0], lbl_bon[1][0], 'Bon', fontsize=11, ha='center', va='center', color='#444444', fontweight='bold', zorder=5)
    label_ternary_vertices(ax, 'TiO$_2$', '10×MnO', '10×P$_2$O$_5$')
    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.08, 1.1)
    ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Mullen1983_TiO2_MnO_P2O5.png', out_dir)
    return (fig, ax)

def plot_tasmiddlemostplut(gd, out_dir=None, save=True):
    """TAS Plutonic (Middlemost 1994) — 深成岩全碱-硅分类图
    多边形坐标源自 GCDkit 6.3.0 TASMiddlemostPlut.r 源码翻译
    16 个主分类区，无叠加层
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(10, 7.5))
    _mm_data = load_boundary('cls', 'tas_middlemost_plut')
    _MM_FIELDS = {k: [tuple(p) for p in v] for k, v in _mm_data['fields'].items()}
    _MM_LABELS = _mm_data['labels']
    for name, poly in _MM_FIELDS.items():
        n = len(poly)
        for i in range(n):
            seg = tuple(sorted([poly[i], poly[(i + 1) % n]]))
            ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]], color='#333333', lw=0.6, zorder=4)
    for name, poly in _MM_FIELDS.items():
        cx = sum((p[0] for p in poly)) / len(poly)
        cy = sum((p[1] for p in poly)) / len(poly)
        label = _MM_LABELS.get(name, name)
        ax.text(cx, cy, label, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#444444', zorder=6)
    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(34, 90)
    ax.set_ylim(0, 19)
    ax.set_xticks(range(35, 95, 5))
    ax.set_yticks(range(0, 21, 3))
    _style.style_ax(ax, 'SiO$_2$ (wt.%)', 'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS_Middlemost1994_Plutonic.png', out_dir)
    return (fig, ax)

def plot_frost_fenr(gd, out_dir=None, save=True):
    """Frost et al. (2001) SiO₂ vs Fe# (FeOt/(FeOt+MgO)) 铁质-镁质花岗岩分类
    精确还原 GCDkit Frost.r Plot 1:
      边界: y = 0.486 + 0.0046 * SiO₂ (FeOt 模式)
      x: 50-80, y: 0-1
      ferroan (上) / magnesian (下)
    所需元素: SiO2, MgO, FeO(T) 或 TFe2O3
    """
    missing = gd.check_elements('SiO2', 'MgO', strict=True)
    if 'FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data:
        return (None, None)
    sio2 = gd.get('SiO2')
    mgo = gd.get('MgO')
    feo_t = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
    labels = gd.labels
    denom = feo_t + mgo
    fe_num = np.where(denom > 0, feo_t / denom, np.nan)
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(50, 80)
    ax.set_ylim(0, 1)
    x_line = np.linspace(50, 77, 50)
    y_line = 0.486 + 0.0046 * x_line
    ax.plot(x_line, y_line, color='#333333', lw=1.5, zorder=4)
    ax.text(60, 0.9, 'ferroan', fontsize=10, ha='center', va='center',
            color='#444444', fontweight='bold', zorder=5)
    ax.text(60, 0.6, 'magnesian', fontsize=10, ha='center', va='center',
            color='#444444', fontweight='bold', zorder=5)
    _style.scatter_samples(ax, sio2, fe_num, labels, groups=gd.groups)
    _style.add_legend(ax)
    _style.style_ax(ax, 'SiO$_2$ (wt.%)', 'FeO$_t$/(FeO$_t$+MgO)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Frost2001_Fenum_SiO2.png', out_dir)
    return (fig, ax)


def plot_frost_mali(gd, out_dir=None, save=True):
    """Frost et al. (2001) SiO₂ vs MALI (Na₂O+K₂O-CaO) 碱-钙分类
    精确还原 GCDkit Frost.r Plot 2:
      3 条二次曲线边界:
        alkalic/alkali-calcic:  y = -41.86 + 1.112*x - 0.00572*x²
        alkali-calcic/calc-alkalic: y = -44.72 + 1.094*x - 0.00527*x²
        calc-alkalic/calcic: y = -45.36 + 1.0043*x - 0.00427*x²
      x: 50-80, y: -8 ~ 12
    所需元素: SiO2, Na2O, K2O, CaO
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', 'CaO', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    na2o = gd.get('Na2O')
    k2o = gd.get('K2O')
    cao = gd.get('CaO')
    labels = gd.labels
    mali = na2o + k2o - cao
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(50, 80)
    ax.set_ylim(-8, 12)
    x_line = np.linspace(50, 77, 50)
    # 3 quadratic boundaries
    y1 = -41.86 + 1.112 * x_line - 0.00572 * x_line**2  # alkalic / alkali-calcic
    y2 = -44.72 + 1.094 * x_line - 0.00527 * x_line**2  # alkali-calcic / calc-alkalic
    y3 = -45.36 + 1.0043 * x_line - 0.00427 * x_line**2  # calc-alkalic / calcic
    ax.plot(x_line, y1, color='#333333', lw=1.5, zorder=4)
    ax.plot(x_line, y2, color='#333333', lw=1.5, zorder=4)
    ax.plot(x_line, y3, color='#333333', lw=1.5, zorder=4)
    ax.text(56, 7.7, 'alkalic', fontsize=10, ha='center', va='center',
            color='#444444', fontweight='bold', zorder=5)
    ax.text(61, 3.0, 'alkali-calcic', fontsize=10, ha='center', va='center',
            color='#444444', fontweight='bold', zorder=5, rotation=25)
    ax.text(61, 0.5, 'calc-alkalic', fontsize=10, ha='center', va='center',
            color='#444444', fontweight='bold', zorder=5, rotation=25)
    ax.text(65, -2.5, 'calcic', fontsize=10, ha='center', va='center',
            color='#444444', fontweight='bold', zorder=5)
    _style.scatter_samples(ax, sio2, mali, labels, groups=gd.groups)
    _style.add_legend(ax)
    _style.style_ax(ax, 'SiO$_2$ (wt.%)', 'MALI (Na$_2$O+K$_2$O-CaO)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Frost2001_MALI_SiO2.png', out_dir)
    return (fig, ax)


def plot_frost_asi_ank(gd, out_dir=None, save=True):
    """Frost et al. (2001) ASI vs A/NK 铝饱和分类
    精确还原 GCDkit Frost.r Plot 3:
      ASI = Al₂O₃ / (2*CaO - 3.33*P₂O₅ + Na₂O + K₂O)
      A/NK = Al₂O₃ / (Na₂O + K₂O)
      x: 0.5-1.9, y: 0.6-3.5
      h=1, v=1 分界线
      metaluminous / peraluminous / peralkaline
    所需元素: Al2O3, CaO, Na2O, K2O, P2O5 (P2O5 可选)
    """
    missing = gd.check_elements('Al2O3', 'CaO', 'Na2O', 'K2O', strict=True)
    if missing:
        return (None, None)
    al2o3 = gd.get('Al2O3')
    cao = gd.get('CaO')
    na2o = gd.get('Na2O')
    k2o = gd.get('K2O')
    p2o5 = gd.get('P2O5')
    labels = gd.labels
    # ASI = Al2O3 / (2*CaO - 3.33*P2O5 + Na2O + K2O)
    p = np.where(np.isnan(p2o5), 0, p2o5)
    denom = 2 * cao - 3.33 * p + na2o + k2o
    asi_val = np.where(denom > 0, al2o3 / denom, np.nan)
    a_nk = al2o3 / (na2o + k2o)
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.set_xlim(0.5, 1.9)
    ax.set_ylim(0.6, 3.5)
    ax.axhline(y=1.0, color='#666666', ls='--', lw=0.8, zorder=2)
    ax.axvline(x=1.0, color='#666666', ls='--', lw=0.8, zorder=2)
    ax.text(0.55, 3.0, 'metaluminous', fontsize=10, ha='left', va='center',
            color='#444444', fontweight='bold', zorder=3)
    ax.text(1.85, 3.0, 'peraluminous', fontsize=10, ha='right', va='center',
            color='#444444', fontweight='bold', zorder=3)
    ax.text(0.55, 0.8, 'peralkaline', fontsize=10, ha='left', va='center',
            color='#444444', fontweight='bold', zorder=3)
    _style.scatter_samples(ax, asi_val, a_nk, labels, groups=gd.groups)
    _style.add_legend(ax)
    _style.style_ax(ax, 'ASI', 'A/NK')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Frost2001_ASI_ANK.png', out_dir)
    return (fig, ax)


def plot_pearce1996(gd, out_dir=None, save=True):
    """Pearce (1996) Nb/Y–Zr/Ti 火山岩分类图
    基于 GCDkit 源码 Pearce1996.r 的精确边界坐标
    所需元素: Nb, Y, Zr, Ti
    """
    missing = gd.check_elements('Nb', 'Y', 'Zr', 'Ti', strict=True)
    if missing:
        return (None, None)
    nb = gd.get('Nb')
    yi = gd.get('Y')
    zr = gd.get('Zr')
    ti = gd.get('Ti')
    labels = gd.labels
    nb_y = np.where(yi > 0, nb / yi, np.nan)
    zr_ti = np.where(ti > 0, zr / ti, np.nan)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xscale('log', base=10)
    ax.set_yscale('log', base=10)
    ax.set_xlim(0.01, 100)
    ax.set_ylim(0.001, 2)
    ax.set_xticks([0.01, 0.1, 1, 10, 100])
    ax.set_yticks([0.001, 0.01, 0.1, 1])
    ax.set_xticklabels(['0.01', '0.1', '1', '10', '100'])
    ax.set_yticklabels(['0.001', '0.01', '0.1', '1'])
    bx1 = [0.01, 0.67, 2.81, 50, 100]
    by1 = [0.0076, 0.024, 0.0355, 0.0781, 0.0944]
    bx2 = [0.01, 0.67, 2.81, 50, 100]
    by2 = [0.026, 0.082, 0.12, 0.2663, 0.3227]
    top_x = [0.065, 0.67, 5.52]
    top_y = [2, 0.2, 2]

    ax.plot(bx1, by1, color='#333333', lw=1.5, zorder=4)
    ax.plot(bx2, by2, color='#333333', lw=1.5, zorder=4)
    ax.plot([0.67, 0.67], [0.001, 0.2], color='#333333', lw=1.5, zorder=4)
    ax.plot([2.81, 2.81], [0.001, 0.957], color='#333333', lw=1.5, zorder=4)
    ax.plot(top_x, top_y, color='#333333', lw=1.5, zorder=4)
    text_cfgs = [('basalt', 0.08, 0.003, 0, 'center'),
                 ('alkali\nbasalt', 1.5, 0.01, 0, 'center'),
                 ('foidite', 8, 0.01, 0, 'left'),
                 ('andesite\nbasaltic andesite', 0.1, 0.03, 17, 'center'),
                 ('trachy-\nandesite', 1.5, 0.06, 17, 'center'),
                 ('tephriphonolite', 10, 0.095, 17, 'center'),
                 ('rhyolite\ndacite', 0.1, 0.2, 0, 'center'),
                 ('trachyte', 1.5, 0.2, 0, 'center'),
                 ('phonolite', 10, 0.4, 0, 'center'),
                 ('alkali\nrhyolite', 0.8, 0.6, 0, 'center')]
    for txt, x, y, rot, ha in text_cfgs:
        ax.text(x, y, txt, fontsize=10, ha=ha, va='center', color='#444444', fontweight='bold', rotation=rot, zorder=5)
    _style.scatter_samples(ax, nb_y, zr_ti, labels, groups=gd.groups)
    _style.add_legend(ax)
    _style.style_ax(ax, 'Nb/Y', 'Zr/Ti')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1996_NbY_ZrTi.png', out_dir)
    return (fig, ax)