# Frontend Slides Bold Pack - Design Specification

> PPT-safe translation layer for design-forward HTML slide aesthetics inspired by Frontend Slides.

## I. Template Overview

| Property | Description |
| --- | --- |
| **Template Name** | frontend_slides_bold |
| **Use Cases** | Creative business decks, AI and product storytelling, founder narratives, research readouts that need stronger visual taste |
| **Design Tone** | Editorial, design-led, confident, non-generic |
| **Theme Mode** | Mixed theme; selected visual direction determines light/dark balance |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| **Format** | Standard 16:9 |
| **Dimensions** | 1280 x 720 px |
| **viewBox** | `0 0 1280 720` |
| **Page Margins** | 56px left/right, 44px top/bottom |
| **Safe Area** | x: 56-1224, y: 44-676 |

## III. Color Scheme

| Role | Value | Usage |
| --- | --- | --- |
| **Paper** | `#F6F1E7` | Light editorial backgrounds |
| **Ink** | `#171717` | Primary text |
| **Night** | `#101521` | Dark cover and chapter backgrounds |
| **Cobalt** | `#245BFF` | High-contrast accent |
| **Signal Yellow** | `#E9FF36` | Small highlight and tags |
| **Coral** | `#FF6B4A` | Warm secondary accent |
| **Muted Line** | `#D8D0C2` | Grid, dividers, low-emphasis structure |

## IV. Typography System

| Role | Chinese | English | Fallback tail |
| --- | --- | --- | --- |
| **Title** | `"Microsoft YaHei"` | `Impact`, `"Arial Black"` | `sans-serif` |
| **Body** | `"Microsoft YaHei"` | `Arial` | `sans-serif` |
| **Emphasis** | `SimSun` | `Georgia` | `serif` |
| **Code** | - | `Consolas`, `"Courier New"` | `monospace` |

Per-role font stacks:

- Title: `Impact, "Arial Black", "Microsoft YaHei", sans-serif`
- Body: `"Microsoft YaHei", Arial, sans-serif`
- Emphasis: `Georgia, SimSun, serif`
- Code: `Consolas, "Courier New", monospace`

## V. Page Structure

- Header: compact eyebrow, section marker, or slide number.
- Content: asymmetrical by default; use cards only when parallel comparison is real.
- Footer: minimal source/page marker.
- `page_rhythm`: alternate `anchor`, `dense`, and `breathing` pages where content permits.

## VI. Page Types

- `01_cover.svg`: dark editorial cover with oversized typography and accent tags.
- `02_toc.svg`: structured agenda with editorial index blocks.
- `02_chapter.svg`: poster-like chapter divider.
- `03_content.svg`: flexible content scaffold with split and grid cues.
- `04_ending.svg`: quiet closing page with strong final message.

## VII. Layout Modes

| Mode | Use |
| --- | --- |
| **Anchor** | One idea, big type, strong whitespace |
| **Dense** | Data, comparison, structured analysis |
| **Breathing** | Chapter pause, quote, hero image, or emotional reset |

## VIII. Spacing Specification

| Element | Value |
| --- | --- |
| Safe margin | 56px |
| Section gap | 28-44px |
| Card padding | 24px |
| Card radius | 0-8px |
| Divider weight | 1-3px |

## IX. SVG Technical Constraints

Use inline SVG styles only. Do not use `script`, `style`, `class`, `foreignObject`, `mask`, text animation, CSS variables, or browser-only layout behavior.

## X. Placeholder Specification

Use canonical placeholders: `{{TITLE}}`, `{{SUBTITLE}}`, `{{DATE}}`, `{{AUTHOR}}`, `{{CHAPTER_NUM}}`, `{{CHAPTER_TITLE}}`, `{{PAGE_TITLE}}`, `{{CONTENT_AREA}}`, `{{PAGE_NUM}}`, `{{SOURCE}}`, `{{THANK_YOU}}`, `{{CONTACT_INFO}}`.

## XI. Usage Guide

Run `scripts/template_recommender.py` first. Use this template folder as the PPT-safe base, then encode the chosen Frontend Slides direction in the project `design_spec.md` and `spec_lock.md`.
