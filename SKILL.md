---
name: presentation-studio
description: >
  Content-first presentation creation system with reusable customer templates,
  authority-based narrative frameworks, multi-format SVG design, image-model routing,
  quality audits, and editable PPTX export. Use when the user asks to create, improve,
  structure, template, or export a PPT or presentation.
---

# Presentation Studio Skill

> AI-driven multi-format SVG content generation system. Converts source documents into high-quality SVG pages through multi-role collaboration and exports to PPTX.

**Core Pipeline**: `Source → Project → Template Choice/Persistence → Nine Confirmations → Draft Ghost Deck → User Outline Approval → Detailed Content → Design Spec → [Image_Generator] → SVG + Notes → Unified Content/Visual Check + Independent Audit → Export`

**Universal content rule**: Every invocation that creates or restructures a presentation MUST classify the user's scenario from audience, occasion, and narrative goal, then generate and validate content with the matching rules in `references/content-quality-framework.md`. This requirement applies to all future presentation projects, not only examples or demonstration decks.

**Silent-reading rule**: A finished deck must be understandable without listening to the speaker notes. Use notes as a source for sharper page copy, but visible slide text must communicate the page's user-facing value. For Chinese decks, final copy must be reviewed with `references/humanized-copy-review.md` and revised into natural, specific Chinese.

**Speech/report conversion rule**: When converting a speech draft, meeting briefing, work report, or other long structured prose, follow `references/content-quality-framework.md` §7.2: include a TOC / agenda page, keep persistent section labels on content pages, preserve important paragraph facts in visible body copy, and add one meaningful chart/diagram/structured visual per substantive page.

**Foundation and attribution rule**: Presentation Studio inherits PPT Master's SVG authoring and SVG-to-DrawingML export foundation. When explaining this system or comparing it with PPT Master, read `references/ppt-master-foundation.md` and state the verified advantages without overclaiming token savings. When using Frontend Slides-inspired aesthetics, read `references/frontend-slides-design-pack.md`, credit Zara Zhang's `zarazhangrui/frontend-slides` for design inspiration, and distinguish Presentation Studio's added private template persistence mechanism.

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one of them constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST be executed in order; the output of each step is the input for the next. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for the user to say "continue"
> 2. **BLOCKING = HARD STOP** — Steps marked ⛔ BLOCKING require a full stop; the AI MUST wait for an explicit user response before proceeding and MUST NOT make any decisions on behalf of the user
> 3. **NO CROSS-PHASE BUNDLING** — Cross-phase bundling is FORBIDDEN. (Note: the Nine Confirmations and User Outline Approval in Step 4 are ⛔ BLOCKING — the AI MUST present recommendations or the proposed outline and wait for explicit user confirmation before proceeding.)
> 4. **GATE BEFORE ENTRY** — Each Step has prerequisites (🚧 GATE) listed at the top; these MUST be verified before starting that Step
> 5. **NO SPECULATIVE EXECUTION** — "Pre-preparing" content for subsequent Steps is FORBIDDEN (e.g., writing SVG code during the Strategist phase)
> 6. **NO SUB-AGENT SVG GENERATION** — Executor Step 6 SVG generation is context-dependent and MUST be completed by the current main agent end-to-end. Delegating page SVG generation to sub-agents is FORBIDDEN
> 7. **ONE UNIFIED INDEPENDENT AUDIT REQUIRED** — Do not dispatch outline or mid-production content audits. After detailed content, design, image generation, SVG pages, and speaker notes are complete, run one unified final gate. Dispatch a read-only sub-agent to audit both content and visual quality before export. The sub-agent returns findings only and never generates or patches slides.
> 8. **SEQUENTIAL PAGE GENERATION ONLY** — In Executor Step 6, after the global design context is confirmed, SVG pages MUST be generated sequentially page by page in one continuous pass. Grouped page batches (for example, 5 pages at a time) are FORBIDDEN
> 9. **SPEC_LOCK RE-READ PER PAGE** — Before generating each SVG page, Executor MUST `read_file <project_path>/spec_lock.md`. All colors / fonts / icons / images MUST come from this file — no values from memory or invented on the fly. Executor MUST also look up the current page's `page_rhythm` tag and apply the matching layout discipline (`anchor` / `dense` / `breathing` — see executor-base.md §2.1). This rule exists to resist context-compression drift on long decks and to break the uniform "every page is a card grid" default
> 10. **OUTLINE BEFORE DETAILED CONTENT** — Before user approval, create only `ghost_deck.md` and `outline_manifest.json`. Do not draft slide body copy, detailed claims, evidence, source footers, image prompts, or visual specifications.
> 11. **DIRECT USER OUTLINE APPROVAL** — Present the draft Ghost Deck directly to the user after generation. Do not run an automated outline checker or independent outline audit unless the user explicitly requests one. Record approval in `<project_path>/outline_approval.md`. Without this file, do not generate `content_manifest.json`.
> 12. **COMPLETE PRODUCTION BEFORE UNIFIED QA** — After outline approval, generate detailed content, visual specification, images, SVG pages, and speaker notes. Then run the unified automated checks and one independent content-plus-visual audit. Export only after all blocking findings are fixed.
> 13. **USER-EDITED ARTIFACT IS THE CURRENT SOURCE OF TRUTH** — If the user has manually edited, uploaded, or otherwise updated a PPTX after the skill's last export, that latest user-edited PPTX becomes the authoritative working version. Do not regenerate from stale `svg_output/`, `svg_final/`, `content_manifest.json`, or earlier exports unless the user explicitly asks to rebuild from source. Before making further slide edits, inspect or ingest the latest user-edited PPTX and apply changes on top of it, or ask the user to provide it if it is not available.

