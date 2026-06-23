#!/usr/bin/env python3
"""
Glitter / ICPMSDataCal → REE 图

Parses LA-ICP-MS spot data from GLITTER 4.0 CSV and ICPMSDataCal XLS exports,
normalizes to CI Chondrite (Sun & McDonough 1995), and plots REE diagrams.

Uses the same normalization constants and log-scale styling as IgneousWR's
plot_ree() (SRC-01), but handles the inverted data layout (elements=rows,
spots=columns) that GeochemData cannot parse.

Usage:
  python3 glitter_zircon_ree.py /path/to/data/dir [/path/to/output/dir]
  python3 glitter_zircon_ree.py /path/to/data/dir --chondrite MS95 --dl half

<MDL handling: half (default, ½ MDL), zero, or nan.
Chondrite refs: MS95 (default, Sun & McDonough 1995), NAKAMURA1974,
                BOYNTON1984, ANDERS1989, PALME2014.
"""
import sys, os, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── CI Chondrite (Sun & McDonough 1995, default) ──
CHONDRITE = {
    'La': 0.237, 'Ce': 0.613, 'Pr': 0.0928, 'Nd': 0.457,
    'Sm': 0.148, 'Eu': 0.0563, 'Gd': 0.199, 'Tb': 0.0361,
    'Dy': 0.246, 'Ho': 0.0546, 'Er': 0.160, 'Tm': 0.0247,
    'Yb': 0.161, 'Lu': 0.0246,
}
REE_ORDER = ['La','Ce','Pr','Nd','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu']

# 已知标准物质名称（col2 匹配用）
STD_NAMES = ('srm', 'gj-1', 'nist', 'ple', '91500', 'standard', 'qh', 'qdh')

CHONDRITE_ALIASES = {
    'MS95':       {'La':0.237, 'Ce':0.613, 'Pr':0.0928, 'Nd':0.457, 'Sm':0.148, 'Eu':0.0563, 'Gd':0.199, 'Tb':0.0361, 'Dy':0.246, 'Ho':0.0546, 'Er':0.160, 'Tm':0.0247, 'Yb':0.161, 'Lu':0.0246},
    'NAKAMURA1974':{'La':0.329, 'Ce':0.865, 'Pr':0.120, 'Nd':0.630, 'Sm':0.203, 'Eu':0.077, 'Gd':0.276, 'Tb':0.0492, 'Dy':0.343, 'Ho':0.0759, 'Er':0.225, 'Tm':0.0330, 'Yb':0.220, 'Lu':0.0339},
    'BOYNTON1984':{'La':0.310, 'Ce':0.808, 'Pr':0.122, 'Nd':0.600, 'Sm':0.195, 'Eu':0.0735, 'Gd':0.259, 'Tb':0.0474, 'Dy':0.322, 'Ho':0.0718, 'Er':0.210, 'Tm':0.0324, 'Yb':0.209, 'Lu':0.0322},
    'ANDERS1989':{'La':0.235, 'Ce':0.603, 'Pr':0.0891, 'Nd':0.452, 'Sm':0.147, 'Eu':0.0560, 'Gd':0.196, 'Tb':0.0363, 'Dy':0.243, 'Ho':0.0556, 'Er':0.159, 'Tm':0.0249, 'Yb':0.161, 'Lu':0.0247},
    'PALME2014': {'La':0.2414,'Ce':0.6194,'Pr':0.0939,'Nd':0.4737,'Sm':0.1536,'Eu':0.05883,'Gd':0.2069,'Tb':0.03797,'Dy':0.2558,'Ho':0.05644,'Er':0.1655,'Tm':0.02609,'Yb':0.1687,'Lu':0.02503},
}


def parse_value(v, dl_strategy='half'):
    """Handle <MDL values: half, zero, or nan."""
    if isinstance(v, str):
        v = v.strip()
        m = re.match(r'<([\d.]+)', v)
        if m:
            val = float(m.group(1))
            if dl_strategy == 'half':   return val / 2
            elif dl_strategy == 'zero': return 0.0
            else:                       return np.nan
        try:
            return float(v)
        except ValueError:
            return np.nan
    if isinstance(v, (int, float)):
        return float(v)
    return np.nan


