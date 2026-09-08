"""Render a Bride's Cheat Sheet carousel: 7 slides, 1080x1350, from a spec dict.

The generator used to live in a scratch folder outside the repo and was lost
when the container was reclaimed, taking the exact type scale and palette with
it. It lives here now so an issue can always be re-rendered or corrected.

Usage:
    python carousels/make_cheat_sheet.py 06        # writes brides-cheat-sheet-06/

Fonts: Playfair Display (bundled in assets/fonts) for display type, Inter for
everything else. Inter is fetched into assets/fonts on first run because it is
a variable font and the repo keeps only what the reel renderer needs.
"""
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")
W, H = 1080, 1350

INTER_URL = ("https://raw.githubusercontent.com/google/fonts/main/ofl/inter/"
             "Inter%5Bopsz,wght%5D.ttf")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

# Dark plate (cover + CTA), light plates alternating warm/cool on the content
# slides so five slides in a row never read as one flat block.
SLATE = (44, 62, 77)
SLATE_2 = (52, 73, 90)
CREAM_TEXT = (242, 237, 228)
GOLD = (200, 183, 132)
NAVY = (43, 58, 71)
WARM = (236, 229, 219)
COOL = (221, 227, 233)
MUTED = (110, 125, 138)


def _inter():
    p = os.path.join(FONT_DIR, "Inter.ttf")
    if not os.path.exists(p):
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve(INTER_URL, p)
    return p


def sans(size, wght=500):
    f = ImageFont.truetype(_inter(), size)
    try:
        f.set_variation_by_axes([14, wght])
    except Exception:                      # static build, or no variation support
        pass
    return f


def serif(size, italic=False):
    name = "PlayfairDisplay-Italic.ttf" if italic else "PlayfairDisplay.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def _w(d, s, f, tr=0):
    return d.textlength(s, font=f) + tr * max(0, len(s) - 1)


def tracked(d, cx, y, s, f, fill, tr=0, anchor="m"):
    """Letter-spaced run. Pillow has no tracking, so step glyph by glyph."""
    total = _w(d, s, f, tr)
    x = cx - total / 2 if anchor == "m" else cx
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tr


def _plate(dark, warm=False):
    """Background wash. A soft diagonal gradient plus one very faint disc —
    flat fills looked like a slide template, and a photo is not always on hand."""
    top = SLATE if dark else (WARM if warm else COOL)
    bot = SLATE_2 if dark else tuple(max(0, c - 12) for c in top)
    img = Image.new("RGB", (W, H), top)
    grad = Image.new("L", (1, H))
    for y in range(H):
        grad.putpixel((0, y), int(255 * (y / H) ** 1.3))
    img = Image.composite(Image.new("RGB", (W, H), bot), img, grad.resize((W, H)))
    disc = Image.new("L", (W, H), 0)
    ImageDraw.Draw(disc).ellipse([-140, H - 420, 420, H + 140], fill=26 if dark else 16)
    glow = tuple(min(255, c + (34 if dark else 22)) for c in bot)
    img = Image.composite(Image.new("RGB", (W, H), glow), img,
                          disc.filter(ImageFilter.GaussianBlur(40)))
    return img


def _header(d, n, total, dark, label="BRIDE'S CHEAT SHEET"):
    f = sans(19, 700)
    ink = (150, 165, 178) if dark else MUTED
    tracked(d, 52, 44, label, f, GOLD if dark else ink, tr=3.2, anchor="l")
    tracked(d, W - 52 - _w(d, f"{n} / {total}", f, 3.2), 44, f"{n} / {total}",
            f, ink, tr=3.2, anchor="l")


def _emoji(img, xy, char, size):
    """Noto Color Emoji only ships one bitmap size; render then scale."""
    try:
        f = ImageFont.truetype(EMOJI, 109)
    except OSError:
        return
    tile = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((0, 0), char, font=f, embedded_color=True)
    tile = tile.crop(tile.getbbox() or (0, 0, 1, 1)).resize((size, size), Image.LANCZOS)
    img.paste(tile, xy, tile)


def _pill(img, d, cx, cy, text, f, bg, fg, padx=34, pady=17, tr=3.0, emoji=None):
    tw = _w(d, text, f, tr) + (int(f.size * 1.5) if emoji else 0)
    box = [cx - tw / 2 - padx, cy - f.size / 2 - pady,
           cx + tw / 2 + padx, cy + f.size / 2 + pady]
    d.rounded_rectangle(box, radius=(box[3] - box[1]) / 2, fill=bg)
    tracked(d, cx - (int(f.size * 0.75) if emoji else 0), cy - f.size * 0.62,
            text, f, fg, tr=tr)
    if emoji:
        _emoji(img, (int(cx + tw / 2 - f.size * 1.1), int(cy - f.size * 0.72)),
               emoji, int(f.size * 1.4))


def _lines(d, lines, cx, top, f, fill, lead, gold_word=None):
    """Centred display type. One word may be picked out in gold."""
    y = top
    for line in lines:
        if gold_word and gold_word in line.split():
            parts, x = line.split(" "), cx - _w(d, line, f) / 2
            for i, wd in enumerate(parts):
                s = wd + (" " if i < len(parts) - 1 else "")
                d.text((x, y), s, font=f, fill=GOLD if wd == gold_word else fill)
                x += d.textlength(s, font=f)
        else:
            d.text((cx, y), line, font=f, fill=fill, anchor="ma")
        y += lead
    return y


