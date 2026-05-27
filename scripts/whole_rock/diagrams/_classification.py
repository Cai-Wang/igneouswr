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
    线性坐标 X=Th, Y=Co。
    分界线: Th=2 垂线 及 Co=25, Co=80 水平线
    区域: Tholeiitic, Calc-alkaline, High-K calc-alkaline
    所需元素: Co, Th
    """
    missing = gd.check_elements('Co', 'Th', strict=True)
    if missing:
        return None, None
    co = gd.get('Co'); th = gd.get('Th')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(8, 7))

    # 分界线: 水平 Co=25, Co=80；垂直 Th=2
    ax.axhline(25, 0, 1, color='k', lw=1.0)
    ax.axhline(80, 0, 1, color='k', lw=1.0)
    ax.axvline(2, 0, 1, color='k', lw=1.0)

    # 区域标注（系列名称）
    ax.text(6, 60, 'Tholeiitic', fontsize=9, ha='center', fontstyle='italic', alpha=0.7)
    ax.text(6, 40, 'Calc-alkaline', fontsize=9, ha='center', fontstyle='italic', alpha=0.7)
    ax.text(6, 100, 'High-K\ncalc-alkaline', fontsize=9, ha='center', fontstyle='italic', alpha=0.7)

    _style.scatter_samples(ax, th, co, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 15); ax.set_ylim(0, 120)
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
    An=CaO（钙长石标准分子）, Ab=Na₂O（钠长石标准分子）, Or=K₂O（钾长石标准分子）
    按 O'Connor (1965) / Streckeisen (1976) 花岗岩类岩石分类
    所需元素: Na2O, K2O, CaO, Al2O3, SiO2
    """
    missing = gd.check_elements('Na2O', 'K2O', 'CaO', 'Al2O3', 'SiO2', strict=True)
    if missing:
        return None, None
    na2o = gd.get('Na2O'); k2o = gd.get('K2O'); cao = gd.get('CaO')
    al2o3 = gd.get('Al2O3'); sio2 = gd.get('SiO2')
    labels = gd.labels
    # 简化标准矿物计算（仅做三角图投点用）
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

    # ── O'Connor (1965) 花岗岩类分类界线 ──
    # 每条界线由 (An%, Ab%, Or%) 三元坐标的两个端点定义
    # 界线的走向为从一条边出发，终止于另一条边
    _ocomor_boundaries = [
        # 每条 (An_arr, Ab_arr, Or_arr) → 分界线
        ([0.0, 17.5, 30.0],  [70.0, 52.5, 30.0],  [30.0, 30.0, 30.0]),   # Trondhjemite 上边界
        ([20.0, 44.0, 20.0],  [60.0, 36.0, 20.0],  [20.0, 20.0, 20.0]),   # 第2条
        ([16.3, 35.8, 35.0],  [48.7, 29.2, 35.0],  [35.0, 35.0, 35.0]),   # 第3条
        ([12.5, 27.5, 50.0],  [37.5, 22.5, 50.0],  [50.0, 50.0, 50.0]),   # 第4条
        ([25.0, 12.5, -0.5],  [75.5, 37.5, 50.0],  [-0.5, 50.0, 50.0]),   # 第5条
        ([12.5, 2.5, 50.0],   [37.5, 7.5, 90.0],   [50.0, 90.0, 90.0]),   # 第6条
        ([2.5, 5.5, 90.0],    [7.5, 4.5, 90.0],    [90.0, 90.0, 90.0]),   # 第7条
    ]
    for a_arr, b_arr, c_arr in _ocomor_boundaries:
        a_np = np.array(a_arr); b_np = np.array(b_arr); c_np = np.array(c_arr)
        bx, by = ternary_to_xy(a_np, b_np, c_np)
        ax.plot(bx, by, 'k-', lw=1.0, zorder=4)

    # ── 分类区域填充 ──
    # 用7条界线将三角图分为8个区域，填充淡色便于区分
    # 区域填充用围成的多边形顶点
    SQ = SQRT3_2
    T = np.array([0.5, SQ])   # An 顶点
    L = np.array([0.0, 0.0])  # Ab 顶点
    R = np.array([1.0, 0.0])  # Or 顶点

    # 计算每条界线端点的投影坐标
    bnd_coords = []
    for a_arr, b_arr, c_arr in _ocomor_boundaries:
        a_np = np.array(a_arr); b_np = np.array(b_arr); c_np = np.array(c_arr)
        bx, by = ternary_to_xy(a_np, b_np, c_np)
        bnd_coords.append((bx, by))

    # ── 区域 1: An 顶角区（Anorthite-rich）──
    # An 顶点 → 界线0起点 → 界线0终点 → 回到 An
    r1_x = np.concatenate([[T[0]], bnd_coords[0][0], [T[0]]])
    r1_y = np.concatenate([[T[1]], bnd_coords[0][1], [T[1]]])
    ax.fill(r1_x, r1_y, color='#ffe0b2', alpha=0.25, ec='none', zorder=1)

    # ── 区域 2: An-Ab 边附近 → 界线0 ~ 界线1 ──
    r2_x = np.concatenate([bnd_coords[0][0], bnd_coords[1][0]])
    r2_y = np.concatenate([bnd_coords[0][1], bnd_coords[1][1]])
    ax.fill(r2_x, r2_y, color='#fff9c4', alpha=0.25, ec='none', zorder=1)

    # ── 区域 3: 界线1 ~ 界线2 ──
    r3_x = np.concatenate([bnd_coords[1][0], bnd_coords[2][0][::-1]])
    r3_y = np.concatenate([bnd_coords[1][1], bnd_coords[2][1][::-1]])
    ax.fill(r3_x, r3_y, color='#c8e6c9', alpha=0.25, ec='none', zorder=1)

    # ── 区域 4: 界线2 ~ 界线3 ──
    r4_x = np.concatenate([bnd_coords[2][0], bnd_coords[3][0][::-1]])
    r4_y = np.concatenate([bnd_coords[2][1], bnd_coords[3][1][::-1]])
    ax.fill(r4_x, r4_y, color='#b3e5fc', alpha=0.25, ec='none', zorder=1)

    # ── 区域 5: 界线3 ~ 界线4 ──
    r5_x = np.concatenate([bnd_coords[3][0], bnd_coords[4][0][::-1]])
    r5_y = np.concatenate([bnd_coords[3][1], bnd_coords[4][1][::-1]])
    ax.fill(r5_x, r5_y, color='#d1c4e9', alpha=0.25, ec='none', zorder=1)

    # ── 区域 6: 界线4 ~ 界线5 ──
    r6_x = np.concatenate([bnd_coords[4][0], bnd_coords[5][0][::-1]])
    r6_y = np.concatenate([bnd_coords[4][1], bnd_coords[5][1][::-1]])
    ax.fill(r6_x, r6_y, color='#f8bbd0', alpha=0.25, ec='none', zorder=1)

    # ── 区域 7: 界线5 ~ 界线6 ──
    r7_x = np.concatenate([bnd_coords[5][0], bnd_coords[6][0][::-1]])
    r7_y = np.concatenate([bnd_coords[5][1], bnd_coords[6][1][::-1]])
    ax.fill(r7_x, r7_y, color='#d7ccc8', alpha=0.25, ec='none', zorder=1)

    # ── 区域 8: Or 角区（界线6 ~ Or 顶点）──
    r8_x = np.concatenate([bnd_coords[6][0], [R[0]], [R[0]]])
    r8_y = np.concatenate([bnd_coords[6][1], [R[1]], [R[1]]])
    ax.fill(r8_x, r8_y, color='#cfd8dc', alpha=0.30, ec='none', zorder=1)

    # ── 分类标注 ──
    # 每个区域中心放分类名称（通过三元坐标找个中点）
    # 按 O'Connor (1965) 花岗岩类分类
    labels_text = [
        ('Anorthite\n(An>50%)', [75, 15, 10]),
        ('Gabbro/\nDiorite', [50, 35, 15]),
        ('Quartz\nDiorite', [38, 42, 20]),
        ('Granodiorite', [22, 48, 30]),
        ('Quartz\nMonzonite', [12, 48, 40]),
        ('Granite\n(Trondhjemite)', [5, 45, 50]),
        ('Granite\n(Adamelite)', [5, 10, 85]),
        ('Syenogranite\n(Alkali Granite)', [3, 3, 94]),
    ]
    for text, (a_pct, b_pct, c_pct) in labels_text:
        lx, ly = ternary_to_xy(np.array([a_pct]), np.array([b_pct]), np.array([c_pct]))
        ax.text(lx[0], ly[0], text, fontsize=7.5, ha='center', va='center',
                color='#444444', fontweight='bold', zorder=5)

    label_ternary_vertices(ax, 'An\n(Anorthite)', 'Ab\n(Albite)', 'Or\n(Orthoclase)')
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
    """Q-A-P 深成岩分类三元图（Streckeisen, 1976 / Le Maitre et al., 2002）
    顶点: Q=石英, A=碱性长石, P=斜长石
    按 IUGS 推荐标准，适用于 Q ≥ 10% 的火成岩（含石英岩石）
    所需元素: SiO2, Na2O, K2O, CaO, Al2O3
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', 'CaO', 'Al2O3', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    cao = gd.get('CaO'); al2o3 = gd.get('Al2O3')
    labels = gd.labels
    # 简化 Q-A-P 计算
    q = np.maximum(sio2 - 50, 0); a = na2o + k2o; p = cao + al2o3 - a - q
    p = np.maximum(p, 0)
    total = q + a + p
    mask = total == 0
    q_n = np.where(mask, 0, q/total*100)
    a_n = np.where(mask, 0, a/total*100)
    p_n = np.where(mask, 0, p/total*100)
    x_d, y_d = ternary_to_xy(q_n, a_n, p_n)
    valid = ~np.isnan(x_d) & ~np.isnan(y_d)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners)
    draw_ternary_grid(ax)
    draw_ternary_ticks(ax)

    # ── Streckeisen (1976) QAP 深成岩分类界线 ──
    # Q 的等值线：Q=20, Q=60 两条水平线
    # A/(A+P) 等值线 = 从 Q 顶点出发的射线：10%, 35%, 65%, 90%
    # 每条射线: A = K*(100-Q), P = (1-K)*(100-Q), 其中 K = A/(A+P)

    q_lines = [20, 60]
    for q_val in q_lines:
        # 水平线：从 (Q=q, A=0, P=100-q) 到 (Q=q, A=100-q, P=0)
        pts_a = np.array([q_val, q_val])
        pts_b = np.array([0.0, 100 - q_val])
        pts_c = np.array([100 - q_val, 0.0])
        lx, ly = ternary_to_xy(pts_a, pts_b, pts_c)
        ax.plot(lx, ly, 'k-', lw=1.2, zorder=4)

    # A/(A+P) 射线（从 Q=0 边出发到 Q=100 即 Q顶点）
    ap_ratios = [0.10, 0.35, 0.65, 0.90]
    ap_labels = ['0.10', '0.35', '0.65', '0.90']
    for k in ap_ratios:
        q_vals = np.array([0.0, 90.0])
        a_vals = k * (100 - q_vals)
        p_vals = (1 - k) * (100 - q_vals)
        lx, ly = ternary_to_xy(q_vals, a_vals, p_vals)
        ax.plot(lx, ly, 'k--', lw=0.8, zorder=4)

    # ── 颜色区域填充 ──
    SQ = SQRT3_2
    T = np.array([0.5, SQ])    # Q 顶点
    L = np.array([0.0, 0.0])   # A 顶点
    R = np.array([1.0, 0.0])   # P 顶点

    # 计算 Q=20 和 Q=60 的端点 xy
    q20_a = np.array([20, 20]); q20_b = np.array([0, 80]); q20_c = np.array([80, 0])
    q20_xy = ternary_to_xy(q20_a, q20_b, q20_c)

    q60_a = np.array([60, 60]); q60_b = np.array([0, 40]); q60_c = np.array([40, 0])
    q60_xy = ternary_to_xy(q60_a, q60_b, q60_c)

    # 计算 A/(A+P) 射线的端点坐标（Q=0 底边上的点）
    ray_endpoints = []
    for k in ap_ratios:
        qv = np.array([0.0]); av = k * 100.0; pv = (1-k) * 100.0
        rx, ry = ternary_to_xy(qv, av, pv)
        ray_endpoints.append([rx[0], ry[0]])

    # 区域 1: Q > 60, A/(A+P) < 0.35 之间 — 富石英区
    # 用 Q=60 线 + Q 顶点 + A/(A+P)=0.35 射线围合
    k35_a = np.array([0, 90]); k35_b = np.array([35, 3.5]); k35_c = np.array([65, 6.5])
    k35_xy = ternary_to_xy(k35_a, k35_b, k35_c)
    # k65
    k65_a = np.array([0, 90]); k65_b = np.array([65, 3.5]); k65_c = np.array([35, 6.5])
    k65_xy = ternary_to_xy(k65_a, k65_b, k65_c)
    # k10
    k10_a = np.array([0, 90]); k10_b = np.array([10, 9]); k10_c = np.array([90, 1])
    k10_xy = ternary_to_xy(k10_a, k10_b, k10_c)
    # k90
    k90_a = np.array([0, 90]); k90_b = np.array([90, 1]); k90_c = np.array([10, 9])
    k90_xy = ternary_to_xy(k90_a, k90_b, k90_c)

    # 区域 (Q>60, 高石英) — Q60 线以上到 Q 顶点之间的狭长区域，按 A/(A+P)分
    # 实际上 Q>60 的区域很小，用淡色整体填充
    r_qhi_x = np.concatenate([q60_xy[0], [T[0]]])
    r_qhi_y = np.concatenate([q60_xy[1], [T[1]]])
    ax.fill(r_qhi_x, r_qhi_y, color='#f8bbd0', alpha=0.20, ec='none', zorder=1)

    # 区域: 20 < Q < 60, 按 A/(A+P) 划分
    # Q20 到 Q60 之间 → 梯形

    # Q20~Q60, A/(A+P)<0.10
    r1_x = np.concatenate([q20_xy[0], q60_xy[0][::-1]])
    r1_y = np.concatenate([q20_xy[1], q60_xy[1][::-1]])
    ax.fill(r1_x, r1_y, color='#c8e6c9', alpha=0.18, ec='none', zorder=1)

    # 总区域: Q<20, 用底边直接画
    r_low_x = np.concatenate([[T[0]], q20_xy[0], [L[0]], [R[0]]])
    r_low_y = np.concatenate([[T[1]], q20_xy[1], [L[1]], [R[1]]])
    ax.fill(r_low_x, r_low_y, color='#fff9c4', alpha=0.12, ec='none', zorder=1)

    # ── 岩石名称标注 ──
    # 根据 Streckeisen (1976) 标准 QAP 分区命名
    rock_labels = [
        # (文本, (Q%, A%, P%), fontsize)
        ('Quartzolite\n(>90% Q)', (90, 5, 5), 8),
        ('Quartz-rich\nGranitoid', (40, 30, 30), 8),
        ('Alkali\nGranite', (35, 80, 15), 8),
        ('Granite', (35, 25, 40), 8),
        ('Granodiorite', (35, 15, 50), 8),
        ('Tonalite', (35, 7, 58), 8),
        ('Quartz\nAlkali\nSyenite', (10, 80, 10), 7),
        ('Quartz\nSyenite', (10, 50, 40), 7),
        ('Quartz\nMonzonite', (10, 33, 57), 7),
        ('Quartz\nMonzodiorite', (10, 20, 70), 7),
        ('Quartz\nDiorite', (10, 7, 83), 7),
        ('Alkali\nSyenite', (3, 85, 12), 7),
        ('Syenite', (3, 50, 47), 7),
        ('Monzonite', (3, 33, 64), 7),
        ('Monzodiorite', (3, 20, 77), 7),
        ('Diorite/\nGabbro', (3, 7, 90), 7),
    ]
    for text, (q_pct, a_pct, p_pct), fs in rock_labels:
        lx, ly = ternary_to_xy(np.array([q_pct]), np.array([a_pct]), np.array([p_pct]))
        ax.text(lx[0], ly[0], text, fontsize=fs, ha='center', va='center',
                color='#333333', fontweight='bold', zorder=5)

    label_ternary_vertices(ax, 'Q\n(Quartz)', 'A\n(Alkali Feldspar)', 'P\n(Plagioclase)')
    _style.scatter_samples(ax, x_d[valid], y_d[valid], labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'QAPF_Streckeisen1976.png', out_dir)
    return fig, ax

# ────────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════
# TAS 全碱-硅分类图（Le Bas et al., 1992）
# 多边形坐标源自 pyrolite TAS() classifier 提取
# ════════════════════════════════════════════════════════════

# 17 个分类区多边形顶点 (SiO₂, Na₂O+K₂O)
_TAS_FIELDS = {
    'Ba': [(45.00,5.00), (52.00,5.00), (45.00,2.00)],
    'Bs': [(45.00,2.00), (52.00,5.00), (52.00,0.00), (45.00,0.00)],
    'F':  [(35.00,9.00), (37.00,14.00), (52.50,18.00), (52.50,14.00),
           (48.40,11.50), (45.00,9.40), (41.00,7.00), (41.00,3.00), (37.00,3.00)],
    'O1': [(52.00,0.00), (52.00,5.00), (57.00,5.90), (57.00,0.00)],
    'O2': [(57.00,0.00), (57.00,5.90), (63.00,7.00), (63.00,0.00)],
    'O3': [(63.00,0.00), (63.00,7.00), (69.00,8.00), (77.30,0.00)],
    'Pc': [(41.00,3.00), (45.00,3.00), (45.00,2.00), (45.00,0.00), (41.00,0.00)],
    'Ph': [(52.50,14.00), (52.50,18.00), (57.00,18.00), (63.00,16.20),
           (61.00,13.50), (57.60,11.70)],
    'R':  [(69.00,8.00), (71.80,13.50), (85.90,6.80), (87.50,4.70), (77.30,0.00)],
    'S1': [(45.00,5.00), (49.40,7.30), (52.00,5.00)],
    'S2': [(49.40,7.30), (53.00,9.30), (57.00,5.90), (52.00,5.00)],
    'S3': [(53.00,9.30), (57.60,11.70), (61.00,8.60), (63.00,7.00), (57.00,5.90)],
    'T1': [(57.60,11.70), (61.00,13.50), (63.00,16.20), (71.80,13.50), (61.00,8.60)],
    'T2': [(61.00,8.60), (71.80,13.50), (69.00,8.00), (63.00,7.00)],
    'U1': [(41.00,3.00), (41.00,7.00), (45.00,9.40), (49.40,7.30), (45.00,5.00), (45.00,3.00)],
    'U2': [(45.00,9.40), (48.40,11.50), (53.00,9.30), (49.40,7.30)],
    'U3': [(48.40,11.50), (52.50,14.00), (57.60,11.70), (53.00,9.30)],
}

_TAS_LABELS = {
    'Ba': 'Basanite',       'Bs': 'Basalt',
    'F':  'Foidite',        'O1': 'Basaltic\nAndesite',
    'O2': 'Andesite',       'O3': 'Dacite',
    'Pc': 'Picrobasalt',    'Ph': 'Phonolite',
    'R':  'Rhyolite',       'S1': 'Trachy-\nbasalt',
    'S2': 'Basaltic\ntrachyandesite',  'S3': 'Trachy-\nandesite',
    'T1': 'Trachyte\n(Q<20%)',         'T2': 'Trachyte\n(Q>20%)',
    'U1': 'Tephrite\n(Ol<10%)',        'U2': 'Phono-\ntephrite',
    'U3': 'Tephri-\nphonolite',
}

_TAS_FILLS = {
    'Ba': '#B3D9FF', 'Bs': '#87CEEB', 'F':  '#FF6B6B',
    'O1': '#FFE066', 'O2': '#F0E040', 'O3': '#FFD700',
    'Pc': '#98D8C8', 'Ph': '#FF6EB4', 'R':  '#FF4500',
    'S1': '#90EE90', 'S2': '#32CD32', 'S3': '#228B22',
    'T1': '#DDA0DD', 'T2': '#BA55D3', 'U1': '#B0C4DE',
    'U2': '#778899', 'U3': '#708090',
}


def plot_tas(gd, out_dir=None, save=True):
    """TAS 全碱-硅分类图（Le Bas et al., 1992）
    多边形坐标源自 pyrolite TAS classifier（已去除 pyrolite 依赖）
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    alk = na2o + k2o
    labels = gd.labels

    fig, ax = plt.subplots(figsize=(10, 7))

    # 绘制分类多边形
    for name, poly in _TAS_FIELDS.items():
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        fc = _TAS_FILLS.get(name, '#D8D8D8')
        ax.fill(xs, ys, facecolor=fc, edgecolor='#555555',
                lw=0.5, alpha=0.35, zorder=1)

    # 绘制唯一边界线（避免重复描边）
    segments = set()
    for name, poly in _TAS_FIELDS.items():
        n = len(poly)
        for i in range(n):
            seg = tuple(sorted([poly[i], poly[(i+1) % n]]))
            segments.add(seg)
    for seg in segments:
        ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                'k-', lw=0.6, zorder=2)

    # 碱性/亚碱性分界线
    ax.plot([45, 52], [2, 5], 'k--', lw=1.2, zorder=3)

    # 分类区标签（多边形质心）
    for name, poly in _TAS_FIELDS.items():
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        label = _TAS_LABELS.get(name, name)
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=6.5, fontweight='bold', color='#333333', zorder=5)

    # 样品点
    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(35, 90); ax.set_ylim(0, 18)
    ax.set_xticks(range(35, 95, 5))
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'Na$_2$O+K$_2$O (wt.%)')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'TAS.png', out_dir)
    return fig, ax


