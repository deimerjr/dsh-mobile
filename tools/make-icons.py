#!/usr/bin/env python
"""Genera iconos y splash de DSH Mobile (Capacitor Android)."""
import os, glob
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "android", "app", "src", "main", "res")

C1 = (43, 109, 246)   # #2b6df6
C2 = (127, 178, 255)  # #7fb2ff
INK = (255, 255, 255)
MUTED = (147, 164, 183)
BG1 = (11, 15, 20)
BG2 = (22, 38, 58)

def font_path():
    for p in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
        if os.path.exists(p):
            return p
    return None

FONT = font_path()

def gradient(size, c1, c2, diagonal=True):
    w, h = size
    img = Image.new("RGB", size)
    d = ImageDraw.Draw(img)
    n = w + h if diagonal else h
    for i in range(n):
        t = i / max(1, n - 1)
        col = tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))
        if diagonal:
            d.line([(i, 0), (0, i)], fill=col)
        else:
            d.line([(0, i), (w, i)], fill=col)
    return img

def wordmark(draw, box, text, fill=INK, max_w=0.62, max_h=0.30):
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    size = 10
    f = ImageFont.truetype(FONT, size)
    # escala para que quepa en ancho/alto
    while True:
        f = ImageFont.truetype(FONT, size)
        bb = draw.textbbox((0, 0), text, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        if tw > W * max_w or th > H * max_h:
            size -= 1
            f = ImageFont.truetype(FONT, size)
            bb = draw.textbbox((0, 0), text, font=f)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            break
        size += 1
    tx = x0 + (W - tw) / 2 - bb[0]
    ty = y0 + (H - th) / 2 - bb[1]
    draw.text((tx, ty), text, font=f, fill=fill)

def rounded_mask(size, radius_ratio=0.22):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    r = int(min(size) * radius_ratio)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=r, fill=255)
    return m

def circle_mask(size):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([0, 0, size[0] - 1, size[1] - 1], fill=255)
    return m

def make_launcher(size, mask_ratio, radius=0.22):
    img = gradient((size, size), C1, C2).convert("RGBA")
    d = ImageDraw.Draw(img)
    wordmark(d, (0, 0, size, size), "DSH")
    if mask_ratio == "round":
        img.putalpha(circle_mask((size, size)))
    else:
        img.putalpha(rounded_mask((size, size), radius))
    return img

def make_foreground(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    wordmark(d, (0, 0, size, size), "DSH", max_w=0.62, max_h=0.26)
    return img

def make_splash(size):
    w, h = size
    img = gradient((w, h), BG1, BG2).convert("RGBA")
    d = ImageDraw.Draw(img)
    s = int(min(w, h) * 0.34)
    logo = gradient((s, s), C1, C2).convert("RGBA")
    ld = ImageDraw.Draw(logo)
    wordmark(ld, (0, 0, s, s), "DSH")
    logo.putalpha(rounded_mask((s, s), 0.24))
    x = (w - s) // 2
    y = int(h * 0.5 - s * 0.62)
    img.alpha_composite(logo, (x, y))
    try:
        f = ImageFont.truetype(FONT, max(14, int(min(w, h) * 0.045)))
        txt = "DeepSeek Harness"
        bb = d.textbbox((0, 0), txt, font=f)
        tw = bb[2] - bb[0]
        d.text(((w - tw) / 2, y + s + int(min(w, h) * 0.05)), txt, font=f, fill=MUTED)
    except Exception:
        pass
    return img

# --- iconos legacy y foreground ---
densities = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
for name, scale in densities.items():
    d = os.path.join(RES, "mipmap-" + name)
    if not os.path.isdir(d):
        continue
    size = int(48 * scale)
    make_launcher(size, "square").save(os.path.join(d, "ic_launcher.png"))
    make_launcher(size, "round").save(os.path.join(d, "ic_launcher_round.png"))
    make_foreground(int(108 * scale)).save(os.path.join(d, "ic_launcher_foreground.png"))

# --- splash ---
for path in glob.glob(os.path.join(RES, "drawable*", "splash.png")):
    im = Image.open(path)
    make_splash(im.size).save(path)

print("iconos y splash regenerados")
