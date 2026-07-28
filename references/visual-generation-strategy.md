# Visual Generation Strategy

Use this reference during the Strategist confirmation and Image_Generator phases.

## 1. Recommend before asking

Run:

```bash
python3 scripts/image_strategy_recommender.py \
  --audience "<audience>" \
  --goal "<narrative goal>" \
  --brief "<content summary>" \
  --delivery "<pptx|pptx+video>" \
  --json
```

Present one recommended strategy, its reason, and the available alternatives. The user must confirm the visual production strategy before the Design Specification is written.

The strategy question is required for every deck unless the user has already selected a route. Recommend from the audience and narrative goal, then let the user confirm: pure SVG, host-native image tool, one named advanced web model, or hybrid. A host-native tool with an undisclosed model identity is a separate choice; it never satisfies a named advanced-model requirement.

## 2. User-facing choices

| Choice | Use when | Execution |
|---|---|---|
| SVG design | Data, processes, architecture, consulting, editable diagrams | Build locally as PPT-safe SVG |
| Host-native image tool | Drafts, decorative assets, speed-first work where the exact model is not required | Use the current host tool; label the model as `host-selected/unspecified` |
| ChatGPT Images 2.0 | Cinematic hero images, photorealism, editing, precise instruction following | Open `https://chatgpt.com/images` and verify Images 2.0 before submission |
| Nano Banana Pro | Text-rich visuals, infographics, multilingual or knowledge-heavy images | Open `https://gemini.google.com/` and verify `Nano Banana Pro / Gemini 3 Pro Image` before submission |
| Seedream 5.0 Pro | Dense infographics, Chinese commercial visuals, storyboards, controlled editing | Open `https://dreamina.capcut.com/seedream/seedream-5-0-pro` and verify `Seedream 5.0 Pro` before submission |
| Seedance 2.0 | Motion-led openings, event or product-launch sequences | Open `https://dreamina.capcut.com/tools/seedance-2-0` and verify `Seedance 2.0` before submission |
| Hybrid | Most audience-facing decks | Use SVG for information-bearing pages and one selected advanced model only for specified hero assets |

Read `templates/image_models/model_catalog.json` as the machine-readable source. Keep model names and web entries there, not in ad hoc prompts.

## 3. Selection rules

1. Treat the user's choice as a lock. Record `strategy`, `selected_model`, `route`, and `model_verification` in `spec_lock.md`.
2. If the user chooses a named advanced model, open only that model's web route. Verify the exact model identity in the page UI before submitting a prompt.
3. If the UI defaults to a different model, stop before submission and ask the user to select the required model or approve a different strategy.
4. Never describe a host-native result as Image 2.0, Nano Banana Pro, Seedream, or Seedance unless the tool result explicitly attests that identity.
5. A hybrid plan may mix SVG with one named advanced model. Mixing multiple paid or advanced models requires explicit user approval.
6. Seedance is a video model. For standard PPTX delivery, save the video as a companion asset and use a selected keyframe in the slide. Do not claim the PPTX embeds video unless the export pipeline verifies that it does.
7. If the current host offers image generation, record it as `host-native` unless the host exposes an exact model attestation. Do not infer Image 2.0 from the host name, UI surface, or visual quality.

## 4. Web automation contract

- Submit each filename once.
- Poll visible job state every 20-30 seconds.
- Stop automation after 5 minutes with no completed asset.
- Keep the tab and status sidecar available for human inspection.
- Do not refresh, resubmit, duplicate the prompt, change models, or start another generation for the same filename.
- Mark the resource `Needs-Manual` with the selected model, web route, elapsed time, and last visible status.

## 4.1 Hybrid parallel split

When the confirmed strategy is `hybrid`, the main agent MAY split image preparation into two helper sub-agents after `images/image_prompts.md` exists and `spec_lock.md` has locked the selected model:

| Helper | Scope | Required output | Forbidden |
|---|---|---|---|
| Advanced Web Image Agent | Named web-model raster assets such as Image 2.0, Nano Banana Pro, Seedream, or Seedance keyframes | Final image files in `images/` and one status sidecar per asset | Refreshing, resubmitting, changing model, changing prompt meaning, generating local fallbacks |
| SVG Asset Draft Agent | Local editable visual components for information-bearing pages | Component drafts under `svg_assets/drafts/` plus short usage notes | Creating final page SVGs, changing page titles, changing `spec_lock.md`, exporting PPTX |

The split is only for asset preparation. The main agent owns final page composition: it must read `spec_lock.md` before every page and integrate raster assets and SVG component drafts into `svg_output/` sequentially. If a helper output conflicts with the approved outline, selected model, or visual lock, discard or revise it in the main-agent context before page generation.

## 5. Resource-level routing

Each generated resource records:

```yaml
visual_strategy: svg | host-native | advanced-web | hybrid
selected_model: none | host-selected | image-2 | nano-banana-pro | seedream-5-pro | seedance-2
route: local-svg | host-native | web
web_entry: none | https://...
model_verification: not-required | explicit-ui | rejected-unknown
fallback_policy: none-without-user-approval
watchdog_seconds: 300
poll_interval_seconds: 25
```

The Image Resource List adds `Model` and `Route` columns. Motion assets also add `Media` with `video` or `keyframe`.
