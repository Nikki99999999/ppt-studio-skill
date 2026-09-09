# pipeline export

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete; content, visuals, and notes passed the unified automated checks and independent sub-agent audit.

If a user-edited PPTX exists after a prior export, stop this SVG-to-PPTX export path unless the user explicitly wants to overwrite or rebuild from the SVG source. The latest user-edited PPTX is the live artifact; subsequent changes must be applied to that file or first round-tripped into the project source. Never silently replace a user-edited deck with an older generated source state.

> ⚠️ The following three command steps MUST be **executed individually one at a time**. Each command must complete and be confirmed successful before running the next.
> ❌ **NEVER** put all three commands in a single code block or single shell invocation.

Run the canonical three-command pipeline (same as `references/shared-standards.md` §5):

**Step 7.1** — Split speaker notes:
```bash
${PYTHON} ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** — SVG post-processing (icon embedding / image crop & embed / text flattening / rounded rect to path):
```bash
${PYTHON} ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

The finalizer automatically checks the rewritten `svg_final/` text artifacts and returns failure on encoding errors. A successful exit is required before export; no separate Step 7.3 encoding command is needed. The Step 6 project-wide check remains required.

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
${PYTHON} ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> -s final
# Output: exports/<project_name>_<timestamp>.pptx + exports/<project_name>_<timestamp>_svg.pptx
```

**Step 7.4** — Archive the final deck:

Select the user-facing finished PPTX (normally the non-`_svg` PPTX unless the user explicitly needs the SVG-only variant), then move it to:

```text
C:\Users\picc\Desktop\AI\Codex\context-infrastructure\knowledge\docs\<purpose_or_owner>\<optional_topic>\
```

Use a purpose- or owner-based folder name. Preserve the project `exports/` folder for build history only; the final deliverable must live in the knowledge docs archive. If the target file already exists, add a timestamp suffix instead of overwriting it.

> ❌ **NEVER** use `cp` as a substitute for `finalize_svg.py` — it performs multiple critical processing steps
> ❌ **NEVER** export directly from `svg_output/` — MUST use `-s final` to export from `svg_final/`
> ❌ **NEVER** add extra flags like `--only`

---
