# runtime bootstrap

> Load only when routed here by SKILL.md. Paths such as `references/`, `scripts/`, and `templates/` are relative to `${SKILL_DIR}`, not this reference directory. Host instructions and user authorization take precedence.

## Runtime Environment Bootstrap (MANDATORY)

- Never assume a fixed working directory or sandbox path. In particular, `D:\luo\ai\pptagent` is a host-local example, not a portable workflow fact.
- Resolve `${SKILL_DIR}` from the directory containing this loaded `SKILL.md`; resolve `<project_path>` to an explicit absolute path.
- Resolve `${PYTHON}` once from the current host's dependency/runtime resolver when available, otherwise from a verified Python interpreter on `PATH`. `${PYTHON}` in commands below is a documentation placeholder that MUST be replaced with that actual executable; do not assume the command name is `python3`.
- Before the first pipeline script, run the core preflight. Before a dependency-bearing phase, run its matching phase preflight. Missing dependencies are a hard stop for that phase, not a reason to switch to an invented directory or interpreter.

```bash
${PYTHON} ${SKILL_DIR}/scripts/environment_preflight.py --phase core
```

Phase-specific values are `pdf`, `docx`, `html`, `epub`, `ipynb`, `pptx-source`, `web`, `production`, `image-gemini`, and `image-openai`. Pass `--project-path <project_path>` once the project exists. Install only the dependencies required by the selected phase; the preflight prints the resolved interpreter, skill root, repository root, and an actionable install hint. The PNG compatibility renderer is optional for the native editable PPTX; add `--require-compat-renderer` only when the legacy SVG-plus-PNG fallback variant is required.
