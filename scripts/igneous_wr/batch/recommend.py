"""
batch/recommend.py — 推荐图件调度

功能：
- recommended_diagrams 根据岩石类型推荐图件列表
- plot_recommended 一键出所有推荐图
- 内部使用 DIAGRAM_REGISTRY 过滤缺元素图

注意：内部 import 倒挂层 — 已全部改为 igneous_wr/ 包内引用（2026-06-05）
"""
from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY, MAFIC_DIAGRAMS, FELSIC_DIAGRAMS
import numpy as np


# 辅助：从 DIAGRAM_REGISTRY 按 fn 快速查找
_registry_by_fn = {d.fn: d for d in DIAGRAM_REGISTRY}


def _registry_lookup(fn):
    return _registry_by_fn.get(fn)


def _ti_from_tio2(gd, elem):
    """Ti → TiO2 回退检查。"""
    return elem == 'Ti' and 'TiO2' in gd._elem_data


def recommended_diagrams(gd, rock_type='auto'):
    """根据岩石类型推荐图件列表。

    Args:
        gd: GeochemData 实例
        rock_type: 'mafic', 'felsic', 或 'auto'（自动从 SiO₂ 判断）

    Returns:
        (list of (plot_fn, description), list of (desc, reason)) — 推荐图和跳过的图
    """
    if rock_type == 'auto':
        sio2 = gd.get('SiO2')
        sio2_min = np.nanmin(sio2) if not np.all(np.isnan(sio2)) else 0
        rock_type = 'mafic' if sio2_min < 52 else 'felsic'
        type_name = '镁铁质 (Mafic, SiO₂ min < 52%)' if sio2_min < 52 else '长英质 (Felsic, SiO₂ min ≥ 52%)'
    elif rock_type == 'mafic':
        type_name = '镁铁质 (Mafic)'
    else:
        type_name = '长英质 (Felsic)'

    pool = MAFIC_DIAGRAMS if rock_type == 'mafic' else FELSIC_DIAGRAMS

    results = []
    skipped = []
    for fn, desc, needed, any_of in pool:
        spec = _registry_lookup(fn)
        review_tag = ""
        if spec:
            if spec.review_status == "experimental":
                review_tag = " [实验性]"
            elif spec.review_status == "needs_review":
                review_tag = " [未校正]"
        missing = [e for e in needed if e not in gd._elem_data and not _ti_from_tio2(gd, e)]
        if missing:
            skipped.append((desc, missing))
            continue
        if any_of:
            any_present = [e for e in any_of if e in gd._elem_data or _ti_from_tio2(gd, e)]
            if not any_present:
                skipped.append((desc, f"any_of {any_of} 全部缺失"))
                continue
        results.append((fn, desc, review_tag))

    print(f"[IgneousWR] 岩性判定: {type_name}")
    print(f"[IgneousWR] 推荐图件: {len(results)} 张")
    for fn, desc, tag in results:
        print(f"   ✓ {fn.__name__:28s} — {desc}{tag}")
    if skipped:
        print(f"[IgneousWR] 因缺元素跳过: {len(skipped)} 张")
        for desc, missing in skipped:
            print(f"   ✗ 缺 {missing}  → 跳过 {desc}")

    return results, skipped


def plot_recommended(gd, out_dir=None, rock_type='auto'):
    """根据岩石类型一键出所有推荐图。

    Args:
        gd: GeochemData 实例
        out_dir: 输出目录，None 则用默认
        rock_type: 'mafic', 'felsic', 或 'auto'（自动从 SiO₂ 判断）

    Returns:
        dict — {'success': [(fn_name, file), ...], 'skipped': [(desc, reason), ...]}
    """
    from igneous_wr.report.style import DEFAULT_OUT_DIR, _OUT_DIR
    final_dir = out_dir or _OUT_DIR or DEFAULT_OUT_DIR

    diagrams, skipped_pre = recommended_diagrams(gd, rock_type=rock_type)
    success = []
    skipped = list(skipped_pre)

    for item in diagrams:
        fn = item[0]
        desc = item[1]
        try:
            fig_result = fn(gd, out_dir=final_dir)
            if isinstance(fig_result, tuple) and len(fig_result) == 2 and fig_result[0] is None:
                skipped.append((desc, "缺关键元素（strict check 未通过）"))
                continue
            # 从 DIAGRAM_REGISTRY 查文件名，而非 FILENAME_MAP（已移除）
            from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY
            fname = f'{fn.__name__}.png'
            for d in DIAGRAM_REGISTRY:
                if d.fn.__name__ == fn.__name__:
                    fname = d.filename
                    break
            success.append((fn.__name__, fname))
        except Exception as e:
            skipped.append((desc, str(e)))

    print(f"\n[IgneousWR] ==== 推荐出图完成 ====")
    print(f"   ✓ 成功: {len(success)} 张")
    for name, fname in success:
        print(f"      {name:28s} → {fname}")
    if skipped:
        print(f"   ✗ 跳过: {len(skipped)} 项")
        for desc, reason in skipped:
            print(f"      {desc} ({reason})")

    # 自动生成 HTML 报告
    gd_path = gd.path if hasattr(gd, 'path') else None
    try:
        from igneous_wr.report.style import generate_report_html
        generate_report_html(
            success, skipped, gd=gd, out_dir=final_dir, rock_type=rock_type)
    except Exception as e:
        print(f"[IgneousWR] ⚠️ 报告生成跳过: {e}")

    return {'success': success, 'skipped': skipped}
