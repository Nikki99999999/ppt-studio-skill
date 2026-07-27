#!/usr/bin/env python3
"""Recommend a PPT visual production strategy from audience and narrative goals."""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent
    / "templates"
    / "image_models"
    / "model_catalog.json"
)


def _terms(*values: str) -> str:
    return " ".join(value or "" for value in values).lower()


def recommend(audience: str, goal: str, brief: str, delivery: str) -> dict:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        catalog = json.load(handle)

    items = {item["id"]: item for item in catalog["strategies"]}
    text = _terms(audience, goal, brief, delivery)
    scores = {key: 0 for key in items}
    reasons = {key: [] for key in items}

    def add(strategy: str, points: int, reason: str) -> None:
        scores[strategy] += points
        reasons[strategy].append(reason)

    if any(term in text for term in ("管理层", "董事会", "汇报", "数据", "流程", "架构", "咨询", "internal", "executive", "board", "data", "process", "architecture")):
        add("svg", 7, "受众重视结构、数据和可编辑性")
    if any(term in text for term in ("公众", "客户", "营销", "品牌", "发布", "故事", "情绪", "public", "client", "marketing", "brand", "launch", "story")):
        add("image-2-web", 6, "叙事需要高质感主视觉和情绪表达")
    if any(term in text for term in ("信息图", "知识", "教育", "文字", "多语言", "infographic", "knowledge", "education", "text", "multilingual")):
        add("nano-banana-pro-web", 7, "内容需要文字、知识和信息图表达")
        add("seedream-5-pro-web", 6, "内容适合高密度信息图或多语言画面")
    if any(term in text for term in ("中文", "商业", "电商", "海报", "storyboard", "chinese", "commercial", "poster")):
        add("seedream-5-pro-web", 6, "内容偏中文商业视觉或故事板")
    if any(term in text for term in ("视频", "动态", "片头", "展会", "舞台", "motion", "video", "opener", "event")):
        add("seedance-2-web", 8, "交付目标明确包含动态叙事")
    if any(term in text for term in ("草稿", "快速", "低成本", "draft", "fast", "quick", "low cost")):
        add("host-native", 5, "当前优先速度和探索")

    if max(scores.values()) == 0:
        add("svg", 4, "默认优先稳定、可编辑和可控")
        add("image-2-web", 3, "可为封面或章节页补充高质感主视觉")

    ranked = sorted(items, key=lambda key: (-scores[key], key))
    primary = ranked[0]

    if primary == "svg" and scores["image-2-web"] >= 4:
        recommendation = {
            "id": "hybrid",
            "strategy": "hybrid",
            "selected_model": "image-2",
            "route": "web",
            "label": "Hybrid: SVG + ChatGPT Images 2.0",
            "reason": "主体页面用 SVG 保证信息清晰与可编辑，封面和关键章节页用高级模型增强视觉冲击。"
        }
    else:
        recommendation = {
            "id": primary,
            "strategy": (
                "advanced-web"
                if items[primary]["tier"] == "advanced"
                else primary
            ),
            "selected_model": {
                "image-2-web": "image-2",
                "nano-banana-pro-web": "nano-banana-pro",
                "seedream-5-pro-web": "seedream-5-pro",
                "seedance-2-web": "seedance-2"
            }.get(primary, "host-selected" if primary == "host-native" else "none"),
            "route": items[primary]["route"],
            "label": items[primary]["label"],
            "reason": "；".join(reasons[primary]) or "与当前受众和叙事目标最匹配。"
        }

    alternatives = []
    for key in ranked:
        if key == primary:
            continue
        alternatives.append(
            {
                "id": key,
                "label": items[key]["label"],
                "tier": items[key]["tier"],
                "reason": "；".join(reasons[key]) or "可作为成本、速度或媒介形态不同的替代方案。"
            }
        )
        if len(alternatives) == len(items) - 1:
            break

    return {
        "inputs": {
            "audience": audience,
            "narrative_goal": goal,
            "brief": brief,
            "delivery": delivery
        },
        "recommended": recommendation,
        "alternatives": alternatives,
        "selection_required": True,
        "advanced_model_policy": "When a named advanced model is selected, use only its verified web route. Do not silently switch models.",
        "catalog_updated": catalog["updated"]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audience", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--brief", default="")
    parser.add_argument("--delivery", default="pptx")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = recommend(args.audience, args.goal, args.brief, args.delivery)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"Recommended: {result['recommended']['label']}")
    print(f"Reason: {result['recommended']['reason']}")
    print("Alternatives:")
    for item in result["alternatives"]:
        print(f"- {item['label']} [{item['tier']}]: {item['reason']}")


if __name__ == "__main__":
    main()
