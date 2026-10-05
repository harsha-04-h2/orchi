from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import math
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

SRC_A = Image.open(ROOT / "orchi.png").convert("RGB")
SRC_B = Image.open(ROOT / "Cyberpunk Luxury Poster Collective.png").convert("RGB")


def cover(img, size, crop=(0.5, 0.5), scale=1.0):
    w, h = img.size
    tw, th = size
    factor = max(tw / w, th / h) * scale
    nw, nh = int(w * factor), int(h * factor)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = int((nw - tw) * crop[0])
    y = int((nh - th) * crop[1])
    return resized.crop((x, y, x + tw, y + th))


def grade(img, brightness=0.82, contrast=1.12, color=0.72, tint=(0, 0, 0), tint_alpha=0.0):
    out = ImageEnhance.Brightness(img).enhance(brightness)
    out = ImageEnhance.Contrast(out).enhance(contrast)
    out = ImageEnhance.Color(out).enhance(color)
    if tint_alpha:
        tint_layer = Image.new("RGB", out.size, tint)
        out = Image.blend(out, tint_layer, tint_alpha)
    return out


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


def light_beam(img, x=0.58, color=(238, 231, 214), alpha=80, width=0.16):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = int(w * x)
    half = int(w * width)
    poly = [(cx - half, 0), (cx + half, 0), (cx + int(half * 0.2), h), (cx - int(half * 1.4), h)]
    draw.polygon(poly, fill=(*color, alpha))
    overlay = overlay.filter(ImageFilter.GaussianBlur(42))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def red_practical(img, x=0.66, y=0.58, radius=0.32):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    r = int(min(w, h) * radius)
    cx, cy = int(w * x), int(h * y)
    for i in range(r, 0, -8):
        a = int(72 * (1 - i / r) ** 1.7)
        draw.ellipse((cx - i, cy - i, cx + i, cy + i), fill=(145, 22, 20, a))
    return Image.alpha_composite(img.convert("RGBA"), overlay.filter(ImageFilter.GaussianBlur(16))).convert("RGB")


def grain(img, amount=16, opacity=0.18):
    random.seed(42)
    w, h = img.size
    noise = Image.new("L", (w, h))
    noise.putdata([random.randrange(0, amount) for _ in range(w * h)])
    noise = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, ImageEnhance.Contrast(noise).enhance(2.4), opacity)


def rules(img, density=7, alpha=30):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(1, density):
        x = int(w * i / density)
        draw.line((x, 0, x, h), fill=(232, 226, 212, alpha), width=1)
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def save(name, img, quality=92):
    img = grain(vignette(img), opacity=0.12)
    img.save(OUT / name, quality=quality, optimize=True)


WIDE = (1800, 1125)
TALL = (1200, 1600)
SQUARE = (1400, 1400)

save("attention-establishing.jpg", light_beam(grade(cover(SRC_A, WIDE, (0.44, 0.42), 1.08), 0.72, 1.2, 0.54, (10, 13, 15), 0.08), 0.48, alpha=58))
save("macro-detail.jpg", red_practical(grade(cover(SRC_B, WIDE, (0.44, 0.48), 1.74).filter(ImageFilter.GaussianBlur(0.55)), 0.64, 1.44, 0.5), 0.42, 0.54, 0.2))
save("book-spread-left.jpg", grade(cover(SRC_B, SQUARE, (0.25, 0.58), 1.2), 0.88, 1.1, 0.72))
save("book-spread-right.jpg", grade(cover(SRC_A, SQUARE, (0.66, 0.48), 1.24), 0.84, 1.08, 0.62, (18, 16, 14), 0.08))
save("montage-portrait.jpg", red_practical(grade(cover(SRC_B, WIDE, (0.16, 0.35), 1.22), 0.7, 1.24, 0.72), 0.68, 0.45, 0.22))
save("montage-silver.jpg", light_beam(grade(cover(SRC_A, WIDE, (0.58, 0.5), 1.16), 0.7, 1.16, 0.38, (6, 9, 11), 0.1), 0.7, alpha=70))
save("method-silhouette.jpg", light_beam(grade(cover(SRC_A, WIDE, (0.72, 0.48), 1.36).filter(ImageFilter.GaussianBlur(0.4)), 0.42, 1.42, 0.25), 0.22, alpha=100, width=0.11))
save("service-brand.jpg", rules(grade(cover(SRC_A, WIDE, (0.32, 0.48), 1.1), 0.74, 1.22, 0.56)))
save("service-content.jpg", red_practical(grade(cover(SRC_B, WIDE, (0.58, 0.5), 1.04), 0.72, 1.2, 0.7), 0.52, 0.48, 0.26))
save("service-digital.jpg", rules(light_beam(grade(cover(SRC_A, WIDE, (0.78, 0.45), 1.32), 0.62, 1.18, 0.35), 0.82, alpha=42), 11, 22))
save("service-growth.jpg", red_practical(grade(cover(SRC_B, WIDE, (0.35, 0.62), 1.16), 0.62, 1.32, 0.62), 0.78, 0.64, 0.34))
save("studio-bts-a.jpg", grade(cover(SRC_A, TALL, (0.25, 0.46), 1.3), 0.72, 1.16, 0.46, (20, 18, 15), 0.08))
save("studio-bts-b.jpg", red_practical(grade(cover(SRC_B, TALL, (0.68, 0.42), 1.34), 0.66, 1.18, 0.58), 0.34, 0.38, 0.2))
save("cta-climax.jpg", red_practical(light_beam(grade(cover(SRC_B, WIDE, (0.5, 0.52), 1.08), 0.55, 1.22, 0.66), 0.5, alpha=42), 0.58, 0.58, 0.42))

print(f"Generated {len(list(OUT.glob('*.jpg')))} visuals in {OUT}")
