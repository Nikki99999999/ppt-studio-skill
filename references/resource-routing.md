# resource routing

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

## Main Pipeline Scripts

| Script | Purpose |
|--------|---------|
| `${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py` | PDF to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/doc_to_md.py` | Documents to Markdown — native Python for DOCX/HTML/EPUB/IPYNB, pandoc fallback for legacy formats (.doc/.odt/.rtf/.tex/.rst/.org/.typ) |
| `${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py` | PowerPoint to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.py` | Web page to Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.cjs` | Node.js fallback for WeChat / TLS-blocked sites (use only if `curl_cffi` is unavailable; `web_to_md.py` now handles WeChat when `curl_cffi` is installed) |
| `${SKILL_DIR}/scripts/project_manager.py` | Project init / validate / manage |
| `${SKILL_DIR}/scripts/environment_preflight.py` | Resolve the active interpreter / skill root and verify phase dependencies without fixed host paths |
| `${SKILL_DIR}/scripts/artifact_encoding_checker.py` | Strict project-wide UTF-8 / BOM / replacement-character / mojibake gate |
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