# ────────────────────────────────────────────────────────────
# K₂O–SiO₂ 钾系列分类图（Peccerillo & Taylor, 1976）
# ────────────────────────────────────────────────────────────

def plot_k2o_sio2(gd, out_dir=None, save=True):
    """K₂O–SiO₂ 钾系列分类图（Middlemost, 1975 / Le Maitre et al., 2002）
    所需元素: SiO2, K2O
    分界线: Low-K, Medium-K, High-K, Shoshonitic
    界线坐标参考 Le Maitre et al. (2002) Fig. 4.4
    """
    missing = gd.check_elements('SiO2', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); k2o = gd.get('K2O')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(8, 7))

    # ── 背景颜色区域 ──
    # Low-K: 最下方区域（淡黄色）
    # Medium-K: Low-K ~ Medium-K 之间（淡绿色）
    # High-K: Medium-K ~ High-K 之间（淡蓝色）
    # Shoshonitic: High-K 以上（淡粉色）

    # 用多边形填充各区域（覆盖全 x 范围 45~80，y 上限取 8）
    # Low-K / Medium-K 分界线: (45,0.5) → (75,2.5)
    # Medium-K / High-K 分界线: (50,1.5) → (75,4.0)
    # High-K / Shoshonitic 分界线: (55,2.5) → (75,6.0)

    # Shoshonitic 区域: 在 High-K/Shoshonitic 界线上方
    sho_x = [55, 75, 80, 80, 55]
    sho_y = [2.5, 6.0, 8.0, 8.0, 8.0]
    ax.fill(sho_x, sho_y, color='#f48fb1', alpha=0.20, ec='none', zorder=0)

    # High-K 区域: 在 Medium-K/High-K 与 High-K/Shoshonitic 之间
    hk_x = [50, 75, 75, 55]
    hk_y = [1.5, 4.0, 6.0, 2.5]
    ax.fill(hk_x, hk_y, color='#90caf9', alpha=0.20, ec='none', zorder=0)

    # Medium-K 区域: 在 Low-K/Medium-K 与 Medium-K/High-K 之间
    mk_x = [45, 75, 75, 50]
    mk_y = [0.5, 2.5, 4.0, 1.5]
    ax.fill(mk_x, mk_y, color='#a5d6a7', alpha=0.20, ec='none', zorder=0)

    # Low-K 区域: 在 Low-K/Medium-K 分界线下方 → 到底部 y=0
    lk_x = [45, 75, 75, 45]
    lk_y = [0.0, 0.0, 2.5, 0.5]
    ax.fill(lk_x, lk_y, color='#fff9c4', alpha=0.25, ec='none', zorder=0)

    # ── 分界线（Middlemost 1975 标准坐标）──
    # Low-K / Medium-K
    ax.plot([45, 75], [0.5, 2.5], 'k-', lw=0.8, zorder=3)
    # Medium-K / High-K
    ax.plot([50, 75], [1.5, 4.0], 'k--', lw=0.8, zorder=3)
    # High-K / Shoshonitic
    ax.plot([55, 75], [2.5, 6.0], '-.', color='#444444', lw=0.8, zorder=3)

    # ── 区域标注 ──
    ax.text(57, 0.3, 'Low-K\nTholeiitic', fontsize=10, ha='center', va='bottom',
            color='#f57f17', fontweight='bold', zorder=4)
    ax.text(62, 1.2, 'Medium-K\nCalc-alkaline', fontsize=10, ha='center', va='center',
            color='#2e7d32', fontweight='bold', zorder=4)
    ax.text(65, 3.3, 'High-K\nCalc-alkaline', fontsize=10, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=4)
    ax.text(62, 6.8, 'Shoshonitic', fontsize=10, ha='center', va='center',
            color='#c62828', fontweight='bold', zorder=4)

    _style.scatter_samples(ax, sio2, k2o, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(42, 82); ax.set_ylim(0, 8)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'K$_2$O (wt.%)')

    # 覆盖：关闭网格（style_ax 默认打开网格，K₂O-SiO₂ 分类型不要网格）
    ax.grid(False)

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
    标准布局：F 顶角，A 左下，M 右下
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
    # F 顶角，A 左下，M 右下 → ternary_to_xy(f_p, a_p, m_p)
    x_d = np.where(valid, ternary_to_xy(f_p, a_p, m_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(f_p, a_p, m_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)

    # ── Irvine & Baragar (1971) 精确分界线 ──
    # 数据点：%A=F% (顶角), %B=A% (左下), %C=M% (右下)
    boundary_A = np.array([
        32.90, 38.61, 44.51, 49.39, 52.69, 54.30, 54.43, 53.41,
        51.57, 49.21, 46.69, 44.12, 41.78, 39.52, 37.50, 35.59,
        33.69, 31.70
    ])
    boundary_B = np.array([
        62.10, 53.38, 44.49, 36.61, 30.32, 25.70, 22.56, 20.59,
        19.44, 18.79, 18.32, 17.86, 17.24, 16.46, 15.49, 14.42,
        13.32, 12.31
    ])
    boundary_C = np.array([
        5.00, 8.00, 11.00, 14.00, 17.00, 20.00, 23.01, 26.00,
        28.99, 32.00, 34.99, 38.02, 40.98, 44.02, 47.01, 49.99,
        52.98, 56.00
    ])
    b_x, b_y = ternary_to_xy(boundary_A, boundary_B, boundary_C)
    ax.plot(b_x, b_y, 'k-', lw=1.8, zorder=5)

    # ── 区域填充：Tholeiitic (上) / Calc-Alkaline (下) ──
    # 从左上角 → 沿框架到右下角 → 回起点构成闭合填充
    # 取边界上方区域（Tholeiitic）: 从 A 顶点出发 → 沿框架走 → 边界折回去
    # 上区：A顶点(0,0) → F顶点(0.5, SQRT3_2) → M顶点(1,0) → 边界反向走
    SQ = SQRT3_2
    from_top = np.array([0.5, SQ])  # F 顶点
    from_left = np.array([0.0, 0.0])  # A 顶点
    from_right = np.array([1.0, 0.0])  # M 顶点
    # Tholeiitic（上区）: F→A 沿左边 + A→M 沿底边 + M→边界终点 反向 → 边界折回 → 边界起点→F
    th_x = np.concatenate([[from_top[0]], [from_left[0]], [from_right[0]], b_x[::-1]])
    th_y = np.concatenate([[from_top[1]], [from_left[1]], [from_right[1]], b_y[::-1]])
    ax.fill(th_x, th_y, color='#e57373', alpha=0.18, ec='none', zorder=1)

    # Calc-Alkaline（下区）: 边界以下
    ca_x = np.concatenate([[from_top[0]], b_x, [from_right[0]]])
    ca_y = np.concatenate([[from_top[1]], b_y, [from_right[1]]])
    ax.fill(ca_x, ca_y, color='#64b5f6', alpha=0.18, ec='none', zorder=1)

    # ── 区域标注 ──
    # Tholeiitic 标注在分界线上方靠左区域
    label_th_x, label_th_y = ternary_to_xy(np.array([45]), np.array([40]), np.array([15]))
    ax.text(label_th_x[0], label_th_y[0], 'Tholeiitic',
            fontsize=12, ha='center', va='center',
            color='#c62828', fontweight='bold', zorder=6)
    # Calc-Alkaline 标注在分界线下方靠右区域
    label_ca_x, label_ca_y = ternary_to_xy(np.array([25]), np.array([30]), np.array([45]))
    ax.text(label_ca_x[0], label_ca_y[0], 'Calc-Alkaline',
            fontsize=12, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=6)

    label_ternary_vertices(ax, 'FeO*', r'Na$_2$O+K$_2$O', 'MgO')
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

    # ── 底色填充 ──
    # Metaluminous (A/CNK < 1, A/NK > 1) — 左上，淡绿色
    x_ml = [0, 1, 1, 0]
    y_ml = [1, 1, 3, 3]
    ax.fill(x_ml, y_ml, color='#a8e6cf', alpha=0.25, ec='none', zorder=0)

    # Peraluminous (A/CNK > 1, A/NK > 1) — 右上，淡蓝色
    x_pa = [1, 3, 3, 1]
    y_pa = [1, 1, 3, 3]
    ax.fill(x_pa, y_pa, color='#90caf9', alpha=0.25, ec='none', zorder=0)

    # Peralkaline (A/NK < 1, 全范围) — 下方，淡粉色
    x_pk = [0, 3, 3, 0]
    y_pk = [0, 0, 1, 1]
    ax.fill(x_pk, y_pk, color='#f48fb1', alpha=0.25, ec='none', zorder=0)

    # ── 分界线 ──
    # 垂直线 A/CNK = 1.0
    ax.axvline(x=1.0, color='#444444', ls='--', lw=1.2, zorder=1)
    # 水平线 A/NK = 1.0
    ax.axhline(y=1.0, color='#444444', ls='--', lw=1.2, zorder=1)
    # 对角线 A/CNK = A/NK (1:1)
    ax.plot([0, 3], [0, 3], color='#444444', ls=':', lw=1.0, zorder=1)

    # ── 区域标注 ──
    ax.text(0.35, 2.2, 'Metaluminous',
            fontsize=11, ha='center', va='center',
            color='#2e7d32', fontweight='bold', zorder=2)
    ax.text(2.0, 2.2, 'Peraluminous',
            fontsize=11, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=2)
    ax.text(1.5, 0.5, 'Peralkaline',
            fontsize=11, ha='center', va='center',
            color='#c62828', fontweight='bold', zorder=2)

    # ── 投点 ──
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

# ════════════════════════════════════════════════════════════
# Winchester & Floyd (1977) — v11 精细底图
# 节点+边界数据源自用户校正的 wf1977_v11.py
# ════════════════════════════════════════════════════════════

# 67 个精心校准的节点坐标 (Nb/Y, Zr/TiO₂)
_WF_NODES = {
    1:  (9.675, 0.148),  2:  (7.980, 0.160),  3:  (6.590, 0.175),
    4:  (5.440, 0.196),  5:  (4.490, 0.224),  6:  (3.710, 0.261),
    7:  (3.250, 0.298),  8:  (2.790, 0.359),  9:  (2.446, 0.433),
    10: (2.215, 0.522),  11: (2.073, 0.630),  12: (1.979, 0.760),
    13: (1.760, 1.365),  14: (1.510, 3.022),  15: (1.451, 0.167),
    16: (1.400, 0.137),  17: (1.318, 0.113),  18: (1.220, 0.095),
    19: (0.950, 0.136),  20: (0.317, 0.704),  21: (0.680, 0.085),
    22: (0.195, 0.119),  23: (0.665, 0.078),  24: (0.652, 0.069),
    25: (0.652, 0.027),  26: (0.652, 0.002),  27: (0.652, 0.019),
    28: (0.542, 0.026),  29: (0.450, 0.026),  30: (0.374, 0.026),
    31: (0.311, 0.027),  32: (0.021, 0.061),  33: (0.568, 0.017),
    34: (0.494, 0.015),  35: (0.405, 0.014),  36: (0.332, 0.013),
    37: (0.273, 0.0124), 38: (0.239, 0.012),  39: (0.150, 0.012),
    40: (0.095, 0.012),  41: (0.060, 0.012),  42: (0.412, 0.013),
    43: (0.344, 0.011),  44: (0.287, 0.009),  45: (0.264, 0.0082),
    46: (0.234, 0.007),  47: (0.211, 0.006),  48: (0.190, 0.005),
    49: (0.029, 0.005),  50: (0.735, 0.020),  51: (0.827, 0.021),
    52: (0.932, 0.022),  53: (1.050, 0.023),  54: (1.182, 0.024),
    55: (1.332, 0.024),  56: (1.520, 0.024),  57: (1.735, 0.023),
    58: (1.980, 0.0218), 59: (2.260, 0.020),  60: (2.579, 0.018),
    61: (2.944, 0.016),  62: (3.637, 0.020),  63: (4.319, 0.0250),
    64: (4.962, 0.031),  65: (5.516, 0.038),  66: (10.000, 0.039),
    67: (2.867, 0.004),
}

# 9 条唯一边界边（节点索引列表）
_WF_EDGES = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],                # L1 Phonolite
    [13, 15, 16, 17, 18],                                              # L2 Comendite-Rhyolite
    [19, 21, 23, 24, 25, 26],                                          # L3 Rhyodacite-Dacite
    [21, 22],                                                           # L4 分叉
    [25, 28, 29, 30, 31, 32],                                          # L5 Andesite upper
    [41, 40, 39, 38, 37, 36, 35, 34, 33, 27, 50, 51, 52, 53, 54,     # L6 合并线
     55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66],
    [42, 43, 44, 45, 46, 47, 48, 49, 48, 47, 46, 45, 44, 43, 42, 34],# L7 底部U形
    [61, 67],                                                           # L8 J-F向下分支
    [65, 18, 19, 20],                                                   # L9 连接线
]

