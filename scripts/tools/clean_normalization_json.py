"""清理 normalization.json 中的数据问题"""
import json
import os

# 用 __file__ 推导路径，避免硬编码
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(SCRIPT_DIR, '..', '..', 'igneous_wr', 'core', 'references', 'normalization.json')

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

changes = []

# ── N2: NMORB_LONG 和 PRIMITIVE_MANTLE_LONG 是完全重复 ──
# 检查 NMORB_LONG vs NMORB
long_keys = ['NMORB_LONG_SUN_AND_MS_1989', 'PRIMITIVE_MANTLE_LONG_SUN_AND_MS_1989']
short_keys = ['NMORB_SUN_AND_MS_1989', 'PRIMITIVE_MANTLE_SUN_AND_MS_1989']

for long_k, short_k in zip(long_keys, short_keys):
    if long_k in data and data.get(long_k) == data.get(short_k):
        # 移到 aliases
        data['_aliases'][long_k] = short_k
        del data[long_k]
        changes.append(f'{long_k} → alias of {short_k}')
        print(f'  ✓ {long_k} → alias of {short_k}')

# ── N1: CL Chondrite O'Neil/O'Neill 重命名 ──
# CL_CHONDRITE_PALME_AND_ONEIL_2014 = 76 ��素 (FULL)
# CL_CHONDRITE_PALME_AND_ONEILL_2014 = 30 元素 (SHORT)
old_full = 'CL_CHONDRITE_PALME_AND_ONEIL_2014'
old_short = 'CL_CHONDRITE_PALME_AND_ONEILL_2014'
new_full = 'CL_CHONDRITE_PALME_AND_ONEILL_2014_FULL'
new_short = 'CL_CHONDRITE_PALME_AND_ONEILL_2014_SHORT'

if old_full in data and old_short in data:
    data[new_full] = data.pop(old_full)
    data[new_short] = data.pop(old_short)
    changes.append(f'{old_full} → {new_full} (76 elements)')
    changes.append(f'{old_short} → {new_short} (30 elements)')
    print(f'  ✓ {old_full} → {new_full}')
    print(f'  ✓ {old_short} → {new_short}')

    # 更新 NORM_DICT 中的键名
    norm = data['_NORM_DICT']
    replacements = {
        "Cl Chondrite (Palme & O'Neil 2014)": "Cl Chondrite (Palme & O'Neill 2014, FULL)",
        "Cl Chondrite (Palme & O'Neill 2014)": "Cl Chondrite (Palme & O'Neill 2014, SHORT)",
    }
    for old_label, new_label in replacements.items():
        if old_label in norm:
            norm[new_label] = norm.pop(old_label)
            changes.append(f'NORM_DICT: "{old_label}" → "{new_label}"')
            print(f'  ✓ NORM_DICT: "{old_label}" → "{new_label}"')
    
    # 更新 _aliases 中的引用
    for alias, target in list(data['_aliases'].items()):
        if target == old_full:
            data['_aliases'][alias] = new_full
            changes.append(f'  alias {alias}: {old_full} → {new_full}')
        elif target == old_short:
            data['_aliases'][alias] = new_short
            changes.append(f'  alias {alias}: {old_short} → {new_short}')

# 保存
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\n✅ {len(changes)} changes applied')
