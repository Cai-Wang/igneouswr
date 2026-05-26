# 手动合并主量与微量元素 Excel 数据

当数据来自实验室检测报告（主量元素和微量元素分属不同 Excel 文件的不同工作表）时，`merge_excel.py` 可能不适用。这里记录通用的手动合并方法，支持任意工作表名和混合格式。

## 典型场景

- 文件 A（主量）：`TKHS11b-260120-031 陈宇阳+FeO.xlsx`，数据在"数据页"表
  - 第1行：列名（实验室编号, 样品编号, SiO2, Al2O3, ...FeO）
  - 第2行：单位行（`%`、`wt%`占位）
  - 第3-18行：实际数据
  - 第1列（"实验室编号"）为空，需跳过
- 文件 B（微量）：`TKHS2-260120-031 陈宇阳.xlsx`，数据在"数据页"表
  - 第1行：列名（样品编号, Li, Be, Sc, ...U）
  - 第2-26行：实际数据
  - 末尾有 GSR 标准物质行和"以下空白"行，需过滤

## 合并脚本模板

```python
import pandas as pd, openpyxl, os

def merge_major_trace(major_file, trace_file, out_path='merged.xlsx'):
    # 读取主量
    wb = openpyxl.load_workbook(major_file, data_only=True)
    ws = wb['数据页']
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_col=ws.max_column))]
    data = [list(row) for row in ws.iter_rows(min_row=3, values_only=True) if row[1] is not None]
    df_major = pd.DataFrame(data, columns=headers)
    df_major = df_major.drop(columns=['实验室编号'], errors='ignore')
    df_major.columns = [c.strip() if c else c for c in df_major.columns]
    df_major.rename(columns={'样品编号': 'Sample'}, inplace=True)
    
    # 读取微量
    wb2 = openpyxl.load_workbook(trace_file, data_only=True)
    ws2 = wb2['数据页']
    headers2 = [c.value for c in next(ws2.iter_rows(min_row=1, max_col=ws2.max_column))]
    data2 = []
    for row in ws2.iter_rows(min_row=2, values_only=True):
        r0 = str(row[0] or '')
        if r0 and not r0.startswith(('样品','单位','以下','GSR','推荐值','空白')):
            data2.append(list(row))
    df_trace = pd.DataFrame(data2, columns=headers2)
    df_trace.columns = [c.strip() if c else c for c in df_trace.columns]
    df_trace.rename(columns={'样品编号': 'Sample'}, inplace=True)
    
    merged = df_major.merge(df_trace, on='Sample', how='left')
    
    # 转置格式（Row1=元素横铺, Row4+=数据）
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.cell(row=1, column=1, value='Sample ID')
    for j, c in enumerate(merged.columns[1:], 2):
        ws_out.cell(row=1, column=j, value=c)
    for i, (_, r) in enumerate(merged.iterrows(), 4):
        for j, c in enumerate(merged.columns, 1):
            ws_out.cell(row=i, column=j, value=r[c])
    wb_out.save(out_path)
    print(f'合并完成: {out_path} ({len(merged)} 样品 x {len(merged.columns)-1} 元素)')
```

## 常见陷阱

| 问题 | 原因 | 解决 |
|------|------|------|
| Ti 列冲突或缺失 | 主量有 TiO2(wt%)，微量有 Ti(ppm) 但列名不匹配 | 手动指定列顺序或用列号硬编码 |
| 样品数不一致 | 微量文件末尾有标准物质（GSR-x） | 过滤 `'GSR'`、`'推荐值'`、`'以下空白'` |
| 数据全为 NaN | 样品编号含有不可见空格 | 对 Sample 列做 `.str.strip()` |
| GeochemData 读为 0 样品 | 保存了4行表头格式但skill预期转置格式 | 用转置格式保存（Row1=元素名，Row4+=数据） |
