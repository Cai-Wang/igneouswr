# 全岩地球化学 Skill — 架构审阅与重构方向

*来源：2026-05-27 用户审阅。用户指出本 skill 已从"一个绘图脚本"发展为"小型数据工程 + 绘图引擎"。*

## 观点提炼

> 基础不错（GeochemData、集中 DIAGRAM_REGISTRY、分模块绘图、quick_validate.py），但图件到 70 张后，稳定性风险来自"数据入口不一致、图件依赖漏登记、输出污染、全局状态、验证不够深"。

## 建议架构

```
igneous-geochemistry/
  SKILL.md
  references/
  scripts/
    igneous_geochem/
      io/                      # Excel 读取、合并、样品编号、单位、schema 校验
      core/                    # GeochemData、标准化、化学计算、岩性判断
      diagrams/
        registry.py 或 specs.yaml
        classification/
        source/
        evolution/
        tectonic/
        boundaries/            # SVG/RockPlot 边��数据 JSON，不硬编码进函数
      report/                  # HTML 报告
      batch/                   # 多图幅批处理
      cli.py                   # 命令入口
    quick_validate.py
    pyproject.toml 或 requirements.txt
```

**关键原则：图幅数据不进 skill 本体。** Skill 是"工具和规则"，图幅数据归项目工作区：

```
project/
  manifest.yaml                # 每个图幅的输入文件、sheet、样品前缀、岩性策略
  data/raw/<sheet_id>/
  data/interim/<sheet_id>/merged.xlsx
  data/curated/geochem.parquet 或标准 xlsx
  runs/<run_id>/<sheet_id>/figures/
  runs/<run_id>/<sheet_id>/report.html
  runs/<run_id>/qc.json
```

## 已识别的 5 个具体风险（按优先级）

### P0 — registry 依赖漏项（已完成）
- `plot_gdyb_dydystar` 实际用 Gd，registry 没声明 ✅ 已修
- `plot_harker` 实际用 FeO/TFe2O3，registry 没声明 ✅ 已修
- `plot_jensen` 实际用 TiO2，registry 没声明 ✅ 已修
- `plot_ohta_arai` 实际用 Sm，registry 没声明 ✅ 已修
- `plot_pearce1982` 实际需要 Ti/Nb/Sr，registry 只写 Zr/Y ✅ 已修
- `plot_zr_covariance` 实际需要 10 元素，registry 只写 Zr ✅ 已修

### P0 — 静态验证（已完成）
`quick_validate.py` 新增 `test_element_dependency_integrity()`：
- 扫描所有绘图模块中 `gd.get()` 和 `check_elements()` 的实际调用
- 与 `DIAGRAM_REGISTRY` 的 `needed` + `any_of` 交叉验证
- 依赖不匹配直接标记失败
- 在 `--quick` 和完整模式均执行

### P1 — 依赖清单（已完成）
- `requirements.txt` 锁定 numpy>=1.24, matplotlib>=3.6, scipy>=1.10, openpyxl>=3.1
- `main()` 启动时 preflight 检查：Python >= 3.10 + 所有依赖版本
- SKILL.md 安装说明已移除 pyrolite，明确标注"不含 pyrolite"

### P2 — 输出目录项目化（已完成）
- `DEFAULT_OUT_DIR` 从 `whole_rock_output` 改为 `../runs/default`
- 清理 `geochem_output/` 和 `whole_rock_output/` 残留目录
- `.gitignore` 补 `runs/`、`*_output/`、`geochem_output/`

### P3 — whole_rock_core.py 拆包（待办）
目前 `whole_rock_core.py` 同时承担：Excel 读取、数据模型、导入所有图、注册表、推荐调度、报告调用。

### P4 — 边界数据独立化（待办）
RockPlot/SVG 提取的边界坐标应放 JSON/YAML，带 `source`、`axis_mapping`、`transform`、`checksum`。

### P5 — 图幅管线（待办）
多图幅场景用 `manifest.yaml + batch runner + qc.json`，每个图幅独立运行、独立日志、独立报告。

## 中期结构演进路径

```
# 短期（已做）
修 registry 依赖漏项
加 test_element_dependency_integrity()
补 requirements.txt + preflight
输出路径从 skill 目录移出

# 中期（待做）
scripts/ → scripts/igneous_geochem/
拆分 io/ core/ diagrams/registry report/ batch/ cli.py

# 长期（待做）
manifest.yaml + batch runner + qc.json
每个图幅独立运行，失败不影响其他
```