## Agent Decomposition Policy

The pipeline gates remain serial, but independent helper work MAY be delegated to sub-agents when it improves elapsed time without weakening narrative consistency.

| Phase | Sub-agent use | Boundary |
|---|---|---|
| Source research / source extraction | Allowed when sources are independent | Return extracted facts, citations, and risks only; main agent decides deck structure |
| Template discovery / customer template analysis | Allowed | Return candidate templates, tokens, constraints, and validation notes only |
| Image model route research or long-running web status observation | Allowed when the model route is already user-confirmed | Submit at most once per asset; poll and report status; never refresh, resubmit, switch model, or edit prompts without main-agent/user approval |
| Hybrid image production | Allowed after `image_prompts.md` exists and the user-selected model is locked | Use two independent helpers when useful: one Advanced Web Image Agent for named web-model raster assets, and one SVG Asset Draft Agent for local editable visual components |
| SVG asset drafting | Allowed for standalone components only | Return component SVG snippets, layout sketches, or symbol drafts under `<project_path>/svg_assets/drafts/`; do not create final page SVGs |
| Detailed content drafting | Usually keep with main agent | If delegated, sub-agent produces raw copy alternatives only; main agent owns final `content_manifest.json` and approved-outline alignment |
| SVG page generation | Forbidden | Main agent generates every SVG sequentially and re-reads `spec_lock.md` before each page |
| Speaker notes | Allowed only after all SVG pages exist | Return notes draft only; main agent checks alignment with slide content |
| Final QA / audit | Required | One read-only sub-agent must audit content and visual quality together before export |
| Export | Forbidden | Main agent runs post-processing and PPTX export |

In a hybrid strategy, the Advanced Web Image Agent and SVG Asset Draft Agent may run in parallel, because their outputs are independent assets. The main agent must still integrate both outputs into the final page SVGs sequentially in Step 6.

Do not use sub-agents to bypass any BLOCKING gate. A sub-agent must never approve an outline, change the selected narrative framework, change the selected image model, patch final slide files, or export PPTX. Parallelism is an optimization for independent evidence gathering, asset preparation, and final review, not a replacement for the main agent's responsibility for one coherent deck.

