"""
io/excel.py — Excel 数据读取与检测限解析

功能：
- Excel 文件查找（find_excel）
- 标准/转置格式自动检测
- 检测限字符串解析（<0.50 → 半值/零值/NaN）
- 元素别名映射（FeO/TFe2O3 等）
"""
import os, glob
import numpy as np

# ── 元素配置 ──
ELEM_ALIAS = {
    'TFe2O3': 'TFe2O3', 'TFe\u2082O\u2083': 'TFe2O3', 'Fe2O3': 'TFe2O3', 'Fe2O3T': 'TFe2O3',
    'FeO': 'FeO', 'FeO*': 'FeO',
    'SiO2': 'SiO2', 'SiO\u2082': 'SiO2',
    'Na2O': 'Na2O', 'Na\u2082O': 'Na2O',
    'K2O': 'K2O', 'K\u2082O': 'K2O',
    'MgO': 'MgO',
    'Al2O3': 'Al2O3', 'Al\u2082O\u2083': 'Al2O3',
    'CaO': 'CaO',
    'TiO2': 'TiO2', 'TiO\u2082': 'TiO2',
}

KNOWN_ELEMENTS = {
    'SiO2','TiO2','Al2O3','TFe2O3','FeO','MnO','MgO','CaO','Na2O','K2O',
    'P2O5','LOI','TOTAL','Li','Be','Sc','Ti','V','Cr','Mn','Co','Ni','Cu','Zn',
    'Ga','Rb','Sr','Y','Zr','Nb','Mo','Sn','Cs','Ba','La','Ce','Pr','Nd',
    'Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Tl','Pb','Th','U'
}

# 检测限解析策略
DL_STRATEGY_HALF = 'half'
DL_STRATEGY_ZERO = 'zero'
DL_STRATEGY_NAN  = 'nan'


def parse_value(v, dl_strategy='half'):
    """解析单元格值：检测限字符串 → 按策略处理，数字字符串 → float，杂字符串 → NaN。"""
    if v is None:
        return np.nan
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s:
        return np.nan
    if s.startswith('<') or s.startswith('\u2264'):
        try:
            val = float(s.lstrip('<\u2264').strip())
            if dl_strategy == 'half':
                return val * 0.5
            elif dl_strategy == 'zero':
                return 0.0
            else:
                return np.nan
        except ValueError:
            return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def find_excel(path=None):
    """查找 Excel 数据文件。

    1. 用户明确指定路径 → 直接用
    2. 当前工作目录搜索 *merged*geochem*.xlsx
    3. 找到 1 个 → 用；多个 → 报告；0 个 → 报错
    """
    if path:
        if os.path.exists(path):
            return path
        raise FileNotFoundError(f"指定的 Excel 文件不存在: {path}")

    candidates = glob.glob('*merged*geochem*.xlsx')
    if not candidates:
        candidates = glob.glob('*geochem*.xlsx')
    if len(candidates) == 1:
        print(f"[IgneousWR] 自动发现 Excel: {candidates[0]}")
        return candidates[0]
    elif len(candidates) > 1:
        raise FileNotFoundError(
            f"找到多个 Excel 文件: {candidates}\\n请用 EXCEL 参数指定路径。")
    else:
        raise FileNotFoundError("未找到 Excel 文件，请用 EXCEL 参数指定路径。")
