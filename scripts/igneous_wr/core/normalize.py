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

_JSON_PATH = os.path.join(os.path.dirname(__file__), 'references', 'normalization.json')

with open(_JSON_PATH) as _f:
    _DATA = json.load(_f)

# ── 加载字典常量 → 模块级变量 ──────────────────────────

for _name, _value in _DATA.items():
    if _name.startswith('_'):
        continue
    globals()[_name] = _value

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