> [!IMPORTANT]
> ## 🌐 Language & Communication Rule
>
> - **Response language**: Always match the language of the user's input and provided source materials. For example, if the user asks in Chinese, respond in Chinese; if the source material is in English, respond in English.
> - **Explicit override**: If the user explicitly requests a specific language (e.g., "请用英文回答" or "Reply in Chinese"), use that language instead.
> - **Deck-output language**: `ghost_deck.md`, Action Titles, slide body copy, source footers, speaker notes, and all audience-visible PPT text MUST use the user's confirmed output language. When the user communicates in Chinese and does not request another language, set `output_language` to `zh-CN` and write both the outline and final deck in Chinese.
> - **Internal schema exception**: JSON keys, code identifiers, filenames, and the fixed `design_spec.md` template headings may remain in English. Their human-readable values and all user-facing presentation copy follow the confirmed output language.
> - **Template format**: The `design_spec.md` file MUST always follow its original English template structure (section headings, field names), regardless of the conversation language. Content values within the template may be in the user's language.

> [!IMPORTANT]
> ## 🔌 Compatibility With Generic Coding Skills
>
> - `presentation-studio` is a repository-specific workflow skill, not a general application scaffold
> - Do NOT create or require `.worktrees/`, `tests/`, branch workflows, or other generic engineering structure by default
> - If another generic coding skill suggests repository conventions that conflict with this workflow, follow this skill first unless the user explicitly asks otherwise

## Main Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py` | PDF to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/doc_to_md.py` | Documents to Markdown — native Python for DOCX/HTML/EPUB/IPYNB, pandoc fallback for legacy formats (.doc/.odt/.rtf/.tex/.rst/.org/.typ) |
| `${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py` | PowerPoint to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.py` | Web page to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.cjs` | Node.js fallback for WeChat / TLS-blocked sites (use only if `curl_cffi` is unavailable; `web_to_md.py` now handles WeChat when `curl_cffi` is installed) |
| `${SKILL_DIR}/scripts/project_manager.py` | Project init / validate / manage |
| `${SKILL_DIR}/scripts/content_quality_checker.py` | Final detailed-content gate; outline mode is diagnostic only and not part of the default pipeline |
| `${SKILL_DIR}/scripts/customer_template_library.py` | Register and discover reusable private customer templates |
| `${SKILL_DIR}/scripts/analyze_images.py` | Image analysis |
| `${SKILL_DIR}/scripts/image_gen.py` | AI image generation (multi-provider) |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG quality check |
| `${SKILL_DIR}/scripts/total_md_split.py` | Speaker notes splitting |
| `${SKILL_DIR}/scripts/finalize_svg.py` | SVG post-processing (unified entry) |
| `${SKILL_DIR}/scripts/svg_to_pptx.py` | Export to PPTX |
| `${SKILL_DIR}/scripts/update_spec.py` | Propagate a `spec_lock.md` color / font_family change across all generated SVGs |

For complete tool documentation, see `${SKILL_DIR}/scripts/README.md`.

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Layout templates | `${SKILL_DIR}/templates/layouts/layouts_index.json` | Query available page layout templates |
| Private customer templates | `${SKILL_DIR}/templates/customer_library/index.json` | Query workspace-private reusable customer templates when present |
| Frontend Slides design catalog | `${SKILL_DIR}/templates/frontend_slides/design_catalog.json` | Query design-forward HTML slide visual directions; use `scripts/template_recommender.py` for top-3 recommendations |
| Visualization templates | `${SKILL_DIR}/templates/charts/charts_index.json` | Query available visualization SVG templates (charts, infographics, diagrams, frameworks) |
| Icon library | `${SKILL_DIR}/templates/icons/` | See `${SKILL_DIR}/templates/icons/README.md`; search icons on demand with `ls templates/icons/<library>/ \| grep <keyword>` |

## Standalone Workflows

| Workflow | Path | Purpose |
|----------|------|---------|
| `create-template` | `workflows/create-template.md` | Standalone template creation workflow |

---

## Workflow

### Step 1: Source Content Processing

