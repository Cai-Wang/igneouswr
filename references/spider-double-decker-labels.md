# 蛛网图双行错位标签（Double-decker）

## 使用场景

REE 和蛛网图等宽等高排版时（常见 80mm 面板），蛛网 29 个元素需要塞进同一宽度。
单行放不下（需 5pt 字太小），改双行错位（每行 ~15 个，8pt 清晰）。

## 核心代码

```python
ax.set_xticks(range(29))
ax.set_xticklabels(SPIDER_ORDER, fontsize=8)

for i, lb in enumerate(ax.get_xticklabels()):
    if i % 2 == 0:
        lb.set_y(-0.04)     # 下行
        lb.set_va('top')
    else:
        lb.set_y(0.04)      # 上行
        lb.set_va('bottom')
```

面板高度 55-60mm。

## 字号参考

| 面板宽度 | 建议字号 |
|---------|---------|
| 80mm | 8pt |
| 85mm（单栏） | 8-9pt |
| 175mm（双栏） | 9-10pt |

## 完整流程

1. `GeochemData(path)` 读数据
2. 用 `matplotlib-scientific-layout` 的 `A4Grid(1, 2, ..., wspace=5)` 建布局
3. 画图：REE 14 元素 8-10pt，蛛网 29 元素 8pt 双行错位
4. `auto_gap('L', 'R')` 实测 ylabel 宽度自动重排
5. `layout.save('output.png')`
