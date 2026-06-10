# O'Connor Volcanic An-Ab-Or 分类三角图 (CLS-12) 校正记录

## 图件信息
- 图号: CLS-12
- 登记名: plot_oconnor_volc
- 出处: O'Connor (1965) 火山岩 An-Ab-Or 分类
- SVG 来源: RockPlot 三角图
- 校正日期: 2026-06-10
- 参考审查: AI 审查报告（将 mineralogical 长石分类误判为 O'Connor 标准矿物分类，采纳排版建议忽略类型误判）

## 坐标数据
7 条 O'Connor 分界线定义在 `_ocomorv_all` (ocomorv_0~ocomorv_6)：
- 每条线由 2 个端点定义
- 数据空间: (An%, Ab%, Or%) 三元比

## 区域填充
8 个颜色区域对应的原始成分点（用于 `ternary_to_xy` 标注定位）：
- Anorthite (An>50%): (75, 15, 10)
- Gabbro/Diorite: (50, 35, 15)
- Quartz Diorite: (38, 42, 20)
- Granodiorite: (22, 48, 30)
- Quartz Monzonite: (12, 48, 40)
- Granite (Trondhjemite): (5, 45, 50)
- Granite (Adamelite): (5, 10, 85)
- Syenogranite (Alkali Granite): (3, 3, 94)

## 视觉规范
- 分界线 lw=1.0（从 1.2 下调）
- 颜色区域 alpha=0.22-0.25
- 标注 fontsize=7.5, 粗体, #444444
- 顶点名: An(Anorthite) / Ab(Albite) / Or(Orthoclase)

## 注意事项
- 审查报告误判为矿物学长石分类图。实际上 An/Ab/Or 来自 CaO/Na₂O/K₂O 的标准矿物计算，不是 plagioclase 系列。采纳了排版改进（外框变细、顶点加全名），忽略了类型误判。
- 坐标当前仍硬编码在 `_classification.py` 中，未来应随坐标外置工作一起抽离。
