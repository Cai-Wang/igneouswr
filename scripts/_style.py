"""_style.py — 兼容门面，直接引用 igneous_wr.report.style 模块"""
import sys
_style_mod = sys.modules.get('igneous_wr.report.style')
if _style_mod is None:
    import igneous_wr.report.style as _style_mod
# 把新模块的 globals 接管到本模块的 globals
_style_mod.__dict__['__name__'] = __name__
# 同步所有符号
sys.modules[__name__] = _style_mod
