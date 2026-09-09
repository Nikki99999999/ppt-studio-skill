# pipeline source templates

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

### Step 1: Source Content Processing

🚧 **GATE**: User has provided source material (PDF / DOCX / EPUB / URL / Markdown file / text description / conversation content — any form is acceptable).

When the user provides non-Markdown content, convert immediately:

| User Provides | Command |
|---------------|---------|
| PDF file | `${PYTHON} ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office document | `${PYTHON} ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| PPTX / PowerPoint deck | `${PYTHON} ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / other | `${PYTHON} ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| Web link | `${PYTHON} ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| WeChat / high-security site | `${PYTHON} ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` (requires `curl_cffi`; falls back to `node web_to_md.cjs <URL>` only if that package is unavailable) |
| Markdown | Read directly |

**✅ Checkpoint — Confirm source content is ready, proceed to Step 2.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready (Markdown file, user-provided text, or requirements described in conversation are all valid).

```bash
${PYTHON} ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format <format>
```

Format options: `ppt169` (default), `ppt43`, `xhs`, `story`, etc. For the full format list, see `references/canvas-formats.md`.

Import source content (choose based on the situation):

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `${PYTHON} ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
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
${PYTHON} ${SKILL_DIR}/scripts/template_recommender.py "<brief>" --audience "<audience>" --tone "<tone>" --density "<density>"
```

Present exactly three recommendations plus the free-design option and wait for the user's choice if the user explicitly asked to choose. If the user selects a Frontend Slides direction, copy `${SKILL_DIR}/templates/layouts/frontend_slides_bold/` into the project templates and record the selected direction name in the Nine Confirmations and `spec_lock.md`.

**User-provided template reference and persistence.** Read `references/template-library-persistence.md`. If the user provides HTML/PPTX/PDF/screenshots/brand guide as a design source, ingest it as a reference style and reconstruct a reusable PPT-safe template package. After validation, register the derived package with `scripts/customer_template_library.py`; future projects can discover it from `templates/customer_library/index.json`. Keep the original upload in the source project and keep customer packages private to the workspace by default. For HTML slides, extract design tokens and layout intent; do not copy HTML runtime, JavaScript, CSS classes, animations, or browser-only layout behavior into PPT output.

**Soft hint (non-blocking, optional).** Before Step 4, if the user's content is an obvious strong match for an existing template (e.g., clearly an academic defense, a government report, a McKinsey-style consulting deck, or a Frontend Slides direction) AND the user has given no template signal, the AI MAY emit a single-sentence notice and continue without waiting:

> Note: the library has a template `<name>` that matches this scenario closely. Say the word if you want to use it; otherwise I'll continue with free design.

This is a hint, not a question — do NOT block, do NOT require an answer. Skip the hint entirely when the match is weak or ambiguous.

> To create a new global template, read `workflows/create-template.md`

**✅ Checkpoint — Default path proceeds to Step 4 without user interaction. If a template trigger fired, template files are copied before advancing.**

---