# 岩石类型分区标签 (Nb/Y, Zr/TiO₂, 文本, 字号)
_WF_LABELS = [
    (4.5,  0.8,   'Phonolite',             11),
    (4.5,  0.08,  'Trachyte',              10),
    (0.7,  0.5,   'Comendite',             10),
    (0.32, 0.30,  'Rhyolite',              10),
    (0.195, 0.050, 'Rhyodacite\nDacite',    9),
    (1.5,  0.04,  'Trachyandesite',        10),
    (0.095, 0.025, 'Andesite',             10),
    (0.190, 0.002, 'Sub-alkaline\nbasalt',  9),
    (0.095, 0.007, 'Andesite,\nBasalt',     8),
    (1.18, 0.010, 'Alkali basalt',         10),
    (7.0,  0.006, 'Basanite',              10),
]


def plot_winchester_floyd(gd, out_dir=None, save=True):
    """Winchester & Floyd (1977) Zr/TiO2–Nb/Y 火山岩分类图
    精细底图 v11 — 67 节点 × 9 条校正边界线
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

    # v11 精细边界线
    for edge in _WF_EDGES:
        xs = [_WF_NODES[n][0] for n in edge]
        ys = [_WF_NODES[n][1] for n in edge]
        ax.plot(xs, ys, color='#333333', linewidth=1.8,
                linestyle='-', solid_capstyle='round', zorder=2)

    # 岩石类型标签
    for rx, ry, text, fs in _WF_LABELS:
        ax.text(rx, ry, text, fontsize=fs, color='#555555',
                ha='center', va='center', fontweight='normal', zorder=3)

    _style.scatter_samples(ax, nb_yi, zr_tio2, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(0.01, 15); ax.set_ylim(0.001, 10)
    _style.style_ax(ax, 'Nb/Y', 'Zr/TiO\\u2082')
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
    分区: WPB (板内), MORB (洋中脊), IAB (岛弧)
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

    # ── 分界线 ──
    ax.plot(cabanis_bd_xy[0], cabanis_bd_xy[1], 'k-', lw=1.2, zorder=4)

    # ── 区域填充 ──
    SQ = SQRT3_2
    T = np.array([0.5, SQ])   # Y/15 顶点
    L = np.array([0.0, 0.0])  # La/10 顶点
    R = np.array([1.0, 0.0])  # Nb/8 顶点

    # 区域 1: WPB (板内玄武岩) — La/10 高, Nb/8 高区
    # 大致在三角图左下角，底边附近，由点0→点1→...→点18→点19→点0围成
    # 实际这是整个多边形内部的一个区域
    # 用多边形的第一个子分段：点0～点2（到右边Nb=0）
    wpb_seg = list(range(0, 3))  # 点0-2
    wpb_x = [cabanis_bd_xy[0][i] for i in wpb_seg]
    wpb_y = [cabanis_bd_xy[1][i] for i in wpb_seg]
    # 闭合到底边和右边
    p2 = (cabanis_bd_xy[0][2], cabanis_bd_xy[1][2])
    p0 = (cabanis_bd_xy[0][0], cabanis_bd_xy[1][0])
    wpb_x += [p2[0], R[0], L[0], p0[0]]
    wpb_y += [p2[1], R[1], L[1], p0[1]]
    ax.fill(wpb_x, wpb_y, color='#a5d6a7', alpha=0.20, ec='none', zorder=1)

    # 区域 2: IAB (岛弧玄武岩) — La/10 高, Y/15 高, Nb/8 低
    # 围在左边附近
    iab_seg = list(range(2, 9))  # 点2到点8，沿Nb=0边
    iab_x = [cabanis_bd_xy[0][i] for i in iab_seg]
    iab_y = [cabanis_bd_xy[1][i] for i in iab_seg]
    p2 = (cabanis_bd_xy[0][2], cabanis_bd_xy[1][2])
    p8 = (cabanis_bd_xy[0][8], cabanis_bd_xy[1][8])
    iab_x += [p8[0], T[0], p2[0]]
    iab_y += [p8[1], T[1], p2[1]]
    ax.fill(iab_x, iab_y, color='#ffcc80', alpha=0.20, ec='none', zorder=1)

    # 区域 3: MORB (洋中脊玄武岩) — Y/15 高, Nb/8 和 La/10 低
    # 从上部分
    morb_seg = list(range(8, 12))  # 点8到点11
    morb_x = [cabanis_bd_xy[0][i] for i in morb_seg]
    morb_y = [cabanis_bd_xy[1][i] for i in morb_seg]
    p8 = (cabanis_bd_xy[0][8], cabanis_bd_xy[1][8])
    p11 = (cabanis_bd_xy[0][11], cabanis_bd_xy[1][11])
    morb_x += [p11[0], T[0], p8[0]]
    morb_y += [p11[1], T[1], p8[1]]
    ax.fill(morb_x, morb_y, color='#90caf9', alpha=0.20, ec='none', zorder=1)

    # ── 区域标注 ──
    # WPB 标注点：La/10 高, Nb/8 中, Y/15 低
    l_wpb = ternary_to_xy(np.array([15]), np.array([55]), np.array([30]))
    ax.text(l_wpb[0][0], l_wpb[1][0], 'WPB\n(Within-plate\nBasalt)',
            fontsize=8, ha='center', va='center',
            color='#2e7d32', fontweight='bold', zorder=5)

    # IAB 标注点：La/10 中, Y/15 中, Nb/8 低
    l_iab = ternary_to_xy(np.array([50]), np.array([42]), np.array([8]))
    ax.text(l_iab[0][0], l_iab[1][0], 'IAB\n(Island Arc\nBasalt)',
            fontsize=8, ha='center', va='center',
            color='#e65100', fontweight='bold', zorder=5)

    # MORB 标注点：Y/15 高, 其他低
    l_morb = ternary_to_xy(np.array([75]), np.array([20]), np.array([5]))
    ax.text(l_morb[0][0], l_morb[1][0], 'MORB\n(Mid-Ocean\nRidge Basalt)',
            fontsize=8, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=5)

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
    """Mullen (1983) TiO₂-10×MnO-10×P₂O₅ 基性岩构造判别三角图
    SVG轴标: 顶=TiO₂, 左下=10×MnO, 右下=10×P₂O₅
    分区: IAT (岛弧拉斑), MORB (洋中脊), OIT (洋岛拉斑), OIA+CAB (洋岛碱性+钙碱)
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

    # ── 区域填充（Mullen 1983 标准分区）──
    # 三角图顶点
    T_tio2 = np.array([0.5, SQRT3_2])   # TiO2 顶
    L_10mno = np.array([0.0, 0.0])       # 10×MnO 左下
    R_10p2o5 = np.array([1.0, 0.0])      # 10×P₂O₅ 右下

    # m0 曲线是外缘边界（点0→1→2→3→4）
    # m1 曲线从左上到中右（点0→1→2）
    # m2 曲线从左中到右中（横贯）
    # m3 直线从中间到底边

    # 区域 1: IAT — m1 上方, 靠近 TiO2 顶角
    # 由 m1 (3点) + 顶部围成
    m1_x = mullen_1_xy[0].tolist()
    m1_y = mullen_1_xy[1].tolist()
    iat_x = m1_x + [T_tio2[0], m1_x[0]]
    iat_y = m1_y + [T_tio2[1], m1_y[0]]
    ax.fill(iat_x, iat_y, color='#ffcc80', alpha=0.20, ec='none', zorder=1)

    # 区域 2: MORB — m1下方, m2上方, 右侧
    # 从 m1终点 → m3上段 → m0右侧下段 → 右底角
    m3_p0 = (mullen_3_xy[0][0], mullen_3_xy[1][0])  # 与m1/m2交点
    m3_p1 = (mullen_3_xy[0][1], mullen_3_xy[1][1])  # 底边点
    m0_p4 = (mullen_0_xy[0][4], mullen_0_xy[1][4])  # (0,8,92) 右下
    m1_p2 = (mullen_1_xy[0][2], mullen_1_xy[1][2])  # m1终点
    m2_p2 = (mullen_2_xy[0][2], mullen_2_xy[1][2])  # m2终点(右端)

    # MORB: m3上方, R底角, m0之间
    morb_x = [m3_p0[0], m3_p1[0], R_10p2o5[0], m0_p4[0], m1_p2[0]]
    morb_y = [m3_p0[1], m3_p1[1], R_10p2o5[1], m0_p4[1], m1_p2[1]]
    ax.fill(morb_x, morb_y, color='#90caf9', alpha=0.20, ec='none', zorder=1)

    # 区域 3: OIT — m2左上方, 左侧
    m2_p0 = (mullen_2_xy[0][0], mullen_2_xy[1][0])  # (39,61,0) 左边始点
    m0_p0 = (mullen_0_xy[0][0], mullen_0_xy[1][0])  # (59,41,0) 左边
    m0_p1 = (mullen_0_xy[0][1], mullen_0_xy[1][1])
    m2_p1 = (mullen_2_xy[0][1], mullen_2_xy[1][1])
    # OIT: 左上区域
    oit_x = [m0_p0[0], m0_p1[0], m2_p1[0], m2_p0[0], L_10mno[0]]
    oit_y = [m0_p0[1], m0_p1[1], m2_p1[1], m2_p0[1], L_10mno[1]]
    ax.fill(oit_x, oit_y, color='#a5d6a7', alpha=0.20, ec='none', zorder=1)

    # 区域 4: OIA+CAB — m2下方, m3右侧, 底部
    oia_x = [m2_p1[0], m2_p2[0], m3_p0[0], m3_p1[0], R_10p2o5[0], L_10mno[0], m2_p1[0]]
    oia_y = [m2_p1[1], m2_p2[1], m3_p0[1], m3_p1[1], R_10p2o5[1], L_10mno[1], m2_p1[1]]
    ax.fill(oia_x, oia_y, color='#f48fb1', alpha=0.20, ec='none', zorder=1)

    # ── 区域标注 ──
    lbl_iat = ternary_to_xy(np.array([45]), np.array([30]), np.array([25]))
    ax.text(lbl_iat[0][0], lbl_iat[1][0], 'IAT\n(Island Arc\nTholeiite)',
            fontsize=8, ha='center', va='center',
            color='#e65100', fontweight='bold', zorder=5)

    lbl_morb = ternary_to_xy(np.array([20]), np.array([10]), np.array([70]))
    ax.text(lbl_morb[0][0], lbl_morb[1][0], 'MORB\n(Mid-Ocean\nRidge Basalt)',
            fontsize=8, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=5)

    lbl_oit = ternary_to_xy(np.array([15]), np.array([55]), np.array([30]))
    ax.text(lbl_oit[0][0], lbl_oit[1][0], 'OIT\n(Ocean Island\nTholeiite)',
            fontsize=8, ha='center', va='center',
            color='#2e7d32', fontweight='bold', zorder=5)

    lbl_oia = ternary_to_xy(np.array([10]), np.array([35]), np.array([55]))
    ax.text(lbl_oia[0][0], lbl_oia[1][0], 'OIA +\nCAB',
            fontsize=8, ha='center', va='center',
            color='#c62828', fontweight='bold', zorder=5)

    # 4 条分界线（加粗）
    for xy in [mullen_0_xy, mullen_1_xy, mullen_2_xy, mullen_3_xy]:
        ax.plot(xy[0], xy[1], 'k-', lw=1.5, zorder=4)

    # 顶点标签（修正化学式格式）
    label_ternary_vertices(ax, 'TiO\u2082', '10\u00d7MnO', '10\u00d7P\u2082O\u2085')

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
    """Jensen (1976) 阳离子分类三角图（Cation Plot）
    端元: 顶=Al+Fe³⁺+Ti, 左下=Mg+Fe²⁺+Mn, 右下=Ca+Na+K
    Jensen (1976) 原图使用阳离子百分比（Cation %），而非氧化物 wt%。
    数据由 wt% 自动转换为阳离子数再归一化到 100%。
    所需元素: Al2O3, FeO/TFe2O3, TiO2, MgO, MnO, CaO, Na2O, K2O
    """
    needed = ('Al2O3', 'MgO', 'CaO', 'Na2O', 'K2O', 'TiO2')
    missing = gd.check_elements(*needed, strict=True)
    if missing or ('FeO' not in gd._elem_data and 'TFe2O3' not in gd._elem_data):
        return None, None
    missing = gd.check_elements('MnO', strict=False)
    al2o3 = gd.get('Al2O3'); mgo = gd.get('MgO')
    feo = gd.get('FeO'); tfe2 = gd.get('TFe2O3'); tio2 = gd.get('TiO2')
    cao = gd.get('CaO'); na2o = gd.get('Na2O'); k2o = gd.get('K2O')
    mno = gd.get('MnO') if gd.get('MnO') is not None else np.zeros_like(al2o3)
    labels = gd.labels

    # 摩尔质量
    M_Al2O3, M_Fe2O3, M_FeO, M_TiO2 = 101.96, 159.69, 71.844, 79.866
    M_MgO, M_MnO, M_CaO, M_Na2O, M_K2O = 40.304, 70.937, 56.08, 61.98, 94.20

    # Fe²⁺/Fe³⁺ 分配（Jensen 1976 标准，FeOt → FeO:Fe2O3 = 85:15）
    feot = feot_calc(feo, tfe2)
    feo_m = feot * 0.85
    fe2o3_m = feot * 0.15

    # 阳离子数计算
    al_cat = al2o3 / M_Al2O3 * 2       # Al³⁺
    fe3_cat = fe2o3_m / M_Fe2O3 * 2    # Fe³⁺
    ti_cat = tio2 / M_TiO2 * 1          # Ti⁴⁺
    fe2_cat = feo_m / M_FeO * 1         # Fe²⁺
    mg_cat = mgo / M_MgO * 1            # Mg²⁺
    mn_cat = mno / M_MnO * 1            # Mn²⁺
    ca_cat = cao / M_CaO * 1            # Ca²⁺
    na_cat = na2o / M_Na2O * 2          # Na⁺
    k_cat = k2o / M_K2O * 2             # K⁺

    # Jensen 三角图三端元
    top = al_cat + fe3_cat + ti_cat      # Al + Fe³⁺ + Ti
    left = mg_cat + fe2_cat + mn_cat     # Mg + Fe²⁺ + Mn
    right = ca_cat + na_cat + k_cat       # Ca + Na + K

    total = top + left + right
    valid = (total > 0) & ~np.isnan(total)
    top_p = np.where(valid, top/total*100, 0)
    left_p = np.where(valid, left/total*100, 0)
    right_p = np.where(valid, right/total*100, 0)
    x_d = np.where(valid, ternary_to_xy(top_p, left_p, right_p)[0], np.nan)
    y_d = np.where(valid, ternary_to_xy(top_p, left_p, right_p)[1], np.nan)
    fig, ax = plt.subplots(figsize=(10, 9))
    corners = ternary_corners()
    draw_ternary_frame(ax, corners); draw_ternary_grid(ax); draw_ternary_ticks(ax)

    SQ = SQRT3_2
    T = np.array([0.5, SQ])   # FeOt+TiO2 顶
    L = np.array([0.0, 0.0])  # Al2O3 左下
    R = np.array([1.0, 0.0])  # MgO 右下

    # Jensen 三元图分区：
    # 大类: Komatiitic (科马提岩质) — 底边附近, Mg+Fe²+Mn 高
    #       Tholeiitic (拉斑系列) — 顶部, Al+Fe³+Ti 高
    #       Calc-alkaline (钙碱系列) — 右侧, Ca+Na+K 高

    # ── 颜色区域填充（直接取现有的分界线）──
    # 区域 1: Komatiitic 区域 — jensen_0 下方 (Al+Fe3+Ti=50%线)
    k_x = np.concatenate([jensen_0_xy[0], jensen_0_xy[0][0:1]])
    k_y = np.concatenate([jensen_0_xy[1], jensen_0_xy[1][0:1]])
    ax.fill(k_x, k_y, color='#c8e6c9', alpha=0.25, ec='none', zorder=1)

    # 区域 2: Tholeiitic — jensen_1 上方围顶角
    SQ = SQRT3_2
    T = np.array([0.5, SQ])   # Al+Fe³+Ti 顶
    th_x = np.concatenate([jensen_1_xy[0], [T[0]], jensen_1_xy[0][0:1]])
    th_y = np.concatenate([jensen_1_xy[1], [T[1]], jensen_1_xy[1][0:1]])
    ax.fill(th_x, th_y, color='#ffcc80', alpha=0.22, ec='none', zorder=1)

    # 区域 3: Calc-alkaline — jensen_2 右侧
    ca_x = np.concatenate([jensen_2_xy[0], jensen_1_xy[0][::-1]])
    ca_y = np.concatenate([jensen_2_xy[1], jensen_1_xy[1][::-1]])
    ax.fill(ca_x, ca_y, color='#b3e5fc', alpha=0.22, ec='none', zorder=1)

    # 区域 4: 左下区（Ca+Na+K 高残余区）
    L = np.array([0.0, 0.0])  # Mg+Fe²+Mn 左下
    ca2_x = np.concatenate([jensen_2_xy[0], [L[0]], jensen_2_xy[0][0:1]])
    ca2_y = np.concatenate([jensen_2_xy[1], [L[1]], jensen_2_xy[1][0:1]])
    ax.fill(ca2_x, ca2_y, color='#f8bbd0', alpha=0.22, ec='none', zorder=1)

    # ── 分界线 ──
    for xy in _jensen_all:
        ax.plot(xy[0], xy[1], 'k-', lw=0.8, zorder=4)

    # ── 区域标注 ──
    # 注意：以下标签的 % 值是在新端元空间(Al+Fe3+Ti / Mg+Fe2+Mn / Ca+Na+K)中的位置
    # Komatiitic (Mg+Fe2+Mn 高)
    l_k = ternary_to_xy(np.array([20]), np.array([50]), np.array([30]))
    ax.text(l_k[0][0], l_k[1][0], 'Komatiitic', fontsize=8, ha='center', va='center',
            color='#2e7d32', fontweight='bold', zorder=5)

    # Tholeiitic (Al+Fe³+Ti 高)
    l_th = ternary_to_xy(np.array([60]), np.array([25]), np.array([15]))
    ax.text(l_th[0][0], l_th[1][0], 'Tholeiitic', fontsize=8, ha='center', va='center',
            color='#e65100', fontweight='bold', zorder=5)

    # Calc-alkaline (中间偏左)
    l_ca = ternary_to_xy(np.array([15]), np.array([40]), np.array([45]))
    ax.text(l_ca[0][0], l_ca[1][0], 'Calc-alkaline', fontsize=8, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=5)

    label_ternary_vertices(ax, 'Al+Fe\u00b3\u207a+Ti', 'Mg+Fe\u00b2\u207a+Mn', 'Ca+Na+K')
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
    An=CaO（钙长石标准分子）, Ab=Na₂O（钠长石标准分子）, Or=K₂O（钾长石标准分子）
    按 O'Connor (1965) 标准矿物分类
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

    # ── O'Connor (1965) 分界线 ──
    for xy in _ocomorv_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.0, zorder=4)

    # ── 颜色区域填充 ──
    SQ = SQRT3_2
    T = np.array([0.5, SQ])   # An 顶点
    L = np.array([0.0, 0.0])  # Ab 顶点
    R = np.array([1.0, 0.0])  # Or 顶点

    # 计算每条界线的投影坐标
    bnd_coords = []
    for xy in _ocomorv_all:
        bnd_coords.append(xy)

    # 8 个区域依次填充
    fills = [
        ([T[0]], [T[1]]),           # 起点 An 顶点
        (bnd_coords[0][0], bnd_coords[0][1]),
        ([T[0]], [T[1]]),
    ]
    # 区域 1: An 顶角区
    r1_x = np.concatenate([[T[0]], bnd_coords[0][0], [T[0]]])
    r1_y = np.concatenate([[T[1]], bnd_coords[0][1], [T[1]]])
    ax.fill(r1_x, r1_y, color='#ffe0b2', alpha=0.25, ec='none', zorder=1)

    # 其他区域: 相邻界线之间
    for i in range(len(bnd_coords) - 1):
        rx = np.concatenate([bnd_coords[i][0], bnd_coords[i+1][0][::-1]])
        ry = np.concatenate([bnd_coords[i][1], bnd_coords[i+1][1][::-1]])
        colors = ['#fff9c4', '#c8e6c9', '#b3e5fc', '#d1c4e9', '#f8bbd0', '#d7ccc8']
        ax.fill(rx, ry, color=colors[i % len(colors)], alpha=0.22, ec='none', zorder=1)

    # 最后一个区域: Or 角区
    r_last_x = np.concatenate([bnd_coords[-1][0], [R[0]], [R[0]]])
    r_last_y = np.concatenate([bnd_coords[-1][1], [R[1]], [R[1]]])
    ax.fill(r_last_x, r_last_y, color='#cfd8dc', alpha=0.25, ec='none', zorder=1)

    # ── 分类标注 ──
    # 按 O'Connor (1965) / Streckeisen 火山岩分类
    labels_text = [
        ('Anorthite\n(An>50%)', [75, 15, 10]),
        ('Gabbro/\nDiorite', [50, 35, 15]),
        ('Quartz\nDiorite', [38, 42, 20]),
        ('Granodiorite', [22, 48, 30]),
        ('Quartz\nMonzonite', [12, 48, 40]),
        ('Granite\n(Trondhjemite)', [5, 45, 50]),
        ('Granite\n(Adamelite)', [5, 10, 85]),
        ('Syenogranite\n(Alkali Granite)', [3, 3, 94]),
    ]
    for text, (a_pct, b_pct, c_pct) in labels_text:
        lx, ly = ternary_to_xy(np.array([a_pct]), np.array([b_pct]), np.array([c_pct]))
        ax.text(lx[0], ly[0], text, fontsize=7.5, ha='center', va='center',
                color='#444444', fontweight='bold', zorder=5)

    label_ternary_vertices(ax, 'An\n(Anorthite)', 'Ab\n(Albite)', 'Or\n(Orthoclase)')
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
