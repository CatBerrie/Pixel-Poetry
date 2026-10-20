#!/usr/bin/env python3
"""
🌿 Pixel Poetry photo maker
------------------------
1. Put your ORIGINAL photos in the folder called  originals
2. Open a terminal in this folder and run:   python3 make_photos.py
3. Copy the new lines it prints into the  photos  list in index.html,
   then write your own title + caption + category + date.

For every original photo it makes two copies:
  photos/<name>.jpg                      what visitors see (smaller, location data removed)
  photos/download/<name>-pixelpoetry.jpg   what the Download button gives (with the Pixel Poetry watermark)

It also picks the 5 main colors of each photo (for the color chips in the viewer).

You need Pillow once:   pip3 install pillow
"""
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
WEB_MAX = 1600          # longest side (in pixels) of the copy shown on the website
DL_MAX = 2000           # longest side (in pixels) of the free download copy
WATERMARK = "Pixel Poetry"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# The script tries these fonts one by one and uses the first one it finds (Mac, Linux, Windows)
FONTS = [
    "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/Library/Fonts/Georgia Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "C:/Windows/Fonts/georgiai.ttf",
]


def slugify(text):
    """'My Photo (1)' -> 'my-photo-1'  (safe for file names and web addresses)"""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_font(size):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size)   # newer Pillow can size the built-in font
    except TypeError:
        return ImageFont.load_default()


def open_clean(path):
    """Open a photo, fix its rotation, and keep its color profile."""
    img = Image.open(path)
    icc = img.info.get("icc_profile")
    img = ImageOps.exif_transpose(img).convert("RGB")
    return img, icc


def fit(img, max_side):
    """Shrink so the longest side is at most max_side (never enlarges)."""
    w, h = img.size
    scale = max_side / max(w, h)
    if scale < 1:
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    return img


def save_jpeg(img, path, quality, icc):
    path.parent.mkdir(parents=True, exist_ok=True)
    # No EXIF is written, so GPS location and camera details never reach the website.
    img.save(path, "JPEG", quality=quality, optimize=True, progressive=True, icc_profile=icc)


def sparkle(cx, cy, r):
    """The 4-point star used in the watermark badge."""
    pts = []
    for i in range(8):
        angle = math.pi / 4 * i - math.pi / 2
        rad = r if i % 2 == 0 else r * 0.32
        pts.append((cx + math.cos(angle) * rad, cy + math.sin(angle) * rad))
    return pts


def add_watermark(img):
    W, H = img.size
    m = min(W, H)
    base = img.convert("RGBA")

    # 1) a faint diagonal pattern over the whole photo (hard to crop away)
    size = max(16, int(m * 0.045))
    font = load_font(size)
    text_w = int(font.getlength(WATERMARK))
    diag = int(math.hypot(W, H)) + 4
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    step_x, step_y = int(text_w * 2.4), int(size * 4.6)
    for row, y in enumerate(range(0, diag, step_y)):
        offset = step_x // 2 if row % 2 else 0
        for x in range(-step_x + offset, diag, step_x):
            draw.text((x + 2, y + 2), WATERMARK, font=font, fill=(0, 20, 10, 70))   # soft shadow
            draw.text((x, y), WATERMARK, font=font, fill=(255, 255, 255, 88))        # white text
    layer = layer.rotate(28, resample=Image.BICUBIC)
    left, top = (diag - W) // 2, (diag - H) // 2
    base = Image.alpha_composite(base, layer.crop((left, top, left + W, top + H)))

    # 2) a small badge near the bottom:  ✦ Pixel Poetry
    size2 = max(20, int(m * 0.052))
    font2 = load_font(size2)
    bbox = font2.getbbox(WATERMARK)
    text_h, text_w2 = bbox[3] - bbox[1], int(font2.getlength(WATERMARK))
    star = int(size2 * 0.85)
    gap, pad_x, pad_y = int(size2 * 0.35), int(size2 * 0.75), int(size2 * 0.38)
    box_w = pad_x * 2 + star + gap + text_w2
    box_h = max(text_h, star) + pad_y * 2
    cx, cy = W // 2, int(H * 0.86)
    box = (cx - box_w // 2, cy - box_h // 2, cx + box_w // 2, cy + box_h // 2)
    badge = Image.new("RGBA", base.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.rounded_rectangle(box, radius=box_h // 2, fill=(6, 30, 18, 150),
                         outline=(190, 255, 190, 140), width=max(1, size2 // 18))
    sx = box[0] + pad_x + star // 2
    bd.polygon(sparkle(sx, cy, star / 2), fill=(217, 249, 157, 255))
    bd.text((sx + star // 2 + gap, cy), WATERMARK, font=font2, fill=(240, 255, 225, 255), anchor="lm")
    return Image.alpha_composite(base, badge).convert("RGB")


def get_palette(img, n=5):
    """The n most common (and different enough) colors of a photo, as #rrggbb."""
    small = img.copy()
    small.thumbnail((120, 120))
    q = small.convert("RGB").quantize(colors=10, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    picked = []
    for count, idx in sorted(q.getcolors(), reverse=True):
        color = tuple(pal[idx * 3: idx * 3 + 3])
        far_enough = all(math.dist(color, p) > 45 for p in picked)
        if far_enough:
            picked.append(color)
        if len(picked) == n:
            break
    return ["#%02x%02x%02x" % c for c in picked]


def process(src, photos_dir, force=False):
    """Make the website copy + the watermarked download copy for one original photo."""
    src, photos_dir = Path(src), Path(photos_dir)
    name = slugify(src.stem)
    web_path = photos_dir / f"{name}.jpg"
    dl_path = photos_dir / "download" / f"{name}-pixelpoetry.jpg"
    img, icc = open_clean(src)
    web = fit(img, WEB_MAX)
    if force or not web_path.exists():
        save_jpeg(web, web_path, 82, icc)
    if force or not dl_path.exists():
        save_jpeg(add_watermark(fit(img, DL_MAX)), dl_path, 88, icc)
    thumb_path = photos_dir / "thumb" / f"{name}.jpg"          # small copy the gallery grid loads (keeps scrolling smooth)
    if force or not thumb_path.exists():
        thumb_path.parent.mkdir(exist_ok=True)
        save_jpeg(fit(img, 900), thumb_path, 78, icc)
    return {"file": web_path.name, "w": web.width, "h": web.height, "colors": get_palette(web)}


def main():
    originals, photos_dir = HERE / "originals", HERE / "photos"
    originals.mkdir(exist_ok=True)
    files = [p for p in sorted(originals.iterdir()) if p.suffix.lower() in EXTENSIONS]
    if not files:
        print("No photos found. Put your originals in the 'originals' folder first 🌱")
        return
    page = (HERE / "index.html").read_text(encoding="utf-8") if (HERE / "index.html").exists() else ""
    lines = []
    for f in files:
        info = process(f, photos_dir)
        print(f"✔ {f.name}  ->  photos/{info['file']}  +  photos/download/{slugify(f.stem)}-pixelpoetry.jpg")
        if f'file:"{info["file"]}"' in page:
            continue                                  # already listed in index.html
        title = slugify(f.stem).replace("-", " ").title()
        lines.append(f'  {{ file:"{info["file"]}", title:"{title}", caption:"", category:"blooms", '
                     f'date:"", w:{info["w"]}, h:{info["h"]}, colors:{json.dumps(info["colors"])} }},')
    if lines:
        print("\nPaste these into the photos list in index.html, then write your own title + caption ✍️\n")
        print("\n".join(lines))
    else:
        print("\nEverything is already listed in index.html 🌿")


if __name__ == "__main__":
    main()
