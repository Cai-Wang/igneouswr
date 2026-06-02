"""_chem.py — 兼容门面，直接引用 igneous_wr.core.chem 模块"""
import sys
_mod = sys.modules.get('igneous_wr.core.chem')
if _mod is None:
    import igneous_wr.core.chem as _mod
_mod.__dict__['__name__'] = __name__
sys.modules[__name__] = _mod
