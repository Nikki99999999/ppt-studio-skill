#!/usr/bin/env python3
"""Validate a presentation's pre-approval outline or post-approval detailed content."""

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FRAMEWORKS = {"minto", "duarte-zen", "kawasaki"}
SCENARIO_FRAMEWORK = {
    "decision": "minto",
    "public": "duarte-zen",
    "pitch": "kawasaki",
}
STRUCTURAL_ROLES = {"cover", "chapter", "toc", "ending", "appendix"}
STRUCTURED_SOURCE_TYPES = {"speech", "briefing", "report", "work-report", "official-report", "meeting-briefing"}
INFORMATION_VISUAL_TYPES = {
    "chart",
    "kpi",
    "timeline",
    "process",
    "relationship-map",
    "table",
    "matrix",
    "structured-infographic",
    "diagram",
    "map",
}
GENERIC_TITLES = {
    "\u5e02\u573a\u6982\u51b5",
    "\u9879\u76ee\u80cc\u666f",
    "\u6838\u5fc3\u4f18\u52bf",
    "\u89e3\u51b3\u65b9\u6848",
    "\u603b\u7ed3",
    "\u4e0b\u4e00\u6b65",
    "market overview",
    "background",
    "key advantages",
    "solution",
    "summary",
    "next steps",
    "agenda",
    "introduction",
}
CONJUNCTION_RE = re.compile(r"(?:\band\b|&|\u548c|\u4e0e|\u53ca)", re.IGNORECASE)
CJK_RE = re.compile(r"[\u3400-\u9fff]")
AI_FLAVOR_RE = re.compile(
    r"(?:"
    r"不仅(?:仅)?[^。；;]{0,24}而且|"
    r"不(?:是|只是|仅仅是)[^。；;]{0,30}而是|"
    r"值得注意的是|"
    r"在这个背景下|"
    r"标志着|"
    r"深远影响|"
    r"未来可期|"
    r"迈向新阶段|"
    r"持续追求卓越|"
    r"无缝|"
    r"直观|"
    r"强大|"
    r"开创性|"
    r"令人叹为观止|"
    r"多个来源显示|"
    r"行业专家认为|"
    r"观察者指出"
    r")"
)

