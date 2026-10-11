#!/usr/bin/env python3
"""VistelaCo Studio — brand content generator.

  python3 studio.py reel  INPUT.mp4 --hook "..." [--cta DATE] [--out out/x.mp4]
  python3 studio.py carousel spec.json      (slides -> 1080x1350 PNG)
  python3 studio.py story    spec.json      (frames -> 1080x1920 PNG)
  python3 studio.py highlights              (all highlight covers)
"""
import argparse, json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")

# ── Brand ────────────────────────────────────────────────────────────
EMERALD = "#1E4736"
IVORY = "#FBF8F2"
GOLD = "#C9A867"
INK = "#0F1F18"

def font(name, size, weight=None):
    path = {
        "serif": "PlayfairDisplay.ttf",
        "serif-italic": "PlayfairDisplay-Italic.ttf",
        "sans": "OpenSans.ttf",
        "hook": "ArchivoBlack.ttf",   # Latin only — English hooks
    }[name]
    f = ImageFont.truetype(os.path.join(FONTS, path), size)
    if weight:
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
    return f

def wrap(draw, text, f, max_w):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=f) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines

def text_block(draw, text, f, cx, y, max_w, fill, spacing=1.25, align="center"):
    """Draw wrapped text; returns bottom y."""
    lh = int(f.size * spacing)
    for line in wrap(draw, text, f, max_w):
        w = draw.textlength(line, font=f)
        x = cx - w / 2 if align == "center" else cx
        draw.text((x, y), line, font=f, fill=fill)
        y += lh
    return y

def block_height(draw, text, f, max_w, spacing=1.25):
    return len(wrap(draw, text, f, max_w)) * int(f.size * spacing)

