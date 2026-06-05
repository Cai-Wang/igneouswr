# references/

本目录包含 IgneousWR 图件的设计文档、边界坐标依据和参考来源。

## 内容分类

- `*-spec.md` / `*-boundary.md` — 每张图校正时的坐标依据和设计规范
- `*-data.md` — 边界坐标和分界线数据的独立文档
- `gcd-*.md` — 从 GCDkit 提取的参考文献和坐标信息
- `pearce*-spec.md` — Pearce 系列图的坐标规范和修改说明
- `style-guide.md` — 统一的绘图风格指南
- `data-preparation.md` / `ratio-computation.md` — 数据处理流程
- `geochem-table-formatting.md` — 数据表格排版规范

## 目录结构

```
references/
  README.md                     # 本文件
  *.md                           # 边界 spec、学术参考、固定工作流
  dev-notes/                     # 调试记录、开发笔记（不随开源发布）
```

> `dev-notes/` 包含内部开发过程中的调试记录和重构历史，已通过 `.gitignore`
> 排除在开源发布之外。有兴趣的贡献者可查阅 git log 了解完整历史。