🚧 **GATE**: User has provided source material (PDF / DOCX / EPUB / URL / Markdown file / text description / conversation content — any form is acceptable).

When the user provides non-Markdown content, convert immediately:

| User Provides | Command |
|---------------|---------|
| PDF file | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office document | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| PPTX / PowerPoint deck | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / other | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| Web link | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| WeChat / high-security site | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` (requires `curl_cffi`; falls back to `node web_to_md.cjs <URL>` only if that package is unavailable) |
| Markdown | Read directly |

**✅ Checkpoint — Confirm source content is ready, proceed to Step 2.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready (Markdown file, user-provided text, or requirements described in conversation are all valid).

```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format <format>
```

Format options: `ppt169` (default), `ppt43`, `xhs`, `story`, etc. For the full format list, see `references/canvas-formats.md`.

Import source content (choose based on the situation):

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| User provided text directly in conversation | No import needed — content is already in conversation context; subsequent steps can reference it directly |

> ⚠️ **MUST use `--move`**: All source files (original PDF / MD / images) MUST be **moved** (not copied) into `sources/` for archiving.
> - Markdown files generated in Step 1, original PDFs, original MDs — **all** must be moved into the project via `import-sources --move`
> - Intermediate artifacts (e.g., `_files/` directories) are handled automatically by `import-sources`
> - After execution, source files no longer exist at their original location

**✅ Checkpoint — Confirm project structure created successfully, `sources/` contains all source files, converted materials are ready. Proceed to Step 3.**

---

### Step 3: Template Option

🚧 **GATE**: Step 2 complete; project directory structure is ready.

**Default path — free design with smart style recommendation.** Proceed directly to Step 4 when the user has no template preference. Do NOT block on a template question by default. Free design remains valid, but the AI should recommend a suitable visual direction when the content strongly benefits from a known style. When `templates/customer_library/index.json` exists, include matching workspace-private templates in recommendation candidates.

**Template flow is opt-in.** Enter it only when one of these explicit triggers appears in the user's prior messages:

1. User names a specific template (e.g., "用 mckinsey 模板" / "use the academic_defense template")
2. User names a style / brand reference that maps to a template (e.g., "McKinsey 那种" / "Google style" / "学术答辩样式")
3. User explicitly asks what templates exist (e.g., "有哪些模板可以用")
4. User mentions HTML slides / Frontend Slides / design template import, or provides an HTML slide design file
5. User asks for stronger aesthetics, more template options, or wants to choose a visual direction

When trigger 1-3 fires: read `${SKILL_DIR}/templates/layouts/layouts_index.json`, resolve the match (or list available options for trigger 3), and copy template files to the project directory:

```bash
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.svg <project_path>/templates/
cp ${SKILL_DIR}/templates/layouts/<template_name>/design_spec.md <project_path>/templates/
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.png <project_path>/images/ 2>/dev/null || true
cp ${SKILL_DIR}/templates/layouts/<template_name>/*.jpg <project_path>/images/ 2>/dev/null || true
```

When trigger 4-5 fires, or when the user asks to choose from templates, read `references/frontend-slides-design-pack.md`, run:

```bash
python3 ${SKILL_DIR}/scripts/template_recommender.py "<brief>" --audience "<audience>" --tone "<tone>" --density "<density>"
```

Present exactly three recommendations plus the free-design option and wait for the user's choice if the user explicitly asked to choose. If the user selects a Frontend Slides direction, copy `${SKILL_DIR}/templates/layouts/frontend_slides_bold/` into the project templates and record the selected direction name in the Nine Confirmations and `spec_lock.md`.

**User-provided template reference and persistence.** Read `references/template-library-persistence.md`. If the user provides HTML/PPTX/PDF/screenshots/brand guide as a design source, ingest it as a reference style and reconstruct a reusable PPT-safe template package. After validation, register the derived package with `scripts/customer_template_library.py`; future projects can discover it from `templates/customer_library/index.json`. Keep the original upload in the source project and keep customer packages private to the workspace by default. For HTML slides, extract design tokens and layout intent; do not copy HTML runtime, JavaScript, CSS classes, animations, or browser-only layout behavior into PPT output.

**Soft hint (non-blocking, optional).** Before Step 4, if the user's content is an obvious strong match for an existing template (e.g., clearly an academic defense, a government report, a McKinsey-style consulting deck, or a Frontend Slides direction) AND the user has given no template signal, the AI MAY emit a single-sentence notice and continue without waiting:

> Note: the library has a template `<name>` that matches this scenario closely. Say the word if you want to use it; otherwise I'll continue with free design.

This is a hint, not a question — do NOT block, do NOT require an answer. Skip the hint entirely when the match is weak or ambiguous.

> To create a new global template, read `workflows/create-template.md`

**✅ Checkpoint — Default path proceeds to Step 4 without user interaction. If a template trigger fired, template files are copied before advancing.**

---

### Step 4: Strategist Phase (MANDATORY — cannot be skipped)

🚧 **GATE**: Step 3 complete; default free-design path taken, or (if triggered) template files copied into the project.

First, read the role definition:
```
Read references/strategist.md
```

> ⚠️ **Mandatory gate in `strategist.md`**: Before writing `design_spec.md`, Strategist MUST `read_file templates/design_spec_reference.md` and produce the spec following its full I–XI section structure. See `strategist.md` Section 1 for the explicit gate rule.

**Must complete the Nine Confirmations** (full template structure in `templates/design_spec_reference.md`):

⛔ **BLOCKING**: The Nine Confirmations MUST be presented to the user as a bundled set of recommendations, and you MUST **wait for the user to confirm or modify** before producing the Ghost Deck, outline manifest, detailed content manifest, or visual specification. This is the first core confirmation point in the workflow.

1. Canvas format
2. Page count range
3. Target audience
4. Narrative framework + style objective: select Minto for decision/strategy decks, Duarte + Presentation Zen for public speaking/launches, or Kawasaki 10/20/30 for fundraising and business-development pitches. Read `references/content-quality-framework.md`.
5. Color scheme
6. Icon usage approach
7. Typography plan
8. Visual production strategy: SVG design, host-native image tool, one named advanced web model, or hybrid. Strategist MUST recommend based on target audience and narrative goal, then wait for the user's selection. Read `references/visual-generation-strategy.md` and run `scripts/image_strategy_recommender.py`. Named advanced choices include ChatGPT Images 2.0, Nano Banana Pro, Seedream 5.0 Pro, and Seedance 2.0; Seedance is a video route, not a static-image model.
9. Template / visual direction: free design, named library template, Frontend Slides direction, or user-provided reference. If Frontend Slides is selected, include the chosen direction and fallback template package `frontend_slides_bold`.

**Outline Approval and Production Handoff (MANDATORY)**:

1. Read `references/content-quality-framework.md`.
2. For Chinese decks, read `references/humanized-copy-review.md` before writing detailed slide body copy.
3. Classify the scenario from audience, occasion, narrative goal, and requested action. Choose exactly one primary framework: Minto for decision/strategy/board/business review; Duarte + Presentation Zen for speech/launch/public communication; Kawasaki 10/20/30 for fundraising/sales/business-development pitch. For mixed scenarios, record one primary framework and only compatible secondary checks.
4. Draft the structure only. Write `<project_path>/ghost_deck.md` with ordered Action Titles and one sentence per page in the confirmed output language.
5. Write `<project_path>/outline_manifest.json` from `templates/outline_manifest_reference.json`. Include scenario, framework, narrative goal, requested decision/action, output language, Action Titles, one point per page, and only high-level visual assumptions needed for outline approval. Do not include detailed body copy, claims, evidence, source footers, or image prompts.
   - For speech/report conversion decks, include the TOC/agenda page and `section_title` for each content page in the outline so the user can verify the source logic before production.
6. Present the user-facing outline directly: page count, framework, titles-test sequence, one sentence per page, and any high-impact visual/model assumptions. Do not run an outline checker or independent outline audit by default.
7. ⛔ **BLOCKING**: Wait for explicit user approval or requested changes to the outline before generating detailed slide content.
8. When approved, write `<project_path>/outline_approval.md` with approval status, timestamp, approved page list, selected framework, selected image strategy, user change requests if any, and the exact user approval message or a short paraphrase. Update `outline_manifest.json` approval status.
9. Generate detailed audience-facing content according to the selected framework. Write `<project_path>/content_manifest.json` from `templates/content_manifest_reference.json`, including final Action Titles, body copy, claims, evidence, source mapping, visible source footers, silent-reading notes, and humanized-copy review status. The page order, titles, and single points MUST match the approved outline. If content work requires a material outline change, return to the outline approval gate.
   - For speech/report conversion decks, each content page must preserve the source paragraph's important information in visible body copy and specify a meaningful visualization type.
10. Continue directly to `design_spec.md`, image generation when selected, sequential SVG construction, and speaker notes.
11. Run the content checker, SVG checker, conditional template-aesthetic checker, and unified independent audit only after the full deck is ready and before export.

If the user has provided images, run the analysis script **before outputting the design spec** (do NOT directly read/open image files — use the script output only):
```bash
python3 ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

> ⚠️ **Image handling rule**: The AI must NEVER directly read, open, or view image files (`.jpg`, `.png`, etc.). All image information must come from the `analyze_images.py` script output or the Design Specification's Image Resource List.

**Output**:
- `<project_path>/ghost_deck.md` — title-only argument and one-point-per-page plan
- `<project_path>/outline_manifest.json` — pre-approval structure, language, framework, Action Titles, and one point per page
- `<project_path>/outline_approval.md` — explicit user approval record for the final outline
- `<project_path>/content_manifest.json` — post-approval slide body copy, claims, evidence, visible source footers, and source mapping
- `<project_path>/design_spec.md` — human-readable design narrative
- `<project_path>/spec_lock.md` — machine-readable execution contract (distilled from the decisions in design_spec.md; Executor re-reads this before every page). See `templates/spec_lock_reference.md` for the skeleton.

**✅ Checkpoint — Phase deliverables complete, auto-proceed to next step**:
```markdown
## ✅ Strategist Phase Complete
- [x] Nine Confirmations completed (user confirmed)
- [x] Ghost Deck and outline manifest generated
- [x] User outline approval recorded in outline_approval.md
- [x] Detailed content manifest generated
- [x] Design Specification & Content Outline generated
- [x] Execution lock (spec_lock.md) generated
- [ ] **Next**: Auto-proceed to [Image_Generator / Executor] phase
```

---

### Step 5: Image_Generator Phase (Conditional)

🚧 **GATE**: Step 4 complete; Nine Confirmations and user outline approval are recorded, detailed content is generated, and Design Specification is ready.

> **Trigger condition**: The confirmed visual production strategy includes `host-native`, `advanced-web`, or `hybrid` resources. Pure SVG and user-provided-only strategies skip directly to Step 6.

Read `references/image-generator.md`
Read `references/visual-generation-strategy.md`

1. Extract all images with status `Pending` from the design spec
2. Generate prompt document → `<project_path>/images/image_prompts.md`
3. Route each asset according to the confirmed strategy in `spec_lock.md`:
   - `svg`: no raster generation; Executor constructs the visual locally
   - `host-native`: use the current host image tool and record the model as `host-selected/unspecified`; do not infer Image 2.0 or any named advanced model from the host environment
   - named advanced model: open only the corresponding `web_entry` from `templates/image_models/model_catalog.json`, verify the exact model in the UI, then submit once
   - `hybrid`: use SVG for information-bearing pages and the one user-selected model for listed hero assets
4. Never silently replace the selected model. A host-native tool with an undisclosed identity cannot satisfy a named-model choice. If exact web model identity cannot be verified, mark the asset `Needs-Manual`.

**✅ Checkpoint — Confirm image generation attempted for every row, proceed to Step 6**:
```markdown
## ✅ Image_Generator Phase Complete
- [x] Prompt document created
- [x] Each image: status is either `Generated` (file present in images/) or `Needs-Manual` (reported to user with filename + reason)
- [x] No row remains `Pending`
```

> On generation failure or a 5 min browser watchdog handoff, do NOT halt — follow the Failure Handling rule in `references/image-generator.md` §4.3. Poll every 20-30 seconds; do not blindly refresh, resubmit, switch models, or start a duplicate generation. Mark the row `Needs-Manual`, report filename + selected model + reason, and continue to Step 6.

---

### Step 6: Executor Phase

🚧 **GATE**: Step 4 (and Step 5 if triggered) complete; all prerequisite deliverables are ready.

Read the role definition based on the selected style:
```
Read references/executor-base.md          # REQUIRED: common guidelines
Read references/executor-general.md       # General flexible style
Read references/executor-consultant.md    # Consulting style
Read references/executor-consultant-top.md # Top consulting style (MBB level)
```

> Only need to read executor-base + one style file.

**Design Parameter Confirmation (Mandatory)**: Before generating the first SVG, the Executor MUST review and output key design parameters from the Design Specification (canvas dimensions, color scheme, font plan, body font size) to ensure spec adherence. See executor-base.md Section 2 for details.

**Per-page spec_lock re-read (Mandatory)**: Before generating **each** SVG page, Executor MUST `read_file <project_path>/spec_lock.md` and use only the colors / fonts / icons / images listed there. This resists context-compression drift on long decks. See executor-base.md §2.1 for details.

> ⚠️ **Main-agent only rule**: SVG generation in Step 6 MUST remain with the current main agent because page design depends on full upstream context (source content, design spec, template mapping, image decisions, and cross-page consistency). Do NOT delegate any slide SVG generation to sub-agents.
> ⚠️ **Generation rhythm rule**: After confirming the global design parameters, the Executor MUST generate pages sequentially, one page at a time, while staying in the same continuous main-agent context. Do NOT split Step 6 into grouped page batches such as 5 pages per batch.

**Visual Construction Phase**:
- Generate SVG pages sequentially, one page at a time, in one continuous pass → `<project_path>/svg_output/`

**Logic Construction Phase**:
- Generate speaker notes → `<project_path>/notes/total.md`

**Unified Final Quality Gate (Mandatory)** — after detailed content, design, images, all SVGs, and speaker notes are complete, and BEFORE post-processing/export:

1. Run the detailed-content checker:
```bash
python3 ${SKILL_DIR}/scripts/content_quality_checker.py <project_path> --stage content
```
2. Run the SVG checker against the authored SVG source:
```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```
- Any `error` (banned SVG features, viewBox mismatch, spec_lock drift, etc.) MUST be fixed on the offending page before proceeding — go back to Visual Construction, re-generate that page, re-run the check.
- Geometry errors from `layout_auditor.py` (text outside container, table row/column misalignment, canvas overflow) are also hard errors and MUST be fixed before proceeding. Overlap warnings should be reviewed against intended layering; fix unintended occlusion before release.
- `warning` entries (e.g., low-resolution image, non-PPT-safe font tail) should be reviewed and fixed when straightforward; may be acknowledged and released otherwise.
- Running the checker against `svg_output/` is required — running it only after `finalize_svg.py` is too late (finalize rewrites SVG and some violations get masked).

3. For template-driven or Frontend Slides-inspired decks, run the aesthetic checker:
```bash
python3 ${SKILL_DIR}/scripts/template_aesthetic_checker.py <project_path>
```
- Aesthetic score must be >= 80 unless the deck is intentionally strict / low-variation and the reason is recorded.
- Fix repeated card grids, weak hierarchy, missing rhythm, and unclear visual direction before proceeding.

4. After all automated checks pass, dispatch one sub-agent for a unified read-only audit. Provide the raw project path and require review of `ghost_deck.md`, `outline_approval.md`, `content_manifest.json`, `design_spec.md`, `spec_lock.md`, image records, `notes/total.md`, generated SVGs, automated checker outputs, and `references/humanized-copy-review.md` for Chinese copy.
- The sub-agent MUST audit content and visuals together: framework fit, argument chain, approved-outline alignment, Action Titles, one-page-one-point discipline, unsupported claims, source footers, silent-reading comprehension, speaker-note-to-slide value transfer, language quality, Chinese humanization / AI-flavor removal, unintended occlusion, table misalignment, text overflow, missing hierarchy, template aesthetics, and spec/rhythm drift.
- For speech/report conversion decks, the sub-agent MUST also check that the TOC exists, section labels are visible and consistent, each substantive page has an information-bearing chart/diagram/structured visual, and important source-paragraph facts are not over-compressed into one vague sentence.
- The sub-agent MUST return findings only; it MUST NOT edit files, generate replacement SVG, or continue the PPT pipeline
- If the sub-agent reports actionable issues, the main agent fixes them, re-runs every affected automated checker, and repeats the unified audit when content or layout changed materially.
- If a sub-agent is unavailable in the current host, stop before export and report the audit as blocked. A manual self-review does not satisfy this gate.

**✅ Checkpoint — Confirm all SVGs and notes are fully generated and quality-checked. Proceed directly to Step 7 post-processing**:
```markdown
## ✅ Executor Phase Complete
- [x] All SVGs generated to svg_output/
- [x] Speaker notes generated at notes/total.md
- [x] content_quality_checker.py passed
- [x] svg_quality_checker.py passed (0 errors)
- [x] template_aesthetic_checker.py passed when applicable
- [x] Unified independent content-and-visual audit completed
```

---

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete; content, visuals, and notes passed the unified automated checks and independent sub-agent audit.

If a user-edited PPTX exists after a prior export, stop this SVG-to-PPTX export path unless the user explicitly wants to overwrite or rebuild from the SVG source. The latest user-edited PPTX is the live artifact; subsequent changes must be applied to that file or first round-tripped into the project source. Never silently replace a user-edited deck with an older generated source state.

> ⚠️ The following three sub-steps MUST be **executed individually one at a time**. Each command must complete and be confirmed successful before running the next.
> ❌ **NEVER** put all three commands in a single code block or single shell invocation.

Run the canonical three-command pipeline (same as `references/shared-standards.md` §5):

**Step 7.1** — Split speaker notes:
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** — SVG post-processing (icon embedding / image crop & embed / text flattening / rounded rect to path):
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
# Output: exports/<project_name>_<timestamp>.pptx + exports/<project_name>_<timestamp>_svg.pptx
```

> ❌ **NEVER** use `cp` as a substitute for `finalize_svg.py` — it performs multiple critical processing steps
> ❌ **NEVER** export directly from `svg_output/` — MUST use `-s final` to export from `svg_final/`
> ❌ **NEVER** add extra flags like `--only`

---

## Role Switching Protocol

Before switching roles, you **MUST first read** the corresponding reference file — skipping is FORBIDDEN. Output marker:

```markdown
## [Role Switch: <Role Name>]
📖 Reading role definition: references/<filename>.md
📋 Current task: <brief description>
```

---

## Reference Resources

| Resource | Path |
|----------|------|
| Shared technical constraints | `references/shared-standards.md` |
| Canvas format specification | `references/canvas-formats.md` |
| PPT Master inherited foundation | `references/ppt-master-foundation.md` |
| Image layout specification | `references/image-layout-spec.md` |
| Frontend Slides design pack | `references/frontend-slides-design-pack.md` |
| SVG image embedding | `references/svg-image-embedding.md` |
| Icon library | `templates/icons/README.md` |

---

## Notes

- Local preview: `python3 -m http.server -d <project_path>/svg_final 8000`
- **Troubleshooting**: If the user encounters issues during generation (layout overflow, export errors, blank images, etc.), recommend checking `docs/faq.md` — it contains known solutions sourced from real user reports and is continuously updated
