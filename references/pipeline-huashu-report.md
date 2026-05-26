# HTML 报告美化流水线：igneous-geochemistry → huashu-md-html

> 如何把 `plot_recommended()` 生成的原始 HTML 报告升级为 huashu-md-html 风格的出版物级报告。

## 问题

`_style.py` 中的 `generate_report_html()` 生成的 HTML 报告功能完整（lightbox 放大、2 列网格、跳过列表、摘要统计），但风格朴素（Times New Roman + 白底灰边），不属于 huashu-md-html 的「反 AI slop 审美」体系。

## 推荐方案：Markdown 报告 + huashu md_to_html.py

这是经过 2026-05-11 25SMH14/17 项目验证的完整流水线。当所有 PNG 图件已生成后：

### Step 1：手动编写 Markdown 报告

在输出目录中创建 `report.md`，每张图用 `![描述](文件名.png)` 引用。Pandoc 的 `--copy-images` 或 `--inline-images` 会自动处理图片路径。建议按功能分类：分类图 → 演化图 → 微量元素图 → 源区图 → 构造图，最后加文件清单表格。

### Step 2：运行 md_to_html.py

```bash
SKILL_HUSHU=/home/twoper/.hermes/skills/productivity/huashu-md-html

# 选项 A：copy-images 模式（图片文件与 HTML 并列，轻量推荐）
cd 输出目录/
python3 $SKILL_HUSHU/scripts/md_to_html.py report.md --theme report --copy-images -o report.html

# 选项 B：inline-images 模式（所有图片 base64 嵌入为单文件）
# 注意：md_to_html.py 的 --inline-images 在 Pandoc 通过 stdin (-) 接收 Markdown 时
# 无法正确解析相对图片路径（因为 py 脚本无法确定 Markdown 的源目录）。
# 解决方案：先生成 HTML，再用 Python 手动 base64 嵌入图片：
python3 $SKILL_HUSHU/scripts/md_to_html.py report.md --theme report -o report_raw.html
python3 -c "
import base64, mimetypes, re
from pathlib import Path
html = Path('report_raw.html').read_text()
# 替换外链 CSS 为内嵌
css_path = Path('$SKILL_HUSHU/templates/report/theme.css')
css = css_path.read_text()
html = html.replace('<link rel=\"stylesheet\" .../>', f'<style>\n{css}\n</style>')
# base64 嵌入所有本地图片
def inline(m):
    src = m.group(2)
    if src.startswith(('http://','https://','data:')):
        return m.group(0)
    fp = (Path.cwd() / src).resolve()
    if not fp.exists():
        return m.group(0)
    b64 = base64.b64encode(fp.read_bytes()).decode('ascii')
    return f'{m.group(1)}\"data:image/png;base64,{b64}\"'
html = re.sub(r'(<img[^>]+src=)\"([^\"]+)\"', inline, html)
Path('report_standalone.html').write_text(html)
"
```

### Step 3：打开验证

- `report.html`（copy-images 模式）：双击在浏览器打开，需与图片在同一目录
- `report_standalone.html`（base64 嵌入模式）：单文件，无需任何目录依赖，可直接分享或发给合作者

## 路径 B：Pandoc 不可用时（WSL 回退）

直接手写 HTML，但遵循 huashu-md-html 审美底线（见下表）。推荐模板参考：`页首-摘要-分类区块-源区区块-演化区块-构造区块-页脚`。

## 路径 C：优先用 `generate_report_html()` 的内置风格

在 skill 的 `_style.py::generate_report_html()` 中增加 huashu 风格预设作为选项，或直接修改默认 CSS 风格。

## huashu-md-html 审美底线（反 AI slop 规则）

| 类别 | 必须 | 禁止 |
|------|------|------|
| 配色 | 克制色（赤陶橙 #CD5C5C / Tufte 象牙白 #FFFFF8 / 墨水蓝 #2B3A67 / 安静灰 #6B7280） | 紫渐变、赛博霓虹、深蓝底 #0D1117、彩虹色 |
| 字体 | 中衬线(思源宋/PingFang SC) + 英 serif/Inter；代码 JetBrains Mono | Comic Sans、Roboto/Arial display 大字重 |
| 容器 | 诚实分隔（细线、留白、字体级差） | 圆角卡片+左 border accent、阴影堆叠 |
| 节奏 | 行高1.75-1.85(中)、最大宽760-820px | 顶到边密集排版、<1.4行高、>900px宽体 |

## 实施记录

- 2026-05-11: 首次实践。25SMH14/17 共出 24 张图，原始报告只含推荐入口的 8 张。补跑了全部镁铁质图件（TAS/AFM/Meschede/Wood/Pearce-Cann/四联/Shervais/Saccani 等）和源区图件（Pearce 2008/Stern/Pearce 1983/Sc-V/BaTh-LaSm 等）。发现 md_to_html.py --inline-images 在 stdin 模式下无法解析图片路径，改用两步法：Pandoc 出 HTML → Python 手动 CSS inline + base64 图片。最终文件 18MB，24 图全部内嵌，双击即可打开。
