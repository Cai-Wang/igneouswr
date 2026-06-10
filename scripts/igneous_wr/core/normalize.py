"""
_normalize.py — 标准化参考值常量 + 标准化函数

所有参考值已外置到 references/normalization.json。
本文件是 JSON 加载器 + normalize() 函数 + 常用别名。

选择指南：
  - REE配分图: CHONDRITE_MS95 (默认) 或 CHONDRITE_NAKAMURA1974
  - 蛛网图: PRIMITIVE_MANTLE_MS95 (默认) 或 PRIMITIVE_MANTLE_LONG_SM89
  - MORB标准化: NMORB_SM89 / EMORB_SM89 / NMORB_IMMOBILE
  - OIB: OIB_SM89
  - 地壳: UCC_TM95 / MCC_RG2003 / LCC_TM95
  - 沉积物: GLOSS_PLANK1998 / GLOSS_II_PLANK2014
  - 地幔端元: DMM_SALTERS2004 / EM1 / EM2 / HIMU
"""
import json
import os
import re

_JSON_PATH = os.path.join(os.path.dirname(__file__), 'references', 'normalization.json')

with open(_JSON_PATH, encoding='utf-8') as _f:
    _DATA = json.load(_f)

# ── 公开 API 列表（IDE 类型提示友好）─────────────────────

__all__ = [
    'CHONDRITE', 'PRIMITIVE_MANTLE',
    'REE_ORDER', 'SPIDER_ORDER', 'NORM_DICT',
    'normalize',
    'CHONDRITE_MS95', 'CHONDRITE_NAKAMURA1974', 'CHONDRITE_BOYNTON1984',
    'CHONDRITE_ANDERS1989', 'CHONDRITE_PALME2014',
    'PRIMITIVE_MANTLE_MS95', 'PRIMITIVE_MANTLE_LONG_SM89',
    'PRIMITIVE_MANTLE_IMMOBILE', 'PM_SM89', 'REE_PM_MS95',
    'NMORB_SM89', 'EMORB_SM89', 'NMORB_IMMOBILE', 'OIB_SM89', 'PM_SM89',
    'MORB_PEARCE1983', 'MORB_PEARCE1996',
    'DMM_SALTERS2004', 'UCC_TM95', 'LCC_TM95', 'MCC_RG2003',
    'GLOSS_PLANK1998', 'GLOSS_II_PLANK2014', 'ORG_PEARCE1984', 'N_MORB',
    'REE_CHONDRITE_MS_AND_SUN_1995', 'REE_CHONDRITE_NAKAMURA_1974',
    'REE_CHONDRITE_BOYNTON_1984', 'REE_CHONDRITE_ANDERS_AND_GREVESSE_1989',
    'REE_CHONDRITE_ONEILL_2016', 'REE_CHONDRITE_PALME_AND_ONEILL_2014',
    'PRIMITIVE_MANTLE_MS_AND_SUN_1995', 'PRIMITIVE_MANTLE_SUN_AND_MS_1989',
    'PRIMITIVE_MANTLE_LONG_SUN_AND_MS_1989',
    'PRIMITIVE_MANTLE_IMMOBILE_SUN_AND_MS_1989',
    'CL_CHONDRITE_MS_AND_SUN_1995',
    'CL_CHONDRITE_PALME_AND_ONEILL_2014_FULL',
    'CL_CHONDRITE_PALME_AND_ONEILL_2014_SHORT',
    'NMORB_SUN_AND_MS_1989', 'NMORB_LONG_SUN_AND_MS_1989',
    'NMORB_IMMOBILE_SUN_AND_MS_1989_IN_PEARCE_2014',
    'EMORB_SUN_AND_MS_1989', 'OIB_SUN_AND_MS_1989',
    'UPPER_CONTINENTAL_CRUST_TAYLOR_AND_MCLENNAN_1995',
    'LOWER_CONTINENTAL_CRUST_TAYLOR_AND_MCLENNAN_1995',
    'MIDDLE_CONTINENTAL_CRUST_RUDNICK_AND_GAO_2003',
    'BULK_CONTINENTAL_CRUST_TAYLOR_AND_MCLENNAN_1995',
    'GLOSS_PLANK_AND_LANGMUIR_1998', 'GLOSS_II_PLANK_2014',
    'ORG_PEARCE_ET_AL__1984', 'MORB_PEARCE_1983', 'MORB_PEARCE_1996',
    'DMM_COMPONENT', 'EM1_COMPONENT', 'EM2_COMPONENT', 'HIMU_COMPONENT',
    'DEPLETED_MANTLE_SALTERS_AND_STRACKE_2004',
    'REE_PRIMITIVE_MANTLE_MS_AND_SUN_1995',
    'REE_UPPER_CONTINENTAL_CRUST_TAYLOR_AND_MCLENNAN_1995',
    'CHONDRITES_SUN_ET_AL__1980', 'CHONDRITES_THOMPSON_1982',
    'PRIMORDIAL_MANTLE_WOOD_ET_AL__1979',
    'CONTINENTAL_ARC_AND_ACTIVE_MARGIN_SEDIMENTS_FLOYD_ET_AL__1991',
    'OCEANIC_ISLAND_ARC_SEDIMENTS_FLOYD_ET_AL__1991',
    'PASSIVE_MARGIN_SEDIMENTS_FLOYD_ET_AL__1991',
    'SEDIMENTS_GLOSS_II_PLANK_2014',
    'SEDIMENTS_UPPER_CONTINENTAL_CRUST_TAYLOR_AND_MCLENNAN_1995',
    'HSE_PRIMITIVE_MANTLE_CONCENTRATIONS_BECKER_ET_AL__2006',
    'HSE_CHONDRITE_CONCENTRATIONS_JOCHUM_1996',
    'PGE_CHONDRITE_CONCENTRATIONS_JOCHUM_1996',
    'PGE_PRIMITIVE_MANTLE_CONCENTRATIONS_MS_AND_SUN_1995',
]

