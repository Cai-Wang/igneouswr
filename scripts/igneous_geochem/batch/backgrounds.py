"""
backgrounds.py — 批量生成所有图件的纯底图（无数据投点）

功能：
  - 遍历 DIAGRAM_REGISTRY 全部 70 张图，生成纯底图
  - 两种模式：
    mode='minimal': 所有元素为 NaN，0 样品 — 适合验证大部分图
    mode='full':    伪造 5 个样品的全元素数据 + patch scatter 为空 — 覆盖全部 70 张
                    （含 REE/蛛网图、Ti 依赖图、参数需计算的图等）
  - 输出文件名自动为 registry 中定义的 spec.filename（CLS-01_xxx.png 格式）
  - 整合了旧 batch_backgrounds.py + batch_backgrounds_fix.py 的功能

用法（通过 CLI 包装器，或直接 import）：
    from igneous_geochem.batch.backgrounds import run_batch
    run_batch(mode='full', out_dir='../runs/backgrounds')
"""
import os, sys
import numpy as np

# ── 项目默认输出路径 ──
DEFAULT_OUT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'runs', 'backgrounds'
))

# ── 注册表 ──
from igneous_geochem.diagrams.registry import DIAGRAM_REGISTRY


# ════════════════════════════════════════════════════════════════
# FakeGeochemData — 伪造的 GeochemData
# ════════════════════════════════════════════════════════════════
class FakeGeochemData:
    """伪造的 GeochemData，完全 mock 出图所需全部接口。

    mode='minimal':
        所有 get() 返回 np.array([], dtype=float)（0 样品全 NaN）
        groups=None → scatter 不画出任何点
        check_elements() 返回空列表

    mode='full':
        提供 5 个假样品的全元素数据（Ti = 6000 ppm, 其他元素随机值）
        groups 设为一组 'G1'
        check_elements() 返回空列表
        scatter_samples 会被 patch 为空操作 → 不出点
    """

    _ALL_ELEMS = [
        'SiO2','TiO2','Al2O3','Fe2O3','FeO','TFe2O3','FeOt','MnO','MgO',
        'CaO','Na2O','K2O','P2O5','LOI','Total',
        'Li','Be','Sc','V','Cr','Co','Ni','Cu','Zn','Ga',
        'Rb','Sr','Y','Zr','Nb','Mo','Ag','Cd','In','Sn','Sb',
        'Cs','Ba','La','Ce','Pr','Nd','Sm','Eu','Gd','Tb','Dy',
        'Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Tl','Pb',
        'Bi','Th','U',
        'Ti',   # ppm 级 Ti（非 TiO2），PearceCann/Shervais 等需要
        'BaO',
    ]

    def __init__(self, mode='minimal'):
        self.mode = mode
        self.labels = []
        self.groups = None

        if mode == 'full':
            N = 5
            self.labels = ['SMP01', 'SMP02', 'SMP03', 'SMP04', 'SMP05']
            self.groups = ['G1', 'G1', 'G1', 'G1', 'G1']
            self._data = {}
            rng = np.random.default_rng(42)
            for elem in self._ALL_ELEMS:
                if elem == 'Ti':
                    self._data[elem] = np.array([6000.0, 6200.0, 5800.0, 6400.0, 6100.0],
                                                dtype=float)
                elif elem in ('SiO2', 'Al2O3'):
                    self._data[elem] = np.array([48.0, 52.0, 56.0, 60.0, 64.0], dtype=float)
                elif elem in ('FeO', 'FeOt', 'MgO', 'CaO', 'Na2O', 'K2O', 'TiO2', 'P2O5'):
                    self._data[elem] = np.array([3.0, 4.0, 5.0, 6.0, 7.0], dtype=float)
                elif elem in ('TFe2O3', 'Fe2O3'):
                    self._data[elem] = np.array([5.0, 6.0, 7.0, 8.0, 9.0], dtype=float)
                elif elem in ('MnO',):
                    self._data[elem] = np.array([0.1, 0.12, 0.15, 0.11, 0.13], dtype=float)
                elif elem in ('LOI', 'Total'):
                    self._data[elem] = np.array([1.0, 0.5, 0.8, 0.3, 0.6], dtype=float)
                elif elem in ('BaO',):
                    self._data[elem] = np.array([0.05, 0.06, 0.04, 0.07, 0.05], dtype=float)
                else:
                    self._data[elem] = rng.uniform(1, 100, N).astype(float)
        else:
            self._data = {}
        self._elem_data = self._data

    def get(self, elem_name, default=None):
        if self.mode == 'minimal':
            return np.array([], dtype=float)
        canon = self._elem_data.get(elem_name)
        if canon is not None:
            return canon
        from whole_rock_core import ELEM_ALIAS
        alias = ELEM_ALIAS.get(elem_name, None)
        if alias and alias in self._elem_data:
            return self._elem_data[alias]
        print(f"  ⚠️ FakeGeochemData: 缺少元素 '{elem_name}'")
        return np.full(len(self.labels) if self.mode == 'full' else 0, np.nan)

    def check_elements(self, *elems, strict=False):
        return []

    def has_element(self, elem_name):
        if self.mode == 'minimal':
            return True
        return elem_name in self._elem_data or elem_name.upper() in self._elem_data

    def get_any(self, *elems):
        for e in elems:
            val = self.get(e)
            if np.any(~np.isnan(val)):
                return val
        return np.full(len(self.labels) if self.mode == 'full' else 0, np.nan)


# ════════════════════════════════════════════════════════════════
# 主循环
# ════════════════════════════════════════════════════════════════
def run_batch(mode='full', out_dir=None):
    if out_dir is None:
        out_dir = DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    print(f"模式: {mode}")
    print(f"输出目录: {out_dir}")
    print(f"共 {len(DIAGRAM_REGISTRY)} 张图")
    print("=" * 60)

    # ── full 模式：patch scatter_samples 为空操作 ──
    if mode == 'full':
        from igneous_geochem.report import style as _style_mod
        _original_scatter = _style_mod.scatter_samples
        _style_mod.scatter_samples = lambda *a, **kw: None

    # ── patch save_fig 用 spec.filename 输出 ──
    from igneous_geochem.report.style import save_fig as _orig_save_fig
    from igneous_geochem.report import style as _style_mod_for_save
    _current_spec = [None]

    def _patched_save_fig(fig, old_filename, _out_dir):
        new_name = _current_spec[0].filename
        return _orig_save_fig(fig, new_name, _out_dir)

    _style_mod_for_save.save_fig = _patched_save_fig

    success = []
    failed = []

    for i, spec in enumerate(DIAGRAM_REGISTRY, 1):
        _current_spec[0] = spec
        fn = spec.fn
        out_name = spec.filename

        try:
            print(f"[{i:2d}/{len(DIAGRAM_REGISTRY)}] {out_name}", end='')

            gd = FakeGeochemData(mode=mode)
            fig, ax = fn(gd, out_dir=out_dir, save=True)

            if fig is not None:
                success.append(out_name)
                print(f"  ✓")
            else:
                print(f"  ⚠ 函数返回 None")
                failed.append(out_name)

        except Exception as e:
            print(f"  ❌ {type(e).__name__}: {e}")
            failed.append(out_name)

    # ── 恢复 ──
    if mode == 'full':
        _style_mod.scatter_samples = _original_scatter
    _style_mod_for_save.save_fig = _orig_save_fig

    print("=" * 60)
    print(f"成功: {len(success)}, 失败: {len(failed)}")
    if failed:
        print("失败列表:")
        for f in failed:
            print(f"  - {f}")
    return success, failed
