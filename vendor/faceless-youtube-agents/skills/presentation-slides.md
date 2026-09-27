# Presentation Slides — Enhanced Text-Heavy Style

You are converting a narration script into presentation-quality slides using a **two-stage pipeline** adapted from the idea-to-presentation engine. This produces dramatically better text-heavy slides than generic image prompts.

## When to Use

Use this skill instead of the default `script-to-slides.md` when the style is `presentation`.

## Two-Stage Pipeline

### Stage 1: Design System + Outline

Before generating any slide prompts, create a locked design system:

```json
{
  "design_system": {
    "style_description": "1-2 sentences describing the visual approach",
    "color_palette": {
      "background": "#hex",
      "primary": "#hex",
      "secondary": "#hex",
      "accent": "#hex",
      "text": "#hex"
    },
    "visual_motifs": ["motif1", "motif2", "motif3"],
    "typography_style": "heading and body text style description",
    "mood": "2-4 words"
  }
}
```

**Rules for the design system:**
- Choose 5 hex colors that match the topic's mood and energy
- Pick 3 visual motifs that will recur across all slides for continuity
- Define typography (e.g., "bold condensed uppercase headings, clean sans-serif body")
- Lock this in — every slide references these exact hex values

### Stage 2: Generate Slides with Rich Prompts

For each slide, produce three components:

#### Image Prompt (4-8 sentences, MUST include ALL of these):

1. `"A wide 16:9 [mood] presentation slide."` — always start with this
2. **Background**: exact treatment using design system hex codes by VALUE (write `"#1A1A2E"` not `"background color"`)
3. **Foreground elements**: what objects, icons, diagrams, charts appear and WHERE
4. **On-screen text**: every piece of text that appears, in quotes, with exact placement and styling:
   - Placement: top-left, top-center, top-right, center, bottom-left, bottom-center, bottom-right
   - Styling: font weight, relative size, color hex
5. **Style details**: texture, gradients, effects, shadows
6. **Mood and lighting**: atmosphere consistent with the design system
7. **Continuity**: reference visual elements from the previous slide

#### On-Screen Text (structured dict):

```json
{
  "headline": "The main title text",
  "subtitle": "Secondary text",
  "bullet_points": ["Point 1", "Point 2", "Point 3"],
  "stat": "87%",
  "callout": "Key insight highlighted",
  "footnote": "Source: Example 2026"
}
```

Use as many keys as the slide needs. Common keys:
- `headline` — main title
- `subtitle` — secondary title
- `body` — paragraph text
- `bullet_points` — array of bullet items
- `stat` — a key number or metric (displayed large and bold)
- `callout` — highlighted aside or tip
- `diagram_labels` — array of labels for visual elements
- `code_snippet` — code shown on screen
- `footnote` — small attribution or source

#### Narration

The voiceover script for this slide. MUST:
- Match the slide duration at ~2.5 words/second
- NEVER just read the on-screen text — add depth, context, or narrative
- Flow naturally from the previous slide

### Adaptive Complexity by Content Type

Adjust the visual approach based on what's being explained:

| Content Type | Visual Approach |
|---|---|
| Educational / How-to | Labeled diagrams, step-by-step visual flows, numbered processes, arrows connecting concepts |
| Statistics / Data | Large stat hero numbers, minimal bar/pie charts, before/after comparisons |
| Listicle / Tips | Clean numbered items, icon + text pairs, card layouts |
| Storytelling / History | Timeline layouts, key moment snapshots, quote cards |
| Comparison | Split-screen layouts, vs. cards, feature grids |
| Technical | Architecture diagrams, flowcharts, code snippets with syntax highlighting |

### Example Image Prompt (Presentation Style)

> A wide 16:9 bold modern presentation slide. Deep #0D1117 background with subtle diagonal gradient from #0D1117 to #161B22. Top-left: small category label "STEP 3" in uppercase #58A6FF with letter-spacing. Center-left: large bold headline reading "Automate Your Workflow" in white #F0F6FC, condensed sans-serif. Below the headline: three bullet points with #58A6FF circle icons, each line in #8B949E reading "Connect your data sources", "Set trigger conditions", "Deploy in one click". Right side: a clean flat illustration of interconnected nodes and arrows in #58A6FF and #238636 on a dark card with #21262D background and subtle border. Bottom-right corner: small "3/10" slide counter in muted #484F58. Consistent geometric line pattern from previous slides visible in top-right corner.

## Output Format

Same `slides.json` structure as `script-to-slides.md`, but with the addition of `on_screen_text` and `design_system`:

```json
{
  "title": "Video Title",
  "description": "YouTube description",
  "tags": ["tag1", "tag2"],
  "style": "presentation",
  "design_system": {
    "style_description": "...",
    "color_palette": {
      "background": "#hex",
      "primary": "#hex",
      "secondary": "#hex",
      "accent": "#hex",
      "text": "#hex"
    },
    "visual_motifs": ["...", "...", "..."],
    "typography_style": "...",
    "mood": "..."
  },
  "thumbnail_prompt": "...",
  "slides": [
    {
      "slide_number": 1,
      "narration": "...",
      "image_prompt": "A wide 16:9 bold modern presentation slide. Deep #0D1117 background...",
      "on_screen_text": {
        "headline": "...",
        "subtitle": "...",
        "bullet_points": ["...", "..."]
      },
      "duration": 5
    }
  ]
}
```

## Quality Checks

1. Every image prompt references at least 3 hex codes from the design system
2. Every image prompt includes ALL on-screen text with placement and styling
3. On-screen text dict matches what's described in the image prompt
4. Narration word count ≈ duration × 2.5 (±5 words)
5. First slide sets the visual tone — describe the style fully
6. Visual motifs appear in at least 50% of slides
7. No two consecutive slides have the same layout structure