# ── 加载字典常量 → 模块级变量 ──────────────────────────

for _name, _value in _DATA.items():
    if _name.startswith('_'):
        continue
    globals()[_name] = _value

# ── 键名校验 ──────────────────────────────────────────

# 验证 JSON 加载的常量名格式
_ALLOWED_NAME = re.compile(r'^[A-Z][A-Z0-9_]*$')
for _name, _value in _DATA.items():
    if _name.startswith('_'):
        continue
    if not _ALLOWED_NAME.match(_name):
        raise RuntimeError(f"Invalid constant name in normalization.json: {_name!r}")

# ── 元素顺序 ───────────────────────────────────────────

REE_ORDER = _DATA['_REE_ORDER']
SPIDER_ORDER = _DATA['_SPIDER_ORDER']

# ── NORM_DICT（名称到常量的映射）───────────────────────

NORM_DICT = {}
for _label, _var_name in _DATA['_NORM_DICT'].items():
    # 先查直接变量名，再查别名
    if _var_name in globals():
        NORM_DICT[_label] = globals()[_var_name]
    elif _var_name in _DATA.get('_aliases', {}):
        _final = _DATA['_aliases'][_var_name]
        NORM_DICT[_label] = globals()[_final]

# ── 旧接口兼容 + 别名 ──────────────────────────────────

for _alias, _target_name in _DATA.get('_aliases', {}).items():
    if _target_name in globals():
        globals()[_alias] = globals()[_target_name]


def normalize(data_dict, ref):
    """将元素浓度按参考值标准化。

    Parameters
    ----------
    data_dict : dict
        元素名 -> 浓度值的映射 (ppm)
    ref : dict
        标准化参考值字典（如 CHONDRITE_MS95）

    Returns
    -------
    dict
        标准化后的值。元素不在 ref 中或输入为 NaN 时返回 NaN。
    """
    if not isinstance(ref, dict):
        raise TypeError(f"normalize() ref must be a dict, got {type(ref).__name__}")
    import numpy as np
    result = {}
    for k, v in data_dict.items():
        if k in ref and ref[k] > 0:
            try:
                if not (isinstance(v, float) and np.isnan(v)):
                    result[k] = v / ref[k]
                else:
                    result[k] = np.nan
            except (TypeError, ZeroDivisionError):
                result[k] = np.nan
        else:
            result[k] = np.nan
    return result
