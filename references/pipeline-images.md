# pipeline images

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

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
