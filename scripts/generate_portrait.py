#!/usr/bin/env python3
"""
Generate a self-typing ASCII portrait SVG from a photo.
Usage: python3 generate_portrait.py <input.jpg> <output.svg>
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
import cv2

RAMP = " .`:-=+*cs#%@"
COLS = 90
CHAR_W = 7.74
FONT_SIZE = 12.9
LINE_H = 12.9
FILL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"


def remove_background(img: Image.Image) -> Image.Image:
    """Background removal. Prefers rembg; falls back to OpenCV GrabCut (no model download)."""
    try:
        from rembg import remove
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        out = remove(buf.getvalue())
        result = Image.open(io.BytesIO(out)).convert("RGBA")
        white = Image.new("RGBA", result.size, (255, 255, 255, 255))
        white.paste(result, mask=result.split()[3])
        return white.convert("RGB")
    except ImportError:
        print("info: rembg not available, using GrabCut fallback", file=sys.stderr)
        return grabcut_background(img)


def grabcut_background(img: Image.Image) -> Image.Image:
    """Soft elliptical vignette mask. Reliable for a centered head-and-shoulders
    crop without depending on background texture (GrabCut fails on textured walls
    or foliage near the subject)."""
    arr = np.array(img.convert("RGB")).astype(np.float32)
    h, w = arr.shape[:2]

    cy, cx = h * 0.44, w * 0.5   # face/shoulders center, slightly above vertical middle
    ry, rx = h * 0.62, w * 0.56  # ellipse radii - generous enough to keep shoulders

    yy, xx = np.mgrid[0:h, 0:w]
    dist = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2

    # smooth falloff: 1 inside, 0 outside, soft transition band
    inner, outer = 0.75, 1.15
    mask = np.clip((outer - np.sqrt(dist)) / (outer - inner), 0, 1)
    mask = cv2.GaussianBlur(mask.astype(np.float32), (31, 31), 0)

    white_bg = np.full_like(arr, 255.0)
    mask3 = mask[:, :, None]
    out = arr * mask3 + white_bg * (1 - mask3)
    return Image.fromarray(out.astype(np.uint8))


def process_image(path: str, cols: int = COLS):
    img = Image.open(path)
    img = remove_background(img)

    arr = np.array(img.convert("L"))

    # bilateral filter: smooth skin, keep edges
    arr = cv2.bilateralFilter(arr, d=9, sigmaColor=75, sigmaSpace=75)

    # CLAHE local contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    arr = clahe.apply(arr)

    # darkening curve (v/255)^1.7
    arr = arr.astype(np.float64) / 255.0
    arr = np.power(arr, 1.7)
    arr = (arr * 255.0).astype(np.uint8)

    h, w = arr.shape
    rows = max(1, round(cols * (h / w) * 0.48))

    small = cv2.resize(arr, (cols, rows), interpolation=cv2.INTER_AREA)
    return small


def to_ascii_rows(pixels: np.ndarray) -> list[str]:
    n = len(RAMP) - 1
    lines = []
    for row in pixels:
        chars = []
        for v in row:
            idx = int(round((v / 255.0) * n))
            chars.append(RAMP[idx])
        lines.append("".join(chars))
    return lines


def build_svg(rows: list[str]) -> str:
    n_rows = len(rows)
    n_cols = len(rows[0]) if rows else 0
    width = round(n_cols * CHAR_W) + 20
    height = round(n_rows * LINE_H) + 20

    defs = (
        "\n  <defs>\n    <style>\n"
        "      .row { font-family: 'JetBrains Mono', 'Liberation Mono', "
        "'DejaVu Sans Mono', monospace;\n"
        f"             font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; white-space: pre; }}\n"
        "    </style>\n  </defs>"
    )

    body = []
    for i, row in enumerate(rows):
        y = 10 + (i + 1) * LINE_H
        row_w = round(len(row) * CHAR_W)
        clip_id = f"clip{i}"
        begin = round(i * 0.09, 2)
        dur = 0.5
        escaped = (
            row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        body.append(f"""
  <clipPath id="{clip_id}">
    <rect x="10" y="{y - LINE_H}" width="0" height="{LINE_H + 4}">
      <animate attributeName="width" from="0" to="{row_w}" begin="{begin}s" dur="{dur}s" fill="freeze" />
    </rect>
  </clipPath>
  <text x="10" y="{y}" class="row" clip-path="url(#{clip_id})">{escaped}</text>
  <rect x="10" y="{y - LINE_H + 2}" width="{CHAR_W}" height="{LINE_H}" fill="{FILL_COLOR}">
    <animate attributeName="x" from="10" to="{10 + row_w}" begin="{begin}s" dur="{dur}s" fill="freeze" />
    <set attributeName="opacity" to="0" begin="{begin + dur}s" fill="freeze" />
  </rect>""")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="{BG_COLOR}" />{defs}
{''.join(body)}
</svg>"""
    return svg


def main():
    if len(sys.argv) != 3:
        print("usage: generate_portrait.py <input.jpg> <output.svg>", file=sys.stderr)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    pixels = process_image(src)
    rows = to_ascii_rows(pixels)
    svg = build_svg(rows)
    with open(dst, "w") as f:
        f.write(svg)
    print(f"wrote {dst} ({len(rows)} rows x {len(rows[0]) if rows else 0} cols)")


if __name__ == "__main__":
    main()
