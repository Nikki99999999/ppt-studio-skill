#!/usr/bin/env python3
"""Lightweight aesthetic gate for PPT Studio design specs and SVG pages."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET


SCORES = {
    "hierarchy": 20,
    "typography": 15,
    "grid_whitespace": 15,
    "rhythm": 15,
    "semantic_fit": 15,
    "consistency": 10,
    "variation": 10,
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def collect_svg_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".svg":
        return [path]
    for sub in ("svg_output", "svg_final"):
        candidate = path / sub
        if candidate.exists():
            return sorted(candidate.glob("*.svg"))
    return sorted(path.glob("*.svg"))


def svg_metrics(svg_path: Path) -> dict[str, int]:
    text = read_text(svg_path)
    metrics = {
        "cards": len(re.findall(r"<rect\b[^>]*(?:rx=\"(?:8|1[0-9]|2[0-4])\"|ry=\"(?:8|1[0-9]|2[0-4])\")", text)),
        "texts": len(re.findall(r"<text\b", text)),
        "images": len(re.findall(r"<image\b", text)),
        "lines": len(re.findall(r"<(?:line|polyline|path)\b", text)),
        "font_sizes": 0,
    }
    metrics["font_sizes"] = len(set(re.findall(r"font-size=\"([0-9]+)", text)))
    try:
        ET.fromstring(text)
    except ET.ParseError:
        metrics["xml_error"] = 1
    return metrics


def score_project(project_path: Path) -> dict[str, object]:
    design_spec = read_text(project_path / "design_spec.md")
    spec_lock = read_text(project_path / "spec_lock.md")
    svgs = collect_svg_files(project_path)
    metrics = [svg_metrics(path) for path in svgs]

    score = dict(SCORES)
    findings: list[str] = []

    if not svgs:
        score["consistency"] -= 10
        findings.append("No SVG files found for aesthetic inspection.")

    if "page_rhythm" not in spec_lock and "page_rhythm" not in design_spec:
        score["rhythm"] -= 10
        findings.append("Missing page_rhythm plan; deck may collapse into repeated card grids.")

    rhythm_values = set(re.findall(r"\b(anchor|dense|breathing)\b", spec_lock + "\n" + design_spec))
    if len(rhythm_values) < 2:
        score["variation"] -= 6
        findings.append("Fewer than two rhythm modes detected; add anchor/dense/breathing variation when content allows.")

    if "Typography" not in design_spec and "font" not in spec_lock.lower():
        score["typography"] -= 8
        findings.append("Typography system is not explicit enough.")

    if "Color" not in design_spec and "colors" not in spec_lock.lower():
        score["semantic_fit"] -= 6
        findings.append("Color system is not explicit enough.")

    if metrics:
        card_pages = sum(1 for item in metrics if item["cards"] >= 3)
        if card_pages >= max(3, int(len(metrics) * 0.7)):
            score["variation"] -= 6
            findings.append("Most pages look card-heavy; introduce poster, split, full-bleed, or negative-space pages.")
        weak_hierarchy = sum(1 for item in metrics if item["font_sizes"] < 2 and item["texts"] > 3)
        if weak_hierarchy:
            score["hierarchy"] -= min(12, weak_hierarchy * 3)
            findings.append("Some text-heavy pages expose fewer than two font-size levels.")
        xml_errors = sum(item.get("xml_error", 0) for item in metrics)
        if xml_errors:
            score["consistency"] -= 10
            findings.append("One or more SVG files are not parseable XML.")

    for key, value in list(score.items()):
        score[key] = max(0, value)

    total = sum(score.values())
    pass_gate = total >= 80 and all(value >= int(SCORES[key] * 0.4) for key, value in score.items())
    return {
        "total": total,
        "pass": pass_gate,
        "dimensions": score,
        "findings": findings,
        "files_checked": [str(path) for path in svgs],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a lightweight PPT aesthetic gate.")
    parser.add_argument("project_path", help="Project path or template directory")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = score_project(Path(args.project_path).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Aesthetic score: {result['total']}/100")
        print(f"Pass: {result['pass']}")
        for key, value in result["dimensions"].items():
            print(f"- {key}: {value}")
        if result["findings"]:
            print("Findings:")
            for finding in result["findings"]:
                print(f"- {finding}")
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
