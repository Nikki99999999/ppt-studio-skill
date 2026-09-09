# agent decomposition

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

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
