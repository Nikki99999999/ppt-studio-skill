# PPT Master Foundation

Read this reference when explaining what Presentation Studio inherits from PPT Master or when comparing the two systems.

## Primary Sources

- Repository README: https://github.com/hugohe3/ppt-master/blob/main/README.md
- Why PPT Master: https://github.com/hugohe3/ppt-master/blob/main/docs/why-ppt-master.md
- Technical design: https://github.com/hugohe3/ppt-master/blob/main/docs/technical-design.md
- Skill entry: https://github.com/hugohe3/ppt-master/blob/main/skills/ppt-master/SKILL.md

## Verified Foundation Advantages

1. **SVG authoring layer**: the AI authors constrained SVG instead of constructing the PPTX/OOXML package directly.
2. **Native PowerPoint compilation**: scripts compile supported SVG structures into DrawingML objects, preserving native text, shapes, connectors, picture geometry, fills, effects, and eligible charts/tables.
3. **Inspectable source of truth**: `svg_output/` remains the authored source. It can be opened, checked, edited, archived, and compiled again without regenerating the entire deck from the model.
4. **Preview and delivery separation**: SVG source, finalized SVG preview, quality reports, and editable PPTX serve distinct authoring, inspection, and delivery needs.
5. **Local and open workflow**: source conversion and export run locally; the project is open source, does not add a presentation-platform subscription, and can run in multiple Agent-capable environments.
6. **Reasoning-to-delivery pipeline**: the workflow connects narrative planning, visual construction, native PowerPoint output, notes, and reuse rather than optimizing only one layer.

## Token Claim Boundary

Do not claim that the SVG route always uses fewer model tokens. The primary sources support lower authoring complexity, inspectability, reuse, and reduced rework. They do not provide a universal token benchmark against every alternative.

Preferred wording:

> SVG reduces the complexity of the model's authoring target and preserves a reusable source layer.

Avoid:

> SVG always saves tokens.
