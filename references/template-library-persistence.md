# Reusable Customer Template Library

Use this reference whenever the user uploads a PPTX, PDF, HTML slide deck, screenshots, brand guide, or existing project as a design template.

## 1. Persistence policy

Every successfully reconstructed customer template becomes reusable after validation.

- Archive the original upload in the current project's `sources/` directory.
- Build a PPT-safe derived template package. Do not reuse browser runtime code or raw slide XML as the final template.
- Register only the sanitized derived package in `templates/customer_library/`.
- Keep customer templates private to the workspace by default.
- Do not commit original customer files, confidential logos, personal data, or private derived templates to Git.
- Promotion into the public `templates/layouts/` library requires explicit publication approval and a privacy review.

## 2. Reusable package

Each private template package contains:

```text
templates/customer_library/<template_id>/
├── design_spec.md
├── 01_cover.svg
├── 02_chapter.svg
├── 03_content.svg
├── 04_ending.svg
├── 02_toc.svg                 # optional
├── tokens.json                # optional
├── preview.png                # optional
├── asset_manifest.json        # optional
├── assets/                    # sanitized SVG/raster assets only
└── provenance.json            # written by the registrar
```

The registrar rejects symlinks, hidden files, Git metadata, raw PPT/PPTX/PDF/HTML files, archives, unsupported assets, unexpected paths, and files over 20 MB. It copies only allowlisted files.

`provenance.json` records source filename, SHA-256, source project, import time, visibility, publication approval, validation report hash, validator, and validation status. It must not contain customer secrets or absolute source paths.

## 3. Validation and registration

First generate a JSON validation report from the SVG, asset, privacy, and license checks:

```json
{
  "passed": true,
  "validated_by": "main-agent + independent-audit",
  "checks": ["svg", "assets", "privacy", "license"]
}
```

Only a report with `passed: true` and a non-empty `validated_by` may be registered:

```bash
python3 scripts/customer_template_library.py register \
  --template-dir "<prepared_template_dir>" \
  --id "<template_id>" \
  --label "<display_name>" \
  --summary "<one sentence>" \
  --keywords "<tag1,tag2,tag3>" \
  --source-file "<original_template_file>" \
  --source-project "<project_name>" \
  --validation-report "<validation_report.json>"
```

The command lints and copies the sanitized package into `templates/customer_library/<template_id>/`, writes provenance, and updates `templates/customer_library/index.json`.

Registration is fail-closed:

- A package cannot enter the recommendation index without an explicit passing validation report.
- An existing template ID is never overwritten automatically.
- The same source hash can be reused without creating another package.
- Name or hash conflicts require a new ID or explicit human resolution.
- Every registered template remains `private-workspace` with `publish_approved: false`.

## 4. Discovery and reuse

Template recommendation reads both:

- Public library: `templates/layouts/layouts_index.json`
- Private customer library: `templates/customer_library/index.json`

When a private customer template matches the user, show it as `Workspace private template`. Copy its derived SVG and sanitized assets into the new project. Never copy the original customer upload into another project.

## 5. Public promotion

When the user later asks to publish or push the repository:

1. List private templates separately.
2. Exclude every private package from Git by default.
3. Promote only explicitly approved, sanitized packages into `templates/layouts/`.
4. Remove customer names, confidential text, personal data, and restricted assets.
5. Re-run SVG quality, aesthetic, content, and independent sub-agent audits.
6. Update the repository and Skill name to `presentation-studio`.
