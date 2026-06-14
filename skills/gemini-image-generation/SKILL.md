---
name: gemini-image-generation
description: >-
  Generate and edit images with the Google Gemini API using Nano Banana 2
  (gemini-3.1-flash-image) or Nano Banana Pro (gemini-3-pro-image). Use this
  whenever the user wants to create, generate, edit, restyle, composite, or
  upscale images through the Gemini / Google AI API with an API key — including
  text-to-image, image editing/inpainting, multi-image composition, character
  or product consistency across shots, infographics, logos, mockups, or
  rendering legible text inside an image. Trigger on mentions of "Nano Banana",
  "Gemini image", "generate/make an image with Gemini", or Google image
  generation, even if the exact model id is not named.
license: MIT
---

# Gemini Image Generation (Nano Banana 2 / Pro)

Generate and edit images with Google's Gemini image models. These are
multimodal models called through the standard `generateContent` method — the
image comes back as **base64 inline data inside a response part**, not from a
dedicated image endpoint.

## Setup

```bash
pip install google-genai pillow
export GEMINI_API_KEY="your-key"   # or GOOGLE_API_KEY
```

The SDK reads the key from the environment, so `genai.Client()` needs no
arguments. The older `google-generativeai` package is deprecated — use
`google-genai`.

## Choose the model

| Need | Model id | Notes |
|------|----------|-------|
| Fast, high-volume, most jobs (**default**) | `gemini-3.1-flash-image` | "Nano Banana 2". GA/stable. |
| 4K, dense/precise text, complex layouts, studio quality | `gemini-3-pro-image` | "Nano Banana Pro". GA/stable, ~2× the price. |
| Legacy | `gemini-2.5-flash-image` | The original "Nano Banana". |

Use the **non-`-preview`** ids in production — the `-preview` aliases are being
retired. If an id ever 404s, list what's available with
`client.models.list()` and check https://ai.google.dev/gemini-api/docs/models.

## Fastest path: use the bundled script

For one-off generation or editing, `scripts/generate_image.py` already handles
the request shape, config, and saving the bytes. Read it before reinventing it.

```bash
# Text to image
python scripts/generate_image.py "a photorealistic bowl of ramen, steam rising, moody side light" -o ramen.png

# With size + aspect ratio
python scripts/generate_image.py "minimalist mountain logo, flat vector" --aspect-ratio 1:1 --size 2K -o logo.png

# Edit / compose: pass one or more input images (edit, restyle, or combine)
python scripts/generate_image.py "place this product on a sunlit marble countertop" -i product.png -o scene.png

# Use the higher-quality model for text-heavy work
python scripts/generate_image.py "an infographic titled 'Q3 RESULTS' with three labeled bars" -m gemini-3-pro-image --size 4K -o chart.png
```

## Minimal code (when you need to embed it)

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-flash-image",
    contents=["A red panda barista pulling an espresso shot, warm cafe lighting"],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K"),
    ),
)

for part in response.candidates[0].content.parts:
    if getattr(part, "thought", False):
        continue                       # skip interim reasoning parts
    if part.text:
        print(part.text)
    elif part.inline_data:
        part.as_image().save("output.png")   # as_image() returns a PIL image
```

**Editing** works the same way — put the input image part(s) *before* the text
instruction in `contents`:

```python
contents=[
    types.Part.from_bytes(data=open("photo.png", "rb").read(), mime_type="image/png"),
    "Remove the parked cars and make it a quiet empty street at dawn.",
]
```

## Key parameters (`types.ImageConfig`)

- `aspect_ratio` — one of `"1:1" "2:3" "3:2" "3:4" "4:3" "4:5" "5:4" "9:16" "16:9" "21:9"` (plus banner ratios `1:4 4:1 1:8 8:1`).
- `image_size` — `"512"`, `"1K"`, `"2K"`, `"4K"`. The `K` **must be uppercase**.
- `output_mime_type` — e.g. `"image/png"` or `"image/jpeg"`.

Set `response_modalities=["TEXT", "IMAGE"]` on `GenerateContentConfig`.

## What works and what to expect

- **Reference images:** up to ~14 total (Flash: ~10 objects + 4 character refs; Pro: ~6 objects + 5 character refs). Use character refs for consistency across shots.
- **Text rendering:** strong, especially on Pro. For text-heavy images, the
  docs' best trick is to *first* ask the model to draft the wording in chat,
  *then* ask it to render the image with that exact text.
- **Multi-turn editing:** use `client.chats.create(...)` and send follow-up
  instructions to refine an image conversationally.
- **No negative prompts and no seed.** These image models don't support either.
  Describe what you *do* want (positive framing) — say "an empty street" rather
  than "a street with no cars."
- **SynthID watermark** is always embedded and cannot be removed.
- Single image returned per call; loop the parts to find it.

## Prompting essentials

Describe a *scene*, don't list keywords. The reliable structure is:
**Subject + Action + Setting + Composition + Style (+ exact text in quotes)**.

Read `references/prompting.md` for the full guide, templates (photoreal,
product, logo, sticker, infographic, typography), and editing patterns.

## More detail

- `references/models-and-pricing.md` — model catalog, per-image pricing, limits, rate-limit notes.
- `references/prompting.md` — prompt engineering: scene description, camera/lens vocabulary, text-in-image, editing, character consistency.
