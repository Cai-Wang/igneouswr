import numpy as np
import matplotlib.pyplot as plt
import igneous_wr.report.style as _style
from igneous_wr.core.chem import feot_calc
from igneous_wr.boundaries.core import load_boundary

def plot_miyashiro(gd, out_dir=None, save=True, ax=None):
    """Miyashiro (1974) FeOt/MgO vs SiO₂ 🔥火山岩
    底图数据来自 boundaries/evo/miyashiro.json
    所需元素: SiO2, FeO, TFe2O3, MgO
    """
    missing = gd.check_elements('SiO2', 'MgO', strict=True)
    if missing:
        return (None, None)
    feo_ok = not gd.check_elements('FeO')
    tfe2_ok = not gd.check_elements('TFe2O3')
    if not (feo_ok or tfe2_ok):
        print('[IgneousWR] ❌ 缺少 FeO 和 TFe2O3，无法计算 FeOt/MgO')
        return (None, None)
    sio2 = gd.get('SiO2')
    feo = gd.get('FeO')
    tfe2 = gd.get('TFe2O3')
    mgo = gd.get('MgO')
    feot = feot_calc(feo, tfe2)
    feot_mgo = np.where(mgo > 0, feot / mgo, np.nan)
    labels = gd.labels
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        new_fig = True
    else:
        fig = ax.figure
        new_fig = False
    bd = load_boundary('evo', 'miyashiro')
    for ln in bd.get('lines', []):
        pts = ln['points']
        ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], ln['style'], color=ln['color'], lw=ln['linewidth'], zorder=ln.get('zorder', 3))
    for fr in bd.get('fill_regions', []):
        pass
    for ann in bd.get('annotations', []):
        ax.text(ann['x'], ann['y'], ann['text'], fontsize=ann.get('fontsize', 10), fontstyle=ann.get('fontstyle', 'italic'), ha=ann.get('ha', 'center'), va=ann.get('va', 'center'), color=ann['color'], fontproperties=_style.times_prop)
    ax.set_xlim(bd['axes']['xlim'])
    ax.set_ylim(bd['axes']['ylim'])
    _style.style_ax(ax, bd['axes']['xlabel'], bd['axes']['ylabel'])
    _style.scatter_samples(ax, sio2, feot_mgo, labels, groups=gd.groups)
    if new_fig:
        plt.tight_layout(pad=0.3)
    if save and new_fig:
        _style.save_fig(fig, 'Miyashiro1974_FeOtMgO_SiO2.png', out_dir)
    return (fig, ax)


def plot_mgo_sio2(gd, out_dir=None, save=True, ax=None):
    """MgO vs SiO₂ 哈克图解
    底图只有轴和网格，无分界线
    所需元素: SiO2, MgO
    """
    missing = gd.check_elements('SiO2', 'MgO', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    mgo = gd.get('MgO')
    labels = gd.labels
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        new_fig = True
    else:
        fig = ax.figure
        new_fig = False
    ax.set_xlim(40, 82)
    ax.set_ylim(0, 25)
    _style.scatter_samples(ax, sio2, mgo, labels, groups=gd.groups)
    # 动态轴范围：数据 ±5% padding
    x_min, x_max = np.nanmin(sio2), np.nanmax(sio2)
    y_min, y_max = np.nanmin(mgo), np.nanmax(mgo)
    x_pad = (x_max - x_min) * 0.05
    y_pad = (y_max - y_min) * 0.05
    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(max(0, y_min - y_pad), y_max + y_pad)
    _style.style_ax(ax, 'SiO$_2$', 'MgO')
    if new_fig:
        plt.tight_layout(pad=0.3)
    if save and new_fig:
        _style.save_fig(fig, 'MgO_SiO2.png', out_dir)
    return (fig, ax)


def plot_p2o5_sio2(gd, out_dir=None, save=True, ax=None):
    """P₂O₅ vs SiO₂ 哈克图解
    底图只有轴和网格，无分界线
    所需元素: SiO2, P2O5
    """
    missing = gd.check_elements('SiO2', 'P2O5', strict=True)
    if missing:
        return (None, None)
    sio2 = gd.get('SiO2')
    p2o5 = gd.get('P2O5')
    labels = gd.labels
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        new_fig = True
    else:
        fig = ax.figure
        new_fig = False
    ax.set_xlim(40, 82)
    ax.set_ylim(0, 2)
    _style.scatter_samples(ax, sio2, p2o5, labels, groups=gd.groups)
    # 动态轴范围：数据 ±5% padding
    x_min, x_max = np.nanmin(sio2), np.nanmax(sio2)
    y_min, y_max = np.nanmin(p2o5), np.nanmax(p2o5)
    x_pad = (x_max - x_min) * 0.05
    y_pad = (y_max - y_min) * 0.05
    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(max(0, y_min - y_pad), y_max + y_pad)
    _style.style_ax(ax, 'SiO$_2$', 'P$_2$O$_5$')
    if new_fig:
        plt.tight_layout(pad=0.3)
    if save and new_fig:
        _style.save_fig(fig, 'P2O5_SiO2.png', out_dir)
    return (fig, ax)
