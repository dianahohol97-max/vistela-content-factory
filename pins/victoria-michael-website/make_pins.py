"""Compose Pinterest pins for the ivory envelope wedding website listing.

Sources: pins/victoria-michael-website/src/*.jpg (Canva page exports fetched
by .github/workflows/fetch-canva-sources.yml).
Output: output/pins/victoria-michael-website/*.jpg, 1000x1500 (2:3).

Run from the repo root: python3 pins/victoria-michael-website/make_pins.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "pins", "victoria-michael-website", "src")
OUT = os.path.join(ROOT, "output", "pins", "victoria-michael-website")
FONTS = os.path.join(ROOT, "assets", "fonts")

W, H = 1000, 1500

# palette sampled from the design: warm ivory, cream card, deep warm brown
IVORY = (242, 236, 226)
CREAM = (247, 242, 234)
BROWN = (74, 58, 42)
TAUPE = (138, 122, 102)
PILL_BG = (74, 58, 42)
PILL_FG = (244, 238, 228)

PHONE = os.path.join(ROOT, "assets", "phone_mockup.png")
PHONE_SCREEN = (169, 150, 915, 1772)  # transparent screen rect in the 1080x1920 asset
LAPTOP = os.path.join(ROOT, "assets", "laptop_mockup.png")
LAPTOP_SCREEN = (78, 720, 1002, 1240)


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if weight is not None:
        f.set_variation_by_axes([weight])
    return f


def text_w(draw, s, f, tracking=0):
    if tracking:
        return sum(draw.textlength(ch, font=f) + tracking for ch in s) - tracking
    return draw.textlength(s, font=f)


def draw_tracked(draw, xy, s, f, fill, tracking):
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking


def eyebrow(draw, y, s):
    f = font("Montserrat.ttf", 24, 560)
    tr = 9
    w = text_w(draw, s, f, tr)
    draw_tracked(draw, ((W - w) / 2, y), s, f, TAUPE, tr)


def headline(draw, y, lines, size=68):
    f = font("PlayfairDisplay.ttf", size, 540)
    for line in lines:
        w = draw.textlength(line, font=f)
        draw.text(((W - w) / 2, y), line, font=f, fill=BROWN)
        y += int(size * 1.22)
    return y


def script_line(draw, y, s, size=64):
    f = ImageFont.truetype(os.path.join(FONTS, "GreatVibes-Regular.ttf"), size)
    w = draw.textlength(s, font=f)
    draw.text(((W - w) / 2, y), s, font=f, fill=BROWN)
    return y + int(size * 1.1)


def subline(draw, y, s):
    f = font("Montserrat.ttf", 25, 460)
    w = draw.textlength(s, font=f)
    draw.text(((W - w) / 2, y), s, font=f, fill=TAUPE)


def pills(draw, labels, y=None):
    y = y if y is not None else H - 92
    f = font("Montserrat.ttf", 21, 600)
    tr = 3
    pad, gap, h = 26, 14, 52
    widths = [text_w(draw, s, f, tr) + 2 * pad for s in labels]
    x = (W - (sum(widths) + gap * (len(labels) - 1))) / 2
    for s, wd in zip(labels, widths):
        draw.rounded_rectangle((x, y, x + wd, y + h), radius=h / 2, fill=PILL_BG)
        draw_tracked(draw, (x + pad, y + (h - 26) / 2), s, f, PILL_FG, tr)
        x += wd + gap


def canvas():
    img = Image.new("RGB", (W, H), IVORY)
    # soft vertical sheen so the flat ivory reads like fabric
    top = Image.new("L", (1, H), 0)
    for yy in range(H):
        top.putpixel((0, yy), int(14 * (1 - abs(yy - H * 0.42) / (H * 0.9))))
    sheen = Image.new("RGB", (W, H), (255, 255, 255))
    img = Image.composite(sheen, img, top.resize((W, H)))
    return img


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *im.size), radius=radius, fill=255)
    im = im.convert("RGBA")
    im.putalpha(mask)
    return im


def shadow_card(img, box, radius=24, blur=18, alpha=60, offset=(0, 14)):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.rounded_rectangle((box[0] + offset[0], box[1] + offset[1], box[2] + offset[0], box[3] + offset[1]),
                        radius=radius, fill=(60, 45, 30, alpha))
    return Image.alpha_composite(img.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(blur)))


def phone_with(screen_img, out_h):
    """Return a phone mockup RGBA scaled so its full height equals out_h,
    with screen_img cover-cropped into the screen."""
    phone = Image.open(PHONE).convert("RGBA")
    sx0, sy0, sx1, sy1 = PHONE_SCREEN
    sw, sh = sx1 - sx0, sy1 - sy0
    fit = cover(screen_img, sw, sh)
    layer = Image.new("RGBA", phone.size, (0, 0, 0, 0))
    layer.paste(rounded(fit, 84), (sx0, sy0))
    layer = Image.alpha_composite(layer, phone)
    scale = out_h / layer.height
    return layer.resize((int(layer.width * scale), out_h), Image.LANCZOS)


def cover(im, w, h, anchor="top"):
    ratio = max(w / im.width, h / im.height)
    im2 = im.resize((max(1, int(im.width * ratio)), max(1, int(im.height * ratio))), Image.LANCZOS)
    x = (im2.width - w) // 2
    y = 0 if anchor == "top" else (im2.height - h) // 2
    return im2.crop((x, y, x + w, y + h))


def paste_center(img, layer, cx, cy):
    img.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    img.convert("RGB").save(os.path.join(OUT, name), "JPEG", quality=90)
    print("saved", name)


def src(name):
    return Image.open(os.path.join(SRC, name)).convert("RGB")


# ---------------------------------------------------------------- pin 1: envelope hero
def pin_envelope():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 74, "WEDDING WEBSITE TEMPLATE")
    y = headline(d, 128, ["An invitation they", "open like a gift"], 74)
    subline(d, y + 26, "Envelope entry · 6 pages · RSVP · Countdown")

    p1 = src("p1-envelope.jpg")  # 1638x920 landscape, envelope centered
    crop = cover(p1, 860, 900, anchor="center")
    box = (70, 452, 930, 1352)
    img = shadow_card(img, box)
    img.alpha_composite(rounded(crop, 26), (box[0], box[1]))
    d = ImageDraw.Draw(img)
    pills(d, ["EDITABLE IN CANVA FREE", "INSTANT DOWNLOAD"])
    save(img, "pin-envelope-hero.jpg")


# ---------------------------------------------------------------- pin 2: menu on phone
def pin_menu_phone():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 70, "ALL-IN-ONE WEDDING WEBSITE")
    y = headline(d, 122, ["Your whole wedding", "in one link"], 70)
    ph = phone_with(src("p2-menu.jpg"), 1010)
    paste_center(img, ph, W / 2, 880)
    d = ImageDraw.Draw(img)
    pills(d, ["RSVP FORM", "COUNTDOWN", "MAPS & FAQ"])
    save(img, "pin-menu-phone.jpg")


# ---------------------------------------------------------------- pin 3: laptop details
def pin_laptop():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 88, "EDITABLE CANVA WEBSITE")
    y = headline(d, 146, ["Every detail,"], 74)
    y = script_line(d, y + 6, "beautifully in place", 96)
    subline(d, y + 20, "Countdown · Love story · Timeline · Dress code · FAQ")

    p3 = src("p3-details.jpg")
    hero = p3.crop((0, 100, p3.width, 100 + int(p3.width * 520 / 924)))

    lap = Image.open(LAPTOP).convert("RGBA")
    sx0, sy0, sx1, sy1 = LAPTOP_SCREEN
    fit = cover(hero, sx1 - sx0, sy1 - sy0)
    layer = Image.new("RGBA", lap.size, (0, 0, 0, 0))
    layer.paste(fit, (sx0, sy0))
    layer = Image.alpha_composite(layer, lap)
    layer = layer.crop((0, 640, 1080, 1330))  # tighten to the laptop itself
    scale = 940 / layer.width
    layer = layer.resize((940, int(layer.height * scale)), Image.LANCZOS)
    paste_center(img, layer, W / 2, 810)

    # second card: countdown strip under the laptop
    strip_y = int(p3.height * 0.3955)
    strip_w = p3.width
    strip_h = int(strip_w * 190 / 800)
    sx = (p3.width - strip_w) // 2
    strip = p3.crop((sx, strip_y, sx + strip_w, strip_y + strip_h)).resize((800, 190), Image.LANCZOS)
    box = (100, 1130, 900, 1320)
    img = shadow_card(img, box, radius=18)
    img.alpha_composite(rounded(strip, 18), (box[0], box[1]))

    d = ImageDraw.Draw(img)
    pills(d, ["LIVE COUNTDOWN", "EDIT IN CANVA FREE"])
    save(img, "pin-laptop-details.jpg")


# ---------------------------------------------------------------- pin 4: RSVP phone
def pin_rsvp():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 70, "BUILT-IN RSVP FORM")
    y = headline(d, 122, ["Guests RSVP right", "on your website"], 70)
    p5 = src("p5-rsvp.jpg")
    # crop to the form itself (center column of the page)
    x0 = int(p5.width * 0.28)
    x1 = int(p5.width * 0.72)
    formcrop = p5.crop((x0, 0, x1, p5.height))
    ph = phone_with(formcrop, 990)
    paste_center(img, ph, W / 2, 872)
    d = ImageDraw.Draw(img)
    pills(d, ["NO PAPER", "NO CHASING", "ONE LINK"])
    save(img, "pin-rsvp-phone.jpg")


# ---------------------------------------------------------------- pin 5: gallery
def pin_gallery():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 74, "PHOTO GALLERY PAGE")
    y = headline(d, 128, ["Your story,"], 70)
    y = script_line(d, y + 6, "in pictures", 100)
    subline(d, y + 18, "A separate gallery page for the moments that brought you here")
    p6 = src("p6-gallery.jpg")
    top = p6.crop((0, 0, p6.width, int(p6.height * 0.42)))
    crop = cover(top, 860, 830, anchor="top")
    box = (70, 502, 930, 1332)
    img = shadow_card(img, box)
    img.alpha_composite(rounded(crop, 26), (box[0], box[1]))
    d = ImageDraw.Draw(img)
    pills(d, ["GALLERY PAGE", "ADD YOUR PHOTOS", "CANVA FREE"])
    save(img, "pin-gallery.jpg")


if __name__ == "__main__":
    pin_envelope()
    pin_menu_phone()
    pin_laptop()
    pin_rsvp()
    pin_gallery()


# ================================================================ batch 2
def label_under(d, cx, y, s):
    f = font("Montserrat.ttf", 20, 600)
    tr = 4
    w = text_w(d, s, f, tr)
    draw_tracked(d, (cx - w / 2, y), s, f, TAUPE, tr)


def rot_card(im, angle, radius=16):
    """Rounded card with a soft edge, rotated, on transparent layer."""
    card = rounded(im, radius)
    return card.rotate(angle, expand=True, resample=Image.BICUBIC)


# ---------------------------------------------------------------- pin 6: all six pages
def pin_six_pages():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 64, "COMPLETE WEDDING WEBSITE")
    y = headline(d, 112, ["One link."], 66)
    y = script_line(d, y + 2, "Six beautiful pages", 92)

    pages = [
        ("p1-envelope.jpg", "ENVELOPE", "top"),
        ("p2-menu.jpg", "INVITATION", "top"),
        ("p3-details.jpg", "DETAILS", "top"),
        ("p4-travel.jpg", "TRAVEL & STAY", "top"),
        ("p5-rsvp.jpg", "RSVP", "top"),
        ("p6-gallery.jpg", "GALLERY", "top"),
    ]
    cw, ch, lw = 424, 264, 40  # card size + label band
    gx, gy = 36, 34
    x0 = (W - (2 * cw + gx)) / 2
    y0 = 400
    for i, (name, label, anchor) in enumerate(pages):
        r, c = divmod(i, 2)
        im = src(name)
        if name == "p3-details.jpg":
            im = im.crop((0, 100, im.width, 100 + int(im.width * ch / cw)))
        if name == "p6-gallery.jpg":
            im = im.crop((0, 0, im.width, int(im.height * 0.35)))
        if name == "p2-menu.jpg":
            im = im.crop((0, int(im.height*0.06), im.width, im.height))
        crop = cover(im, cw, ch, anchor=anchor)
        cx = x0 + c * (cw + gx)
        cy = y0 + r * (ch + lw + gy)
        box = (cx, cy, cx + cw, cy + ch)
        img_l = shadow_card(img, box, radius=14, blur=12, alpha=48, offset=(0, 8))
        img.paste(img_l, (0, 0))
        img.alpha_composite(rounded(crop, 14), (int(cx), int(cy)))
        d = ImageDraw.Draw(img)
        label_under(d, cx + cw / 2, cy + ch + 12, label)
    pills(d, ["RSVP FORM", "COUNTDOWN", "EDIT IN CANVA"])
    save(img, "pin-six-pages.jpg")


# ---------------------------------------------------------------- pin 7: full details scroll
def pin_full_scroll():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 64, "EVERY SECTION INCLUDED")
    y = headline(d, 112, ["The whole website,"], 64)
    y = script_line(d, y + 4, "at a glance", 94)

    p3 = src("p3-details.jpg")
    cols, gap = 3, 22
    col_h = 920
    col_w = (900 - gap * (cols - 1)) // cols
    seg = p3.height // cols
    x = (W - (col_w * cols + gap * (cols - 1))) / 2
    y0 = 410
    for i in range(cols):
        strip = p3.crop((0, i * seg, p3.width, (i + 1) * seg))
        strip = strip.resize((col_w, int(seg * col_w / p3.width)), Image.LANCZOS)
        strip = strip.crop((0, 0, col_w, min(col_h, strip.height)))
        box = (x, y0, x + col_w, y0 + strip.height)
        img_l = shadow_card(img, box, radius=12, blur=12, alpha=46, offset=(0, 8))
        img.paste(img_l, (0, 0))
        img.alpha_composite(rounded(strip, 12), (int(x), y0))
        x += col_w + gap
    d = ImageDraw.Draw(img)
    pills(d, ["COUNTDOWN", "TIMELINE", "DRESS CODE", "FAQ"])
    save(img, "pin-full-scroll.jpg")


# ---------------------------------------------------------------- pin 8: guest journey
def pin_journey():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 60, "WHAT YOUR GUESTS SEE")
    y = headline(d, 106, ["Not just a link -"], 62)
    y = script_line(d, y + 2, "a little journey", 90)

    steps = [
        ("p1-envelope.jpg", "They tap the sealed envelope", "center"),
        ("p2-menu.jpg", "Your invitation unfolds", "top"),
        ("p3-details.jpg", "Details, countdown & timeline", "top"),
        ("p5-rsvp.jpg", "They RSVP right there", "top"),
    ]
    iw, ih = 400, 196
    row_h = 240
    y0 = 392
    numf = font("PlayfairDisplay.ttf", 44, 560)
    txtf = font("Montserrat.ttf", 26, 520)
    for i, (name, caption, anchor) in enumerate(steps):
        im = src(name)
        if name == "p3-details.jpg":
            im = im.crop((0, int(im.height * 0.3955), im.width, int(im.height * 0.3955) + int(im.width * ih / iw)))
        if name == "p5-rsvp.jpg":
            im = im.crop((int(im.width*0.25), int(im.height*0.30), int(im.width*0.75), im.height))
        crop = cover(im, iw, ih, anchor=anchor)
        left = i % 2 == 0
        ix = 70 if left else W - 70 - iw
        iy = y0 + i * row_h
        box = (ix, iy, ix + iw, iy + ih)
        img_l = shadow_card(img, box, radius=14, blur=12, alpha=46, offset=(0, 8))
        img.paste(img_l, (0, 0))
        img.alpha_composite(rounded(crop, 14), (ix, iy))
        d = ImageDraw.Draw(img)
        # number + caption on the other side
        tx0 = ix + iw + 44 if left else 70
        tx1 = W - 70 if left else ix - 44
        n = str(i + 1)
        d.text((tx0, iy + 30), n, font=numf, fill=BROWN)
        words, line, lines = caption.split(), "", []
        for wd in words:
            t = (line + " " + wd).strip()
            if d.textlength(t, font=txtf) <= tx1 - tx0:
                line = t
            else:
                lines.append(line); line = wd
        lines.append(line)
        ty = iy + 96
        for ln in lines:
            d.text((tx0, ty), ln, font=txtf, fill=(94, 78, 60))
            ty += 36
    pills(d, ["ENVELOPE ENTRY", "6 PAGES", "ONE LINK"])
    save(img, "pin-journey.jpg")


# ---------------------------------------------------------------- pin 9: vinyl / music
def pin_vinyl():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 74, "MUSIC VIDEO PAGE INCLUDED")
    y = headline(d, 128, ["An invitation that"], 66)
    y = script_line(d, y + 4, "plays your song", 96)
    subline(d, y + 18, "Vinyl details · your track · animated envelope opening")

    p2 = src("p2-menu.jpg")
    crop = p2.crop((int(p2.width*0.13), 0, int(p2.width*0.87), int(p2.height * 0.36)))
    crop = cover(crop, 840, 780, anchor="top")
    box = (80, 540, 920, 1320)
    img = shadow_card(img, box)
    img.alpha_composite(rounded(crop, 26), (box[0], box[1]))
    d = ImageDraw.Draw(img)
    pills(d, ["ADD YOUR MUSIC", "EDIT IN CANVA FREE"])
    save(img, "pin-vinyl.jpg")


# ---------------------------------------------------------------- pin 10: envelope -> menu duo
def pin_duo():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 70, "ENVELOPE ENTRY PAGE")
    y = headline(d, 122, ["Tap the envelope -"], 64)
    y = script_line(d, y + 2, "the wedding unfolds", 94)

    p1 = src("p1-envelope.jpg")
    env = p1.crop((int(p1.width*0.28), 0, int(p1.width*0.72), p1.height))
    ph1 = phone_with(env, 880).rotate(4, expand=True, resample=Image.BICUBIC)
    ph2 = phone_with(src("p2-menu.jpg"), 880).rotate(-4, expand=True, resample=Image.BICUBIC)
    paste_center(img, ph1, 300, 900)
    paste_center(img, ph2, 700, 940)
    d = ImageDraw.Draw(img)
    pills(d, ["ONE LINK", "6 PAGES", "RSVP & COUNTDOWN"])
    save(img, "pin-duo-phones.jpg")
