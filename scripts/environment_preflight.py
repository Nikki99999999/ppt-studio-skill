#!/usr/bin/env python3
"""Resolve and validate Presentation Studio's runtime without fixed host paths."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parent.parent
REQUIREMENTS_FILE = REPO_ROOT / "requirements.txt"
MIN_PYTHON = (3, 10)

PHASE_MODULES: dict[str, tuple[tuple[str, str], ...]] = {
    "core": (),
    "pdf": (("fitz", "PyMuPDF"),),
    "docx": (("mammoth", "mammoth"),),
    "html": (("markdownify", "markdownify"), ("bs4", "beautifulsoup4")),
    "epub": (("ebooklib", "ebooklib"), ("markdownify", "markdownify")),
    "ipynb": (("nbconvert", "nbconvert"),),
    "pptx-source": (("pptx", "python-pptx"),),
    "web": (("requests", "requests"), ("bs4", "beautifulsoup4")),
    "production": (("PIL", "Pillow"), ("pptx", "python-pptx")),
    "image-gemini": (("PIL", "Pillow"), ("google.genai", "google-genai")),
    "image-openai": (("PIL", "Pillow"), ("openai", "openai")),
}

CORE_SCRIPTS = (
    "project_manager.py",
    "artifact_encoding_checker.py",
    "content_quality_checker.py",
    "svg_quality_checker.py",
    "finalize_svg.py",
    "svg_to_pptx.py",
)


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _renderer_available() -> tuple[bool, str]:
    if _module_available("cairosvg"):
        return True, "cairosvg"
    if _module_available("svglib") and _module_available("reportlab"):
        return True, "svglib + reportlab"
    return False, "cairosvg OR svglib + reportlab"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=(*PHASE_MODULES, "all"), default="core")
    parser.add_argument("--project-path", type=Path)
    parser.add_argument(
        "--require-compat-renderer",
        action="store_true",
        help="Fail when neither CairoSVG nor svglib+reportlab is available",
    )
    args = parser.parse_args()

    phases = tuple(PHASE_MODULES) if args.phase == "all" else (args.phase,)
    errors: list[str] = []
    warnings: list[str] = []

    if sys.version_info < MIN_PYTHON:
        errors.append(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required; found {sys.version.split()[0]}")

    if not SKILL_DIR.is_dir():
        errors.append(f"Resolved SKILL_DIR does not exist: {SKILL_DIR}")
    for script_name in CORE_SCRIPTS:
        if not (SKILL_DIR / "scripts" / script_name).is_file():
            errors.append(f"Required script missing: {SKILL_DIR / 'scripts' / script_name}")
    if not REQUIREMENTS_FILE.is_file():
        warnings.append(f"requirements.txt not found at resolved repository root: {REQUIREMENTS_FILE}")

    if args.project_path:
        project_path = args.project_path.resolve()
        if not project_path.is_dir():
            errors.append(f"Project path is not an existing directory: {project_path}")

    required: dict[str, str] = {}
    for phase in phases:
        for module_name, package_name in PHASE_MODULES[phase]:
            required[module_name] = package_name
    missing_packages = sorted({package for module, package in required.items() if not _module_available(module)})
    if missing_packages:
        errors.append("Missing Python package(s): " + ", ".join(missing_packages))

    renderer = "not checked"
    if "production" in phases:
        renderer_ok, renderer = _renderer_available()
        if not renderer_ok:
            message = (
                "PNG compatibility renderer unavailable; native editable PPTX export still works, "
                "but the SVG compatibility variant will not contain a PNG fallback"
            )
            if args.require_compat_renderer:
                errors.append(message)
            else:
                warnings.append(message)

    if "web" in phases and not _module_available("curl_cffi"):
        warnings.append("curl_cffi is unavailable; TLS-sensitive sites may require the documented Node.js fallback")
    if any(phase in phases for phase in ("docx", "html", "epub", "ipynb")) and not shutil.which("pandoc"):
        warnings.append("pandoc is unavailable; only native document formats for the selected phase are supported")

    print(f"Python executable: {Path(sys.executable).resolve()}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Working directory: {Path.cwd().resolve()}")
    print(f"Resolved SKILL_DIR: {SKILL_DIR}")
    print(f"Resolved repository root: {REPO_ROOT}")
    print(f"Phase: {args.phase}")
    if "production" in phases:
        print(f"PNG renderer: {renderer}")
    for warning in warnings:
        print(f"[WARN] {warning}")
    for error in errors:
        print(f"[ERROR] {error}", file=sys.stderr)

    if errors:
        if REQUIREMENTS_FILE.is_file():
            print(f"Install hint: {sys.executable} -m pip install -r {REQUIREMENTS_FILE}", file=sys.stderr)
        return 1

    print("Environment preflight passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
