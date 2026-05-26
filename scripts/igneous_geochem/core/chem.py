"""
_chem.py — 地球化学计算函数

依赖: numpy
"""

import numpy as np


def feot_calc(feo, tfe2):
    """FeOt = FeO + 0.8998 * TFe2O3。
    - FeO 全 NaN 时仅用 TFe2O3 换算
    - TFe2O3 全 NaN 时仅用 FeO
    - 两者都 NaN 则返回全 NaN
    """
    feo = np.asarray(feo); tfe2 = np.asarray(tfe2)
    if np.all(np.isnan(feo)):
        return 0.8998 * tfe2
    if np.all(np.isnan(tfe2)):
        return feo
    return np.where(np.isnan(feo), 0.8998 * tfe2, feo + 0.8998 * tfe2)
