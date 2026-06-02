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


# ── Ti 换算 ────────────────────────────────────────────────

def tio2_to_ti_ppm(tio2_wt_pct):
    """TiO₂ (wt%) → Ti (ppm)。
    原子量: Ti=47.867, O=15.999, TiO₂=79.865
    Ti 质量比 = 47.867 / 79.865 ≈ 0.5994
    Ti (ppm) = TiO₂ (wt%) × 0.5994 × 10000
    """
    tio2 = np.asarray(tio2_wt_pct, dtype=float)
    return tio2 * 0.5994 * 10000.0
