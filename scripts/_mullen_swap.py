"""Mullen (1983) MTP — 列1、2对调版
完全拷贝 v7 debug 脚本的逻辑，仅将数据点 (MnO×10, TiO₂, P₂O₅×10) 的列1列2互换
→ (TiO₂, MnO×10, P₂O₅×10)
ternary_to_xy 完全不变：a→左下, b→顶角, c→右下
"""
import numpy as np
import matplotlib.pyplot as plt

SCALE = 10.0

def ternary_to_xy(a, b, c):
    s = a + b + c
    a, b, c = a/s, b/s, c/s
    x = SCALE * (c + b / 2)
    y = SCALE * (b * np.sqrt(3) / 2)
    return x, y

def tline(pts, **kwargs):
    xs, ys = zip(*[ternary_to_xy(*p) for p in pts])
    ax.plot(xs, ys, **kwargs)

# ── 原始数据 (Mn, Ti, P) → 对调列1、2 → (Ti, Mn, P) ──
solid_lines = [
    [(77,23,0), (29,30,41), (0,8,92)],       # 原(23,77,0),(30,29,41),(8,0,92)
    [(59,41,0), (27,41,32), (26.87,28.36,44.78)],  # 原(41,59,0),(41,27,32),(28.36,26.87,44.78)
]
dashed_lines = [
    [(39,61,0), (18,61,21), (18,21,60)],     # 原(61,39,0),(61,18,21),(21,18,60)
    [(29,30,41), (45,0,55)],                 # 原(30,29,41),(0,45,55)
]

endpoints = {
    'A': (77,23,0), 'B': (29,30,41), 'C': (0,8,92),
    'D': (59,41,0), 'E': (27,41,32), 'F': (26.87,28.36,44.78),
    'G': (39,61,0), 'H': (18,61,21), 'I': (18,21,60), 'J': (45,0,55),
}

fig, ax = plt.subplots(figsize=(8, 7))

# 三角形边框
tri = [(100,0,0), (0,100,0), (0,0,100), (100,0,0)]
tline(tri, color='black', linewidth=1.5, linestyle='-')

# 网格
for v in range(10, 100, 10):
    tline([(100-v, v, 0), (0, v, 100-v)], color='lightgrey', lw=0.5)
    tline([(v, 0, 100-v), (v, 100-v, 0)], color='lightgrey', lw=0.5)
    tline([(100-v, 0, v), (0, 100-v, v)], color='lightgrey', lw=0.5)

# 刻度
for v in range(0, 101, 10):
    x, y = ternary_to_xy(v, 100-v, 0)
    ax.text(x - 0.3, y, f'{v}', fontsize=7, ha='right', va='center')
for v in range(0, 101, 10):
    x, y = ternary_to_xy(0, 100-v, v)
    ax.text(x + 0.3, y, f'{v}', fontsize=7, ha='left', va='center')
for v in range(0, 101, 10):
    x, y = ternary_to_xy(v, 0, 100-v)
    ax.text(x, y - 0.3, f'{v}', fontsize=7, ha='center', va='top')

# 轴标签
xl, yl = ternary_to_xy(50, 50, 0)
ax.text(xl - 1.0, yl, "MnO$\\times$10", fontsize=13, ha='center', va='center', rotation=60)
xb, yb = ternary_to_xy(50, 0, 50)
ax.text(xb, yb - 0.9, "TiO$_2$", fontsize=13, ha='center', va='center')
xr, yr = ternary_to_xy(0, 50, 50)
ax.text(xr + 1.0, yr, "P$_2$O$_5$$\\times$10", fontsize=13, ha='center', va='center', rotation=-60)

# 分界线
for pts in solid_lines:
    tline(pts, color='black', linewidth=1.5, linestyle='-')
for pts in dashed_lines:
    tline(pts, color='black', linewidth=1.2, linestyle='--')

# 端点标注
for name, pt in endpoints.items():
    x, y = ternary_to_xy(*pt)
    ax.text(x, y, f'{name}({pt[0]},{pt[1]},{pt[2]})',
            fontsize=7, fontweight='bold', ha='center', va='center', color='blue')

# 区域标签
region_labels = {
    'OIT': (65,20,15), 'MORB': (50,18,32),
    'IAT': (35,15,50), 'CAB': (20,42,38),
    'OIA': (15,75,10), 'BON': (10,25,65),
}
for name, pt in region_labels.items():
    x, y = ternary_to_xy(*pt)
    ax.text(x, y, name, fontsize=11, fontweight='bold',
            ha='center', va='center', color='#333333')

ax.set_xlim(-1.5, SCALE + 1.5)
ax.set_ylim(-1.2, SCALE * np.sqrt(3)/2 + 0.8)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
out = '/mnt/c/Users/opcry/Desktop/Mullen1983_MTP_swapped.png'
fig.savefig(out, dpi=400, bbox_inches='tight', facecolor='white')
plt.close(fig)
print(f'Saved: {out}')
