"""Replace the repeated derived visuals with fresh distinct imagery.

Takes the newly generated images from assets/new-visuals/, crops them to the
site's target aspects, applies the site's cinematic grade (vignette + grain),
and overwrites assets/generated/<name>.jpg in place. Hero untouched.
"""
import glob
import math
import random
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "new-visuals"
OUT = ROOT / "assets" / "generated"

WIDE = (1800, 1125)
TALL = (1200, 1600)
SQUARE = (1400, 1400)

# (stem, output filename, target size)
JOBS = [
    ("attention-establishing", "attention-establishing.jpg", WIDE),
    ("macro-detail", "macro-detail.jpg", WIDE),
    ("book-spread-left", "book-spread-left.jpg", SQUARE),
    ("book-spread-right", "book-spread-right.jpg", SQUARE),
    ("montage-portrait", "montage-portrait.jpg", WIDE),
    ("montage-silver", "montage-silver.jpg", WIDE),
    ("method-silhouette", "method-silhouette.jpg", WIDE),
    ("service-brand", "service-brand.jpg", WIDE),
    ("service-content", "service-content.jpg", WIDE),
    ("service-digital", "service-digital.jpg", WIDE),
    ("service-growth", "service-growth.jpg", WIDE),
    ("studio-bts-a", "studio-bts-a.jpg", TALL),
    ("studio-bts-b", "studio-bts-b.jpg", TALL),
    ("cta-climax", "cta-climax.jpg", WIDE),
]


def cover(img, size):
    w, h = img.size
    tw, th = size
    factor = max(tw / w, th / h)
    nw, nh = int(w * factor), int(h * factor)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = int((nw - tw) * 0.5)
    y = int((nh - th) * 0.5)
    return resized.crop((x, y, x + tw, y + th))


def vignette(img, strength=0.72):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    px = mask.load()
    cx, cy = w / 2, h / 2
    maxd = math.hypot(cx, cy)
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / maxd
            px[x, y] = int(255 * min(1, max(0, (d - 0.18) / strength)))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(dark, img, mask.filter(ImageFilter.GaussianBlur(28)))


def grain(img, amount=16, opacity=0.12):
    random.seed(42)
    w, h = img.size
    noise = Image.new("L", (w, h))
    noise.putdata([random.randrange(0, amount) for _ in range(w * h)])
    noise = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, ImageEnhance.Contrast(noise).enhance(2.4), opacity)


for stem, filename, size in JOBS:
    matches = sorted(glob.glob(str(SRC / f"media-generation-{stem}-*.jpg")))
    # exclude the .json sidecars by construction (glob only .jpg)
    matches = [m for m in matches if not m.endswith(".json")]
    if not matches:
        raise SystemExit(f"missing source for {stem}")
    img = Image.open(matches[0]).convert("RGB")
    img = grain(vignette(cover(img, size)), opacity=0.12)
    dest = OUT / filename
    img.save(dest, quality=90, optimize=True)
    print(f"wrote {filename} ({img.size[0]}x{img.size[1]})")

print("done")
