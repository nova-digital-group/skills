# Prompting Gemini Image Models

The single most important principle from Google's guidance: **describe the
scene, don't list keywords.** A narrative paragraph that names the subject,
what it's doing, where it is, how it's framed, and the visual style beats a
comma salad of adjectives almost every time. More specific detail = more
control.

## Build the perfect prompt (checklist)

Work through these in order; each one you skip is a decision the model makes for
you. You rarely need all of them, but naming more = more control.

1. **Subject** — exactly what/who, with concrete attributes ("a weathered brass
   diving helmet," not "a helmet").
2. **Action / pose** — what it's doing or how it's arranged.
3. **Setting** — where, and what's around it.
4. **Composition & camera** — shot type, angle, lens (`85mm portrait`, `macro`,
   `low-angle wide`), depth of field.
5. **Lighting** — direction, quality, time of day (`golden-hour backlight`,
   `soft north-window light`, `harsh chiaroscuro`).
6. **Style / medium** — photoreal, 3D render, watercolor, isometric, film stock.
7. **Exact text** (if any) — in quotes, with the font feel.
8. **Intent** — what the image is *for* (hero banner, sticker, product page); it
   informs framing and negative space.

## The reliable structure

```
[Subject] + [Action/pose] + [Setting/context] + [Composition/framing] + [Style/medium] (+ [exact text in quotes])
```

**Example (text-to-image):**
> A striking fashion model wearing a tailored brown wool coat and structured
> handbag, posing with a confident, slightly-turned stance, against a seamless
> deep cherry-red studio backdrop. Medium-full shot, center-framed. Editorial
> fashion-magazine style, shot on medium-format analog film with pronounced
> grain, high saturation, and cinematic lighting.

## Six things that move quality the most

1. **Be hyper-specific.** "ornate elven plate armor etched with silver leaf, high collar, falcon-wing pauldrons" — not "fantasy armor."
2. **Give context/intent.** Say what the image is *for* (a hero banner, a sticker, a product page). It informs composition and negative space.
3. **Use positive framing.** Describe what should be present. There is **no negative-prompt parameter** — "a serene empty plaza at dawn," never "a plaza with no people."
4. **Control the camera.** Photographic vocabulary works: `wide-angle shot`, `macro shot`, `low-angle perspective`, `85mm portrait lens`, `Dutch angle`, `shallow depth of field (f/1.8)`.
5. **Specify lighting and material.** `three-point softbox setup`, `chiaroscuro with harsh high contrast`, `golden-hour backlight casting long shadows`; name materials ("navy-blue tweed," not "jacket fabric").
6. **Fix consistency by restarting.** If a character's features drift across edits, restart from a single detailed description (or supply character reference images) rather than patching.

## Templates

**Photorealistic shot**
> A photorealistic [shot type] of [subject], [action], set in [environment].
> Illuminated by [lighting], creating [mood]. Captured with [camera/lens],
> emphasizing [textures]. [aspect ratio].

**Product mockup**
> High-resolution, studio-lit product photograph of [product] on [surface].
> [Lighting setup]. [Camera angle]. Ultra-realistic, sharp focus on [detail].

**Logo / text-in-image** (always quote the exact words and name the font feel)
> Create a [logo/poster] for [brand] with the text "[EXACT TEXT]" in a [bold,
> white, sans-serif / elegant brush-script / Century Gothic] style. Design
> should be [aesthetic], with [color scheme].

**Sticker**
> A [style] sticker of [subject], featuring [traits] and [palette],
> [line/shading style]. Background must be white.

**Typography poster (text-as-window)**
> A typographic poster, solid black background, bold letters spelling "NEW YORK"
> filling the center. The text acts as a cut-out window — a photo of the New
> York skyline is visible ONLY inside the letterforms.

## Rendering text reliably

- Put the exact words **in quotes**.
- Name the font character ("heavy blocky Impact," "thin minimalist Century Gothic").
- **Text-first trick:** for text-heavy designs, first chat with the model to
  settle the wording, *then* ask it to render the image with that exact text.
  It produces far cleaner typography than asking for layout + copy in one shot.
- Pro (`gemini-3-pro-image`) handles dense/precise text and 4K layouts best.

## Editing an existing image

Provide the image as a part, then a direct instruction. Be explicit about what
should change and what must stay the same.

- *"Remove the man on the left; keep everything else identical."*
- *"Change the text in this infographic from English to Japanese; preserve the layout, colors, and fonts."*
- *"Relight this product shot as warm golden hour; keep the product unchanged."*

For iterative work, use a chat session and refine across turns:
*"Now make the background a touch darker"* → *"Add a soft rim light on the left."*

The single most effective edit clause is **"do not change anything else"** (or
"keep the layout, colors, and fonts identical") — it stops the model from
silently re-rendering the whole scene when you only wanted a local change.

## Grounded / factual images (Flash only)

For an infographic or map that must reflect real data, enable Search grounding
so the figures and facts come from the live web rather than the model's guess:

```python
config=types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],
    tools=[types.Tool(google_search=types.GoogleSearch())],
)
```

Combine with the **text-first trick**: settle the exact wording in a grounded
chat turn, *then* render it.

## Anti-patterns

- Listing disconnected keywords instead of describing a scene.
- Negative phrasing ("no cars," "without text") — describe the positive instead.
- Expecting a `seed` for reproducibility — not supported on these models.
- Cramming layout + exact copy into one prompt for text-heavy images — split it (text-first trick).
