"""Compose 1080x1920 TikTok frames for the Flip Deal Calculator videos."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, json

W, H = 1080, 1920
SAFE_L, SAFE_R = 64, 940          # keep clear of TikTok's right-side buttons
BG = (14, 24, 21)
INK = (244, 247, 245)
MUTED = (166, 182, 175)
ACCENT = (111, 176, 221)
AMBER = (241, 182, 92)
GOOD = (92, 201, 139)
BAD = (239, 122, 114)
FD = os.environ.get("FONT_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/")

def F(weight, size):
    name = {"black": "InterDisplay-Black.otf", "xbold": "InterDisplay-ExtraBold.otf", "bold": "InterDisplay-Bold.otf",
            "semi": "InterDisplay-SemiBold.otf", "med": "InterDisplay-Medium.otf"}[weight]
    p = FD + name
    if not os.path.exists(p):
        p = FD + "Inter-Bold.otf"
    return ImageFont.truetype(p, size)

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def text_block(draw, text, font, x, y, width, fill, gap=1.18, align="left"):
    lines = wrap(draw, text, font, width)
    lh = int(font.size * gap)
    for i, ln in enumerate(lines):
        tx = x if align == "left" else x + (width - draw.textlength(ln, font=font)) / 2
        draw.text((tx, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh

def colorize(text):
    t = text.strip()
    if t.startswith("−") or t.startswith("-"): return BAD
    return INK

def base(brand=True):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    # soft accent glow top-left
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-400, -500, 700, 500), fill=(22, 52, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.blend(im, glow, 0.9)
    d = ImageDraw.Draw(im)
    if brand:
        f = F("bold", 30)
        label = "FLIP DEAL CALCULATOR"
        tw = d.textlength(label, font=f)
        d.rounded_rectangle((SAFE_L, 118, SAFE_L + tw + 40, 170), radius=26, outline=ACCENT, width=3)
        d.text((SAFE_L + 20, 126), label, font=f, fill=ACCENT)
    return im, d

def paste_shot(im, path, box, crop=None):
    sh = Image.open(path).convert("RGB")
    if crop: sh = sh.crop(crop)
    bx0, by0, bx1, by1 = box
    bw, bh = bx1 - bx0, by1 - by0
    s = min(bw / sh.width, bh / sh.height)
    nw, nh = int(sh.width * s), int(sh.height * s)
    sh = sh.resize((nw, nh), Image.LANCZOS)
    x = bx0 + (bw - nw) // 2
    y = by0 + (bh - nh) // 2
    # shadow
    sd = Image.new("L", (nw + 80, nh + 80), 0)
    ImageDraw.Draw(sd).rounded_rectangle((40, 40, nw + 40, nh + 40), radius=28, fill=170)
    sd = sd.filter(ImageFilter.GaussianBlur(22))
    im.paste((0, 0, 0), (x - 40, y - 26), sd)
    mask = Image.new("L", (nw, nh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, nw, nh), radius=26, fill=255)
    im.paste(sh, (x, y), mask)
    return (x, y, x + nw, y + nh)

def scene_card(spec):
    im, d = base()
    y = 560 if not spec.get("top") else 420
    y = text_block(d, spec["title"], F("black", spec.get("size", 96)), SAFE_L, y, SAFE_R - SAFE_L, INK, gap=1.1)
    if spec.get("sub"):
        y += 40
        text_block(d, spec["sub"], F("semi", 54), SAFE_L, y, SAFE_R - SAFE_L, AMBER, gap=1.2)
    return im

def scene_shot(spec):
    im, d = base()
    y = text_block(d, spec["title"], F("xbold", 70), SAFE_L, 220, SAFE_R - SAFE_L, INK, gap=1.12)
    top = max(y + 30, 360)
    cap_h = 200 if spec.get("caption") else 0
    box = (SAFE_L, top, SAFE_R, 1560 - cap_h)
    r = paste_shot(im, spec["img"], box, spec.get("crop"))
    if spec.get("caption"):
        cy = r[3] + 46
        text_block(d, spec["caption"], F("semi", 46), SAFE_L, cy, SAFE_R - SAFE_L, spec.get("capcolor", AMBER), gap=1.22)
    return im

def scene_stats(spec):
    im, d = base()
    y = text_block(d, spec["title"], F("xbold", 70), SAFE_L, 220, SAFE_R - SAFE_L, INK, gap=1.12)
    y = max(y + 50, 420)
    rows = spec["rows"]
    rh = 230
    for i, (label, val, color) in enumerate(rows):
        top = y + i * (rh + 26)
        d.rounded_rectangle((SAFE_L, top, SAFE_R, top + rh), radius=28, fill=(24, 38, 34), outline=(44, 64, 58), width=2)
        d.text((SAFE_L + 40, top + 34), label, font=F("semi", 44), fill=MUTED)
        col = {"good": GOOD, "bad": BAD, "amber": AMBER, "ink": INK}[color]
        d.text((SAFE_L + 40, top + 96), val, font=F("black", 100), fill=col)
    if spec.get("caption"):
        cy = y + len(rows) * (rh + 26) + 30
        text_block(d, spec["caption"], F("semi", 44), SAFE_L, cy, SAFE_R - SAFE_L, AMBER, gap=1.22)
    return im

def scene_end(spec):
    im, d = base()
    y = text_block(d, spec["title"], F("black", 88), SAFE_L, 520, SAFE_R - SAFE_L, INK, gap=1.1)
    y += 60
    d.rounded_rectangle((SAFE_L, y, SAFE_R, y + 150), radius=75, fill=AMBER)
    f = F("xbold", 54)
    t = spec["cta"]
    d.text((SAFE_L + (SAFE_R - SAFE_L - d.textlength(t, font=f)) / 2, y + 42), t, font=f, fill=(20, 24, 22))
    y += 220
    if spec.get("sub"):
        y = text_block(d, spec["sub"], F("semi", 46), SAFE_L, y, SAFE_R - SAFE_L, MUTED, gap=1.2, align="center")
    text_block(d, "Estimates only. Not financial advice.", F("med", 34), SAFE_L, 1500, SAFE_R - SAFE_L, (120, 138, 131), align="center")
    return im

KIND = {"card": scene_card, "shot": scene_shot, "stats": scene_stats, "end": scene_end}

def build(videos, outdir="frames"):
    os.makedirs(outdir, exist_ok=True)
    for vid, scenes in videos.items():
        for i, sc in enumerate(scenes):
            im = KIND[sc["kind"]](sc)
            im.save(f"{outdir}/{vid}_{i:02d}.png")