def parse_glitter_csv(path, dl_strategy='half'):
    """
    解析 GLITTER 4.0 CSV。
    
    坑：同一文件内有些元素数据在下一行（Si29, Zr91），
    有些在同一行（Ti49, Y89, La139~Lu175）。
    必须检查 parts[1:] 是否有数值，没有再读下一行。
    
    标准过滤：优先用 Zr（锆石~450k ppm vs NIST610~440 ppm），
    回退用 Si（锆石~153k ppm vs NIST610~327k ppm）。
    """
    sample_name = os.path.splitext(os.path.basename(path))[0]
    sample_name = re.sub(r'[-_]?ele$', '', sample_name, flags=re.I)

    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    lines = [l.strip() for l in content.split('\n') if l.strip()]

    # 收集所有元素（REE + Zr + Si）
    elem_data = {}
    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split(',')]
        first = parts[0]
        m = re.match(r'([A-Za-z]+)', first)
        if not m:
            continue
        elem = m.group(1).capitalize()
        if elem not in CHONDRITE and elem not in ('Zr', 'Si'):
            continue

        # 检查数据是在本行还是下一行
        vals_raw = parts[1:]
        has_numbers = any(re.match(r'^[\d.<]', v) for v in vals_raw[:5] if v)
        if not has_numbers and i + 1 < len(lines):
            vals_raw = [p.strip() for p in lines[i+1].split(',')]

        values = []
        for v in vals_raw:
            if v:
                values.append(parse_value(v, dl_strategy))
        elem_data[elem] = values

    if not elem_data:
        return []

    n_spots = max(len(v) for v in elem_data.values())
    zr_vals = elem_data.get('Zr', [])
    si_vals = elem_data.get('Si', [])

    spots = []
    for j in range(n_spots):
        # 标样过滤
        use_zr = j < len(zr_vals) and not np.isnan(zr_vals[j]) and zr_vals[j] > 0
        use_si = j < len(si_vals) and not np.isnan(si_vals[j]) and si_vals[j] > 0

        if use_zr:
            is_zircon = zr_vals[j] > 10000      # 锆石~450k, NIST610~440
        elif use_si:
            is_zircon = si_vals[j] < 200000      # 锆石~153k, NIST610~327k
        else:
            is_zircon = False                    # 无判断依据，跳过

        if not is_zircon:
            continue

        spot_data = {}
        has_any = False
        for e in REE_ORDER:
            arr = elem_data.get(e, [])
            v = arr[j] if j < len(arr) else np.nan
            spot_data[e] = v
            if not np.isnan(v) and v > 0:
                has_any = True

        if has_any:
            spots.append({'id': f'{sample_name}_spot{j+1:03d}', 'data': spot_data})

    return spots


