# PPT Studio Skill

面向 AI IDE 的演示文稿生成 skill，用于从 PDF、DOCX、URL、Markdown 或用户直接输入的内容生成原生可编辑 PPTX。

这版是在 PPT Master 的工程基础上继续优化的，不重新造轮子：保留“先生成 SVG，再导出原生可编辑 PPTX”的主流程，用 SVG 作为中间表示来降低 token 消耗、提高布局可控性，并让最终 PowerPoint 文件保留可编辑元素。

## 主要能力

- 先确认需求，再开始制作：Nine Confirmations 和 Ghost Deck 大纲必须先给用户确认。
- 内容质量有规则：按场景选择 Minto / McKinsey、Duarte / Presentation Zen、Kawasaki 10/20/30 等叙事体系。
- 视觉设计更强：借鉴 `zarazhangrui/frontend-slides` 的设计模板美学，并转成适合 PPT 的 SVG 模板资产。
- 模板可沉淀：用户上传或确认过的模板可以登记、复用、形成私有模板库。
- 生图策略可选：用户可在开始前选择 SVG、本机内置生图工具，或明确使用 ChatGPT Images 2.0、Nano Banana Pro、Seedream / Seedance 等高级网页模型。
- 不冒充模型：如果宿主环境的内置生图工具没有明确披露模型，不把它称为 Image 2.0。
- 防止重复生图：网页生图提交一次后轮询状态；超过 5 分钟仍未完成则交给人工检查，不刷新、不重复提交。
- 最终统一审计：正式导出前统一检查内容、视觉、中文表达、SVG、备注和 PPTX 导出质量。
- 尊重用户更新：如果用户手动改过 PPTX，后续修改必须基于用户最新版本，不能用旧 SVG 或旧 manifest 覆盖用户版本。

## 使用方式

在支持 skill / rules（规则）的 AI IDE 中，让 agent 先读取：

```text
SKILL.md
```

然后按流程制作 PPT。典型提示：

```text
请用 PPT Studio Skill 做一份 6 页中文 PPT。
先完成 Nine Confirmations，并在生成正式内容、设计稿、图片、SVG 或 PPTX 前，把 Ghost Deck 大纲给我确认。
```

## 目录结构

```text
SKILL.md                         核心工作流
references/                      内容、视觉、生图、审计等规则
scripts/                         SVG、PPTX、模板、质量检查等工具
templates/                       内置模板、图标、图表和客户模板索引
workflows/                       模板创建、PPT 美化、故障恢复等扩展流程
requirements.txt                 Python 依赖
.env.example                     可选生图后端配置示例
```

## 推荐执行顺序

1. 读取 `SKILL.md`。
2. 完成 Nine Confirmations。
3. 输出 Ghost Deck，让用户确认大纲。
4. 生成详细内容与视觉方案。
5. 根据用户选择执行 SVG / 高级生图 / 混合生图。
6. 运行内容、视觉、去 AI 味和导出质量检查。
7. 导出原生可编辑 PPTX。

## 依赖

```bash
pip install -r requirements.txt
```

如果要使用网页端高级生图模型，还需要对应网页登录状态和浏览器访问能力。

## License

MIT
