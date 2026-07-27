#!/usr/bin/env python3
"""Register validated, reusable customer templates in a private workspace library."""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILL_DIR = Path(__file__).resolve().parent.parent
LIBRARY_DIR = Path(
    os.environ.get(
        "PRESENTATION_STUDIO_CUSTOMER_LIBRARY",
        str(SKILL_DIR / "templates" / "customer_library"),
    )
).resolve()
INDEX_PATH = LIBRARY_DIR / "index.json"
REQUIRED_FILES = {
    "design_spec.md",
    "01_cover.svg",
    "02_chapter.svg",
    "03_content.svg",
    "04_ending.svg",
}
ALLOWED_TOP_LEVEL = REQUIRED_FILES | {
    "02_toc.svg",
    "tokens.json",
    "preview.png",
    "asset_manifest.json",
}
ALLOWED_ASSET_SUFFIXES = {".svg", ".png", ".jpg", ".jpeg", ".webp"}
DENIED_SUFFIXES = {".ppt", ".pptx", ".pdf", ".html", ".htm", ".zip", ".7z", ".rar"}
MAX_PACKAGE_FILE_BYTES = 20 * 1024 * 1024
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")


def sha256(path: Path | None) -> str | None:
    if path is None:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_index() -> dict:
    if not INDEX_PATH.exists():
        return {"schema_version": 1, "templates": {}}
    with INDEX_PATH.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def save_index(index: dict) -> None:
    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_validation_report(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"Validation report not found: {path}")
    with path.open("r", encoding="utf-8-sig") as handle:
        report = json.load(handle)
    if report.get("passed") is not True:
        raise SystemExit("Validation report must contain passed=true")
    if not str(report.get("validated_by", "")).strip():
        raise SystemExit("Validation report must name validated_by")
    required_checks = {"svg", "assets", "privacy", "license"}
    checks = set(report.get("checks", []))
    if not required_checks.issubset(checks):
        missing = ", ".join(sorted(required_checks - checks))
        raise SystemExit(f"Validation report is missing required checks: {missing}")
    return report


def lint_package(template_dir: Path) -> list[Path]:
    allowed_files: list[Path] = []
    for path in template_dir.rglob("*"):
        relative = path.relative_to(template_dir)
        if path.is_symlink():
            raise SystemExit(f"Template package must not contain symlinks: {relative}")
        if any(part.startswith(".") for part in relative.parts):
            raise SystemExit(f"Template package contains a hidden or Git file: {relative}")
        if path.is_dir():
            if relative.parts[0] != "assets":
                raise SystemExit(f"Unexpected directory in template package: {relative}")
            continue
        if path.stat().st_size > MAX_PACKAGE_FILE_BYTES:
            raise SystemExit(f"Template package file exceeds 20 MB: {relative}")
        if path.suffix.lower() in DENIED_SUFFIXES:
            raise SystemExit(f"Raw source/archive file is forbidden in template package: {relative}")
        if len(relative.parts) == 1:
            if relative.name not in ALLOWED_TOP_LEVEL:
                raise SystemExit(f"Unexpected top-level template file: {relative}")
        elif relative.parts[0] == "assets":
            if path.suffix.lower() not in ALLOWED_ASSET_SUFFIXES:
                raise SystemExit(f"Unsupported or sensitive asset type: {relative}")
        else:
            raise SystemExit(f"Unexpected nested template path: {relative}")
        allowed_files.append(path)
    return allowed_files


def register(args: argparse.Namespace) -> None:
    template_dir = args.template_dir.resolve()
    if not template_dir.is_dir():
        raise SystemExit(f"Template directory not found: {template_dir}")
    if not ID_RE.fullmatch(args.id):
        raise SystemExit("Template ID must use lowercase letters, digits, underscores, or hyphens")

    missing = sorted(name for name in REQUIRED_FILES if not (template_dir / name).exists())
    if missing:
        raise SystemExit(f"Template package is incomplete: {', '.join(missing)}")
    package_files = lint_package(template_dir)
    validation_report_path = args.validation_report.resolve()
    validation_report = load_validation_report(validation_report_path)

    source_file = args.source_file.resolve() if args.source_file else None
    if source_file and not source_file.is_file():
        raise SystemExit(f"Source file not found: {source_file}")
    source_hash = sha256(source_file)

    index = load_index()
    templates = index.setdefault("templates", {})
    for existing_id, metadata in templates.items():
        if (
            source_hash
            and metadata.get("source_sha256") == source_hash
            and metadata.get("validation_status") == "validated-before-registration"
            and metadata.get("visibility") == "private-workspace"
            and metadata.get("publish_approved") is False
        ):
            print(f"REUSED: source already registered as {existing_id}")
            return
    if args.id in templates or (LIBRARY_DIR / args.id).exists():
        raise SystemExit(f"Template ID already exists and will not be overwritten: {args.id}")

    destination = LIBRARY_DIR / args.id
    destination.mkdir(parents=True)
    for source in package_files:
        relative = source.relative_to(template_dir)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    imported_at = datetime.now(timezone.utc).isoformat()
    provenance = {
        "schema_version": 1,
        "template_id": args.id,
        "source_filename": source_file.name if source_file else None,
        "source_sha256": source_hash,
        "source_project": args.source_project,
        "imported_at": imported_at,
        "visibility": "private-workspace",
        "publish_approved": False,
        "validation_status": "validated-before-registration",
        "validated_by": validation_report["validated_by"],
        "validation_report_sha256": sha256(validation_report_path),
    }
    (destination / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    templates[args.id] = {
        "label": args.label,
        "summary": args.summary,
        "keywords": [item.strip() for item in args.keywords.split(",") if item.strip()],
        "path": f"templates/customer_library/{args.id}",
        "visibility": "private-workspace",
        "publish_approved": False,
        "source_sha256": source_hash,
        "imported_at": imported_at,
        "validation_status": "validated-before-registration",
    }
    save_index(index)
    print(f"REGISTERED: {args.id}")
    print(f"PATH: {destination}")


def list_templates(_: argparse.Namespace) -> None:
    index = load_index()
    for template_id, metadata in sorted(index.get("templates", {}).items()):
        print(f"{template_id}\t{metadata.get('label', '')}\t{metadata.get('visibility', '')}")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser("register")
    register_parser.add_argument("--template-dir", type=Path, required=True)
    register_parser.add_argument("--id", required=True)
    register_parser.add_argument("--label", required=True)
    register_parser.add_argument("--summary", required=True)
    register_parser.add_argument("--keywords", required=True)
    register_parser.add_argument("--source-file", type=Path)
    register_parser.add_argument("--source-project", default="")
    register_parser.add_argument("--validation-report", type=Path, required=True)
    register_parser.set_defaults(func=register)

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(func=list_templates)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