def parse_xls_trace(path, dl_strategy='half'):
    """
    解析 ICPMSDataCal .xls 的 TraceEle 表。
    
    标样三重过滤：
    1. col0 == 'std' | 'ref.' | 'standard'
    2. col2 含标准名关键词 (srm, gj-1, nist, ple, 91500, qh, qdh)
    3. ZrO2 < 10 wt%（锆石~60-68%，标样<1%）
    """
    import pandas as pd
    sample_name = os.path.splitext(os.path.basename(path))[0]
    df = pd.read_excel(path, sheet_name='TraceEle', header=None)
    elem_row = df.iloc[1].tolist()
    ncols = len(elem_row)

    col_map = {}
    zr_col = None
    for j in range(ncols):
        val = str(elem_row[j]).strip() if pd.notna(elem_row[j]) else ''
        if val in CHONDRITE:
            col_map[val] = j
        if val.upper() in ('ZRO2', 'ZR'):
            zr_col = j

    if not col_map:
        return []

    spots = []
    for i in range(4, len(df)):
        row = df.iloc[i]

        # col0: 类型标记
        col0 = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ''
        if col0 in ('std', 'ref.', 'standard'):
            continue

        # col2: 标准名（不是 col1！col1 是测点编号如 Sep10T08）
        col2 = str(row.iloc[2]).strip().lower() if len(row) > 2 and pd.notna(row.iloc[2]) else ''
        if any(s in col2 for s in STD_NAMES):
            continue

        # ZrO2 过滤
        if zr_col is not None:
            try:
                zr_float = float(row.iloc[zr_col]) if pd.notna(row.iloc[zr_col]) else np.nan
            except:
                zr_float = np.nan
            if not np.isnan(zr_float) and zr_float < 10:
                continue

        spot_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else f'{sample_name}_row{i}'

        spot_data = {}
        has_any = False
        for e, col_idx in col_map.items():
            v = row.iloc[col_idx] if col_idx < len(row) else np.nan
            val = parse_value(str(v) if pd.notna(v) else 'nan', dl_strategy)
            spot_data[e] = val
            if not np.isnan(val) and val > 0:
                has_any = True

        if has_any:
            spots.append({'id': f'{sample_name}_{spot_name}', 'data': spot_data})

    return spots


