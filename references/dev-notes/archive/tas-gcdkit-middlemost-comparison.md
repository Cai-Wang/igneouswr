# TAS 火山岩图坐标来源对比

## 现状

IgneousWR CLS-01 (`TAS.png`) 的坐标存储在 `boundaries/cls/tas.json`，来源标注为"pyrolite TAS classifier"。

## GCDkit 两个版本的差异

### TAS.r（Le Bas et al. 1986）

- xlim=35~80, ylim=0~16
- 15 个分类区：Foidite, Picrobasalt, Basalt, Basaltic Andesite, Andesite, Dacite, Rhyolite, Trachybasalt, Basaltic Trachyandesite, Trachyandesite, Trachyte/Trachydacite, Tephrite/Basanite, Phonotephrite, Tephriphonolite, Phonolite
- 有 Irvine-Baragar 碱性/亚碱性分界线：11 节点曲线 (39.2,0)→(77.4,10)
- 有 x=45,52,63 三条竖虚线（Ultrabasic/Basic/Intermediate/Acid 分界）
- Rhyolite: (77,0)→(100,0)→(100,25)→(69,25)→(69,8)
- Foidite 底部到 SiO₂=30

### TASMiddlemostVolc.r（Middlemost 1994 改编）

- xlim=34~90, ylim=0~19
- 18 个分类区（多了 Sodalitite/Nephelinolith/Leucitolith、Trachydacite、Silexite）
- 无碱性/亚碱性分界线（注释掉了）
- 无竖虚线（注释掉了）
- Rhyolite: (77.3,0)→(87.5,4.7)→(85.9,6.8)→(71.8,13.5)→(69,8)
- Foidite 底部到 SiO₂=37
- Trachyte/Trachydacite 分开

## IgneousWR TAS.json 与两者的对比

| 特征 | IgneousWR | GCDkit TAS.r | GCDkit TASMMVolc |
|------|-----------|-------------|-----------------|
| 分类区数 | 17 | 15 | 18 |
| Rhyolite 坐标 | 同 MM94 | 不同 | 一致 |
| Foidite 底部 | SiO₂=35 | SiO₂=30 | SiO₂=37 |
| Silexite | 无 | 无 | 有 |
| Sodalitite | 无 | 无 | 有 |
| Trachyte 拆分 | T1/T2 | 合并 | Trachyte+Trachydacite |
| 碱/亚碱线 | 直线 (45,2)-(52,5) | 11节点曲线 | 无 |
| 竖虚线 | 无 | 有 | 无 |

## 多边形边界独立绘制

GCDkit 方式每条 `lines` 独立绘制一个闭合多边形，相邻区域共享的**边被重复画两次**，视觉无影响。
IgneousWR 方式每个多边形独立闭合（poly[i]→poly[(i+1)%n]），同样有重叠——两者本质一致。

如需对齐到 GCDkit TASMiddlemostVolc.r，需要：
1. 替换 `tas.json` 中 Rhyolite 以外的多边形坐标为 Middlemost 1994 坐标
2. 删除碱/亚碱分界线（或保留但标注来源）
3. 可选：添加 Silexite 和 Sodalitite 两区
4. xlim 从 35~90 改为 34~90，ylim 从 0~18 改为 0~19
