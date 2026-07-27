# Frontend Slides Design Pack

Use this reference when the user wants more stylish templates, mentions Frontend Slides, provides an HTML slide reference, or wants to choose a template before PPT generation.

Source observed: Zara Zhang (`zarazhangrui`) / `frontend-slides`:
https://github.com/zarazhangrui/frontend-slides

Observed source facts: the upstream workflow generates three visual previews, lets the user pick a direction, and includes 12 safe preset styles plus 34 optional bold design systems. Presentation Studio translates that selection model into PPT-safe SVG assets instead of using the web runtime.

## Attribution Boundary

- Credit Zara Zhang's `zarazhangrui/frontend-slides` for the design-template aesthetics, visual-direction selection pattern, and page-rhythm inspiration that Presentation Studio studies and adapts.
- Do not describe customer-template persistence as a Zara or Frontend Slides feature.
- Presentation Studio's private customer-template registration, validation, indexing, retrieval, and reuse workflow is an added capability owned by this skill.

## What To Reuse

- Reuse the selection pattern: recommend exactly three visual directions, then let the user pick.
- Reuse the aesthetic taxonomy: safe presets plus bold templates, each with mood, formality, density, scheme, best-for, and avoid-for.
- Reuse the fixed-stage discipline conceptually, but map it to Presentation Studio's `ppt169` SVG viewBox `0 0 1280 720`.

## What Not To Reuse Directly

- Do not embed the HTML runtime in Presentation Studio output.
- Do not use JavaScript, CSS classes, animations, `foreignObject`, or browser-only layout behavior in final SVG templates.
- Do not copy a full template pack into the generation context. Read `templates/frontend_slides/design_catalog.json`, shortlist candidates, and load details only for the selected direction.

## Selection Procedure

Run the recommender when the user asks for stronger aesthetics, template choice, HTML slides, Frontend Slides, or a user-provided design reference:

```bash
python3 ${SKILL_DIR}/scripts/template_recommender.py "<brief>" --audience "<audience>" --tone "<tone>" --density "<density>"
```

Present the top three as visual directions:

1. recommended style name
2. what it is good for
3. what it should avoid
4. fallback Presentation Studio template package: `frontend_slides_bold`

If the user chooses one of the directions, copy `templates/layouts/frontend_slides_bold/` into the project templates and encode the selected visual direction in `design_spec.md` and `spec_lock.md`.

If the user gives their own HTML slide file, treat it as an additional reference source: extract color, typography, spacing, page rhythm, and archetype intent; map it to the closest catalog direction or record it as `user_reference`; then rebuild PPT-safe SVG templates.

## Aesthetic Guardrails

- Every deck needs a visible rhythm plan: `anchor`, `dense`, and `breathing` where the content allows it.
- Avoid three consecutive pages with the same local structure.
- Do not make every content page a symmetric card grid.
- Use graphics only when they explain, compare, sequence, or create a deliberate emotional pause.
- Keep typography role-based: title, body, emphasis, and code may use different stacks, but every stack must end in a PPT-safe installed fallback.
- Palette should not collapse into generic purple/blue gradients on white unless the user's brand requires it.

## Validation

After `svg_quality_checker.py` passes, run:

```bash
python3 ${SKILL_DIR}/scripts/template_aesthetic_checker.py <project_path>
```

Run this checker inside the unified final quality gate after speaker notes are ready. Then include template aesthetics in the required independent content-and-visual sub-agent audit before export.
