# pipeline execution qa

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

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

1. Run the project-wide artifact encoding checker first:
```bash
${PYTHON} ${SKILL_DIR}/scripts/artifact_encoding_checker.py <project_path> --report <project_path>/qa/artifact_encoding_report.json
```
- Any invalid UTF-8, UTF-8 BOM, `U+FFFD`, private-use character, C1 control, recognizable mojibake fragment, or repeated `?` corruption in a Chinese project is a hard error. Fix the originating artifact and rerun this checker before any semantic or SVG checks.

2. Run the detailed-content checker:
```bash
${PYTHON} ${SKILL_DIR}/scripts/content_quality_checker.py <project_path> --stage content
```
3. Run the SVG checker against the authored SVG source:
```bash
${PYTHON} ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```
- Any `error` (banned SVG features, viewBox mismatch, spec_lock drift, etc.) MUST be fixed on the offending page before proceeding — go back to Visual Construction, re-generate that page, re-run the check.
- Geometry errors from `layout_auditor.py` (text outside container, table row/column misalignment, canvas overflow) are also hard errors and MUST be fixed before proceeding. Overlap warnings should be reviewed against intended layering; fix unintended occlusion before release.
- `warning` entries (e.g., low-resolution image, non-PPT-safe font tail) should be reviewed and fixed when straightforward; may be acknowledged and released otherwise.
- Running the checker against `svg_output/` is required — running it only after `finalize_svg.py` is too late (finalize rewrites SVG and some violations get masked).

4. For template-driven or Frontend Slides-inspired decks, run the aesthetic checker:
```bash
${PYTHON} ${SKILL_DIR}/scripts/template_aesthetic_checker.py <project_path>
```
- Aesthetic score must be >= 80 unless the deck is intentionally strict / low-variation and the reason is recorded.
- Fix repeated card grids, weak hierarchy, missing rhythm, and unclear visual direction before proceeding.

5. After all automated checks pass, dispatch one sub-agent for a unified read-only audit. Provide the raw project path and require review of `ghost_deck.md`, `outline_approval.md`, `content_manifest.json`, `design_spec.md`, `spec_lock.md`, image records, `notes/total.md`, generated SVGs, automated checker outputs, and `references/humanized-copy-review.md` for Chinese copy.
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
- [x] artifact_encoding_checker.py passed (0 errors)
- [x] content_quality_checker.py passed
- [x] svg_quality_checker.py passed (0 errors)
- [x] template_aesthetic_checker.py passed when applicable
- [x] Unified independent content-and-visual audit completed
```

---
