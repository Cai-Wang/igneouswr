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

import igneous_wr.report.style as _style
from igneous_wr.core.chem import feot_calc
from igneous_wr.core.ternary import (
    SQRT3_2, ternary_to_xy, ternary_corners,
    draw_ternary_frame, draw_ternary_grid,
    draw_ternary_ticks, label_ternary_vertices,
)
from igneous_wr.boundaries.core import load_boundary


# ────────────────────────────────────────────────────────────
# Co vs Th 判别图（Hastie et al., 2007, Journal of Petrology）
# ────────────────────────────────────────────────────────────

def plot_co_th(gd, out_dir=None, save=True):
    """Th–Co 岩浆系列+岩性判别图（Hastie et al., 2007, Fig. 7）
    X=Co (ppm), Y=Th (ppm)，线性坐标。
    四套分界线均为直线端点坐标（原文 85% 概率等值线）：
      系列: IAT/CA/HK-SHO
      岩性: B/BA+A/D+R
    所需元素: Co, Th
    """
    missing = gd.check_elements('Co', 'Th', strict=True)
    if missing:
        return None, None
    co = gd.get('Co'); th = gd.get('Th')
    labels = gd.labels
    fig, ax = plt.subplots(figsize=(9, 8))

    # 从 Figure 7 原文摘录的坐标系：X=Co, Y=Th
    # 分界线端点 (Co, Th)

    # (A) 岩浆系列分界线
    # IAT – CA: (70, 0.245) → (0, 1.35)
    ax.plot([70, 0], [0.245, 1.35], 'k-', lw=1.5, color='#333333')
    # CA – H-K/SHO: (70, 2.2) → (0, 9)
    ax.plot([70, 0], [2.2, 9], 'k--', lw=1.5, color='#555555', dashes=(6, 3))

    # (B) 岩性分类分界线
    # B – BA/A: (38.4, 0.01) → (24, 100)
    ax.plot([38.4, 24], [0.01, 100], 'k-', lw=1.0, color='#666666')
    # BA/A – D/R: (23, 0.01) → (7, 100)
    ax.plot([23, 7], [0.01, 100], 'k-', lw=1.0, color='#666666')

    # 区域填充（岩浆系列）
    # IAT 区域：CA线右侧/上方
    # CA 区域：IAT-CA线左侧 & CA-HK-SHO线下方
    # HK-SHO区域：CA-HK-SHO线上方
    x_bg = np.linspace(0, 70, 50)
    ia_ca_line = 0.245 + (1.35 - 0.245) * (70 - x_bg) / 70
    ca_hk_line = 2.2 + (9 - 2.2) * (70 - x_bg) / 70

    # IAT 填充（x=0..70, y 从 IAT-CA 线到 figure 上边界）
    ax.fill_between(x_bg, ia_ca_line, 100, alpha=0.08, color='#ffcccc')
    # CA 填充（x=0..70, y 从 CA-HK 线到 IAT-CA 线）
    ax.fill_between(x_bg, ca_hk_line, ia_ca_line, alpha=0.08, color='#cce5ff')
    # HK-SHO 填充（x=0..70, y 从 CA-HK 线到底部）
    ax.fill_between(x_bg, 0, ca_hk_line, alpha=0.08, color='#e6ffe6')

    # 系列标注（彩色粗体，风格对齐 CLS-02）
    ax.text(50, 1.0, 'IAT', fontsize=11, fontweight='bold', color='#cc3333', ha='left', va='bottom')
    ax.text(50, 0.55, 'Calc-alkaline', fontsize=10, fontweight='bold', color='#3366cc', ha='left', va='bottom')
    ax.text(50, 0.10, 'High-K Calc-alkaline\n+ Shoshonite', fontsize=9, fontweight='bold',
            color='#2e8b2e', ha='left', va='bottom')

    # 岩性标注（在右侧区域）
    ax.text(30, 70, 'B', fontsize=10, fontweight='bold', color='#885522', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.7))
    ax.text(15, 25, 'BA/A', fontsize=10, fontweight='bold', color='#885522', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.7))
    ax.text(5, 8, 'D/R*', fontsize=10, fontweight='bold', color='#885522', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.7))

    _style.scatter_samples(ax, co, th, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(0, 75); ax.set_ylim(0, 110)
    ax.set_xticks(range(0, 81, 10))
    _style.style_ax(ax, 'Co (ppm)', 'Th (ppm)')
    ax.grid(False)
    ax.text(0.98, 0.02, 'After Hastie et al. (2007)', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom', style='italic', color='grey')
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

    # 从 JSON 加载 TAS 分类边界
    _tas_data = load_boundary('cls', 'tas')
    _TAS_FIELDS = {k: [tuple(p) for p in v] for k, v in _tas_data['fields'].items()}
    _TAS_LABELS = _tas_data['labels']
    _TAS_FILLS = _tas_data['fills']

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
    """K₂O–SiO₂ 钾系列分类图（Middlemost, 1985, 图9）
    所需元素: SiO2, K2O
    分界线: Low-K, Medium-K, High-K, Shoshonitic
    界线端点坐标参考 Middlemost (1985)
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
        _style.save_fig(fig, 'Middlemost1985_K2O_SiO2.png', out_dir)
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
    # 从 JSON 加载 AFM 边界
    _afm_data = load_boundary('cls', 'afm')
    _afm_bdy = _afm_data['boundary']
    boundary_A = np.array([p['a'] for p in _afm_bdy])
    boundary_B = np.array([p['b'] for p in _afm_bdy])
    boundary_C = np.array([p['c'] for p in _afm_bdy])
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

    # 从 JSON 加载 W&F 边界
    _wf_data = load_boundary('cls', 'winchester_floyd')
    _WF_NODES = {int(k): v for k, v in _wf_data['nodes'].items()}
    _WF_EDGES = _wf_data['edges']
    _WF_LABELS = _wf_data['labels']

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

    # 从 JSON 加载 Cabanis 边界
    _cabanis_raw = load_boundary('cls', 'cabanis')
    _cabanis_poly = _cabanis_raw['polygon']
    cabanis_bd_a = np.array([p['a'] for p in _cabanis_poly])
    cabanis_bd_b = np.array([p['b'] for p in _cabanis_poly])
    cabanis_bd_c = np.array([p['c'] for p in _cabanis_poly])
    cabanis_bd_xy = ternary_to_xy(cabanis_bd_a, cabanis_bd_b, cabanis_bd_c)

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

    # 从 JSON 加载 Mullen 边界并计算 xy
    _mullen_raw = load_boundary('cls', 'mullen')
    _mullen_curves = _mullen_raw['curves']
    m0_xy = ternary_to_xy(
        np.array(_mullen_curves['m0']['a']),
        np.array(_mullen_curves['m0']['b']),
        np.array(_mullen_curves['m0']['c']))
    m1_xy = ternary_to_xy(
        np.array(_mullen_curves['m1']['a']),
        np.array(_mullen_curves['m1']['b']),
        np.array(_mullen_curves['m1']['c']))
    m2_xy = ternary_to_xy(
        np.array(_mullen_curves['m2']['a']),
        np.array(_mullen_curves['m2']['b']),
        np.array(_mullen_curves['m2']['c']))
    m3_xy = ternary_to_xy(
        np.array(_mullen_curves['m3']['a']),
        np.array(_mullen_curves['m3']['b']),
        np.array(_mullen_curves['m3']['c']))

    # ── 分界线: L1+L2 实线, L3+L4 虚线 ──
    ax.plot(m0_xy[0], m0_xy[1], 'k-', lw=1.5, zorder=4)  # L1 实线
    ax.plot(m1_xy[0], m1_xy[1], 'k-', lw=1.5, zorder=4)  # L2 实线
    ax.plot(m2_xy[0], m2_xy[1], 'k--', lw=1.2, zorder=4)  # L3 虚线
    ax.plot(m3_xy[0], m3_xy[1], 'k--', lw=1.2, zorder=4)  # L4 虚线

    # ── 区域标注（坐标来自 GCDkit Mullen.r 源码翻译） ──
    # ternary_to_xy(a,b,c): a=顶角(TiO₂), b=左下(10×MnO), c=右下(10×P₂O₅)
    lbl_oit = ternary_to_xy(np.array([57.7]), np.array([16.1]), np.array([26.1]))
    ax.text(lbl_oit[0][0], lbl_oit[1][0], 'OIT',
            fontsize=11, ha='center', va='center',
            color='#1b5e20', fontweight='bold', zorder=5)

    lbl_iat = ternary_to_xy(np.array([34.6]), np.array([50.7]), np.array([14.7]))
    ax.text(lbl_iat[0][0], lbl_iat[1][0], 'IAT',
            fontsize=11, ha='center', va='center',
            color='#e65100', fontweight='bold', zorder=5)

    lbl_morb = ternary_to_xy(np.array([46.2]), np.array([33.9]), np.array([19.9]))
    ax.text(lbl_morb[0][0], lbl_morb[1][0], 'MORB',
            fontsize=11, ha='center', va='center',
            color='#1565c0', fontweight='bold', zorder=5)

    lbl_cab = ternary_to_xy(np.array([11.5]), np.array([49.2]), np.array([39.2]))
    ax.text(lbl_cab[0][0], lbl_cab[1][0], 'CAB',
            fontsize=11, ha='center', va='center',
            color='#c62828', fontweight='bold', zorder=5)

    lbl_oia = ternary_to_xy(np.array([25.4]), np.array([10.3]), np.array([64.3]))
    ax.text(lbl_oia[0][0], lbl_oia[1][0], 'OIA',
            fontsize=11, ha='center', va='center',
            color='#6a1b9a', fontweight='bold', zorder=5)

    lbl_bon = ternary_to_xy(np.array([17.3]), np.array([71.3]), np.array([11.3]))
    ax.text(lbl_bon[0][0], lbl_bon[1][0], 'Bon',
            fontsize=11, ha='center', va='center',
            color='#b71c1c', fontweight='bold', zorder=5)

    # ── 分界线: L1+L2 实线, L3+L4 虚线 ──
    ax.plot(m0_xy[0], m0_xy[1], 'k-', lw=1.5, zorder=4)  # L1 实线
    ax.plot(m1_xy[0], m1_xy[1], 'k-', lw=1.5, zorder=4)  # L2 实线
    ax.plot(m2_xy[0], m2_xy[1], 'k--', lw=1.2, zorder=4)  # L3 虚线
    ax.plot(m3_xy[0], m3_xy[1], 'k--', lw=1.2, zorder=4)  # L4 虚线

    # 顶点标签
    label_ternary_vertices(ax, 'TiO₂', '10×MnO', '10×P₂O₅')

    _style.scatter_samples(ax, x_d, y_d, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(-0.05, 1.1); ax.set_ylim(-0.08, 0.95)
    ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Mullen1983_TiO2_MnO_P2O5.png', out_dir)
    return fig, ax


# ── Jensen (1976) FeOt+TiO2–Al2O3–MgO 阳离子判别 ─────────


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

    # 从 JSON 加载 Jensen 边界并计算 xy
    _jensen_raw = load_boundary('cls', 'jensen')
    _jensen_curves = _jensen_raw['curves']
    _jensen_xy_list = []
    for key in sorted(_jensen_curves.keys(), key=lambda k: int(k[1:])):
        c = _jensen_curves[key]
        xy = ternary_to_xy(np.array(c['a']), np.array(c['b']), np.array(c['c']))
        _jensen_xy_list.append(xy)
    # 保持向后兼容
    for i, xy in enumerate(_jensen_xy_list):
        globals()['jensen_%d_xy' % i] = xy
    _jensen_all = _jensen_xy_list

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

    # 从 JSON 加载 O'Connor 火山岩边界
    _ocv_raw = load_boundary('cls', 'oconnor_volc')
    _ocomorv_all = []
    for key in sorted(_ocv_raw['curves'].keys(), key=lambda k: int(k[2:])):
        c = _ocv_raw['curves'][key]
        xy = ternary_to_xy(np.array(c['a']), np.array(c['b']), np.array(c['c']))
        _ocomorv_all.append(xy)

    # ── O'Connor (1965) 分界线 ──
    for xy in _ocomorv_all:
        ax.plot(xy[0], xy[1], 'k-', lw=1.0, zorder=4)

    # ── 颜色区域填充 ──
    SQ = SQRT3_2
    T = np.array([0.5, SQ])   # An 顶点
    L = np.array([0.0, 0.0])  # Ab 顶点
    R = np.array([1.0, 0.0])  # Or 顶点

    # 计算每条界线的投影坐标 — 复用 _ocomorv_all
    bnd_coords = [xy for xy in _ocomorv_all]

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
    # 从 JSON 加载 Ohta-Arai 边界
    _ohta_raw = load_boundary('cls', 'ohta_arai')
    _ohta_all = []
    for key in sorted(_ohta_raw['curves'].keys(), key=lambda k: int(k[2:])):
        c = _ohta_raw['curves'][key]
        xy = ternary_to_xy(np.array(c['a']), np.array(c['b']), np.array(c['c']))
        _ohta_all.append(xy)
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
    # 从 JSON 加载 Pearce 1977 边界
    _p77_raw = load_boundary('cls', 'pearce1977')
    _pearce77_all = []
    for key in sorted(_p77_raw['curves'].keys(), key=lambda k: int(k[3:])):
        c = _p77_raw['curves'][key]
        xy = ternary_to_xy(np.array(c['a']), np.array(c['b']), np.array(c['c']))
        _pearce77_all.append(xy)
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


def plot_tasmiddlemostplut(gd, out_dir=None, save=True):
    """TAS Plutonic (Middlemost 1994) — 深成岩全碱-硅分类图
    多边形坐标源自 GCDkit 6.3.0 TASMiddlemostPlut.r 源码翻译
    16 个主分类区，无叠加层
    所需元素: SiO2, Na2O, K2O
    """
    missing = gd.check_elements('SiO2', 'Na2O', 'K2O', strict=True)
    if missing:
        return None, None
    sio2 = gd.get('SiO2'); alk = gd.get('Na2O') + gd.get('K2O')
    labels = gd.labels

    fig, ax = plt.subplots(figsize=(10, 7.5))

    # 从 JSON 加载 Middlemost Plutonic 分类边界
    _mm_data = load_boundary('cls', 'tas_middlemost_plut')
    _MM_FIELDS = {k: [tuple(p) for p in v] for k, v in _mm_data['fields'].items()}
    _MM_LABELS = _mm_data['labels']
    _MM_FILLS = _mm_data['fills']

    # 绘制 16 个主分类多边形（互斥填充）
    for name, poly in _MM_FIELDS.items():
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        fc = _MM_FILLS.get(name, '#D8D8D8')
        ax.fill(xs, ys, facecolor=fc, edgecolor='none',
                alpha=0.35, zorder=1)

    # 去重边绘制
    segments = set()
    for name, poly in _MM_FIELDS.items():
        n = len(poly)
        for i in range(n):
            seg = tuple(sorted([poly[i], poly[(i+1) % n]]))
            segments.add(seg)
    for seg in segments:
        ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                'k-', lw=0.6, zorder=4)

    # 分类标签
    for name, poly in _MM_FIELDS.items():
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        label = _MM_LABELS.get(name, name)
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=6.5, fontweight='bold', color='#333333', zorder=6)

    # 样品点
    _style.scatter_samples(ax, sio2, alk, labels, groups=gd.groups)
    _style.add_legend(ax)

    ax.set_xlim(35, 90); ax.set_ylim(0, 19)
    # 手动设置刻度，避免 style_ax 的 dash bug
    ax.set_xticks(range(35, 95, 5))
    ax.set_yticks(range(0, 21, 3))
    ax.set_xlabel(r'SiO$_2$ (wt.%)', fontsize=11)
    ax.set_ylabel(r'Na$_2$O+K$_2$O (wt.%)', fontsize=11)
    ax.minorticks_on()
    ax.grid(True, which='major', alpha=0.15, lw=0.3)
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


# ── La/Yb vs Yb 判别图 ────────────────────────────────────


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
    # 仅保留 Frost 原文中的界线 — 删除 Y=0.6（该线属于 Irvine & Baragar 体系，与 Frost 无关）
    ax.axhline(0.8, 0, 1, color='k', ls='--', lw=1.5)
    ax.axvline(56, 0, 1, color='grey', ls=':', lw=0.8)

    # 背景色填充: Ferroan (淡粉) / Magnesian (淡蓝)
    ax.fill_between([40, 56], 0.8, 1.0, color='#ffcccc', alpha=0.20, zorder=0)
    ax.fill_between([56, 80], 0.8, 1.0, color='#ffcccc', alpha=0.20, zorder=0)
    ax.fill_between([40, 80], 0.0, 0.8, color='#cce5ff', alpha=0.20, zorder=0)

    ax.text(42, 0.93, 'Ferroan', fontsize=12, ha='left',
            fontweight='bold', color='#cc3333')
    ax.text(42, 0.60, 'Magnesian', fontsize=12, ha='left',
            fontweight='bold', color='#3366cc')

    _style.scatter_samples(ax, sio2, fe_num, labels, groups=gd.groups)
    _style.add_legend(ax)
    ax.set_xlim(40, 80); ax.set_ylim(0.3, 1.0)
    _style.style_ax(ax, r'SiO$_2$ (wt.%)', r'FeO$_t$/(FeO$_t$+MgO)')
    ax.text(0.98, 0.02, 'After Frost et al. (2001)', transform=ax.transAxes,
            fontsize=9, ha='right', va='bottom', style='italic', color='grey')
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


# ── Pearce (1996) Zr/Ti vs Nb/Y 分类图 ───────────────
# 从 GCDkit 源码 Pearce1996.r 提取的精确边界坐标
# X = Nb/Y (log), Y = Zr/Ti (log)


def plot_pearce1996(gd, out_dir=None, save=True):
    """Pearce (1996) Nb/Y–Zr/Ti 火山岩分类图
    基于 GCDkit 源码 Pearce1996.r 的精确边界坐标
    所需元素: Nb, Y, Zr, Ti
    """
    missing = gd.check_elements('Nb', 'Y', 'Zr', 'Ti', strict=True)
    if missing:
        return None, None
    nb = gd.get('Nb'); yi = gd.get('Y')
    zr = gd.get('Zr'); ti = gd.get('Ti')
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

    # ── 边界坐标（GCDkit Pearce1996.r 精确值） ──
    # 下分界线 (subalkaline/alkaline)
    bx1 = [0.01, 0.67, 2.81, 50]
    by1 = [0.0076, 0.024, 0.0355, 0.0781]
    # 上分界线 (andesite/rhyolite-dacite)
    bx2 = [0.01, 0.67, 2.81, 50]
    by2 = [0.026, 0.082, 0.12, 0.2663]
    # 顶部 V 形
    top_x = [0.065, 0.67, 5.52]
    top_y = [2, 0.2, 2]

    # ── 填充区域 ──
    def _poly(xs, ys, color, alpha=0.12):
        from matplotlib.patches import Polygon
        ax.add_patch(Polygon(list(zip(xs, ys)), closed=True,
                              facecolor=color, edgecolor='none',
                              alpha=alpha, zorder=2))

    _poly([0.01, 0.67, 0.67, 0.01], [0.001, 0.001, 0.024, 0.0076], '#1a9850')    # basalt
    _poly([0.67, 2.81, 2.81, 0.67], [0.001, 0.001, 0.0355, 0.024], '#4575b4')     # alkali basalt
    _poly([2.81, 50, 50, 2.81], [0.001, 0.001, 0.0781, 0.0355], '#74add1')         # foidite
    _poly([0.01, 0.67, 0.67, 0.01], [0.0076, 0.024, 0.082, 0.026], '#fee08b')      # andesite
    _poly([0.67, 2.81, 2.81, 0.67], [0.024, 0.0355, 0.12, 0.082], '#f46d43')       # trachyandesite
    _poly([2.81, 50, 50, 2.81], [0.0355, 0.0781, 0.2663, 0.12], '#d73027')          # tephriphonolite
    _poly([0.01, 0.67, 0.67, 0.065, 0.01], [0.026, 0.082, 0.2, 2, 2], '#d7191c')   # rhyolite/dacite
    _poly([0.67, 2.81, 2.81, 0.67], [0.082, 0.12, 0.99, 0.2], '#fdae61')           # trachyte
    _poly([2.81, 50, 50, 5.52, 2.81], [0.12, 0.2663, 2, 2, 0.99], '#54278f')       # phonolite
    _poly([0.065, 0.67, 2.81, 5.52], [2, 0.2, 0.99, 2], '#e31a1c')                  # alkali rhyolite

    # ── 边界线 ──
    ax.plot(bx1, by1, 'k-', lw=2.0, zorder=4)
    ax.plot(bx2, by2, 'k-', lw=2.0, zorder=4)
    # x=0.67 从底部到顶部斜线交点 (0.67,0.20) 截断
    ax.plot([0.67, 0.67], [0.001, 0.20], 'k-', lw=2.0, zorder=4)
    # x=2.81 从底部到 phonolite 边界交点 (2.81,0.99) 截断
    ax.plot([2.81, 2.81], [0.001, 0.99], 'k-', lw=2.0, zorder=4)
    ax.plot(top_x, top_y, 'k-', lw=2.0, zorder=4)

    # ── 岩石类型标签 ──
    # R 源码中 andesite/trachyandesite/tephriphonolite 带 17° 旋转 (srt=17)
    text_cfgs = [
        ('basalt', 0.08, 0.003, 0),
        ('alkali\\nbasalt', 1.5, 0.01, 0),
        ('foidite', 8, 0.01, 0),
        ('andesite\\nbasaltic andesite', 0.1, 0.03, 17),
        ('trachy-\\nandesite', 1.5, 0.06, 17),
        ('tephriphonolite', 10, 0.095, 17),
        ('rhyolite\\ndacite', 0.1, 0.2, 0),
        ('trachyte', 1.5, 0.2, 0),
        ('phonolite', 10, 0.4, 0),
        ('alkali\\nrhyolite', 0.8, 0.6, 0),
    ]
    for txt, x, y, rot in text_cfgs:
        ax.text(x, y, txt, fontsize=10, ha='center', va='center',
                style='italic', color='#444', rotation=rot,
                bbox=dict(boxstyle='round,pad=0.2', fc='white',
                          ec='none', alpha=0.7))

    _style.scatter_samples(ax, nb_y, zr_ti, labels, groups=gd.groups)
    _style.add_legend(ax)
    _style.style_ax(ax, 'Nb/Y', 'Zr/Ti')
    plt.tight_layout(pad=0.3)
    if save:
        _style.save_fig(fig, 'Pearce1996_NbY_ZrTi.png', out_dir)
    return fig, ax


# ── Middlemost (1991) 侵入岩分类 ──────────────────────────


