# RockPlot SVG 坐标提取现状与待办清单

SVG 源文件在 `/tmp/rockplot-extract/dist/svg/diagrams/`（来自 `D:\RockPlot` app.asar 解包），共 55+ 张图。
提取的坐标 JSON 在 `/tmp/extracted_paths.json`（40KB，仅 8 张图已提取）。

## 已完成提取的图

以下 8 张图的边界线像素坐标已在 `/tmp/extracted_paths.json` 中：

| 图 | SVG 文件 | 路径数 | 说明 |
|---|---|---|---|
| Cabanis | Cabanis.svg | 1 条主分界线（20 点） | La/10-Y/15-Nb/8 三角图 |
| Mullen | Mullen.svg | 4 条边界线 | TiO2-10MnO-10P2O5 三角图 |
| Jensen | Jensen.svg | 11 条填充多边形 | Al2O3-FeOt+TiO2-MgO，class="polygons" |
| Harris | Harris.svg | 5 条边界线 | Hf-Rb/30-3Ta 三角图（轴标非预期 Th-Ta） |
| OConnorVolc | OConnorVolc.svg | 7 条直线分区 | Ab-An-Or 三角图 |
| OhtaArai | OhtaArai.svg | 3 条贝塞尔曲线 | F-M-W 三角图（轴标非预期 La/Th-Nb/Y-Hf） |
| Pearce1977 | Pearce1977.svg | 4 条虚线边界 | MgO-FeOt-Al2O3 三角图（轴标非预期 Ti-Zr-Y） |
| MullerKternary | MullerKternary.svg | 3 个并列子图 | 每个等边小三角 |

### 特殊情况
- **QAPFVolc**: 文件存在但有 182 条路径全为 0pts（base64 或其他格式），需换方法
- **MullerKternary**: 3 个独立等边小三角（W=248.03, H=248.03），非标准大三角

## 坐标映射公式

三角图 SVG 映射：
```
三角形顶点（像素）: A=(303.69, 0), B=(0, 526), C=(607.37, 526)
SVG 变换: translate(80, 50)
```

从像素 (px, py) 到三元坐标 (a=顶角, b=左下, c=右下)：
```python
# 离散方法
a_norm = 100 * (1 - py / H)           # 越靠近顶部 = A 越大
b_norm = 100 * (1 - px / W) * (1 - a_norm / 100)  # 靠近左边框 = B 越大
c_norm = 100 - a_norm - b_norm

# 然后 ternary_to_xy(a, b, c) 转换到笛卡尔坐标画图
```

**注意**：这个映射是近似线性，与 `ternary_to_xy()` 的等边三角投影不完全一致。用 SVG 数据时需要比对已知角的刻度标签验证精度。

## 写入 skill 代码的流程

1. 从 `/tmp/extracted_paths.json` 读取 SVG 像素坐标
2. 将像素坐标通过映射公式转为三元百分比 (a, b, c)
3. 用 `ternary_to_xy(a_vals, b_vals, c_vals)` 转为笛卡尔坐标
4. 写入 `_classification.py` 或 `_tectonic.py` 的对应绘图函数
5. 注册到 `whole_rock_core.py` 的 `DIAGRAM_REGISTRY`
6. 验证：跑 quick_validate.py + 模拟数据出图

### 坐标边界线格式

```python
# 在绘图函数中，边界线用三元百分比列表存储
boundary_lines = [
    {
        "a": [ ... ],  # 顶角 % 序列
        "b": [ ... ],  # 左下角 % 序列
        "c": [ ... ],  # 右下角 % 序列，或 100-a-b
        "style": {"ls": "--", "color": "#555", "lw": 1.2},
    },
    ...
]
# 然后用 ternary_to_xy(a, b, c) 转为笛卡尔坐标绘制
```

## 剩余工作

- [ ] Cabanis: 坐标已有（1 条边界线 20 点），需写入 `_classification.py` 绘图函数
- [ ] Mullen: 坐标已有（4 条边界线），需写入 `_classification.py` 绘图函数
- [ ] Jensen: 坐标已有（19 条多边形边界），需写入 `_classification.py` 绘图函数
- [ ] OConnorVolc: 坐标已有（7 条分区线），需写入 `_classification.py` 绘图函数
- [ ] OhtaArai: 坐标已有（4 条曲线），需写入 `_classification.py` 绘图函数
- [ ] Pearce1977: 坐标已有（4 条虚线边界），需写入 `_classification.py` 绘图函数
- [ ] QAPFVolc: 需换方法提取（SVG 路径全为 0pts）
- [ ] Harris: 坐标已有（5 条边界线），需写入 `_tectonic.py`
- [ ] MullerKternary: 坐标已有（3 个子图），需写入 `_tectonic.py`
- [ ] 全部完成后将边界坐标从 `/tmp/extracted_paths.json` 整合到 skill 内部的 `references/` 目录