def gold_rule(draw, cx, y, w=90):
    draw.line([(cx - w // 2, y), (cx + w // 2, y)], fill=GOLD, width=2)

def monogram(draw, cx, cy, r, on_dark=True):
    """Placeholder mark: italic V in a thin gold ring (logo not final)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=max(2, r // 30))
    f = font("serif-italic", int(r * 1.15))
    col = IVORY if on_dark else EMERALD
    draw.text((cx, cy + r * 0.05), "V", font=f, fill=col, anchor="mm")

# ── Reels ────────────────────────────────────────────────────────────
W, H = 1080, 1920

def native_text(text, path, top, size=64):
    """Instagram-native look: white Open Sans Bold, soft shadow, no box."""
    from PIL import ImageFilter
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font("sans", size, "Bold")
    while block_height(d, text, f, 900, 1.22) > 380 and size > 44:
        size -= 4
        f = font("sans", size, "Bold")
    for blur, alpha, dy in ((10, 170, 4), (2, 200, 2)):   # soft glow + tight edge for light backgrounds
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        text_block(ImageDraw.Draw(sh), text, f, W / 2, top + dy, 900, (0, 0, 0, alpha), 1.22)
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(blur)))
    text_block(ImageDraw.Draw(img), text, f, W / 2, top, 900, (255, 255, 255, 255), 1.22)
    img.save(path)

def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                                   "-of", "json", path])
    j = json.loads(out)
    return float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j["streams"])

def reel(args):
    """Native reel: hook on top for the first seconds, CTA over the last seconds. No end card, no brand box."""
    dur, has_audio = probe(args.input)
    hook_end = min(args.hook_seconds, dur)
    cta_start = max(hook_end, dur - args.cta_seconds)
    tmp = tempfile.mkdtemp()
    hp, cp = os.path.join(tmp, "hook.png"), os.path.join(tmp, "cta.png")
    native_text(args.hook, hp, top=250)
    inputs = ["-i", args.input, "-loop", "1", "-t", str(dur), "-i", hp]
    fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,format=yuv420p[base];"
          f"[1:v]format=rgba,fade=t=out:st={max(hook_end-0.3,0)}:d=0.3:alpha=1[hk];"
          f"[base][hk]overlay=0:0:enable='lt(t,{hook_end})'[v1]")
    last = "v1"
    if args.cta:
        native_text(f"Comment {args.cta} for the link", cp, top=1300, size=56)
        inputs += ["-loop", "1", "-t", str(dur), "-i", cp]
        fc += (f";[2:v]format=rgba,fade=t=in:st={cta_start}:d=0.3:alpha=1[ct];"
               f"[{last}][ct]overlay=0:0:enable='gte(t,{cta_start})'[v2]")
        last = "v2"
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", f"[{last}]"]
    if has_audio and not args.mute:
        cmd += ["-map", "0:a", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", "-t", str(dur), args.out]
    subprocess.run(cmd, check=True)
    # cover frame for the grid
    cover = os.path.splitext(args.out)[0] + "_cover.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(min(1.0, hook_end / 2)), "-i", args.out,
                    "-frames:v", "1", "-q:v", "2", cover], check=True)
    print(args.out, cover)

# ── Carousels & stories ──────────────────────────────────────────────
def render_slide(s, size, idx, total):
    w, h = size
    dark = s.get("theme", "light") == "dark"
    bg, fg, accent = (EMERALD, IVORY, IVORY) if dark else (IVORY, INK, EMERALD)
    img = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(img)
    pad = int(w * 0.1)
    maxw = w - 2 * pad
    kind = s.get("type", "content")

    if kind == "photo":
        # full-bleed photo, dark gradient at the bottom, title over it
        ph = Image.open(s["image"]).convert("RGB")
        sc = max(w / ph.width, h / ph.height)
        ph = ph.resize((int(ph.width * sc) + 1, int(ph.height * sc) + 1))
        ph = ph.crop(((ph.width - w) // 2, (ph.height - h) // 2, (ph.width - w) // 2 + w, (ph.height - h) // 2 + h))
        d = ImageDraw.Draw(ph)
        ft = font("serif", int(w * 0.08))
        fb = font("sans", int(w * 0.036))
        th = block_height(d, s["title"], ft, maxw, 1.15)
        bh = block_height(d, s.get("body", ""), fb, maxw, 1.45) if s.get("body") else 0
        story = h > 1.6 * w   # IG story UI + link sticker cover the bottom ~22%
        y = h - int(h * (0.27 if story else 0.11)) - th - (bh + 50 if bh else 0)
        top = y - (int(w * 0.07) if s.get("kicker") else 0)
        # gradient starts just above the text, not at a fixed height
        g0, g1 = top - int(h * 0.13), top + int(h * 0.02)
        grad = Image.new("L", (1, h))
        for yy in range(h):
            t = min(1, max(0, (yy - g0) / max(1, g1 - g0)))
            a = 215 * t ** 1.3
            if story and yy > h * 0.8:   # let the photo show again below the text
                a *= 1 - 0.6 * min(1, (yy - h * 0.8) / (h * 0.15))
            grad.putpixel((0, yy), int(a))
        ph.paste(Image.new("RGB", (w, h), INK), (0, 0), grad.resize((w, h)))
        img = ph
        d = ImageDraw.Draw(img)
        if s.get("kicker"):
            d.text((pad, y - int(w * 0.07)), s["kicker"].upper(), font=font("sans", int(w * 0.03), "SemiBold"), fill=GOLD)
        y = text_block(d, s["title"], ft, pad, y, maxw, IVORY, 1.15, "left")
        if bh:
            text_block(d, s["body"], fb, pad, y + 30, maxw, IVORY, 1.45, "left")
        fs = font("sans", int(w * 0.026), "Regular")
        if not story:
            d.text((pad, h - int(h * 0.045)), "VISTELACO", font=fs, fill=GOLD, anchor="lm")
        if total > 1 and not story:
            d.text((w - pad, h - int(h * 0.045)), f"{idx}/{total}", font=fs, fill=GOLD, anchor="rm")
        return img

    if s.get("image"):
        ph = Image.open(s["image"]).convert("RGB")
        box_h = int(h * 0.5)
        ph = ph.resize((maxw, int(ph.height * maxw / ph.width)))
        ph = ph.crop((0, max(0, (ph.height - box_h) // 2), maxw, max(0, (ph.height - box_h) // 2) + box_h))
        mask = Image.new("L", ph.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, *ph.size], radius=28, fill=255)
        img.paste(ph, (pad, int(h * 0.38)), mask)

    if kind == "cover":
        monogram(d, w // 2, int(h * 0.2), int(w * 0.06), dark)
        y = int(h * 0.32)
        y = text_block(d, s["title"], font("serif", int(w * 0.088)), w / 2, y, maxw, accent, 1.15)
        gold_rule(d, w // 2, y + 30)
        if s.get("subtitle"):
            text_block(d, s["subtitle"], font("serif-italic", int(w * 0.045)), w / 2, y + 70, maxw, fg, 1.35)
    elif kind == "cta":
        y = int(h * 0.3)
        y = text_block(d, s["title"], font("serif", int(w * 0.075)), w / 2, y, maxw, accent, 1.18)
        gold_rule(d, w // 2, y + 30)
        if s.get("body"):
            y = text_block(d, s["body"], font("sans", int(w * 0.036)), w / 2, y + 80, maxw, fg, 1.5)
        if s.get("button"):
            f = font("sans", int(w * 0.038), "SemiBold")
            tw = d.textlength(s["button"], font=f)
            bx0, by0 = w / 2 - tw / 2 - 50, y + 60
            d.rounded_rectangle([bx0, by0, w / 2 + tw / 2 + 50, by0 + 110], radius=55,
                                fill=IVORY if dark else EMERALD)
            d.text((w / 2, by0 + 55), s["button"], font=f, fill=EMERALD if dark else IVORY, anchor="mm")
    else:
        fk = font("sans", int(w * 0.03), "SemiBold")
        ft = font("serif", int(w * 0.082))
        fb = font("sans", int(w * 0.043))
        kh = int(w * 0.075) if s.get("kicker") else 0
        th = block_height(d, s["title"], ft, maxw, 1.15)
        if s.get("image"):
            y = int(h * 0.12)
        else:
            bh = block_height(d, s.get("body", ""), fb, maxw, 1.5) if s.get("body") else 0
            y = int((h - (kh + th + 80 + bh)) / 2 - h * 0.03)
        if s.get("kicker"):
            d.text((pad, y), s["kicker"].upper(), font=fk, fill=GOLD)
            y += kh
        y = text_block(d, s["title"], ft, pad, y, maxw, accent, 1.15, "left")
        d.line([(pad, y + 24), (pad + 110, y + 24)], fill=GOLD, width=3)
        if s.get("body") and not s.get("image"):
            text_block(d, s["body"], fb, pad, y + 80, maxw, fg, 1.5, "left")
        elif s.get("body"):
            text_block(d, s["body"], font("sans", int(w * 0.036)), pad, int(h * 0.38) + int(h * 0.5) + 30,
                       maxw, fg, 1.45, "left")

    # footer
    fs = font("sans", int(w * 0.026), "Regular")
    if h > 1.6 * w:   # stories: bottom is covered by IG UI, no footer
        return img
    d.text((pad, h - int(h * 0.055)), "VISTELACO", font=fs, fill=GOLD, anchor="lm")
    if total > 1:
        d.text((w - pad, h - int(h * 0.055)), f"{idx}/{total}", font=fs, fill=GOLD, anchor="rm")
    return img

def render_set(spec_path, size, suffix):
    spec = json.load(open(spec_path))
    name = spec.get("name", os.path.splitext(os.path.basename(spec_path))[0])
    os.makedirs(os.path.join(ROOT, "out", name), exist_ok=True)
    slides = spec["slides"]
    paths = []
    for i, s in enumerate(slides, 1):
        img = render_slide(s, size, i, len(slides) if suffix == "slide" else 1)
        p = os.path.join(ROOT, "out", name, f"{suffix}-{i:02d}.png")
        img.save(p)
        paths.append(p)
    print("\n".join(paths))

# ── Highlight covers ────────────────────────────────────────────────
# Seasonal covers go right after Shop while their season is live (Halloween until 31 Oct)
HIGHLIGHTS = ["Shop", "Halloween", "Christmas", "Save the Date", "Birthday", "Websites",
              "Reviews", "How it works", "FAQ", "Hi, I'm Diana"]

def icon(d, name, cx, cy, r):
    c, lw = IVORY, 10
    if name == "Shop":
        d.rounded_rectangle([cx - r, cy - r * 0.55, cx + r, cy + r], radius=16, outline=c, width=lw)
        d.arc([cx - r * 0.5, cy - r * 1.15, cx + r * 0.5, cy - r * 0.05], 180, 360, fill=c, width=lw)
    elif name == "Save the Date":
        d.rectangle([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], outline=c, width=lw)
        d.line([(cx - r, cy - r * 0.7), (cx, cy + r * 0.1), (cx + r, cy - r * 0.7)], fill=c, width=lw, joint="curve")
        d.ellipse([cx - 22, cy - 2, cx + 22, cy + 42], fill=GOLD)
    elif name == "Christmas":
        d.ellipse([cx - r * 0.8, cy - r * 0.55, cx + r * 0.8, cy + r * 1.05], outline=c, width=lw)
        d.rectangle([cx - 26, cy - r * 0.9, cx + 26, cy - r * 0.55], fill=GOLD)
        d.arc([cx - 24, cy - r * 1.25, cx + 24, cy - r * 0.85], 180, 360, fill=c, width=8)
    elif name == "Halloween":
        top, bot = cy - r * 0.55, cy + r * 0.85
        for x0, x1 in ((cx - r, cx + r * 0.1), (cx - r * 0.1, cx + r), (cx - r * 0.45, cx + r * 0.45)):
            d.ellipse([x0, top, x1, bot], fill=EMERALD, outline=c, width=lw)  # centre lobe drawn last hides overlaps
        d.line([(cx, top), (cx + 16, cy - r * 0.95)], fill=GOLD, width=lw + 6)
    elif name == "Birthday":
        d.rounded_rectangle([cx - r, cy - r * 0.05, cx + r, cy + r * 0.85], radius=14, outline=c, width=lw)
        d.line([(cx - r, cy + r * 0.35), (cx + r, cy + r * 0.35)], fill=c, width=6)
        for dx in (-0.55, 0, 0.55):
            x = cx + r * dx
            d.line([(x, cy - r * 0.55), (x, cy - r * 0.05)], fill=c, width=lw)
            d.ellipse([x - 13, cy - r * 0.85, x + 13, cy - r * 0.6], fill=GOLD)
    elif name == "Reviews":
        import math
        pts = [(cx + (r if k % 2 == 0 else r * 0.42) * math.sin(k * math.pi / 5),
                cy + 10 - (r if k % 2 == 0 else r * 0.42) * math.cos(k * math.pi / 5)) for k in range(10)]
        d.polygon(pts, outline=c, width=lw)
        d.ellipse([cx - 18, cy - 8, cx + 18, cy + 28], fill=GOLD)
    elif name == "How it works":
        for i, yy in enumerate([-0.6, 0, 0.6]):
            y0 = cy + r * yy
            d.ellipse([cx - r, y0 - 20, cx - r + 40, y0 + 20], fill=GOLD)
            d.line([(cx - r + 70, y0), (cx + r, y0)], fill=c, width=lw)
    elif name == "FAQ":
        d.text((cx, cy), "?", font=font("serif", int(r * 2.2)), fill=c, anchor="mm")
    elif name == "Websites":
        d.rounded_rectangle([cx - r * 0.6, cy - r, cx + r * 0.6, cy + r], radius=30, outline=c, width=lw)
        d.line([(cx - 30, cy + r * 0.78), (cx + 30, cy + r * 0.78)], fill=GOLD, width=lw)
    else:
        d.text((cx, cy), "D", font=font("serif-italic", int(r * 2)), fill=c, anchor="mm")

def highlights(_):
    out = os.path.join(ROOT, "out", "highlights")
    os.makedirs(out, exist_ok=True)
    for i, name in enumerate(HIGHLIGHTS, 1):
        img = Image.new("RGB", (W, H), EMERALD)
        d = ImageDraw.Draw(img)
        # safe zone: IG crops to a centred circle
        d.ellipse([W / 2 - 300, H / 2 - 300, W / 2 + 300, H / 2 + 300], outline=GOLD, width=3)
        icon(d, name, W // 2, H // 2, 150)
        p = os.path.join(out, f"{i:02d}-{name.lower().replace(' ', '-').replace(',', '').replace(chr(39), '')}.png")
        img.save(p)
        print(p)

# ── CLI ─────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reel")
    r.add_argument("input")
    r.add_argument("--hook", required=True)
    r.add_argument("--cta", default="DATE", help="empty string to skip")
    r.add_argument("--hook-seconds", type=float, default=3.0)
    r.add_argument("--cta-seconds", type=float, default=2.5)
    r.add_argument("--mute", action="store_true", help="drop original audio")
    r.add_argument("--out")
    c = sub.add_parser("carousel"); c.add_argument("spec")
    s = sub.add_parser("story"); s.add_argument("spec")
    sub.add_parser("highlights")
    a = ap.parse_args()
    if a.cmd == "reel":
        a.out = a.out or os.path.join(ROOT, "out", os.path.splitext(os.path.basename(a.input))[0] + "_reel.mp4")
        reel(a)
    elif a.cmd == "carousel":
        render_set(a.spec, (1080, 1350), "slide")
    elif a.cmd == "story":
        render_set(a.spec, (1080, 1920), "story")
    else:
        highlights(a)

if __name__ == "__main__":
    main()
