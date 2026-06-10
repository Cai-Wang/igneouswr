"""IgneousWR 核心逻辑单元测试"""

import sys
import os
# 确保可在未安装包时直接运行
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from igneous_wr.io.excel import (
    parse_value, ELEM_ALIAS, KNOWN_ELEMENTS,
    DL_STRATEGY_HALF, DL_STRATEGY_ZERO, DL_STRATEGY_NAN,
)
from igneous_wr.core.chem import feot_calc, tio2_to_ti_ppm
from igneous_wr.core.normalize import CHONDRITE, NORM_DICT, normalize


# ── parse_value ────────────────────────────────────────────

def test_parse_value_none():
    assert np.isnan(parse_value(None))


def test_parse_value_number():
    assert parse_value(42.5) == 42.5
    assert parse_value(0) == 0.0
    assert parse_value(-1.5) == -1.5


def test_parse_value_number_string():
    assert parse_value("42.5") == 42.5


def test_parse_value_empty():
    assert np.isnan(parse_value(""))
    assert np.isnan(parse_value("  "))


def test_parse_value_detection_limit_half():
    assert parse_value("<0.50") == 0.25
    assert parse_value("<1.0") == 0.5


def test_parse_value_detection_limit_zero():
    assert parse_value("<0.50", dl_strategy='zero') == 0.0


def test_parse_value_detection_limit_nan():
    assert np.isnan(parse_value("<0.50", dl_strategy='nan'))


def test_parse_value_garbage():
    assert np.isnan(parse_value("N/D"))
    assert np.isnan(parse_value("bdl"))
    assert np.isnan(parse_value("---"))


# ── ELEM_ALIAS ─────────────────────────────────────────────

def test_elem_alias_common():
    assert ELEM_ALIAS['Fe2O3'] == 'TFe2O3'
    assert ELEM_ALIAS['TFe2O3'] == 'TFe2O3'
    assert ELEM_ALIAS['SiO2'] == 'SiO2'
    assert ELEM_ALIAS['FeO'] == 'FeO'


def test_elem_alias_not_found():
    assert ELEM_ALIAS.get('Unknown123') is None


# ── KNOWN_ELEMENTS ─────────────────────────────────────────

def test_known_elements_major():
    for e in ['SiO2', 'TiO2', 'Al2O3', 'FeO', 'MgO', 'CaO', 'Na2O', 'K2O', 'P2O5']:
        assert e in KNOWN_ELEMENTS, f"{e} should be in KNOWN_ELEMENTS"


def test_known_elements_trace():
    for e in ['La', 'Ce', 'Rb', 'Sr', 'Zr', 'Nb', 'Pb', 'Th', 'U']:
        assert e in KNOWN_ELEMENTS, f"{e} should be in KNOWN_ELEMENTS"


# ── feot_calc ──────────────────────────────────────────────

def test_feot_both_nan():
    result = feot_calc(np.array([np.nan]), np.array([np.nan]))
    assert np.isnan(result[0])


def test_feot_feo_only():
    result = feot_calc(np.array([5.0, 10.0]), np.array([np.nan, np.nan]))
    np.testing.assert_array_almost_equal(result, [5.0, 10.0])


def test_feot_tfe_only():
    result = feot_calc(np.array([np.nan, np.nan]), np.array([10.0, 20.0]))
    # 0.8998 * TFe2O3
    np.testing.assert_array_almost_equal(result, [8.998, 17.996])


def test_feot_both():
    """FeOt = FeO + 0.8998 * TFe2O3"""
    result = feot_calc(np.array([3.0]), np.array([2.0]))
    expected = 3.0 + 0.8998 * 2.0
    np.testing.assert_almost_equal(result[0], expected)


def test_feot_mixed():
    feo = np.array([3.0, np.nan, 5.0])
    tfe = np.array([np.nan, 10.0, 2.0])
    result = feot_calc(feo, tfe)
    # Index 0: feo=3, tfe=NaN → 3 + 0.8998*NaN = NaN
    assert np.isnan(result[0])
    # Index 1: feo=NaN → 0.8998*10 = 8.998
    np.testing.assert_almost_equal(result[1], 8.998)
    # Index 2: feo=5, tfe=2 → 5 + 0.8998*2 = 6.7996
    np.testing.assert_almost_equal(result[2], 5.0 + 0.8998 * 2.0)


