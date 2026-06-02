# 兄弟工程：IgneousWR-GCD 协作说明

## 关系

| 工程 | 目录 | 数据来源 |
|------|------|---------|
| IgneousWR | `~/.hermes/skills/data-science/IgneousWR/` | 手动校准 + 文献坐标 |
| igneouswr-gcd | `~/.hermes/skills/data-science/igneouswr-gcd/` | GCDkit 6.3.0 R 源码翻译 |

两者**架构相同**（data/chem/normalize/ternary/style/diagrams/registry → 纯 matplotlib），但图件数据**来源不同、不混用**。

## 为什么做两个版本

1. **互相验证**：同一张图（如 TAS、AFM、Shand）在两个版本中画出来，可交叉确认边界坐标是否准确
2. **补足缺失**：IgneousWR 有些图缺少 GCDkit 中的版本（如 Cox 1979 TAS, Middlemost 1985 K₂O-SiO₂, Middlemost 1994 侵入岩/火山岩 TAS），GCD 版天然包含
3. **质量参考**：当 IgneousWR 的某张图被用户质疑时，可用 GCD 版作为"基线"对照

## 开发约束

- **绝不复制代码**：两工程间通过 registry、样式系统等设计模式共享"怎么写图"，但具体坐标/分界线/分类名数据不许跨工程复制
- **坐标系注意**：GCDkit 的 AFM 三元图顶点顺序为 A(左底)/M(右底)/F(顶)，与 IgneousWR 的 F(顶)/A(左底)/M(右底) 不同。两个工程各自独立维护，不要求对齐
- **公式差异**：Debon 的 B 值、WinFloyd 的 Zr/TiO₂ 系数、La Roche R1/R2 系数等计算式在两工程间可能存在差异——这是正常的设计分歧，不做统一

## 使用场景

| 场景 | 推荐工程 |
|------|---------|
| 用户已校正好坐标的经典图件 | IgneousWR |
| 需要 GCDkit 原生版本（如 Cox 1979 TAS） | igneouswr-gcd |
| 某图在 IgneousWR 中出错，排查是否坐标问题 | 对比两版出图 |
| 开发新图件时找参考坐标 | igneouswr-gcd（从 R 源码提取更精确） |
