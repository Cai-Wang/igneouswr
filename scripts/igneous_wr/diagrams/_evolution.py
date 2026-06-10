import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import igneous_wr.report.style as _style
from igneous_wr.core.chem import feot_calc
from igneous_wr.boundaries.core import load_boundary
'\n_evolution.py — 演化图：Harker, Miyashiro, Mg#, Zr协变\n'

def plot_miyashiro(gd, out_dir=None, save=True):
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
    fig, ax = plt.subplots(figsize=(8, 6))
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
    _style.add_legend(ax)
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Miyashiro1974_FeOtMgO_SiO2.png', out_dir)
    return (fig, ax)

