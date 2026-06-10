# _classification.py 状态记录

## 当前状态（2026-05-25，已完成全部 RockPlot SVG 整合）

`_classification.py` 已有 **14 个函数可用**（641 行，32KB），所有 6 张 RockPlot SVG 三角图已完成：

### 原有函数（8 个）
- `plot_tas` — TAS 全碱-硅分类图
- `plot_k2o_sio2` — K₂O–SiO₂ 钾系列分类图
- `plot_afm` — AFM 三角图（Irvine & Baragar 1971）
- `plot_shand` — A/CNK–A/NK 铝质分类图
- `plot_winchester_floyd` — Zr/TiO₂–Nb/Y 分类图
- `plot_co_th` — Co-Th 系列判别图（Hastie 2007）
- `plot_an_ab_or` — An-Ab-Or 长石分类图（O'Connor 1965）
- `plot_qapf` — Q-A-PF 深成岩分类图（Streckeisen 1976）

### RockPlot SVG 新增完成（6 个）
- `plot_cabanis` — Cabanis (1989) La/10-Y/15-Nb/8 基性三角图
- `plot_mullen` — Mullen (1983) TiO₂-10MnO-10P₂O₅ 基性三角图
- `plot_jensen` — Jensen (1976) FeOt+TiO₂-Al₂O₃-MgO 阳离子三角图
- `plot_oconnor_volc` — O'Connor (1965) An-Ab-Or 火山岩分类三角图
- `plot_ohta_arai` — Ohta & Arai (2007) M-F-W 三角图
- `plot_pearce1977` — Pearce (1977) FeOt-MgO-Al₂O₃ 三角图

### 当前全技能状态
- `_classification.py`: 27 函数（含全部27张CLS图）✓
- `_tectonic.py`: 20 函数（含全部20张TEC图）✓
- `_source.py`: 15 函数 ✓
- `_evolution.py`: 6 函数 ✓
- **总计**: 68 个绘图函数，DIAGRAM_REGISTRY 已注册 67 条（CLS-25已删除）
- **注册表总数校验**: 67（quick_validate.py 校验码需对应更新）

## 损坏历史

1. **第一次**：~800 行 → 329 bytes（被错误 write_file 覆盖为仅 import 头）
2. **第二次**：329 bytes → 77 行（追加 TAS+K2O 后中断）
3. **第三次**：恢复中通过 heredoc 追加 AFM 时 `&` 符号导致中断

## 推荐恢复方法

**不要**在 chat 中用多次 write_file 或 heredoc 追加。每次 interrupt 或 context 压缩都会丢失进度。

**正确做法**：

```python
# execute_code 中一次性生成
content = '''... 整个文件内容 ...'''
with open('_classification.py', 'w') as f:
    f.write(content)
```

或写一个独立 Python 生成脚本到 `/tmp/gen_cls.py`，然后用 `terminal` 执行。
