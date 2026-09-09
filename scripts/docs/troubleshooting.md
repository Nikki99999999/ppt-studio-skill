# Troubleshooting

## Validation Failed

1. Run:

```bash
python3 scripts/project_manager.py validate <project_path>
```

2. Fix missing files or invalid directories reported by the validator.
3. Re-run validation before post-processing or export.

## SVG Preview Looks Wrong

1. Check the file path and filename.
2. Confirm naming conventions are consistent.
3. Preview via a local server if browser file loading is inconsistent:

```bash
python3 -m http.server --directory <svg_output_path> 8000
```

## Speaker Notes Do Not Split

Check `total.md`:
- headings must start with `# `
- heading text must match SVG filenames
- sections must be separated by `---`

Then rerun:

```bash
python3 scripts/total_md_split.py <project_path>
```

## PPT Export Quality Issues

Preferred sequence:

```bash
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/svg_to_pptx.py <project_path> -s final
```

Do not export directly from `svg_output/` when `svg_final/` exists.

## Dependency Checklist

Do not work around a dependency failure by switching to a hard-coded directory such as `D:\luo\ai\pptagent`. From the loaded skill directory, run the preflight with the same interpreter that will execute the pipeline:

```bash
<python> scripts/environment_preflight.py --phase core
<python> scripts/environment_preflight.py --phase production --project-path <project_path>
```

Use the narrower phase (`pdf`, `docx`, `html`, `epub`, `ipynb`, `pptx-source`, `web`, `image-gemini`, or `image-openai`) when appropriate. The command reports the resolved interpreter and paths. Install extra dependencies only when the selected phase requires them:

The production preflight treats a missing PNG compatibility renderer as a warning because native editable PPTX export remains available. Add `--require-compat-renderer` when the legacy SVG-plus-PNG fallback variant is a required deliverable.

```bash
pip install -r requirements.txt
```

Important optional packages:
- `python-pptx` for PPTX export
- `Pillow` for image utilities
- `numpy` for watermark removal
- `PyMuPDF` for PDF conversion
- `google-genai` / `openai` for image generation backends

## Chinese Text Is Corrupted or QA Reports an Encoding Failure

Run the project-wide checker:

```bash
<python> scripts/artifact_encoding_checker.py <project_path> --report <project_path>/qa/artifact_encoding_report.json
```

Regenerate the named artifact from the last intact UTF-8 source. Do not repair mojibake by guessing or by decoding with `errors="replace"`; once text has become `?` or `U+FFFD`, recover it from the source material. Re-run the checker before the content and SVG quality checks, then run `finalize_svg.py`, which automatically checks rewritten `svg_final/` and blocks export on encoding failure.
