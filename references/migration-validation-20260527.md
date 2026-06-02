# IgneousWR 迁移验证结果 (2026-05-27)

## 验证命令

```bash
cd ~/.hermes/skills/data-science/IgneousWR/scripts
python3 quick_validate.py --quick   # import/registry 检查（秒级回归）
python3 run_test.py                 # 全量出图 + HTML 报告
```

## quick_validate.py --quick 结果

- ✅ 全部 204 项通过
- review_status 分布: verified=24, experimental=26, needs_review=20, deprecated=0
- 注册表总计: 70 张 (mafic: 49, felsic: 32)
- 文件名全部唯一
- 所有图 fn 可调用、rock_types 非空、review_status 已标注
- **元素依赖完整性扫描: 2 处不一致 (见下方)**

## 注册表 vs 代码不一致项

| 图 | registry needed | 代码实际读取的额外元素 | 用途 | 处理 |
|----|----------------|----------------------|------|-----|
| CLS-04 Shand | Al₂O₃, CaO, Na₂O, K₂O | Nb, TiO₂, Y, Zr | ��景着色/参比线 | 不影响出图，记录即可 |
| CLS-11 Jensen | Al₂O₃, FeO/TFe₂O₃, TiO₂, MgO | CaO, K₂O, MnO, Na₂O | 阳离子转换 | 不起跳过检查问题，记录即可 |

## Ti vs TiO₂ 问题

6 张图 needed 写的是 `Ti` 但 `KNOWN_ELEMENTS` 只有 `TiO₂`：
- SRC-02 Spider_PM（蛛网图）
- TEC-03 PearceCann1973_TiZrY
- TEC-04 V_Ti_Sc_ThNb_BaTh_4panel
- TEC-05 Shervais1982_Ti_V
- TEC-14 Pearce1982_ZrY_Zr
- SRC-12 Pearce1995_TiYb_NbYb

影响：用户有 TiO₂ 数据时会跳过这 6 张图。修复：将 Ti 添加到 KNOWN_ELEMENTS，或在 needed 中用 TiO₂ 替代（但图函数内部用 gd.get('Ti') 取数，改 needed 仅影响推荐调度）。

## 全量出图结果 (run_test.py)

- 数据: `/tmp/test_geochem_standard.xlsx` (10样品×41元素)
- 输出: `C:\Users\opcry\Desktop\igenous\` (42张图 + report_20260527.html)
- 成功: 42 张
- 跳过: 7 张（缺 Ti ×6, 缺 MnO+P₂O₅ ×1 影响多重图，无功能bug）
- 有 [`RuntimeWarning: More than 20 figures`] — 已知的 plt.close('all') 问题，已处理
