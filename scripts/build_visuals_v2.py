"""Build the v2 visual set for the ORCHI MEDIA cinematic rebuild.

Takes fresh generated images from assets/new-visuals/, crops to target
aspects, applies the cinematic grade (vignette + grain), writes to
assets/generated/<name>.jpg. Removes superseded v1 files. Hero untouched.
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

JOBS = [
    ("philosophy-portrait", "philosophy-portrait.jpg", WIDE),
    ("detail-eye", "detail-eye.jpg", WIDE),
    ("craft-bts", "craft-bts.jpg", WIDE),
    ("work-spread-left", "work-spread-left.jpg", SQUARE),
    ("work-spread-right", "work-spread-right.jpg", SQUARE),
    ("campaign-car", "campaign-car.jpg", WIDE),
    ("perspective-brutal", "perspective-brutal.jpg", WIDE),
    ("panel-brand", "panel-brand.jpg", TALL),
    ("panel-content", "panel-content.jpg", TALL),
    ("panel-digital", "panel-digital.jpg", TALL),
    ("panel-growth", "panel-growth.jpg", TALL),
    ("manifesto-portrait", "manifesto-portrait.jpg", WIDE),
    ("studio-set", "studio-set.jpg", WIDE),
    ("studio-edit", "studio-edit.jpg", WIDE),
    ("cta-city", "cta-city.jpg", WIDE),
]

# v1 files superseded by the rebuild (hero sources never touched)
REMOVE = [
    "attention-establishing.jpg",
    "macro-detail.jpg",
    "book-spread-left.jpg",
    "book-spread-right.jpg",
    "service-brand.jpg",
    "service-content.jpg",
    "service-digital.jpg",
    "service-growth.jpg",
    "cta-climax.jpg",
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
    matches = [m for m in sorted(glob.glob(str(SRC / f"media-generation-{stem}-*.jpg")))
               if not m.endswith(".json")]
    if not matches:
        raise SystemExit(f"missing source for {stem}")
    img = Image.open(matches[0]).convert("RGB")
    img = grain(vignette(cover(img, size)), opacity=0.12)
    img.save(OUT / filename, quality=90, optimize=True)
    print(f"wrote {filename} ({img.size[0]}x{img.size[1]})")

for name in REMOVE:
    p = OUT / name
    if p.exists():
        p.unlink()
        print(f"removed {name}")

print("done")
