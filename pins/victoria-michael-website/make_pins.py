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
    subline(d, y + 20, "Countdown · Timeline · Dress code · Travel & Stay")

    p3 = src("p3-details.jpg")
    hero = p3.crop((0, 0, p3.width, int(p3.width * 520 / 924)))

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
    eyebrow(d, 74, "OUR STORY IN PICTURES")
    y = headline(d, 128, ["Your love story", "has its own page"], 70)
    p6 = src("p6-gallery.jpg")
    top = p6.crop((0, 0, p6.width, int(p6.height * 0.42)))
    crop = cover(top, 860, 880, anchor="top")
    box = (70, 452, 930, 1332)
    img = shadow_card(img, box)
    img.alpha_composite(rounded(crop, 26), (box[0], box[1]))
    d = ImageDraw.Draw(img)
    pills(d, ["PHOTO GALLERY", "LOVE STORY PAGE", "CANVA"])
    save(img, "pin-gallery.jpg")


if __name__ == "__main__":
    pin_envelope()
    pin_menu_phone()
    pin_laptop()
    pin_rsvp()
    pin_gallery()
