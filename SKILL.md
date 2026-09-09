---
name: ppt-studio
description: "创建、重构或转换演示文稿，将报告、演讲稿、PDF、Word、Markdown、网页或文本制作成可编辑 PPTX，并创建、分析和沉淀可复用演示模板。用户提到 PPT Studio，要求资料转 PPT、系统性重做演示稿、按参考模板制作整套 PPT，或继续维护已有 PPT Studio 项目时使用。单纯咨询演讲建议或与该项目无关的局部文件编辑不触发完整生产流程。"
---

# PPT Studio

Create editable PPTX through source processing, outline approval, detailed content, SVG authoring, unified QA, and export.

## Scope and loading

Use the full production pipeline for new or substantially restructured decks. For questions, inspection, skill maintenance, or edits to an existing project, load only the relevant reference and perform the requested work. Do not start production or request Nine Confirmations merely because this skill was named.

All paths below are relative to `${SKILL_DIR}`, the directory containing this file. Resolve the actual Python interpreter and absolute project path using [runtime-bootstrap.md](references/runtime-bootstrap.md) before running pipeline scripts.

## Essential execution contract

1. Follow phase prerequisites in order. Continue non-blocking work without asking the user to say “continue”.
2. New/restructured decks have two user gates: bundled Nine Confirmations, then direct Ghost Deck outline approval. Before outline approval, create structure only; record approval in `outline_approval.md` before detailed content.
3. Main agent owns final SVG page generation and export. Generate pages sequentially; before each page re-read `spec_lock.md`, including the page rhythm. Use only the confirmed design values and assets.
4. Complete content, design, images, SVGs, and notes before unified QA. Run the automated checks and one read-only independent content/visual audit before export. See the QA reference for required checks and unavailable-auditor handling.
5. User-edited PPTX is authoritative after export. Inspect that version before subsequent edits; rebuilding from older SVG sources requires an explicit user request.
6. Write generated text as UTF-8 without BOM. Prefer direct file editing; programmatic writes must specify UTF-8. Avoid CJK transport through an unverified shell encoding. See [shared-standards.md §0](references/shared-standards.md) for the full contract.
7. Encoding gate: Step 6 checks the whole project before semantic/visual QA. Step 7 finalization automatically checks rewritten `svg_final/` and fails on encoding errors. Export requires successful finalization. Do not add a second manual project-wide encoding scan after finalization.
8. Preserve output language and user choices. Chinese input defaults to Chinese deck copy; JSON keys and fixed specification headings may remain English.
9. Match audience, occasion, and narrative goal to the content framework. Finished slides must make sense without speaker notes. Speech/report conversions preserve important source facts, an agenda, persistent section labels, and meaningful visuals.
10. Use the existing project structure; generic coding skills must not impose worktrees, branches, or test scaffolds on deck production.

## Phase routing

Read the selected reference completely on entering its phase. Load its dependent references only when the stated condition applies; do not preload all references or templates.

| When | Load | Required outcome / next gate |
|---|---|---|
| Before pipeline scripts | [Runtime bootstrap](references/runtime-bootstrap.md) | Resolve runtime and check phase-specific dependencies |
| Steps 1–3: source import, project setup, template choice | [Source and templates](references/pipeline-source-templates.md) | Prepared sources/project; conditional template discovery |
| Step 4: audience, outline, detailed content and design | [Strategy](references/pipeline-strategy.md) | Nine Confirmations → Ghost Deck approval → content/design/spec lock |
| Step 5: confirmed image strategy includes generated assets | [Images](references/pipeline-images.md) | Generate via selected route or record unavailable assets |
| Step 6: sequential SVG authoring, notes and unified QA | [Execution and QA](references/pipeline-execution-qa.md) | Encoding/content/SVG checks, applicable aesthetics, independent audit |
| Step 7: approved deck ready to finalize/export | [Export](references/pipeline-export.md) | Split notes → finalize with encoding guard → export → archive |
| Independent helper work or final audit | [Agent boundaries](references/agent-decomposition.md) | Delegate only permitted independent work |
| Need a script/template index | [Resource routing](references/resource-routing.md) | Locate only relevant resources |
| Creating a reusable template package | [Create template](workflows/create-template.md) | Follow standalone template workflow |

## Conditional content and design references

- New/restructured presentation: [content-quality-framework.md](references/content-quality-framework.md); speech/report conversion uses §7.2.
- Before Chinese body copy or copy review: [humanized-copy-review.md](references/humanized-copy-review.md).
- SVG authoring and compatibility issues: [shared-standards.md](references/shared-standards.md).
- User supplies a template or asks to persist one: [template-library-persistence.md](references/template-library-persistence.md).
- Frontend Slides / HTML design direction: [frontend-slides-design-pack.md](references/frontend-slides-design-pack.md); credit its design inspiration.
- Explaining this system or comparing with PPT Master: [ppt-master-foundation.md](references/ppt-master-foundation.md); distinguish inherited SVG/DrawingML foundation from additions.
- Generation/export troubleshooting: [troubleshooting.md](scripts/docs/troubleshooting.md).

Archive rules and exact commands live in the export reference. Role-specific instructions, schemas, tool implementations and template catalogs are loaded on demand rather than included here.
