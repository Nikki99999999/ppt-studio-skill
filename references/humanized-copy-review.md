# Humanized Copy Review for Chinese Decks

Use this reference during detailed content writing and the final independent audit when the deck output language is Chinese. It adapts the Humanizer-zh approach to presentation copy.

Source: `op7418/Humanizer-zh` (`SKILL.md`) on GitHub. The original skill is a Chinese text-editing skill for identifying and removing AI writing traces.

## Core editing principles

Apply these checks to visible slide copy and speaker notes:

1. Remove filler phrases. Cut connective padding, generic openings, and emphasis crutches that do not carry meaning.
2. Break formulaic structures. Avoid mechanical binary contrast, dramatic setup, and repetitive rhetorical framing.
3. Vary rhythm. Mix short claims with longer explanatory sentences; avoid identical sentence lengths and repeated three-part lists.
4. Trust the reader. State facts and conclusions directly without excessive hand-holding, hedging, or apologetic framing.
5. Remove quotable-sounding slogans when they replace substance. Keep a strong claim only when it is backed by specific evidence or a concrete mechanism.

This review is a release gate for Chinese decks. If a phrase is flagged as AI-flavored, rewrite it before export unless the project records a concrete reason for keeping it. A self-review may draft fixes, but the required final independent audit must check the visible slide copy and speaker notes again.

## Common AI-flavored patterns to flag

Flag and rewrite these patterns when they appear in Chinese presentation copy:

- Inflated significance: "标志着", "体现/证明", "关键时刻", "更广泛趋势", "持续/深远影响" without concrete evidence.
- Marketing blur: "无缝", "直观", "强大", "充满活力", "开创性", "令人叹为观止", "必游/必看", "深刻".
- Vague authority: "行业专家认为", "多个来源显示", "观察者指出" without a named source.
- AI connective habits: "此外", "值得注意的是", "在这个背景下", "从……到……" when they add no information.
- Negative parallelism: "不仅……而且……", "不只是/不仅仅是……而是……", "不是……而是……" when used as a stock contrast. Prefer a direct positive statement of what the system does and why it matters.
- Three-item completeness theater: forced "A、B、C" lists that sound comprehensive but do not improve the argument.
- Overuse of dashes, bold emphasis, emoji markers, and inline heading lists.
- Generic positive conclusions: "未来可期", "迈向新阶段", "持续追求卓越" without a specific next action or measurable outcome.

## Deck-specific adaptation

Presentation copy is not an essay. Do not make every sentence conversational. The goal is concise, natural, decision-useful Chinese.

- Prefer concrete mechanisms and outcomes: "先生成 SVG，再编译为 PowerPoint 原生对象，可检查、可修改、可继续编辑."
- Keep technical terms when they improve precision; explain them once in Chinese when the audience may not know them.
- A page can use fragments and labels, but the main claim must still read like a human wrote it.
- Speaker notes may be warmer and more spoken. Visible slide copy should be direct and compact.
- If notes contain the clearest explanation of value, extract that value sentence into the page body.

## Review score

Use this 50-point review during final audit:

| Dimension | 10-point target |
|---|---|
| Directness | States the claim without circling around it |
| Rhythm | Uses varied sentence lengths and avoids mechanical repetition |
| Reader trust | Respects the reader; avoids over-explaining obvious logic |
| Authenticity | Sounds like a real editor wrote it for this audience |
| Concision | Removes filler while preserving evidence and precision |

Acceptance guidance:

- 45-50: ready.
- 35-44: acceptable only after fixing obvious flagged phrases.
- Below 35: revise visible copy before export.

For release, target 45+ for Chinese decks. Scores below 45 require revision or an explicit exception recorded in `content_manifest.json`.
