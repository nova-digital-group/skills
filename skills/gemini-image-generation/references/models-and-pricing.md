# Gemini Image Models — Catalog, Pricing & Limits

> Researched 2026-06-14 from the official docs. Model ids, pricing, and limits
> change frequently — verify against
> https://ai.google.dev/gemini-api/docs/image-generation,
> https://ai.google.dev/gemini-api/docs/models, and
> https://ai.google.dev/gemini-api/docs/pricing before relying on exact numbers.

## Model ids

| Marketing name | Model id (GA/stable) | Role |
|----------------|----------------------|------|
| **Nano Banana 2** | `gemini-3.1-flash-image` | High-efficiency, production-scale, fast. **Default choice.** |
| **Nano Banana Pro** | `gemini-3-pro-image` | Reasoning core, studio-quality 4K, complex layouts, precise text. |
| Nano Banana (original) | `gemini-2.5-flash-image` | Legacy. |
| Imagen 4 / Fast / Ultra | `imagen-4.0-generate-001`, `imagen-4.0-fast-generate-001`, `imagen-4.0-ultra-generate-001` | Separate dedicated text-to-image API (not the Gemini multimodal path). Good when you want a fixed price-per-image and `number_of_images` 1–4. |

**Imagen uses a different method**, not `generate_content`:

```python
resp = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt="...",
    config=types.GenerateImagesConfig(
        number_of_images=4,            # 1–4
        aspect_ratio="16:9",           # 1:1, 3:4, 4:3, 9:16, 16:9
        image_size="2K",               # 1K or 2K
        person_generation="allow_adult",  # dont_allow / allow_adult / allow_all
    ),
)
for i, gi in enumerate(resp.generated_images):
    gi.image.save(f"out_{i}.png")
```

Imagen **does** support `negative_prompt` and `seed` (the Gemini image models do
not). Billing is flat per image (see pricing below), not per output token.

Both Gemini image models went GA on 2026-05-28; the corresponding
`-preview` aliases (`gemini-3.1-flash-image-preview`, `gemini-3-pro-image-preview`)
were scheduled to sunset 2026-06-25. **Use the non-preview ids.**

If an id stops working, enumerate current models:

```python
for m in client.models.list():
    print(m.name, m.supported_actions)
```

## Capabilities

- **Generation and editing** in the same `generateContent` call (no separate edit endpoint).
- **Reference / character images** — pass image parts before the text instruction. Limits (total ~14): Flash ≈ 10 objects + 4 character refs; Pro ≈ 6 objects + 5 character refs.
- **Text in images** — legible, stylized text for infographics/menus/logos; Pro is best for dense/precise text and 4K layouts.
- **Grounding** — image generation can use Google Search as a tool: `tools=[types.Tool(google_search=types.GoogleSearch())]`, useful for factual infographics.
- **Multi-turn editing** — via `client.chats.create(...)`; Pro preserves visual context across turns ("thought signatures").
- **Video-to-image** — `gemini-3.1-flash-image` can take video context (YouTube URL or Files API upload) as input.
- **SynthID watermark** — always embedded, non-removable.

## Input / output formats

- Input image MIME types: `image/png`, `image/jpeg`, `image/webp`, `image/heic` (PNG/JPEG most common).
- Output: PNG by default, or per `output_mime_type`.
- Pass input images as `types.Part.from_bytes(data=..., mime_type=...)` or `types.Part.from_uri(file_uri=..., mime_type=...)` (e.g. a `gs://` URI or a File API reference).

## Configuration (`types.ImageConfig` inside `GenerateContentConfig`)

| Field | Values |
|-------|--------|
| `aspect_ratio` | `1:1 2:3 3:2 3:4 4:3 4:5 5:4 9:16 16:9 21:9` and banners `1:4 4:1 1:8 8:1` |
| `image_size` | `512` (**Flash only**), `1K`, `2K`, `4K` (uppercase `K`; lowercase is ignored) |
| `output_mime_type` | `image/png`, `image/jpeg` |

Also on `GenerateContentConfig`:
- `response_modalities=["TEXT", "IMAGE"]` (required to get an image back).
- `thinking_config=types.ThinkingConfig(thinking_level="high", include_thoughts=True)` — the model may produce up to two interim images while composing; thinking tokens are always billed. Skip parts where `part.thought` is true.

**Not supported:** negative prompts, seeds, a `number_of_images`/`candidateCount`
knob (that belongs to the separate Imagen API). One image per call.

> Known quirk: some early `gemini-3.1-flash-image-preview` builds reportedly
> ignored `aspect_ratio`/`image_size` on certain edits. If a size constraint
> seems ignored on an edit, re-issue as a fresh generation or restate the
> dimensions in the prompt.

## Pricing (per image, as of June 2026)

Image output is billed per output token (~10× the text rate); a single image is
a fixed token count by resolution. Approximate per-image cost:

**`gemini-3.1-flash-image` (Nano Banana 2)** — image output at $60 / 1M tokens:

| Resolution | ≈ Price/image |
|-----------|---------------|
| 0.5K (512) | $0.045 |
| 1K | $0.067 |
| 2K | $0.101 |
| 4K | $0.151 |

**`gemini-3-pro-image` (Nano Banana Pro)** — image output at $120 / 1M tokens:

| Resolution | ≈ Price/image |
|-----------|---------------|
| 1K / 2K | $0.134 |
| 4K | $0.24 |

Text/thinking output billed separately ($3/1M Flash, $12/1M Pro). Image input
≈ 560 tokens (~$0.001). A 50% Batch API discount is available. **Imagen 4**:
Fast $0.02, Standard $0.04, Ultra $0.06 per image.

> Treat the per-image dollar figures as approximate (derived from token counts);
> the authoritative source is the pricing page.

## Rate limits

Per-model RPM/TPM/RPD numbers are no longer published in the docs — they depend
on your usage tier and are shown in Google AI Studio
(https://aistudio.google.com/rate-limit). Tiers escalate with cumulative spend:
Free → Tier 1 (billing linked) → Tier 2 ($100+ & 3 days) → Tier 3 ($1,000+ & 30 days).
