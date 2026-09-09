# pipeline strategy

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

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
${PYTHON} ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
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
