# WF1977 CLS-05 出图失败诊断（2026-06-07）

## 两种不同的根因，同一症状

CLS-05 (Winchester & Floyd 1977) 出图失败报 `Size is invalid. Valid font size are xx-small, x-small...` 可能由两种完全不同原因引起：

### 原因 A：numpy 2.x 兼容性（本次遇到）

**症状**：
```
TypeError: 'NoneType' object is not iterable  # 伴随其他图也报错，如 REE
或直接：
Size is invalid. Valid font size are xx-small, x-small, small, medium, large...
```

**根因**：系统 matplotlib（通过 apt 安装的）是用 numpy 1.x 编译的。当 `pip install numpy` 升级到 2.x 时，matplotlib 的 Cython 扩展 `.so` 文件无法加载 numpy 2.x 的内部结构。但错误可能不会显示为直接的 `ImportError`，而是表现为 matplotlib 内部的类型判断错误——在字体大小参数验证时，`isinstance(fs, (int, float))` 可能因 numpy 2.x 数据模型变化而返回 `False`，导致 matplotlib fallback 到字符串字号解析路径。

**验证方法**：
```bash
python3 -c "import numpy; print(numpy.__version__)"
# 如果输出 2.x.x
pip install --break-system-packages 'numpy<2'
```

**修复**：降级到 numpy 1.x：
```bash
pip install --break-system-packages 'numpy<2'
```
降级后所有图恢复正常。

**为什么只有部分图报错**：matplotlib 在 numpy 2.x 下的崩溃是路径依赖的。某些图在 `import matplotlib` → 加载 `.so` 扩展时直接崩溃（ImportError）；另一些图走不同代码路径后，在 `fontsize` 参数校验处才暴露问题。

### 原因 B：JSON 标签迭代 bug（2026-06-07 早期版本）

**症状**：
```
Size is invalid. Valid font size are xx-small, x-small...
```

**根因**：`_classification.py::plot_winchester_floyd()` 中迭代 `_WF_LABELS` 时写为：
```python
for rx, ry, text, fs in _WF_LABELS:  # ❌ 隐式解包 dict
```
而 `_WF_LABELS` 是 `[dict, dict, ...]` 列表。`for rx, ry, text, fs in [dict]` 尝试将 dict 解包为 4 元素元组失败。

**修复**：已改为显式 key 访问：
```python
for label in _WF_LABELS:
    rx, ry, text, fs = label['x'], label['y'], label['text'], label['fontsize']
```

### 排查顺序

1. 先检查 numpy 版本。如果 >= 2.x，降级到 <2。
2. 如果 numpy <2 仍报错，检查 JSON 中 labels 的 fontsize 字段是否纯数字。
3. 检查迭代方式是否是显式 key 访问。
