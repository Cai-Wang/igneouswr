"""_ternary.py — 兼容门面，直接引用 igneous_geochem.core.ternary 模块"""
import sys
_mod = sys.modules.get('igneous_geochem.core.ternary')
if _mod is None:
    import igneous_geochem.core.ternary as _mod
_mod.__dict__['__name__'] = __name__
sys.modules[__name__] = _mod
