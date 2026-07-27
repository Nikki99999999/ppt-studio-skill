#!/usr/bin/env python3
"""Recommend Presentation Studio templates, including Frontend Slides visual directions."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "templates" / "frontend_slides" / "design_catalog.json"
LAYOUT_INDEX = ROOT / "templates" / "layouts" / "layouts_index.json"
CUSTOMER_INDEX = Path(
    os.environ.get(
        "PRESENTATION_STUDIO_CUSTOMER_INDEX",
        str(ROOT / "templates" / "customer_library" / "index.json"),
    )
).resolve()

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


WEIGHTS = {
    "scenario": 4,
    "audience": 3,
    "tone": 3,
    "density": 2,
    "scheme": 1,
}

DENSITY_ORDER = {"low": 0, "medium-low": 1, "medium": 2, "medium-high": 3, "high": 4}
FORMALITY_ORDER = {"low": 0, "medium-low": 1, "medium": 2, "medium-high": 3, "high": 4}

SCENARIO_TERMS = {
    "finance": {"finance", "investor", "investment", "board", "bank", "fund", "financing", "strategy"},
    "tech": {"ai", "agent", "developer", "api", "product", "saas", "technical", "architecture", "launch"},
    "research": {"research", "academic", "policy", "white paper", "thesis", "survey", "synthesis"},
    "creative": {"brand", "creative", "design", "agency", "portfolio", "manifesto", "fashion", "culture"},
    "training": {"training", "workshop", "course", "education", "tutorial", "learning"},
    "government": {"government", "public", "policy", "party", "state-owned", "regulation"},
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9][a-z0-9+-]*", value.lower()))


def normalize_density(value: str) -> str:
    value = value.lower()
    if "medium-high" in value or "medium high" in value:
        return "medium-high"
    if "medium-low" in value or "medium low" in value:
        return "medium-low"
    if any(item in value for item in ("dense", "data", "table", "report", "high")):
        return "high"
    if any(item in value for item in ("keynote", "story", "visual", "low", "poster")):
        return "low"
    return "medium"


def normalize_formality(value: str) -> str:
    value = value.lower()
    if "medium-high" in value or "medium high" in value:
        return "medium-high"
    if "medium-low" in value or "medium low" in value:
        return "medium-low"
    if any(item in value for item in ("board", "executive", "government", "academic", "policy", "formal", "investor")):
        return "high"
    if any(item in value for item in ("community", "creator", "workshop", "playful", "casual")):
        return "low"
    return "medium"


def normalize_scheme(value: str) -> str | None:
    value = value.lower()
    if "dark" in value:
        return "dark"
    if "light" in value:
        return "light"
    return None


def infer_scenarios(text: str) -> set[str]:
    tokens = tokenize(text)
    matched: set[str] = set()
    for scenario, terms in SCENARIO_TERMS.items():
        if tokens.intersection(terms) or any(term in text.lower() for term in terms if " " in term):
            matched.add(scenario)
    return matched


def ordinal_match_score(value: str, target: str, order: dict[str, int]) -> int:
    if value not in order or target not in order:
        return 1 if value == target or "medium" in (value, target) else 0
    distance = abs(order[value] - order[target])
    if distance == 0:
        return 2
    if distance == 1:
        return 1
    return 0


def score_template(item: dict[str, Any], query: str, density: str, formality: str, scheme: str | None) -> tuple[int, list[str]]:
    haystack = " ".join(
        [
            item.get("slug", ""),
            item.get("name", ""),
            item.get("best_for", ""),
            item.get("avoid_for", ""),
            " ".join(item.get("mood", [])),
        ]
    ).lower()
    query_tokens = tokenize(query)
    score = 0
    reasons: list[str] = []

    for scenario in infer_scenarios(query):
        if scenario in haystack:
            score += WEIGHTS["scenario"]
            reasons.append(f"scenario:{scenario}")

    overlap = query_tokens.intersection(tokenize(haystack))
    if overlap:
        score += min(6, len(overlap))
        reasons.append("keyword:" + ",".join(sorted(list(overlap))[:4]))

    item_density = item.get("density", "medium")
    density_points = ordinal_match_score(item_density, density, DENSITY_ORDER)
    if density_points == 2:
        score += WEIGHTS["density"]
        reasons.append(f"density:{density}")
    elif density_points == 1:
        score += 1

    item_formality = item.get("formality", "medium")
    formality_points = ordinal_match_score(item_formality, formality, FORMALITY_ORDER)
    if formality_points == 2:
        score += WEIGHTS["audience"]
        reasons.append(f"formality:{formality}")
    elif formality_points == 1:
        score += 1

    if scheme and item.get("scheme") == scheme:
        score += WEIGHTS["scheme"]
        reasons.append(f"scheme:{scheme}")

    avoid_tokens = tokenize(item.get("avoid_for", ""))
    if query_tokens.intersection(avoid_tokens):
        score -= 3
        reasons.append("avoid-overlap")

    return score, reasons


def recommend(args: argparse.Namespace) -> dict[str, Any]:
    catalog = load_json(CATALOG)
    query = " ".join(part for part in [args.brief, args.audience, args.tone, args.density, args.scheme] if part)
    density = normalize_density(" ".join([args.density or "", args.brief or ""]))
    formality = normalize_formality(" ".join([args.audience or "", args.tone or "", args.brief or ""]))
    scheme = normalize_scheme(args.scheme or args.tone or args.brief or "")

    candidates: list[dict[str, Any]] = []
    for source_name in ("safe_presets", "bold_templates"):
        for item in catalog[source_name]:
            score, reasons = score_template(item, query, density, formality, scheme)
            candidates.append(
                {
                    "source": source_name,
                    "slug": item["slug"],
                    "name": item["name"],
                    "score": score,
                    "scheme": item.get("scheme"),
                    "formality": item.get("formality"),
                    "density": item.get("density"),
                    "mood": item.get("mood", []),
                    "best_for": item.get("best_for", ""),
                    "avoid_for": item.get("avoid_for", ""),
                    "reasons": reasons,
                }
            )

    if CUSTOMER_INDEX.exists():
        private_index = load_json(CUSTOMER_INDEX)
        for template_id, metadata in private_index.get("templates", {}).items():
            if (
                metadata.get("visibility") != "private-workspace"
                or metadata.get("publish_approved") is not False
                or metadata.get("validation_status") != "validated-before-registration"
            ):
                continue
            item = {
                "slug": template_id,
                "name": metadata.get("label", template_id),
                "best_for": " ".join(
                    [
                        metadata.get("summary", ""),
                        " ".join(metadata.get("keywords", [])),
                    ]
                ),
                "avoid_for": "",
                "mood": metadata.get("keywords", []),
                "density": metadata.get("density", "medium"),
                "formality": metadata.get("formality", "medium"),
                "scheme": metadata.get("scheme"),
            }
            score, reasons = score_template(item, query, density, formality, scheme)
            candidates.append(
                {
                    "source": "customer_private",
                    "slug": template_id,
                    "name": metadata.get("label", template_id),
                    "score": score + 1,
                    "scheme": item["scheme"],
                    "formality": item["formality"],
                    "density": item["density"],
                    "mood": item["mood"],
                    "best_for": item["best_for"],
                    "avoid_for": "",
                    "reasons": ["workspace-private"] + reasons,
                    "path": metadata.get("path"),
                }
            )

    candidates.sort(key=lambda item: (-item["score"], item["source"], item["slug"]))
    return {
        "query": {
            "brief": args.brief,
            "audience": args.audience,
            "tone": args.tone,
            "density": density,
            "scheme": scheme,
            "formality": formality,
        },
        "recommendations": candidates[: args.top],
        "fallback_template": "frontend_slides_bold",
        "note": "Use the selected visual direction as design language; copy templates/layouts/frontend_slides_bold for Presentation Studio SVG placeholders.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend PPT template directions from a brief.")
    parser.add_argument("brief", help="Deck brief or source summary")
    parser.add_argument("--audience", default="", help="Target audience")
    parser.add_argument("--tone", default="", help="Desired tone")
    parser.add_argument("--density", default="", help="Expected content density")
    parser.add_argument("--scheme", default="", help="light/dark/mixed preference")
    parser.add_argument("--top", type=int, default=3, help="Number of recommendations")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    result = recommend(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print("Template recommendations:")
    for idx, item in enumerate(result["recommendations"], 1):
        print(f"{idx}. {item['name']} ({item['slug']}) score={item['score']}")
        print(f"   mood={', '.join(item['mood'])}; density={item['density']}; formality={item['formality']}; scheme={item['scheme']}")
        print(f"   best_for={item['best_for']}")
        print(f"   reasons={', '.join(item['reasons']) or 'general fallback'}")
    print(f"Fallback Presentation Studio template: {result['fallback_template']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
