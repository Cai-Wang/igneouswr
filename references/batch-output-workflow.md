# 批量出图工作流

当需要一次性输出 skill 中所有可用图件时，分两步：

## 第一步：plot_recommended（依赖检测 + 自动推荐）

```python
from _style import set_out_dir
import whole_rock_core as wrc

set_out_dir('/path/to/output/dir')
gd = wrc.GeochemData('/path/to/data.xlsx')
result = wrc.plot_recommended(gd)
# → 返回 {'success': [...], 'skipped': [...]}
# → 自动生成 report_YYYYMMDD.html
```

- 根据岩性判定自动选择 felsic/mafic 图件列表
- 跳过缺元素的图
- 输出目录也可以不提前设置——默认为 `../runs/default/`

## 第二步：手动补全未被推荐的图

`plot_recommended` 只返回岩性判定对应的推荐列表。有些图（如基性适用的 RockPlot 三角图）可能被跳过但数据实际支持。

```python
from _chem import feot_calc

gd = GeochemData(path)
# 计算 FeOt
feot = feot_calc(gd.get('FeO'), gd.get('TFe2O3'))
gd._elem_data['FeOt'] = feot  # 注入后各图可访问

# 调用所有剩余图：
from whole_rock.diagrams._classification import plot_afm, plot_cabanis, ...
from whole_rock.diagrams._source import plot_ba_th_la_sm, ...
# ...

for func in [plot_afm, plot_cabanis, ...]:
    try:
        func(gd)
    except Exception as e:
        print(f"skip: {e}")
```

### 已知跳过原因

| 原因 | 说明 |
|------|------|
| `'GeochemData' object has no attribute 'data'` | 函数用了 `gd.data['SiO2']` 旧式访问。涉及 ~10 个函数（frost, villaseca, debonba, debonpq, batchelor, maniar, larocheplut, larochevolc, agrawal, verma）。修复：改为 `gd._elem_data` |
| `feot_calc() missing 1 required positional argument: 'tfe2'` | 同一批 10 个函数用了旧签名 `feot_calc(gd)`，当前签名为 `feot_calc(feo, tfe2)`。修复：改为 `feot_calc(gd.get('FeO'), gd.get('TFe2O3'))` |
| `cannot import name 'mol' from '_chem'` | 函数内有死 import `from _chem import mol`，但 `mol` 函数在 `_chem.py` 门面中不存在且从未被实际调用。修复：直接删除该 import 行 |
| 缺 FeOt | 需手动计算 FeOt = FeO + 0.8998×TFe₂O₃ 并注入 `gd._elem_data['FeOt']`。涉及：AFM, Miyashiro |
| 缺特定微量元素 | 跳过有理��数据真没有 |

## 验证

```bash
python3 quick_validate.py --quick  # 秒级回归
python3 quick_validate.py           # 完整模式（出所有图，耗时较长）
```