# ── tio2_to_ti_ppm ─────────────────────────────────────────

def test_tio2_to_ti_ppm_zero():
    assert tio2_to_ti_ppm(0) == 0.0


def test_tio2_to_ti_ppm_typical():
    """TiO₂ 1 wt% = 1 * 0.5994 * 10000 = 5994 ppm Ti"""
    result = tio2_to_ti_ppm(1.0)
    np.testing.assert_almost_equal(result, 5994.0)


def test_tio2_to_ti_ppm_array():
    result = tio2_to_ti_ppm(np.array([0.5, 1.0, 2.0]))
    np.testing.assert_array_almost_equal(result, [2997.0, 5994.0, 11988.0])


# ── normalize ──────────────────────────────────────────────

def test_normalize_basic():
    data = {'La': 100, 'Ce': 200}
    ref = {'La': 10, 'Ce': 50}
    result = normalize(data, ref)
    assert result['La'] == 10.0
    assert result['Ce'] == 4.0


def test_normalize_missing_ref():
    """元素不在 ref 中应返回 NaN"""
    data = {'La': 100, 'K': 5000}
    ref = {'La': 10}
    result = normalize(data, ref)
    assert result['La'] == 10.0
    assert np.isnan(result['K'])


def test_normalize_chondrite_la():
    """验证 CHONDRITE 中 La=0.237, 所以 10 ppm La → 42.19"""
    result = normalize({'La': 10.0}, CHONDRITE)
    np.testing.assert_almost_equal(result['La'], 10.0 / 0.237, decimal=2)


# ── NORM_DICT 一致性 ───────────────────────────────────────

def test_norm_dict_ree_oneil_oneill_consistent():
    """O'Neil 和 O'Neill 键应指向同一 dict 对象"""
    v1 = NORM_DICT["REE chondrite (Palme & O'Neil 2014)"]
    v2 = NORM_DICT["REE chondrite (Palme & O'Neill 2014)"]
    assert v1 is v2, "Both keys must resolve to the same dict"
    assert v1['Tm'] == 0.02609


def test_norm_dict_chondrite_ms95():
    """默认 CHONDRITE 应是 MS95"""
    assert CHONDRITE['Tm'] == 0.0247


def test_cl_chondrite_full_short():
    """CL Chondrite FULL(76) 应为 SHORT(30) 的超集"""
    from igneous_wr.core.normalize import (
        CL_CHONDRITE_PALME_AND_ONEILL_2014_FULL as cl_full,
        CL_CHONDRITE_PALME_AND_ONEILL_2014_SHORT as cl_short,
    )
    assert len(cl_full) == 76
    assert len(cl_short) == 30
    for k, v in cl_short.items():
        assert cl_full[k] == v, f"CL_SHORT[{k}]={v} != CL_FULL[{k}]={cl_full[k]}"
    # SHORT is a perfect subset of FULL
    assert 'Ag' in cl_full and 'Ag' not in cl_short


def test_long_aliases():
    """NMORB_LONG 和 PRIMITIVE_MANTLE_LONG 是别名"""
    from igneous_wr.core.normalize import (
        NMORB_LONG_SUN_AND_MS_1989, NMORB_SUN_AND_MS_1989,
        PRIMITIVE_MANTLE_LONG_SUN_AND_MS_1989, PRIMITIVE_MANTLE_SUN_AND_MS_1989,
    )
    assert NMORB_LONG_SUN_AND_MS_1989 is NMORB_SUN_AND_MS_1989
    assert PRIMITIVE_MANTLE_LONG_SUN_AND_MS_1989 is PRIMITIVE_MANTLE_SUN_AND_MS_1989


def test_norm_dict_cl_full_short():
    """NORM_DICT 中使用 FULL/SHORT 标签"""
    full = [k for k in NORM_DICT if 'FULL' in k]
    short = [k for k in NORM_DICT if 'SHORT' in k]
    assert len(full) == 1
    assert len(short) == 1