def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def validate(
    project: Path,
    stage: str = "content",
    require_outline_approval: bool = False,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    ghost_path = project / "ghost_deck.md"
    ghost_text = ""
    if ghost_path.exists():
        ghost_text = ghost_path.read_text(encoding="utf-8-sig")

    if not ghost_text.strip():
        errors.append("ghost_deck.md is missing or empty")

    manifest_name = "outline_manifest.json" if stage == "outline" else "content_manifest.json"
    manifest_path = project / manifest_name
    if not manifest_path.exists():
        errors.append(f"{manifest_name} is missing")
        return {"passed": False, "errors": errors, "warnings": warnings}

    manifest = load_json(manifest_path)
    outline_manifest = manifest if stage == "outline" else {}
    if stage == "content":
        outline_path = project / "outline_manifest.json"
        if not outline_path.exists():
            errors.append("outline_manifest.json is required before detailed content validation")
            return {"passed": False, "errors": errors, "warnings": warnings}
        outline_manifest = load_json(outline_path)
        require_outline_approval = True

    outline_approval = outline_manifest.get("outline_approval", {})
    outline_approval_file = "outline_approval.md"
    outline_approved = False
    if isinstance(outline_approval, dict):
        outline_approval_file = str(outline_approval.get("approval_file") or outline_approval_file)
        outline_approved = str(outline_approval.get("status", "")).strip().lower() == "approved"
    elif require_outline_approval:
        errors.append("outline_approval must be an object when outline approval is required")

    approval_path = project / outline_approval_file
    if require_outline_approval:
        if not outline_approved:
            errors.append("outline_approval.status must be 'approved' before final content validation")
        if not approval_path.exists() or not approval_path.read_text(encoding="utf-8-sig").strip():
            errors.append(f"{outline_approval_file} is missing or empty")

    framework = manifest.get("framework")
    if framework not in FRAMEWORKS:
        errors.append(f"framework must be one of {sorted(FRAMEWORKS)}")
    scenario = str(manifest.get("scenario", "")).strip().lower()
    if scenario not in {*SCENARIO_FRAMEWORK, "mixed"}:
        errors.append("scenario must be decision, public, pitch, or mixed")
    elif scenario != "mixed" and SCENARIO_FRAMEWORK[scenario] != framework:
        errors.append(
            f"scenario '{scenario}' requires primary framework "
            f"'{SCENARIO_FRAMEWORK[scenario]}', not '{framework}'"
        )
    if not str(manifest.get("framework_rationale", "")).strip():
        errors.append("framework_rationale is required")
    secondary_checks = manifest.get("secondary_checks", [])
    if not isinstance(secondary_checks, list):
        errors.append("secondary_checks must be a list")

    output_language = str(manifest.get("output_language", "")).strip()
    if not output_language:
        errors.append("output_language is required")
    outline_language = str(outline_manifest.get("output_language", "")).strip()
    if stage == "content" and output_language != outline_language:
        errors.append(
            "content_manifest.output_language must match the approved outline_manifest.json"
        )

    source_material_type = str(
        manifest.get("source_material_type")
        or outline_manifest.get("source_material_type")
        or ""
    ).strip().lower()
    is_structured_source = source_material_type in STRUCTURED_SOURCE_TYPES

    if stage == "content":
        allocation = manifest.get("allocation", {})
        allocation_values = [
            allocation.get("structure_percent"),
            allocation.get("content_percent"),
            allocation.get("design_percent"),
        ]
        if allocation_values != [40, 30, 30]:
            warnings.append("recommended effort allocation is 40% structure / 30% content / 30% design")
        if output_language.lower().startswith("zh"):
            silent_review = manifest.get("silent_reading_review", {})
            if not isinstance(silent_review, dict) or str(silent_review.get("status", "")).strip().lower() not in {"passed", "pass", "done"}:
                errors.append("silent_reading_review must be completed for Chinese decks")
            humanized_review = manifest.get("humanized_copy_review", {})
            if not isinstance(humanized_review, dict) or str(humanized_review.get("status", "")).strip().lower() not in {"passed", "pass", "done"}:
                errors.append("humanized_copy_review must be completed with references/humanized-copy-review.md")
            else:
                score = humanized_review.get("score_50")
                try:
                    score_value = float(score)
                except (TypeError, ValueError):
                    errors.append("humanized_copy_review.score_50 must be numeric for Chinese decks")
                else:
                    if score_value < 45 and not str(humanized_review.get("exception_reason", "")).strip():
                        errors.append("humanized_copy_review.score_50 must be >=45 or include exception_reason")

    slides = manifest.get("slides")
    if not isinstance(slides, list) or not slides:
        errors.append("slides must be a non-empty list")
        slides = []

    expected_pages = list(range(1, len(slides) + 1))
    actual_pages = [slide.get("page") for slide in slides]
    if actual_pages != expected_pages:
        errors.append("slide page numbers must be sequential starting at 1")

    if stage == "content" and is_structured_source:
        first_roles = [str(slide.get("role", "")).strip().lower() for slide in slides[:2]]
        if "toc" not in first_roles:
            errors.append(
                "speech/briefing/report decks require a TOC or agenda slide in the first two pages"
            )

    seen_titles: set[str] = set()
    sourced_claims = 0
    unsourced_claims = 0
    for slide in slides:
        page = slide.get("page", "?")
        role = str(slide.get("role", "content")).lower()
        title = str(slide.get("action_title", "")).strip()
        point = str(slide.get("single_point", "")).strip()

        if not title:
            errors.append(f"P{page}: action_title is required")
            continue
        if title not in ghost_text:
            errors.append(f"P{page}: action_title is not present in ghost_deck.md")
        normalized = title.lower().strip(" ：:")
        if normalized in seen_titles:
            errors.append(f"P{page}: duplicate title '{title}'")
        seen_titles.add(normalized)

        if role not in STRUCTURAL_ROLES and normalized in GENERIC_TITLES:
            errors.append(f"P{page}: generic topic title must be rewritten as a conclusion: '{title}'")
        if role not in STRUCTURAL_ROLES and CONJUNCTION_RE.search(title):
            warnings.append(f"P{page}: title may contain more than one point: '{title}'")
        if not point:
            errors.append(f"P{page}: single_point is required")
        if stage == "content" and is_structured_source and role not in STRUCTURAL_ROLES:
            section_title = str(slide.get("section_title", "")).strip()
            if not section_title:
                errors.append(
                    f"P{page}: speech/briefing/report content pages require section_title"
                )
        if output_language.lower().startswith("zh"):
            if not CJK_RE.search(title):
                errors.append(f"P{page}: action_title must contain Chinese for output_language={output_language}")
            if point and not CJK_RE.search(point):
                errors.append(f"P{page}: single_point must contain Chinese for output_language={output_language}")

        if stage == "content":
            body_points = slide.get("body_points", [])
            if role not in STRUCTURAL_ROLES and (
                not isinstance(body_points, list)
                or not any(str(item).strip() for item in body_points)
            ):
                errors.append(f"P{page}: detailed content requires non-empty body_points")
            if (
                output_language.lower().startswith("zh")
                and isinstance(body_points, list)
                and any(str(item).strip() and not CJK_RE.search(str(item)) for item in body_points)
            ):
                errors.append(f"P{page}: body_points must be Chinese for output_language={output_language}")
            if is_structured_source and role not in STRUCTURAL_ROLES:
                visible_body = "".join(str(item).strip() for item in body_points if str(item).strip())
                if len([item for item in body_points if str(item).strip()]) < 2 and len(visible_body) < 45:
                    errors.append(
                        f"P{page}: speech/briefing/report pages must preserve more than one thin sentence of visible body copy"
                    )
                visualization = slide.get("visualization", {})
                visual_type = ""
                visual_purpose = ""
                if isinstance(visualization, dict):
                    visual_type = str(visualization.get("type", "")).strip().lower()
                    visual_purpose = str(visualization.get("purpose", "")).strip()
                if visual_type not in INFORMATION_VISUAL_TYPES or not visual_purpose:
                    errors.append(
                        f"P{page}: speech/briefing/report pages require an information-bearing visualization"
                    )
                source_mapping = slide.get("source_mapping", [])
                if not isinstance(source_mapping, list) or not source_mapping:
                    errors.append(
                        f"P{page}: speech/briefing/report pages require source_mapping"
                    )
            if output_language.lower().startswith("zh"):
                copy_fragments = [title, point]
                if isinstance(body_points, list):
                    copy_fragments.extend(str(item) for item in body_points)
                ai_hits = sorted({hit.group(0) for text in copy_fragments for hit in AI_FLAVOR_RE.finditer(str(text))})
                if ai_hits:
                    errors.append(
                        f"P{page}: possible AI-flavored Chinese phrasing; review with humanized-copy-review.md: "
                        + "、".join(ai_hits[:8])
                    )

            evidence = slide.get("evidence", [])
            if not isinstance(evidence, list):
                errors.append(f"P{page}: evidence must be a list")
                continue
            for item in evidence:
                if not isinstance(item, dict) or not str(item.get("claim", "")).strip():
                    errors.append(f"P{page}: each evidence item needs a claim")
                    continue
                if str(item.get("source", "")).strip():
                    sourced_claims += 1
                else:
                    unsourced_claims += 1
                    errors.append(f"P{page}: claim lacks a Source footer mapping")
            if evidence and not str(slide.get("source_footer", "")).strip():
                errors.append(f"P{page}: evidence requires a visible source_footer")

    if stage == "content":
        outline_slides = outline_manifest.get("slides", [])
        if len(outline_slides) != len(slides):
            errors.append("content slide count must match the approved outline")
        else:
            for outline_slide, content_slide in zip(outline_slides, slides):
                page = content_slide.get("page", "?")
                if content_slide.get("action_title") != outline_slide.get("action_title"):
                    errors.append(f"P{page}: action_title drifted from the approved outline")
                if content_slide.get("single_point") != outline_slide.get("single_point"):
                    errors.append(f"P{page}: single_point drifted from the approved outline")

    if framework == "minto":
        scqa = manifest.get("scqa", {})
        missing = [
            key
            for key in ("situation", "complication", "question", "answer")
            if not str(scqa.get(key, "")).strip()
        ]
        if missing:
            errors.append(f"Minto deck requires complete SCQA fields: missing {', '.join(missing)}")
    elif framework == "duarte-zen":
        if manifest.get("glance_test_seconds", 99) > 3:
            errors.append("Duarte/Zen deck must target a Glance Test of 3 seconds or less")
    elif framework == "kawasaki":
        constraints = manifest.get("pitch_constraints", {})
        if constraints.get("core_slide_count") != 10:
            errors.append("Kawasaki pitch requires 10 core slides")
        if constraints.get("duration_minutes", 999) > 20:
            errors.append("Kawasaki pitch duration must be 20 minutes or less")
        if constraints.get("minimum_font_size", 0) < 30:
            errors.append("Kawasaki pitch minimum font size must be at least 30")

    return {
        "passed": not errors,
        "stage": stage,
        "manifest": manifest_name,
        "framework": framework,
        "output_language": output_language,
        "scenario": scenario,
        "slide_count": len(slides),
        "titles_test_sequence": [slide.get("action_title", "") for slide in slides],
        "outline_approved": outline_approved,
        "outline_approval_file": outline_approval_file,
        "sourced_claims": sourced_claims,
        "unsourced_claims": unsourced_claims,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--stage",
        choices=("outline", "content"),
        default="content",
        help="Validate the pre-approval outline or the post-approval detailed content.",
    )
    parser.add_argument(
        "--require-outline-approval",
        action="store_true",
        help="Require outline_approval.md and outline_manifest.json approval status.",
    )
    args = parser.parse_args()
    result = validate(
        args.project_path,
        stage=args.stage,
        require_outline_approval=args.require_outline_approval,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Content quality: {'PASS' if result['passed'] else 'FAIL'}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
