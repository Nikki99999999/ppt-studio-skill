# Content Quality Framework

This is the mandatory, reusable content-generation framework for every presentation project. It is not tied to any one demo deck. Read it during the Strategist phase before drafting the Ghost Deck, generating detailed content, or starting visual design.

## 1. Classify the scenario before generating content

Classify the presentation from audience, occasion, and narrative goal. Select one primary authority system; use a secondary system only for compatible checks.

| Scenario | Primary authority system | Content-generation contract |
|---|---|---|
| Decision, strategy, board, business review, community or commercial decision report | Barbara Minto's Pyramid Principle plus consulting practice | Conclusion first; Action Titles; MECE; Ghost Deck; evidence supports a decision |
| Speech, launch, public communication, video or conference presentation | Nancy Duarte plus Garr Reynolds' Presentation Zen | Story-driven sequence; 3-second Glance Test; restraint, simplicity, naturalness; sparse and visual |
| Fundraising, sales or business-development pitch | Guy Kawasaki's 10/20/30 | 10 core slides; 20 minutes; minimum 30-point type; appendix carries detail |

If the scenario is mixed:

1. Name one primary system in `outline_manifest.json`, then carry it unchanged into `content_manifest.json` after outline approval.
2. State why it matches the audience's decision or attention contract.
3. Record any secondary checks without importing conflicting density or pacing rules.
4. When uncertain, prioritize the audience's required action: decide, follow, or buy.

These systems are not interchangeable defaults. A visually attractive deck still fails if its content contract does not match the scenario.

## 2. Structure approval before detailed content and design

Use one user approval gate before production and one unified quality gate after production:

1. Draft `ghost_deck.md` in the confirmed output language with ordered Action Titles and one sentence per page.
2. Create `outline_manifest.json` from `templates/outline_manifest_reference.json`. Keep it structural: framework, narrative goal, Action Titles, single points, and high-level visual assumptions only.
3. Present the Ghost Deck directly to the user. Do not run a default outline checker or independent outline audit.
4. Record explicit approval in `<project_path>/outline_approval.md` and update `outline_manifest.json`.
5. Generate detailed audience-facing slide content only after approval. Create `content_manifest.json` from `templates/content_manifest_reference.json`, including body copy, claims, evidence, source mapping, and visible source footers.
6. Continue through visual design, image generation when selected, sequential SVG construction, and speaker notes.
7. At the final pre-export gate, run `scripts/content_quality_checker.py <project_path> --stage content`, `scripts/svg_quality_checker.py <project_path>`, and the template aesthetic checker when applicable.
8. Dispatch one read-only sub-agent audit that reviews content and visuals together. Fix every blocking finding, rerun affected checks, and repeat the audit after material changes.
9. If detailed content requires a material change to page order, Action Titles, or single points at any stage, return to step 1 and obtain approval again.

Allocate effort approximately 40% structure, 30% content, and 30% design. This is an effort guideline, not permission to generate detailed content before outline approval.

## 3. Conclusion-first hierarchy

For the whole deck:

```text
Conclusion or requested action
├── 3–5 supporting arguments
└── Evidence and sources for each argument
```

For decision decks, use SCQA when it improves the opening:

```text
Situation → Complication → Question → Answer
```

The content generator must distinguish facts, analysis, assumptions, and recommendations. It must not invent evidence to make a title sound decisive.

## 4. Action Title

Every non-structural page title states the page's conclusion. A topic label is insufficient.

- Weak: `Market overview`
- Strong: `Germany grows 12% annually, three times faster than the US`

Run the titles test: read only all slide titles in order. They must form a complete argument and make the requested decision, belief, or action obvious.

## 5. One page, one point

Each page records exactly one `single_point`. A title containing `and`, `&`, `和`, `与`, or `及` is a split-page warning unless it expresses one causal or comparative claim.

## 6. Signal over noise

- The page's main point must be understood within 3 seconds.
- Remove decorative elements that compete with the claim.
- Prefer restraint, simplicity, and naturalness.
- Public-speaking pages stay sparse and image-led; spoken explanation carries detail.
- Decision pages may be denser, but every element must prove the title.

## 7. Silent reading and humanized copy

A finished deck must work without a presenter. Speaker notes are a drafting source and delivery aid, not a substitute for audience-facing slide copy.

- Run a silent-reading test before final QA: a reader who only sees the slide pages must understand the deck's main advantages, claims, and requested action.
- Extract the strongest value sentences from speaker notes into the visible slide copy when the page would otherwise require oral explanation.
- Each substantive page should state the user-facing benefit of the mechanism, not only the mechanism label. For example, explain what `SVG → DrawingML → PPTX` gives the user: checkability, repeatable editing, and native PowerPoint editability.
- Keep boundary conditions and caveats in speaker notes, source footers, or README-style supporting text unless they are essential to the page's claim.
- Use speaker notes to add nuance, examples, and delivery rhythm. Do not let notes carry the only explanation of why the page matters.

Chinese copy must also pass a humanized-language review. Read `references/humanized-copy-review.md` for the concrete checklist adapted from Humanizer-zh: remove filler, break formulaic structures, vary rhythm, trust the reader, and preserve technical precision while removing AI-flavored phrasing.

## 8. Consistency creates trust

- Use at most two font families.
- Use a three-to-four-color palette.
- Use a stable alignment grid.
- Every page containing factual claims or data includes a visible `Source:` footer.
- The source footer maps to evidence in `content_manifest.json`.

## 9. Scenario-specific generation and acceptance rules

### Minto decision deck

- Open with the decision, recommendation, or answer.
- Build three to five mutually exclusive, collectively exhaustive supporting arguments when the material supports that structure.
- Use SCQA for the opening when it clarifies the tension.
- Write judgment-sentence Action Titles.
- Allow information density only when hierarchy remains clear.
- Acceptance: titles alone communicate the decision and reasoning chain.

### Duarte and Presentation Zen public presentation

- Build tension and resolution around the audience's desired change.
- Contrast what is with what could be when appropriate.
- Pass the 3-second Glance Test.
- Use large visuals and keep spoken detail out of the slide body.
- Apply restraint, simplicity, and naturalness.
- Acceptance: each page lands one emotional or intellectual beat immediately.

### Kawasaki pitch

- Use ten core slides.
- Design for a twenty-minute delivery target.
- Keep body type at 30 points or larger.
- Explain the problem, value, business logic, proof, team, and ask without reading a script.
- Put additional evidence in an appendix.
- Acceptance: the core story fits the constraints and leaves time for discussion.

## 10. Universal content-quality acceptance

- The pre-approval Ghost Deck passes the titles test and contains no unapproved detailed slide copy.
- The final outline is explicitly approved by the user before any visual design or slide construction starts.
- Detailed slide content is generated only after outline approval and remains aligned with the approved page order, Action Titles, and single points.
- Every non-structural page has an Action Title and one point.
- The final deck passes the silent-reading test: visible slide copy alone communicates the main advantages, claims, and requested action.
- Speaker notes and visible slide copy are aligned; any critical explanation in notes is either visible on the slide or deliberately retained as delivery-only nuance.
- Chinese copy has been reviewed for AI-flavored phrasing and revised into natural, specific language.
- Claims are supported by evidence or explicitly labeled as assumptions.
- Factual claims and data map to visible sources.
- The selected scenario framework's hard constraints pass.
- A read-only sub-agent independently audits the completed content and visual system together before export.

A strong deck lets the audience understand the requested decision by reading only the titles. Opening the body should mainly increase belief in those titles.
