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
import os
import sys

from google import genai
from google.genai import types

try:  # google.genai.errors is the canonical exception module
    from google.genai import errors as genai_errors
except ImportError:  # pragma: no cover - very old SDKs
    genai_errors = None

ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4",
                 "9:16", "16:9", "21:9", "1:4", "4:1", "1:8", "8:1"]
SIZES = ["512", "1K", "2K", "4K"]


def make_client() -> genai.Client:
    """Build a client, failing early with a clear message if no key is set.

    genai.Client() reads GEMINI_API_KEY or GOOGLE_API_KEY from the env. If both
    are set, GOOGLE_API_KEY silently wins — a real footgun when a stale
    GOOGLE_API_KEY shadows a fresh GEMINI_API_KEY, so we warn about it.
    """
    google_key = os.environ.get("GOOGLE_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not google_key and not gemini_key:
        sys.exit("error: no API key. Set GEMINI_API_KEY (or GOOGLE_API_KEY). "
                 "Get one at https://aistudio.google.com/apikey")
    if google_key and gemini_key:
        print("warning: both GOOGLE_API_KEY and GEMINI_API_KEY are set; "
              "GOOGLE_API_KEY takes precedence.", file=sys.stderr)
    # Built-in retry/backoff covers transient 429/5xx without extra code.
    # HttpRetryOptions was added in a newer SDK, so fall back if it's absent.
    try:
        return genai.Client(http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(attempts=5)))
    except (AttributeError, TypeError):
        return genai.Client()


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
    p.add_argument("--size", choices=SIZES, default=None,
                   help="Image size (uppercase K). Note: 512 is Flash-only.")
    p.add_argument("-i", "--image", action="append", default=[],
                   help="Input image(s) for editing/composition/reference. Repeatable.")
    args = p.parse_args()

    client = make_client()

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
        # Both modalities are required — dropping "TEXT" is the #1 cause of a
        # 200 response that contains no image part.
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(**image_cfg) if image_cfg else None,
    )

    try:
        response = client.models.generate_content(
            model=args.model, contents=contents, config=config,
        )
    except Exception as e:  # noqa: BLE001 - surface a clean message, not a traceback
        if genai_errors and isinstance(e, genai_errors.APIError):
            print(f"error: API call failed ({getattr(e, 'code', '?')}): "
                  f"{getattr(e, 'message', e)}", file=sys.stderr)
            return 1
        raise

    saved = False
    for part in response.candidates[0].content.parts:
        if getattr(part, "thought", False):
            continue  # skip interim "thought" images; final render is the last image part
        if getattr(part, "text", None):
            print(part.text)
        elif getattr(part, "inline_data", None):
            part.as_image().save(args.output)
            print(f"Saved image to {args.output}")
            saved = True

    if not saved:
        # Distinguish a safety block from a plain empty response so the user
        # knows whether to rephrase or to debug their request.
        cand = response.candidates[0] if response.candidates else None
        finish = getattr(cand, "finish_reason", None)
        feedback = getattr(response, "prompt_feedback", None)
        detail = ""
        if feedback and getattr(feedback, "block_reason", None):
            detail = f" Prompt was blocked: {feedback.block_reason}."
        elif finish and str(finish) not in ("FinishReason.STOP", "STOP"):
            detail = f" finish_reason={finish}."
        print("error: no image was returned (it may have been blocked by safety "
              f"filters, or the model returned only text).{detail}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