def cover(spec, out):
    img = _plate(dark=True)
    d = ImageDraw.Draw(img)
    _header(d, 1, 7, True, f"BRIDE'S CHEAT SHEET · Nº {spec['number']}")
    tracked(d, W / 2, 462, spec["eyebrow"], sans(21, 700), GOLD, tr=5.0)
    y = _lines(d, spec["title"], W / 2, 512, serif(96, italic=True), CREAM_TEXT,
               100, spec.get("gold_word"))
    # The italic descenders reach well below the line box, so the subtitle needs
    # real air under the title or it reads as a fourth title line.
    d.text((W / 2, y + 54), spec["subtitle"], font=sans(28, 400),
           fill=(206, 214, 221), anchor="ma")
    d.line([W / 2 - 34, y + 128, W / 2 + 34, y + 128], fill=GOLD, width=2)
    tracked(d, W / 2, y + 158, "SWIPE   →", sans(22, 600), (168, 182, 194), tr=5.0)
    img.save(out, quality=94)


def content(spec, i, out):
    card = spec["cards"][i - 2]
    img = _plate(dark=False, warm=(i % 2 == 0))
    d = ImageDraw.Draw(img)
    _header(d, i, 7, False)
    _pill(img, d, W / 2, 176, card["badge"], sans(23, 700), NAVY, CREAM_TEXT)
    _lines(d, card["title"], W / 2, 232, serif(78), NAVY, 82)

    note = card.get("note")
    italic = ImageFont.truetype(os.path.join(FONT_DIR, "PlayfairDisplay-Italic.ttf"), 26)
    top = 520
    if card.get("quote"):
        # Wording issues are only useful if the line can be lifted straight off
        # the screen, so the card holds one quoted block at reading size and
        # nothing else competes with it.
        quote = card["quote"]
        fq = serif(44, italic=True)
        while max(d.textlength(l, font=fq) for l in quote) > W - 216 - 72 and fq.size > 30:
            fq = serif(fq.size - 2, italic=True)   # full templates run long
        box_h = 96 + len(quote) * 62 + (58 if note else 0)
        d.rounded_rectangle([108, top, W - 108, top + box_h], radius=32, fill=(255, 255, 255))
        y = top + 62
        for line in quote:
            d.text((W / 2, y), line, font=fq, fill=NAVY, anchor="ma")
            y += 62
        if note:
            d.text((W / 2, y + 30), note, font=italic, fill=MUTED, anchor="ma")
    else:
        rows = card["rows"]
        box_h = 78 + len(rows) * 80 + (58 if note else 0)
        d.rounded_rectangle([108, top, W - 108, top + box_h], radius=32, fill=(255, 255, 255))
        y = top + 62
        fr = sans(30, 450)
        for row in rows:
            d.ellipse([172, y + 4, 220, y + 52], fill=NAVY)
            d.text((196, y + 26), "✓", font=sans(24, 600), fill=CREAM_TEXT, anchor="mm")
            d.text((242, y + 28), row, font=fr, fill=NAVY, anchor="lm")
            y += 80
        if note:
            d.text((172, y + 16), note, font=italic, fill=MUTED, anchor="lm")
    _pill(img, d, W / 2, 1256, "SAVE THIS", sans(22, 700), NAVY, CREAM_TEXT,
          emoji="📌")
    img.save(out, quality=94)


def cta(spec, out):
    img = _plate(dark=True)
    d = ImageDraw.Draw(img)
    _header(d, 7, 7, True, "")
    tracked(d, W / 2, 412, "BRIDE'S CHEAT SHEET · A NEW ONE EVERY WEEK",
            sans(20, 600), CREAM_TEXT, tr=4.2)
    y = _lines(d, spec["closing"], W / 2, 462, serif(84, italic=True), CREAM_TEXT, 104)
    d.line([W / 2 - 34, y + 24, W / 2 + 34, y + 24], fill=GOLD, width=2)
    line = spec["save_line"]
    f = sans(23, 600)
    tw = _w(d, line, f, 3.2)
    pin, gap = 30, 14
    left = W / 2 - (pin + gap + tw) / 2
    _emoji(img, (int(left), int(y + 56)), "📌", pin)
    tracked(d, left + pin + gap, y + 58, line, f, CREAM_TEXT, tr=3.2, anchor="l")
    _pill(img, d, W / 2, y + 168, "FOLLOW FOR THE NEXT CHEAT SHEET",
          sans(24, 700), (240, 232, 214), NAVY, padx=44, pady=22)
    tracked(d, W / 2, y + 258, "VISTELACO · @dianacreativedesign.co",
            sans(21, 500), (176, 189, 200), tr=4.0)
    img.save(out, quality=94)


def build(spec, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cover(spec, os.path.join(out_dir, "slide-1.jpg"))
    for i in range(2, 7):
        content(spec, i, os.path.join(out_dir, f"slide-{i}.jpg"))
    cta(spec, os.path.join(out_dir, "slide-7.jpg"))
    return out_dir


if __name__ == "__main__":
    import specs
    n = sys.argv[1]
    build(specs.SPECS[n], os.path.join(ROOT, "carousels", f"brides-cheat-sheet-{n}"))
    print(f"brides-cheat-sheet-{n}: 7 slides")
