# 独立调试脚本 → IgneousWR 边界 JSON 迁移模式

## 场景
用户提供了独立运行的 Python 调试脚本（如 `mullen1983_mtp_v7_debug.py`），包含手写坐标且经过逐点校准。需要将这些精确坐标迁移到 IgneousWR 的 `boundaries/cls/{name}.json` 并更新对应的 `plot_{name}()` 函数。

## 流程

### 步骤 1：确认坐标系约定差异

**最关键的一步：识别调试脚本的三元图约定 vs IgneousWR 的约定。**

| 属性 | 调试脚本（可能） | IgneousWR |
|------|-----------------|-----------|
| `ternary_to_xy(a, b, c)` | 参数顺序任意 | 固定 `(top, left, right)` |
| 顶点映射 | 用户自定义 | 顶角=top, 左下=left, 右下=right |
| 坐标格式 | 任意归一化 | 三元百分比（归一化到 100） |

**验证坐标约定：**
```python
# 调试脚本中可能需要打印确认
print(ternary_to_xy.__doc__)  # 看约定
print(f"顶角坐标: {ternary_to_xy(100, 0, 0)}")  # 应接近 (0.5, 0.866)
```

### 步骤 2：推送端点坐标到 JSON 格式

调试脚本中的端点（如 `(23, 77, 0)`）需要按 IgneousWR 的 `(a=top, b=left, c=right)` 顺序重排：

```python
# 调试脚本坐标格式: (MnO×10, TiO₂, P₂O₅×10)
# 调试 ternary_to_xy(a=左下, b=顶, c=右下)
script_pt = (23, 77, 0)  # (mno, tio, p2o5)

# JSON 需要: (a=TiO₂, b=10×MnO, c=10×P₂O₅) = (顶, 左下, 右下)
json_pt = (script_pt[1], script_pt[0], script_pt[2])  # (77, 23, 0)
```

**原则：只交换数值列顺序，不动坐标系顶点标签布局。** 三元图的顶点标签（顶=TiO₂、左下=10×MnO、右下=10×P₂O₅）是最终图件的规范，数据迁就坐标系，而非反之。

### 步骤 3：识别端点→曲线对应

脚本通常有 4 条线（L1-L4），映射到 JSON 的 m0-m3：

| 脚本线 | JSON 曲线 | 线型 | 说明 |
|--------|----------|------|------|
| L1 A→B→C | m0 | 实线 | 常为左上→中→右下 |
| L2 D→E→F | m1 | 实线 | 常为中左→中→中右 |
| L3 G→H→I | m2 | 虚线 | 常为左下→中→底边 |
| L4 B→J | m3 | 虚线 | 常为内部斜线 |

验证端点标签和映射关系无误后，写入 JSON。

### 步骤 4：更新 plot_{name}() 函数

- 保持从 JSON 加载边界的模式（使用 `load_boundary('cls', 'mullen')`）
- 将提取的端点赋给命名的变量（A, B, C, ...），便于区域填充引用
- 区分实线/虚线：`ax.plot(..., 'k-', lw=1.5)` 和 `ax.plot(..., 'k--', lw=1.2)`
- 区域填充使用 `corners['top']`/`corners['left']`/`corners['right']` 而非硬编码 (0.5, 0.866) 等
- 标签坐标用 `ternary_to_xy(np.array([val]), np.array([val]), np.array([val]))` 包裹为数组以兼容标量/向量模式

### 步骤 5：区域填充验证

每个多边形必须：
1. **闭合**：起点=终点（或 matplotlib 自动闭合）
2. **边界对齐**：多边形边界线使用分界线的端点坐标，确保与线重合无缝隙
3. **不重叠**：相邻区域的边界共享同一条分界线的坐标，避免缝隙或覆盖

### 验证

```bash
cd ~/.hermes/skills/data-science/IgneousWR/scripts
python3 -c "
import sys; sys.path.insert(0, '.')
from igneous_wr_core import GeochemData, plot_mullen
# 用测试数据验证
gd = GeochemData('/tmp/test_geochem_standard.xlsx')
fig, ax = plot_mullen(gd, out_dir='/tmp/test_mullen')
"
```

## 已知案例

| 图件 | 日期 | 脚本来源 | 坐标差异 | 处理方式 |
|------|------|---------|---------|---------|
| Mullen MTP | 2026-05-29 | `mullen1983_mtp_v7_debug.py` | 脚本 (MnO×10, TiO₂, P₂O₅×10) → JSON (TiO₂, 10×MnO, 10×P₂O₅) | 列重排：交换第1和第2列 |
| Cabanis | 2026-05-27 | RockPlot SVG | SVG像素→三元空间 | 用 `_pixel_to_ternary` 公式转换 |
