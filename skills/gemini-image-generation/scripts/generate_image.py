#!/usr/bin/env python3
"""Generate or edit images with the Google Gemini API (Nano Banana 2 / Pro).

The Gemini image models are multimodal: you call the standard generate_content
method and the image comes back as base64 inline data inside a response part.
This script handles the request shape, optional size/aspect-ratio config,
reference/edit images, and saving the result.

Requires: pip install google-genai pillow
Auth:     export GEMINI_API_KEY=...   (or GOOGLE_API_KEY)

Examples:
    # text to image
    generate_image.py "a watercolor fox in a snowy forest" -o fox.png

    # size + aspect ratio
    generate_image.py "flat-vector mountain logo" --aspect-ratio 1:1 --size 2K -o logo.png

    # edit / compose: pass one or more input images
    generate_image.py "put this product on a sunlit marble counter" -i product.png -o scene.png

    # higher-quality model for text-heavy work
    generate_image.py "infographic titled 'Q3 RESULTS'" -m gemini-3-pro-image --size 4K -o chart.png
"""
import argparse
import mimetypes
import sys

from google import genai
from google.genai import types

ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4",
                 "9:16", "16:9", "21:9", "1:4", "4:1", "1:8", "8:1"]
SIZES = ["512", "1K", "2K", "4K"]


def guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "image/png"


def main() -> int:
    p = argparse.ArgumentParser(description="Generate or edit images with Gemini.")
    p.add_argument("prompt", help="What to generate, or the edit instruction when -i is given.")
    p.add_argument("-o", "--output", default="output.png", help="Output file path (default: output.png).")
    p.add_argument("-m", "--model", default="gemini-3.1-flash-image",
                   help="Model id (default: gemini-3.1-flash-image / Nano Banana 2). "
                        "Use gemini-3-pro-image for 4K / dense text.")
    p.add_argument("--aspect-ratio", choices=ASPECT_RATIOS, default=None)
    p.add_argument("--size", choices=SIZES, default=None, help="Image size (uppercase K).")
    p.add_argument("-i", "--image", action="append", default=[],
                   help="Input image(s) for editing/composition/reference. Repeatable.")
    args = p.parse_args()

    client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY

    # Input images come first, then the text instruction.
    contents = []
    for path in args.image:
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError as e:
            print(f"error: cannot read input image {path}: {e}", file=sys.stderr)
            return 2
        contents.append(types.Part.from_bytes(data=data, mime_type=guess_mime(path)))
    contents.append(args.prompt)

    image_cfg = {}
    if args.aspect_ratio:
        image_cfg["aspect_ratio"] = args.aspect_ratio
    if args.size:
        image_cfg["image_size"] = args.size

    config = types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(**image_cfg) if image_cfg else None,
    )

    response = client.models.generate_content(
        model=args.model, contents=contents, config=config,
    )

    saved = False
    for part in response.candidates[0].content.parts:
        if getattr(part, "thought", False):
            continue  # skip interim reasoning/thought parts
        if getattr(part, "text", None):
            print(part.text)
        elif getattr(part, "inline_data", None):
            part.as_image().save(args.output)
            print(f"Saved image to {args.output}")
            saved = True

    if not saved:
        print("error: no image was returned (it may have been blocked by safety "
              "filters, or the model returned only text).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
