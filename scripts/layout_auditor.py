#!/usr/bin/env python3
"""
Geometry-level SVG layout auditor for ppt-master.

This complements svg_quality_checker.py by detecting issues weaker models often
miss: text overflow, element overlap, canvas overflow, and table alignment drift.

The auditor is intentionally annotation-aware. Hard errors require explicit
layout contracts such as data-container, data-table-id, data-row, and data-col.
Generic overlap checks are warnings to avoid blocking legitimate layered design.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"

TRANSLATE_RE = re.compile(r"translate\(\s*([-+]?\d*\.?\d+)(?:[\s,]+([-+]?\d*\.?\d+))?\s*\)")
NUMBER_RE = re.compile(r"[-+]?\d*\.?\d+")
IGNORE_ROLES = {
    "background",
    "decoration",
    "decorative",
    "grid",
    "grid-line",
    "connector",
    "axis",
    "tick",
    "divider",
}
MAJOR_ROLES = {
    "container",
    "card",
    "panel",
    "table",
    "cell",
    "chart",
    "image",
    "text-block",
    "title",
    "kpi",
    "callout",
}


@dataclass(frozen=True)
class BBox:
    x: float
    y: float
    w: float
    h: float

    @property
    def x2(self) -> float:
        return self.x + self.w

    @property
    def y2(self) -> float:
        return self.y + self.h

    @property
    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)

    def padded(self, pad: float) -> "BBox":
        return BBox(self.x + pad, self.y + pad, max(0.0, self.w - 2 * pad), max(0.0, self.h - 2 * pad))

    def contains(self, other: "BBox", tolerance: float = 1.0) -> bool:
        return (
            other.x >= self.x - tolerance
            and other.y >= self.y - tolerance
            and other.x2 <= self.x2 + tolerance
            and other.y2 <= self.y2 + tolerance
        )

    def intersection_area(self, other: "BBox") -> float:
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x2, other.x2)
        y2 = min(self.y2, other.y2)
        if x2 <= x1 or y2 <= y1:
            return 0.0
        return (x2 - x1) * (y2 - y1)


@dataclass
class ElementBox:
    label: str
    tag: str
    role: str
    bbox: BBox
    attrs: dict[str, str]
    text: str = ""


def _strip_ns(tag: str) -> str:
    return tag.replace(SVG_NS, "")


def _num(value: str | None, default: float = 0.0) -> float:
    if not value:
        return default
    match = NUMBER_RE.search(str(value))
    if not match:
        return default
    try:
        return float(match.group(0))
    except ValueError:
        return default


def _translation(transform: str | None) -> tuple[float, float]:
    if not transform:
        return 0.0, 0.0
    dx = dy = 0.0
    for match in TRANSLATE_RE.finditer(transform):
        dx += float(match.group(1))
        dy += float(match.group(2) or 0.0)
    return dx, dy


def _attrs(el: ET.Element) -> dict[str, str]:
    return {k: v for k, v in el.attrib.items()}


def _label(attrs: dict[str, str], tag: str, index: int) -> str:
    return attrs.get("id") or attrs.get("data-id") or attrs.get("data-name") or f"{tag}#{index}"


def _text_content(el: ET.Element) -> str:
    return "".join(el.itertext()).strip()


def _text_lines(el: ET.Element) -> list[str]:
    tspans = [_text_content(child) for child in list(el) if _strip_ns(child.tag) == "tspan"]
    lines = [line for line in tspans if line]
    if lines:
        return lines
    text = _text_content(el)
    return [part for part in re.split(r"\n+", text) if part.strip()] or [""]


def _visual_width(text: str, font_size: float) -> float:
    width = 0.0
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff":
            width += font_size
        elif ch.isspace():
            width += font_size * 0.33
        elif ord(ch) > 127:
            width += font_size * 0.72
        else:
            width += font_size * 0.55
    return width


def _bbox_for(el: ET.Element, tag: str, tx: float, ty: float) -> BBox | None:
    attrs = _attrs(el)
    if tag in {"rect", "image", "use", "svg"}:
        x = _num(attrs.get("x")) + tx
        y = _num(attrs.get("y")) + ty
        w = _num(attrs.get("width"))
        h = _num(attrs.get("height"))
        if w > 0 and h > 0:
            return BBox(x, y, w, h)
    if tag == "circle":
        cx = _num(attrs.get("cx")) + tx
        cy = _num(attrs.get("cy")) + ty
        r = _num(attrs.get("r"))
        if r > 0:
            return BBox(cx - r, cy - r, r * 2, r * 2)
    if tag == "ellipse":
        cx = _num(attrs.get("cx")) + tx
        cy = _num(attrs.get("cy")) + ty
        rx = _num(attrs.get("rx"))
        ry = _num(attrs.get("ry"))
        if rx > 0 and ry > 0:
            return BBox(cx - rx, cy - ry, rx * 2, ry * 2)
    if tag == "line":
        x1 = _num(attrs.get("x1")) + tx
        y1 = _num(attrs.get("y1")) + ty
        x2 = _num(attrs.get("x2")) + tx
        y2 = _num(attrs.get("y2")) + ty
        return BBox(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
    if tag == "text":
        x = _num(attrs.get("x")) + tx
        y = _num(attrs.get("y")) + ty
        font_size = _num(attrs.get("font-size"), 16.0)
        line_height = _num(attrs.get("data-line-height"), font_size * 1.25)
        lines = _text_lines(el)
        width = max((_visual_width(line, font_size) for line in lines), default=0.0)
        height = max(font_size, len(lines) * line_height)
        return BBox(x, y - font_size, width, height)
    return None


def _walk(el: ET.Element, tx: float = 0.0, ty: float = 0.0) -> Iterable[tuple[ET.Element, float, float]]:
    dx, dy = _translation(el.attrib.get("transform"))
    ntx = tx + dx
    nty = ty + dy
    yield el, ntx, nty
    for child in list(el):
        yield from _walk(child, ntx, nty)


def _viewbox(root: ET.Element) -> BBox:
    raw = root.attrib.get("viewBox", "")
    parts = [_num(part) for part in raw.split()]
    if len(parts) == 4 and parts[2] > 0 and parts[3] > 0:
        return BBox(parts[0], parts[1], parts[2], parts[3])
    return BBox(0, 0, _num(root.attrib.get("width"), 0), _num(root.attrib.get("height"), 0))


def _issue(level: str, issue_type: str, element: str, message: str, bbox: BBox | None = None) -> dict:
    payload = {
        "level": level,
        "type": issue_type,
        "element": element,
        "message": message,
    }
    if bbox:
        payload["bbox"] = {
            "x": round(bbox.x, 2),
            "y": round(bbox.y, 2),
            "w": round(bbox.w, 2),
            "h": round(bbox.h, 2),
        }
    return payload


def collect_boxes(svg_path: Path) -> tuple[BBox, list[ElementBox]]:
    root = ET.parse(svg_path).getroot()
    canvas = _viewbox(root)
    boxes: list[ElementBox] = []
    for index, (el, tx, ty) in enumerate(_walk(root)):
        tag = _strip_ns(el.tag)
        attrs = _attrs(el)
        if attrs.get("data-layout-ignore", "").lower() == "true":
            continue
        bbox = _bbox_for(el, tag, tx, ty)
        if not bbox or bbox.area <= 0:
            continue
        role = attrs.get("data-role", "").strip().lower()
        boxes.append(ElementBox(_label(attrs, tag, index), tag, role, bbox, attrs, _text_content(el)))
    return canvas, boxes


def audit_file(svg_file: str | Path) -> dict:
    svg_path = Path(svg_file)
    issues: list[dict] = []
    canvas, boxes = collect_boxes(svg_path)
    by_id = {box.label: box for box in boxes}

    for box in boxes:
        if box.tag == "svg":
            continue
        if not canvas.contains(box.bbox, tolerance=2.0):
            level = "error" if box.role and box.role not in IGNORE_ROLES else "warning"
            issues.append(_issue(
                level,
                "canvas_overflow",
                box.label,
                "element extends outside the SVG viewBox",
                box.bbox,
            ))

    for box in boxes:
        if box.tag != "text":
            continue
        max_lines = box.attrs.get("data-max-lines")
        if max_lines:
            line_count = len(_text_lines_from_box_text(box.text))
            if line_count > int(_num(max_lines)):
                issues.append(_issue(
                    "error",
                    "text_line_overflow",
                    box.label,
                    f"text has {line_count} lines, exceeds data-max-lines={max_lines}",
                    box.bbox,
                ))
        container_id = box.attrs.get("data-container")
        if container_id and container_id in by_id:
            padding = _num(box.attrs.get("data-safe-padding") or box.attrs.get("data-padding"), 8.0)
            container = by_id[container_id].bbox.padded(padding)
            if not container.contains(box.bbox, tolerance=2.0):
                issues.append(_issue(
                    "error",
                    "text_overflow",
                    box.label,
                    f"text bbox is outside data-container={container_id} after {padding:g}px padding",
                    box.bbox,
                ))

    _audit_overlaps(boxes, issues)
    _audit_tables(boxes, issues)

    errors = sum(1 for issue in issues if issue["level"] == "error")
    warnings = sum(1 for issue in issues if issue["level"] == "warning")
    return {
        "file": svg_path.name,
        "path": str(svg_path),
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
    }


def _text_lines_from_box_text(text: str) -> list[str]:
    return [part for part in re.split(r"\n+", text.strip()) if part.strip()] or [text]


def _audit_overlaps(boxes: list[ElementBox], issues: list[dict]) -> None:
    candidates = [
        box for box in boxes
        if box.tag != "svg"
        and box.bbox.area > 100
        and (box.role in MAJOR_ROLES or box.attrs.get("data-layout-check") == "true")
        and box.role not in IGNORE_ROLES
    ]
    for i, left in enumerate(candidates):
        for right in candidates[i + 1:]:
            if _is_expected_containment(left, right):
                continue
            inter = left.bbox.intersection_area(right.bbox)
            if inter <= 0:
                continue
            ratio = inter / max(1.0, min(left.bbox.area, right.bbox.area))
            if ratio < 0.08:
                continue
            issues.append(_issue(
                "warning",
                "possible_overlap",
                f"{left.label} / {right.label}",
                f"major layout boxes overlap by {ratio:.0%} of the smaller box",
            ))


def _is_expected_containment(left: ElementBox, right: ElementBox) -> bool:
    pairs = ((left, right), (right, left))
    for outer, inner in pairs:
        if inner.attrs.get("data-container") == outer.label:
            return True
        if outer.bbox.contains(inner.bbox, tolerance=2.0) and inner.role in {"text-block", "title", "kpi"}:
            return True
    if left.attrs.get("data-table-id") and left.attrs.get("data-table-id") == right.attrs.get("data-table-id"):
        return True
    return False


def _audit_tables(boxes: list[ElementBox], issues: list[dict]) -> None:
    table_groups: dict[str, list[ElementBox]] = {}
    for box in boxes:
        table_id = box.attrs.get("data-table-id")
        if not table_id:
            continue
        if box.attrs.get("data-row") is None or box.attrs.get("data-col") is None:
            continue
        table_groups.setdefault(table_id, []).append(box)

    for table_id, cells in table_groups.items():
        rows: dict[int, list[ElementBox]] = {}
        cols: dict[int, list[ElementBox]] = {}
        for cell in cells:
            rows.setdefault(int(_num(cell.attrs.get("data-row"))), []).append(cell)
            cols.setdefault(int(_num(cell.attrs.get("data-col"))), []).append(cell)
        for row, row_cells in rows.items():
            if _spread(cell.bbox.y for cell in row_cells) > 3 or _spread(cell.bbox.h for cell in row_cells) > 3:
                issues.append(_issue(
                    "error",
                    "table_row_misalignment",
                    f"{table_id}:row{row}",
                    "cells in the same row have mismatched y or height values",
                ))
        for col, col_cells in cols.items():
            if _spread(cell.bbox.x for cell in col_cells) > 3 or _spread(cell.bbox.w for cell in col_cells) > 3:
                issues.append(_issue(
                    "error",
                    "table_col_misalignment",
                    f"{table_id}:col{col}",
                    "cells in the same column have mismatched x or width values",
                ))


def _spread(values: Iterable[float]) -> float:
    nums = [v for v in values if not math.isnan(v)]
    if not nums:
        return 0.0
    return max(nums) - min(nums)


def audit_directory(target: str | Path) -> list[dict]:
    target_path = Path(target)
    if target_path.is_file():
        return [audit_file(target_path)]
    svg_dir = target_path / "svg_output" if (target_path / "svg_output").exists() else target_path
    return [audit_file(path) for path in sorted(svg_dir.glob("*.svg"))]


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit SVG geometry layout issues.")
    parser.add_argument("target", help="SVG file, svg_output directory, or presentation-studio project directory")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    reports = audit_directory(args.target)
    total_errors = sum(report["errors"] for report in reports)
    total_warnings = sum(report["warnings"] for report in reports)

    if args.json:
        print(json.dumps({"errors": total_errors, "warnings": total_warnings, "files": reports}, ensure_ascii=False, indent=2))
    else:
        print(f"[LAYOUT] files={len(reports)} errors={total_errors} warnings={total_warnings}")
        for report in reports:
            if not report["issues"]:
                continue
            print(f"\n{report['file']}")
            for issue in report["issues"]:
                print(f"  [{issue['level'].upper()}] {issue['type']}: {issue['element']} - {issue['message']}")

    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
