"""Pinterest pins for the ivory embossed-frame animated save the date
(Etsy listing 4537052447, Canva design family Save_the_Date_1.0 / Frame
Project - Ivory).

Frames are extracted from pins/ivory-frame-save-the-date/src/video-nophoto.mp4
(the clean no-photo version, matching the listing screenshots), composed in
the same layout system as the victoria-michael-website pins.

Run from the repo root: python3 pins/ivory-frame-save-the-date/make_pins.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "pins", "victoria-michael-website"))
import make_pins as vm
from make_pins import (Image, ImageDraw, eyebrow, headline, script_line, subline,
                       pills, canvas, rounded, shadow_card, phone_with, cover,
                       paste_center, label_under)

HERE = os.path.join(ROOT, "pins", "ivory-frame-save-the-date")
SRC = os.path.join(HERE, "src")
vm.OUT = os.path.join(ROOT, "output", "pins", "ivory-frame-save-the-date")
W, H = vm.W, vm.H

FRAMES = {  # frame index in the 480-frame video
    "seal": 10,
    "savethedate": 105,
    "names": 225,
    "calendar": 330,
    "rsvp": 450,
}


def extract_frames():
    import imageio.v3 as iio
    have = all(os.path.exists(os.path.join(SRC, f"{k}.jpg")) for k in FRAMES)
    if have:
        return
    frames = list(iio.imiter(os.path.join(SRC, "video-nophoto.mp4")))
    for name, ix in FRAMES.items():
        Image.fromarray(frames[ix]).save(os.path.join(SRC, f"{name}.jpg"), quality=95)
        print("frame", name, ix)


def frame(name):
    return Image.open(os.path.join(SRC, f"{name}.jpg")).convert("RGB")


# ---------------------------------------------------------------- pin 1: seal hero
def pin_seal():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 74, "ANIMATED SAVE THE DATE VIDEO")
    y = headline(d, 128, ["Sealed with wax,"], 68)
    y = script_line(d, y + 4, "sent by phone", 96)
    subline(d, y + 18, "An embossed envelope opens - and your date is saved")
    crop = cover(frame("seal"), 760, 830, anchor="center")
    box = (120, 470, 880, 1300)
    img = shadow_card(img, box)
    img.alpha_composite(rounded(crop, 26), (box[0], box[1]))
    d = ImageDraw.Draw(img)
    pills(d, ["EDITABLE IN CANVA FREE", "INSTANT DOWNLOAD"])
    vm.save(img, "pin-seal-hero.jpg")


# ---------------------------------------------------------------- pin 2: story strip
def pin_story():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 64, "A VIDEO INVITATION IN 3 ACTS")
    y = headline(d, 112, ["One tap -"], 64)
    y = script_line(d, y + 2, "the whole story", 94)
    cards = [("seal", "THE SEAL"), ("names", "YOUR NAMES"), ("calendar", "THE DATE")]
    cw, ch = 292, 610
    gap = 24
    x = (W - (cw * 3 + gap * 2)) / 2
    y0 = 420
    for name, label in cards:
        crop = cover(frame(name), cw, ch, anchor="center")
        box = (x, y0, x + cw, y0 + ch)
        img_l = shadow_card(img, box, radius=16, blur=12, alpha=48, offset=(0, 8))
        img.paste(img_l, (0, 0))
        img.alpha_composite(rounded(crop, 16), (int(x), y0))
        d = ImageDraw.Draw(img)
        label_under(d, x + cw / 2, y0 + ch + 14, label)
        x += cw + gap
    subline(d, 1128, "Then a built-in RSVP link - guests reply in one tap")
    pills(d, ["ANIMATED VIDEO", "RSVP & QR", "CANVA FREE"])
    vm.save(img, "pin-story-strip.jpg")


# ---------------------------------------------------------------- pin 3: names on phone
def pin_names():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 70, "ELEGANT VIDEO SAVE THE DATE")
    y = headline(d, 122, ["Your names,", "beautifully in motion"], 66)
    ph = phone_with(frame("names"), 1000)
    paste_center(img, ph, W / 2, 878)
    d = ImageDraw.Draw(img)
    pills(d, ["EDIT NAMES & DATE", "SEND BY TEXT OR EMAIL"])
    vm.save(img, "pin-names-phone.jpg")


# ---------------------------------------------------------------- pin 4: calendar
def pin_calendar():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 70, "SAVE OUR DATE")
    y = headline(d, 122, ["A date they will", "never forget"], 66)
    ph = phone_with(frame("calendar"), 1000)
    paste_center(img, ph, W / 2, 878)
    d = ImageDraw.Draw(img)
    pills(d, ["YOUR MONTH & DAY", "ANIMATED HEART", "CANVA"])
    vm.save(img, "pin-calendar-phone.jpg")


# ---------------------------------------------------------------- pin 5: rsvp qr
def pin_rsvp_qr():
    img = canvas().convert("RGBA")
    d = ImageDraw.Draw(img)
    eyebrow(d, 74, "RSVP BUILT INTO THE VIDEO")
    y = headline(d, 128, ["They watch, they scan,"], 62)
    y = script_line(d, y + 4, "they reply", 96)
    crop = cover(frame("rsvp"), 700, 800, anchor="center")
    box = (150, 490, 850, 1290)
    img = shadow_card(img, box)
    img.alpha_composite(rounded(crop, 26), (box[0], box[1]))
    d = ImageDraw.Draw(img)
    pills(d, ["QR CODE RSVP", "NO PAPER", "ONE LINK"])
    vm.save(img, "pin-rsvp-qr.jpg")


if __name__ == "__main__":
    extract_frames()
    pin_seal()
    pin_story()
    pin_names()
    pin_calendar()
    pin_rsvp_qr()
