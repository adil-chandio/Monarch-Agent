# Script to Slides

You are converting a narration script into a structured slides JSON that the YT Video Factory pipeline can process.

## Input

A narration script (plain text) + video configuration:
- **style**: text-heavy | documentary | 3d-render | sketch | anime
- **title**: The video title
- **description**: YouTube description
- **tags**: YouTube tags

## Rules

### Slide Duration
- Each slide covers 3-4 seconds of voiceover (target ~8-10 words per slide at 2.5 words/sec)
- Split narration at sentence boundaries — never mid-sentence
- If a sentence is long (>12 words), it gets its own slide
- If two short sentences total <10 words, combine them into one slide

### Image Prompts — CRITICAL RULE

**The image MUST visually depict exactly what the narration is saying.**

This is the #1 rule. If the narration says "The Federal Reserve printed $120 billion," the image must show something directly related to money printing or the Federal Reserve — NOT a generic stock photo of a city skyline.

**Process for each slide:**
1. Read the narration text
2. Identify the KEY VISUAL SUBJECT — what is being talked about?
3. Build the image prompt around THAT specific subject
4. The viewer should be able to look at the image and guess what the narration says

**Bad example:**
- Narration: "Gold prices hit an all-time high of $3,200 per ounce."
- Bad prompt: "A wide 16:9 photograph of a beautiful sunset over mountains." (WRONG — has nothing to do with gold)
- Good prompt: "A wide 16:9 photorealistic cinematic photograph. Extreme close-up of gleaming gold bars stacked in a vault, warm golden light reflecting off polished surfaces. A digital price display showing rising numbers glows green in the background. Rich, luxurious atmosphere with shallow depth of field."

**Good examples of narration→image matching:**
- "Inflation is at 3.3%" → Show grocery prices, rising charts, expensive receipts
- "The housing market is struggling" → Show empty houses, for-sale signs, suburban streets
- "Oil prices are surging" → Show oil rigs, gas station prices, tanker ships
- "The stock market dropped 500 points" → Show red trading screens, Wall Street, worried traders
- "Your savings are losing value" → Show melting money, shrinking piggy bank, fading dollar bills

### Image Prompt Structure

**For "presentation" style (RECOMMENDED for text-heavy videos):**
- **STOP** — read `skills/presentation-slides.md` and follow its two-stage pipeline instead of the rules below
- Stage 1: Create a locked design system (5 colors, 3 motifs, typography, mood)
- Stage 2: Generate rich 4-8 sentence prompts with structured `on_screen_text` dicts
- This produces dramatically better results than the basic text-heavy approach

**For "text-heavy" style:**
- Start every prompt with: `"A wide 16:9 bold modern flat illustration."`
- Include a 5-color design system (pick once, use for all slides):
  - Background hex, Primary hex, Secondary hex, Accent hex, Text hex
- Reference EVERY hex by value in the prompt (e.g., `"#E94560"` not `"primary"`)
- Describe exact text placement: `"Large white (#FFFFFF) bold text reading 'THE FUTURE IS NOW' centered"`
- Include visual elements that support the text
- Add continuity references between slides

**For "dark-tech" style:**
- Start every prompt with: `"A wide 16:9 dark premium tech illustration."`
- Near-black background (`#0A0A0A` to `#1A1A2E`) with subtle glow effects
- One or two neon accent colors for highlights
- Clean sans-serif typography with wide letter-spacing
- Bake text into images (headlines, stats, callouts)
- Lots of negative space, minimal elements

**For "infographic" style:**
- Start every prompt with: `"A wide 16:9 clean modern infographic illustration."`
- Charts, graphs, data visualizations as main visual elements
- Large stat numbers displayed prominently
- Comparison layouts, ranked lists, timelines
- Bake text into images (labels, values, data points)

**For "whiteboard" style:**
- Start every prompt with: `"A wide 16:9 whiteboard explainer illustration."`
- White background with hand-drawn marker-style diagrams
- Arrows showing flow/process, handwritten annotations
- Simple palette: black lines + 2-3 marker colors
- Bake text into images (labels, annotations)

**For visual-only styles (documentary, 3d-render, sketch, anime, comic, stock):**
- Start every prompt with the style prefix from config
- Describe a vivid, cinematic scene that DIRECTLY illustrates what the narration says
- NO text, NO words, NO labels in the image
- Be SPECIFIC — name the exact objects, settings, and subjects from the narration
- Include camera angle, lighting, mood, and composition details
- Maintain visual continuity (consistent color palette, recurring motifs)

### Thumbnail Prompt
- Generate ONE attention-grabbing thumbnail prompt
- Must include the video title text baked in (large, bold, readable)
- Use contrasting colors, dramatic composition
- Single focal point + title text
- Resolution: 1280x720

### Narration
- Copy EXACTLY from the source script — do not rewrite
- Split at sentence boundaries only

## Output Format

Write the output as `slides.json` in the run directory. Exact structure:

```json
{
  "title": "The Video Title",
  "description": "YouTube video description (2-3 sentences)",
  "tags": ["tag1", "tag2", "tag3"],
  "style": "documentary",
  "design_system": {
    "background": "#0A0A0A",
    "primary": "#E94560",
    "secondary": "#1A1A2E",
    "accent": "#16213E",
    "text": "#FFFFFF"
  },
  "thumbnail_prompt": "A wide 16:9 dramatic thumbnail showing...",
  "slides": [
    {
      "slide_number": 1,
      "narration": "Gold prices hit an all-time high of $3,200 per ounce.",
      "image_prompt": "A wide 16:9 photorealistic cinematic photograph. Extreme close-up of gleaming gold bars stacked in a vault, warm golden light reflecting off polished surfaces. A digital price display showing rising numbers glows green in the background. Rich, luxurious atmosphere with shallow depth of field.",
      "duration": 4
    }
  ]
}
```

### Duration Calculation
For each slide: `duration = max(3, min(10, round(word_count / 2.5)))`

### Quality Checks Before Output
1. All narration segments concatenated = original script (no words added or lost)
2. Every slide has 3-10 second duration
3. Image prompts are 3-6 sentences each (detailed enough for good generation)
4. **EVERY image prompt directly depicts what the narration says** — go slide by slide and verify
5. Thumbnail prompt includes title text
6. design_system is included (even for non-text styles, for visual consistency)
7. No slide has more than ~25 words of narration (split if longer)