def main():
    import argparse
    parser = argparse.ArgumentParser(description='GLITTER/ICPMSDataCal -> REE diagram')
    parser.add_argument('data_dir', help='Directory containing .csv/.xls files')
    parser.add_argument('out_dir', nargs='?', default=None,
                        help='Output directory (default: data_dir/REE_output)')
    parser.add_argument('--chondrite', default='MS95',
                        choices=list(CHONDRITE_ALIASES.keys()),
                        help='Chondrite normalization reference')
    parser.add_argument('--dl', default='half', choices=['half','zero','nan'],
                        help='<MDL handling strategy')
    args = parser.parse_args()

    global CHONDRITE
    CHONDRITE = CHONDRITE_ALIASES[args.chondrite]

    data_dir = os.path.abspath(args.data_dir)
    out_dir = args.out_dir or os.path.join(data_dir, 'REE_output')
    os.makedirs(out_dir, exist_ok=True)

    all_spots = []
    file_records = {}
    files = sorted(os.listdir(data_dir))

    for fname in files:
        fpath = os.path.join(data_dir, fname)
        spots = []
        if fname.endswith('.csv'):
            spots = parse_glitter_csv(fpath, args.dl)
        elif fname.endswith('.xls'):
            try:
                spots = parse_xls_trace(fpath, args.dl)
            except Exception as e:
                print(f'  {fname}: SKIP ({e})')
                continue
        else:
            continue
        if spots:
            indices = list(range(len(all_spots), len(all_spots) + len(spots)))
            all_spots.extend(spots)
            file_records[fname] = indices
            print(f'  {fname}: {len(spots)} spots')

    print(f'\nTotal: {len(all_spots)} spots from {len(file_records)} files')

    if not all_spots:
        print('No valid data found. Exiting.')
        return

    # Auto y-axis range from actual data
    all_normed = []
    for spot in all_spots:
        for e in REE_ORDER:
            v = spot['data'].get(e, np.nan)
            if not np.isnan(v) and v > 0:
                all_normed.append(v / CHONDRITE[e])
    y_min = 10 ** np.floor(np.log10(min(all_normed)))
    y_max = 10 ** np.ceil(np.log10(max(all_normed)))

    # Plot combined
    file_names = sorted(file_records.keys())
    colors = plt.cm.tab20(np.linspace(0, 1, len(file_names)))
    file_color = dict(zip(file_names, colors))

    fig, ax = plt.subplots(figsize=(10, 6.5))
    x_pos = np.arange(len(REE_ORDER))

    for fname in file_names:
        c = file_color[fname]
        indices = file_records[fname]
        n = len(indices)
        lw = 0.5 if n > 50 else (0.6 if n > 20 else 1.0)
        alpha = 0.3 if n > 50 else (0.4 if n > 20 else 0.8)
        for idx in indices:
            spot = all_spots[idx]
            y_vals = np.array([spot['data'][e] / CHONDRITE[e] if not np.isnan(spot['data'][e]) else np.nan for e in REE_ORDER])
            valid = np.isfinite(y_vals) & (y_vals > 0)
            if not any(valid):
                continue
            ax.plot(x_pos[valid], y_vals[valid], color=c, lw=lw, alpha=alpha, zorder=2)
            ax.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=5, edgecolors='none', alpha=alpha, zorder=3)
        if indices:
            ax.plot([], [], color=c, lw=1.5, label=fname)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(REE_ORDER, fontsize=10)
    ax.set_xlim(x_pos[0] - 0.3, x_pos[-1] + 0.3)
    ax.set_yscale('log')
    ax.set_ylim(y_min, y_max)
    yt = [10**i for i in range(int(np.log10(y_min)), int(np.log10(y_max)) + 1)]
    ax.set_yticks(yt)
    ax.set_yticklabels([f'{v:.0e}' if v >= 10000 else (f'{v:.1f}' if v < 1 else f'{v:.0f}') for v in yt])
    ax.set_xlabel('Rare Earth Elements', fontsize=12)
    ax.set_ylabel('Sample / CI Chondrite', fontsize=12)
    ax.tick_params(direction='in', length=5, width=1, labelsize=10)
    ax.axhline(y=1, color='gray', ls='--', lw=0.8, alpha=0.5)
    ax.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2, 10) * 0.1))
    ax.legend(fontsize=6, loc='upper right', ncol=2, framealpha=0.8)
    plt.tight_layout(pad=0.5)
    fig.savefig(os.path.join(out_dir, f'REE_AllSamples_{args.chondrite}.png'), dpi=300)
    print(f'\nSaved: {os.path.join(out_dir, f"REE_AllSamples_{args.chondrite}.png")}')

    # Per-file plots
    for fname in file_names:
        indices = file_records[fname]
        if not indices:
            continue
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        c = file_color[fname]
        for idx in indices:
            spot = all_spots[idx]
            y_vals = np.array([spot['data'][e] / CHONDRITE[e] if not np.isnan(spot['data'][e]) else np.nan for e in REE_ORDER])
            valid = np.isfinite(y_vals) & (y_vals > 0)
            if not any(valid):
                continue
            ax2.plot(x_pos[valid], y_vals[valid], color=c, lw=0.5, alpha=0.5, zorder=2)
            ax2.scatter(x_pos[valid], y_vals[valid], color=c, marker='o', s=5, edgecolors='none', alpha=0.5, zorder=3)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(REE_ORDER, fontsize=10)
        ax2.set_xlim(x_pos[0] - 0.3, x_pos[-1] + 0.3)
        ax2.set_yscale('log')
        ax2.set_ylim(y_min, y_max)
        ax2.set_yticks(yt)
        ax2.set_yticklabels([f'{v:.0e}' if v >= 10000 else (f'{v:.1f}' if v < 1 else f'{v:.0f}') for v in yt])
        ax2.set_xlabel('Rare Earth Elements', fontsize=12)
        ax2.set_ylabel('Sample / CI Chondrite', fontsize=12)
        ax2.tick_params(direction='in', length=5, width=1, labelsize=10)
        ax2.axhline(y=1, color='gray', ls='--', lw=0.8, alpha=0.5)
        ax2.yaxis.set_minor_locator(ticker.LogLocator(subs=np.arange(2, 10) * 0.1))
        base = os.path.splitext(fname)[0]
        plt.tight_layout(pad=0.3)
        fig2.savefig(os.path.join(out_dir, f'REE_{base}.png'), dpi=300)
        plt.close(fig2)

    plt.close(fig)
    print(f'Done. {len(file_names)} per-file plots in {out_dir}')


if __name__ == '__main__':
    main()
