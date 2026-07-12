"""Renderers. Text is drawn by code (zero typos, exact brand colours, brand
font). Pins are 2:3 for Pinterest; carousel slides are 4:5 for Instagram."""
import os
from PIL import Image, ImageDraw, ImageFont
import config as C


def font(size, wght=500):
    f = ImageFont.truetype(C.FONT, size)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def _w(d, s, f, tr=0):
    return sum(d.textlength(c, font=f) for c in s) + tr * (len(s) - 1) if s else 0


def tracked(d, cx, y, s, f, fill, tr=0):
    """Centred, letter-spaced text."""
    x = cx - _w(d, s, f, tr) / 2
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr


def fit(d, s, target_w, start, wght=600):
    sz = start
    while sz > 40:
        f = font(sz, wght)
        if _w(d, s, f) <= target_w:
            return f
        sz -= 2
    return font(40, wght)


def _swatches(d, cx, top, h, colors, bw, hexlabel=True):
    n = len(colors); gap = 16; sw = (bw - gap * (n - 1)) / n; x0 = cx - bw / 2
    for i, hx in enumerate(colors):
        x = x0 + i * (sw + gap)
        d.rounded_rectangle([x, top, x + sw, top + h], radius=10, fill=hx)
        if hexlabel:
            tracked(d, x + sw / 2, top + h + 24, hx.upper().replace("#", ""),
                    font(22, 500), C.MUTED, tr=2)


def _footer(d, W, y_rule, y_brand, y_tag):
    d.line([(W / 2 - 64, y_rule), (W / 2 + 64, y_rule)], fill=C.HAIR, width=2)
    tracked(d, W / 2, y_brand, C.BRAND, font(30, 600), C.INK, tr=9)
    tracked(d, W / 2, y_tag, C.TAGLINE, font(19, 500), C.MUTED, tr=3)


# --- Pinterest pin (2:3) ---------------------------------------------------
def palette_pin(pal, out_path):
    W, H = C.PIN_SIZE
    img = Image.new("RGB", (W, H), C.BG); d = ImageDraw.Draw(img)
    tracked(d, W / 2, 150, "WEDDING COLOUR PALETTE", font(27, 500), C.MUTED, tr=7)
    d.text((W / 2, 250), pal["name"], font=fit(d, pal["name"], 800, 96, 600),
           fill=C.INK, anchor="ma")
    d.line([(W / 2 - 70, 372), (W / 2 + 70, 372)], fill=C.HAIR, width=2)
    _swatches(d, W / 2, 440, 360, pal["colors"], bw=764)
    tracked(d, W / 2, 536 + 360, f"{pal['trend']}  \u00b7  a 2026 wedding palette",
            font(35, 500), C.INK, tr=3)
    _footer(d, W, 1332, 1360, 1416)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


# --- Instagram carousel (4:5) ----------------------------------------------
def _slide_base():
    W, H = C.CAROUSEL_SIZE
    img = Image.new("RGB", (W, H), C.BG)
    return img, ImageDraw.Draw(img), W, H


def _cover(pals, out_path, subtitle="2026 WEDDING TRENDS"):
    img, d, W, H = _slide_base()
    tracked(d, W / 2, 205, subtitle, font(25, 500), C.MUTED, tr=8)
    d.text((W / 2, 285), "Five Wedding", font=font(96, 600), fill=C.INK, anchor="ma")
    d.text((W / 2, 410), "Colour Palettes", font=font(96, 600), fill=C.INK, anchor="ma")
    teaser = [c for p in pals for c in p["colors"][:3]]
    n = len(teaser); gap = 8; bw = 880; sw = (bw - gap * (n - 1)) / n; x0 = W / 2 - bw / 2
    for i, hx in enumerate(teaser):
        x = x0 + i * (sw + gap)
        d.rounded_rectangle([x, 650, x + sw, 770], radius=6, fill=hx)
    tracked(d, W / 2, 860, "SWIPE  \u2192", font(30, 500), C.MUTED, tr=6)
    _footer(d, W, 1232, 1258, 1306)
    img.save(out_path, "PNG")


def _palette_slide(idx, total, pal, out_path):
    img, d, W, H = _slide_base()
    tracked(d, W / 2, 118, f"{idx:02d}  /  {total:02d}", font(24, 500), C.MUTED, tr=5)
    d.text((W / 2, 175), pal["name"], font=fit(d, pal["name"], 940, 96, 600),
           fill=C.INK, anchor="ma")
    d.line([(W / 2 - 64, 312), (W / 2 + 64, 312)], fill=C.HAIR, width=2)
    _swatches(d, W / 2, 382, 430, pal["colors"], bw=820)
    tracked(d, W / 2, 905, f"{pal['trend']}  \u00b7  a 2026 palette", font(33, 500), C.INK, tr=3)
    _footer(d, W, 1232, 1258, 1306)
    img.save(out_path, "PNG")


def _cta(out_path):
    img, d, W, H = _slide_base()
    tracked(d, W / 2, 300, "YOUR TURN", font(25, 500), C.MUTED, tr=8)
    d.text((W / 2, 375), "Which palette", font=font(94, 600), fill=C.INK, anchor="ma")
    d.text((W / 2, 495), "is your vibe?", font=font(94, 600), fill=C.INK, anchor="ma")
    tracked(d, W / 2, 660, "Save this for your wedding moodboard", font(34, 500), C.MUTED, tr=2)
    d.line([(W / 2 - 64, 770), (W / 2 + 64, 770)], fill=C.HAIR, width=2)
    tracked(d, W / 2, 820, "Editable wedding invitations & websites", font(36, 500), C.INK, tr=1)
    tracked(d, W / 2, 890, "@vistelaco   \u00b7   on Etsy", font(34, 600), C.INK, tr=2)
    _footer(d, W, 1232, 1258, 1306)
    img.save(out_path, "PNG")


def carousel(pals, out_dir, cover_subtitle="2026 WEDDING TRENDS"):
    """Render a full carousel (cover + palette slides + CTA). Returns ordered paths."""
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    cover_p = os.path.join(out_dir, "00_cover.png"); _cover(pals, cover_p, cover_subtitle); paths.append(cover_p)
    for i, pal in enumerate(pals, 1):
        p = os.path.join(out_dir, f"{i:02d}_{pal['slug']}.png")
        _palette_slide(i, len(pals), pal, p); paths.append(p)
    cta_p = os.path.join(out_dir, "99_cta.png"); _cta(cta_p); paths.append(cta_p)
    return paths
