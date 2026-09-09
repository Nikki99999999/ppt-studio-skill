#!/usr/bin/env python3
"""Validate Presentation Studio text artifacts as clean UTF-8 without BOM.

The checker is intentionally project-wide: SVG validation alone cannot protect
Markdown, JSON, speaker notes, prompts, or text reports from shell/locale
corruption.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path


TEXT_SUFFIXES = {
    ".svg", ".md", ".markdown", ".json", ".txt", ".xml",
    ".html", ".htm", ".csv", ".yaml", ".yml", ".css",
    ".py", ".js", ".cjs", ".ts", ".ps1", ".sh",
}
CJK_CONTENT_SUFFIXES = {
    ".svg", ".md", ".markdown", ".json", ".txt", ".xml",
    ".html", ".htm", ".csv", ".yaml", ".yml",
}
SKIP_DIRS = {".git", ".venv", "node_modules", "exports", "__pycache__"}
GENERATED_REPORT_NAMES = {"artifact_encoding_report.json"}
UTF8_BOM = b"\xef\xbb\xbf"

# High-signal fragments produced by common UTF-8 -> Latin-1/Windows-1252 or
# UTF-8 -> GBK mis-decoding. Keep this list conservative to avoid rejecting
# legitimate multilingual names.
MOJIBAKE_PATTERNS = {
    "latin1_utf8": re.compile(
        r"(?:\u00c3[\x80-\xBF]|\u00c2[\x80-\xBF]|"
        r"\u00e2(?:\u20ac|\u20ac\u2122|\u20ac\u0153|\u20ac\x9d|"
        r"\u20ac\u201c|\u20ac\u201d|\u20ac\u00a6)|\u00f0\u0178)"
    ),
    "common_gbk": re.compile(
        r"(?:\u6d93\ue15f\u6783|\u93c2\u56e7\u74e7|\u951f\u65a4\u62f7|"
        r"\u9286[\u5099\u509a]|\u9225[\u65ba]|\u9983[\u4e00-\u9fff])"
    ),
}


@dataclass
class Finding:
    path: str
    code: str
    message: str


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def _iter_text_files(root: Path):
    if root.is_file():
        if root.suffix.lower() in TEXT_SUFFIXES:
            yield root
        return

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.name in GENERATED_REPORT_NAMES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts[:-1]):
            continue
        yield path


def _is_chinese_project(root: Path) -> bool:
    manifest = root / "outline_manifest.json" if root.is_dir() else None
    if manifest and manifest.exists():
        try:
            data = json.loads(manifest.read_bytes().decode("utf-8-sig"))
            language = str(data.get("output_language", "")).lower()
            if language.startswith("zh"):
                return True
        except (UnicodeDecodeError, json.JSONDecodeError, OSError):
            pass
    return False


def check_file(path: Path, display_path: str, chinese_project: bool) -> list[Finding]:
    findings: list[Finding] = []
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return [Finding(display_path, "read_error", f"Cannot read file: {exc}")]

    if raw.startswith(UTF8_BOM):
        findings.append(Finding(display_path, "utf8_bom", "UTF-8 BOM is forbidden"))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        findings.append(
            Finding(
                display_path,
                "invalid_utf8",
                f"Strict UTF-8 decoding failed at byte {exc.start}: {exc.reason}",
            )
        )
        return findings

    embedded_bom_offset = 1 if text.startswith("\ufeff") else 0
    if "\ufeff" in text[embedded_bom_offset:]:
        findings.append(Finding(display_path, "embedded_bom", "Embedded U+FEFF detected"))
    if "\ufffd" in text:
        findings.append(Finding(display_path, "replacement_character", "U+FFFD replacement character detected"))
    if "\x00" in text:
        findings.append(Finding(display_path, "nul_character", "NUL character detected in text artifact"))

    private_use = sorted({ch for ch in text if unicodedata.category(ch) == "Co"})
    if private_use:
        sample = " ".join(f"U+{ord(ch):04X}" for ch in private_use[:5])
        findings.append(Finding(display_path, "private_use_character", f"Private-use character(s) detected: {sample}"))

    c1_controls = sorted({ord(ch) for ch in text if 0x80 <= ord(ch) <= 0x9F})
    if c1_controls:
        sample = " ".join(f"U+{value:04X}" for value in c1_controls[:5])
        findings.append(Finding(display_path, "c1_control", f"C1 control character(s) detected: {sample}"))

    for label, pattern in MOJIBAKE_PATTERNS.items():
        match = pattern.search(text)
        if match:
            findings.append(
                Finding(display_path, f"mojibake_{label}", f"Recognizable {label} mojibake pattern detected")
            )

    if chinese_project and path.suffix.lower() in CJK_CONTENT_SUFFIXES and re.search(r"\?{2,}", text):
        findings.append(
            Finding(display_path, "lossy_question_marks", "Repeated '?' detected in a zh-CN project; possible lossy CJK conversion")
        )

    return findings


def check_path(root: Path) -> tuple[list[Path], list[Finding]]:
    files = list(_iter_text_files(root))
    chinese_project = root.is_dir() and _is_chinese_project(root)
    findings: list[Finding] = []
    for path in files:
        display_path = str(path.relative_to(root)) if root.is_dir() else path.name
        findings.extend(check_file(path, display_path, chinese_project))
    return files, findings


def write_report(path: Path, root: Path, files: list[Path], findings: list[Finding]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "root": str(root.resolve()),
        "files_checked": len(files),
        "errors": len(findings),
        "passed": not findings,
        "findings": [asdict(item) for item in findings],
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    _configure_console()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Presentation project directory or one text artifact")
    parser.add_argument("--report", type=Path, help="Optional UTF-8 JSON report path")
    args = parser.parse_args()

    root = args.path.resolve()
    if not root.exists():
        print(f"[ERROR] Path does not exist: {root}", file=sys.stderr)
        return 2

    files, findings = check_path(root)
    if args.report:
        write_report(args.report.resolve(), root, files, findings)

    if not files:
        print(f"[ERROR] No supported text artifacts found under: {root}", file=sys.stderr)
        return 2

    for item in findings:
        print(f"[ERROR] {item.path}: {item.code}: {item.message}")

    if findings:
        print(f"Encoding check failed: {len(findings)} issue(s) in {len(files)} file(s).")
        return 1

    print(f"Encoding check passed: {len(files)} UTF-8 text artifact(s), no BOM or mojibake detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
