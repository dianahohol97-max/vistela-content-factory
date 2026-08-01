"""Build step (run by GitHub Actions).

- Renders all palette pins (2:3) -> output/pins/
- Builds the next few biweekly carousels with ANTI-REPEAT (consecutive
  carousels never share a palette) -> output/carousels/
- Writes queue/pin_queue.json and queue/carousel_queue.json with raw-CDN URLs.

Make posters (deployed separately by Adrian) read the queues and dedup by id in
their own Data Store, so regenerating the queue here is safe/idempotent.
"""
import json
import os
import glob
import hashlib
import datetime as dt
import config as C
import render as R
import render_reel as RR
import rotation as ROT

ROOT = os.path.dirname(os.path.abspath(__file__))
PINS_DIR = os.path.join(ROOT, "output", "pins")
CARS_DIR = os.path.join(ROOT, "output", "carousels")
Q_DIR = os.path.join(ROOT, "queue")
UPCOMING_CAROUSELS = 4   # ~2 months of runway at 1 / 2 weeks


def raw(path_from_root):
    return f"{C.RAW}/{path_from_root.replace(os.sep, '/')}"


VIDEO_EXTS = ("*.mp4", "*.mov", "*.m4v", "*.webm")


def _videos(folder):
    """All video files under a folder (any supported extension), recursive."""
    files = []
    for pat in VIDEO_EXTS:
        files += glob.glob(os.path.join(folder, "**", pat), recursive=True)
    return sorted(files)


def build_pins():
    items = []
    for pal in C.PALETTES:
        rel = f"output/pins/{pal['slug']}.png"
        R.palette_pin(pal, os.path.join(ROOT, rel))
        items.append({
            "id": f"PIN_{pal['slug']}",
            "channels": ["pinterest"],
            "format": "pin",
            "title": f"{pal['name']} Wedding Colour Palette",
            "description": (f"{pal['name']} \u2014 a {pal['trend'].lower()} wedding palette for 2026. "
                            f"Editable, animated wedding invitations & websites from VistelaCo. "
                            f"#{pal['slug'].replace('-', '')}wedding"),
            "link": pal["link"],
            "image_url": raw(rel),
            "board_id": C.PALETTE_BOARD_ID,
            "status": "ready",
        })
    return items


def build_carousels():
    """Anti-repeat: split the library into disjoint sets of 5 and alternate them,
    so no two consecutive carousels share a palette."""
    pals = C.PALETTES
    sets = [pals[i:i + 5] for i in range(0, len(pals), 5) if len(pals[i:i + 5]) == 5]
    if not sets:
        return []
    # deterministic starting point from the ISO week so scheduled runs stay in phase
    start = dt.date.today().isocalendar()[1] // 2
    items = []
    for k in range(UPCOMING_CAROUSELS):
        chosen = sets[(start + k) % len(sets)]
        cid = f"CAR_{k:02d}_{'-'.join(p['slug'] for p in chosen[:1])}"
        out_dir = os.path.join(CARS_DIR, cid)
        paths = R.carousel(chosen, out_dir)
        slides = [raw(os.path.relpath(p, ROOT)) for p in paths]
        names = [p["name"] for p in chosen]
        caption = C.CAPTION_TEMPLATE.format(a=names[0], b=names[1], c=names[2])
        items.append({
            "id": cid,
            "channels": ["instagram_carousel", "facebook"],
            "format": "carousel",
            "caption": caption,
            "slides": slides,          # ordered JPEG/PNG URLs (export JPEG for IG)
            "palettes": names,
            "status": "ready",
        })
    return items


def _yt_title(hook, kw):
    """SEO title for YouTube Shorts. The video hook (curiosity/benefit) leads for
    click-through; a title-case keyword phrase is appended for search, and #Shorts
    tags it as a Short. Only YouTube reads the `title` field, so this never touches
    the IG/TikTok captions. Capped at YouTube's 100-char limit."""
    kw_tc = " ".join(w.capitalize() for w in kw.split())
    base = f"{hook} | {kw_tc}"
    title = base if len(base) <= 90 else hook
    return (title + " #Shorts")[:100]


def _yt_description(copy, kw, link):
    """SEO description for YouTube Shorts. The first line is keyword-rich (that's
    what search indexes), followed by the value prop, a clear CTA + link, and a
    hashtag block (the first 3 hashtags render above the title)."""
    hashtags = " ".join("#" + t for t in copy["yt_hashtags"])
    return (
        f"{copy['value']}\n\n"
        f"✨ 100% editable in Canva — change the names, dates and colours in "
        f"minutes. No designer, no software, delivered instantly.\n"
        f"\U0001F6CD️ Shop this {kw} on Etsy → {link}\n\n"
        f"Animated, editable wedding stationery by VistelaCo — save the dates, "
        f"invitations and wedding websites your guests will actually remember.\n\n"
        f"{hashtags}"
    )


def _prune_reels(out_dir, keep=80):
    """Keep the newest `keep` files in the reels folder.

    NOTE: `keep` counts FILES, and every reel is two files (.mp4 + _cover.jpg),
    so keep=80 retains ~40 reels. This must stay well above Buffer's TikTok queue
    depth: Buffer fetches the raw.githubusercontent video URL at publish time, not
    when the post is queued, and on the Free plan it drains the queue slowly. If a
    reel is pruned before Buffer publishes it, the URL 404s and the post fails with
    'media URL not publicly accessible'. ~40 reels of runway keeps URLs alive far
    longer than the queue can lag. (Full history is in git regardless.)"""
    if not os.path.isdir(out_dir):
        return
    files = sorted((os.path.join(out_dir, f) for f in os.listdir(out_dir)),
                   key=os.path.getmtime, reverse=True)
    for f in files[keep:]:
        try:
            os.remove(f)
        except OSError:
            pass


def build_reels():
    """Phone-reveal reels via the rotation backlog: pair each scene with a
    product (oldest-first, quarantine-aware), rotate the hook, keep the feed even
    at REELS_PER_RUN/day with no repeated pairs. Captions are per product type
    and per platform (clean IG, tagged TikTok/Shorts). Falls back to Hook->Reveal
    when no wedding scenes are available."""
    import re
    items = []
    products = _videos(os.path.join(ROOT, C.INPUT_TEMPLATES))
    scenes = _videos(os.path.join(ROOT, C.INPUT_SCENES))
    if not products:
        return items
    out_dir = os.path.join(ROOT, "output", "reels")
    today = dt.date.today()

    if scenes:
        jobs = ROT.next_pairs(ROOT, scenes, products, C.REELS_PER_RUN, today)
    else:
        week = today.isocalendar()[1]
        jobs = []
        for product in products[:C.REELS_PER_RUN]:
            h = int(hashlib.md5(os.path.basename(product).encode()).hexdigest(), 16)
            jobs.append((None, product, week + h))

    for scene, product, hook_i in jobs:
        cat = C.product_category(product)
        base = os.path.splitext(os.path.basename(product))[0]
        sbase = os.path.splitext(os.path.basename(scene))[0] if scene else "solo"
        shooks = C.SHOWCASE_HOOKS.get(cat, C.SHOWCASE_HOOKS["default"])
        offset = int(hashlib.md5((sbase + base).encode()).hexdigest(), 16)
        hook = shooks[(hook_i + offset) % len(shooks)]
        slug = re.sub(r"[^a-z0-9]+", "-", f"{sbase}-{base}-{today.isoformat()}".lower()).strip("-")
        if scene:
            reel, cover = RR.assemble_phone_reveal(scene, product, hook, out_dir, slug)
        else:
            reel, cover = RR.assemble(product, hook, out_dir, slug)
        link = RR.listing_link_from_filename(base)
        copy = C.PRODUCT_COPY[cat]
        kw = copy["keyword"]
        # Instagram: clean, no hashtags, one natural keyword + CTA to bio
        ig = (f"{hook} \U0001F90D\n\n{copy['value']}\n\n"
              f"This {kw} is on Etsy \u2014 link in bio.")
        tiktok = ig + "\n\n" + " ".join("#" + t for t in copy["tiktok_tags"])
        items.append({
            "id": f"REEL_{slug}",
            "channels": ["instagram_reel", "youtube_short", "tiktok"],
            "format": "video",
            "category": C.product_category(product),
            "title": _yt_title(hook, kw),  # YouTube-only field; SEO title + #Shorts
            "video_url": raw(os.path.relpath(reel, ROOT)),
            "cover_url": raw(os.path.relpath(cover, ROOT)),
            "caption": ig,                 # Instagram (clean)
            "caption_tiktok": tiktok,      # TikTok (with tags)
            "yt_description": _yt_description(copy, kw, link),   # YouTube Shorts (SEO)
            "yt_tags": copy["yt_tags"],
            "tiktok_tags": copy["tiktok_tags"],
            "link": link,
            "share_to_feed": True,
            "status": "ready",
        })
    _prune_reels(out_dir)
    return items


def build_personalize():
    """Personalize-With-Me rubric: one screen-recording reel every
    PERSONALIZE_EVERY_DAYS, oldest-clip-first with a rotating hook."""
    import re
    items = []
    clips = _videos(os.path.join(ROOT, C.INPUT_PERSONALIZE))
    if not clips:
        return items
    today = dt.date.today()
    if today.toordinal() % C.PERSONALIZE_EVERY_DAYS != 0:   # every N days
        return items
    out_dir = os.path.join(ROOT, "output", "reels")
    clip, hook = ROT.next_single(ROOT, clips, C.PERSONALIZE_HOOKS, "pwm", today)
    base = os.path.splitext(os.path.basename(clip))[0]
    slug = re.sub(r"[^a-z0-9]+", "-", f"pwm-{base}-{today.isoformat()}".lower()).strip("-")
    reel, cover = RR.assemble_personalize(clip, hook, out_dir, slug)
    link = RR.listing_link_from_filename(base)
    copy = C.PRODUCT_COPY[C.product_category(clip)]
    kw = copy["keyword"]
    ig = (f"{hook} \U0001F90D\n\n{copy['value']}\n\nThis {kw} is on Etsy \u2014 link in bio.")
    tiktok = ig + "\n\n" + " ".join("#" + t for t in copy["tiktok_tags"])
    items.append({
        "id": f"REEL_{slug}",
        "channels": ["instagram_reel", "youtube_short", "tiktok"],
        "format": "video",
        "category": C.product_category(clip),
        "rubric": "personalize_with_me",
        "title": _yt_title(hook, kw),  # YouTube-only field; SEO title + #Shorts
        "video_url": raw(os.path.relpath(reel, ROOT)),
        "cover_url": raw(os.path.relpath(cover, ROOT)),
        "caption": ig,
        "caption_tiktok": tiktok,
        "yt_description": _yt_description(copy, kw, link),
        "yt_tags": copy["yt_tags"],
        "tiktok_tags": copy["tiktok_tags"],
        "link": link,
        "share_to_feed": True,
        "status": "ready",
    })
    _prune_reels(out_dir)
    return items




def _render_hook_overlay(hook, path):
    """Render the hook line as a transparent 1080x1920 PNG: wrapped text on a
    soft dark pill in the top third (viewers scroll muted — the hook must be
    on-screen, not only in the caption)."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
    words, lines, cur = hook.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= W - 260:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    lh = 76
    block_h = lh * len(lines)
    y0 = 230
    pad_x, pad_y = 44, 34
    box_w = max(d.textlength(l, font=font) for l in lines) + pad_x * 2
    x0 = (W - box_w) / 2
    d.rounded_rectangle([x0, y0 - pad_y, x0 + box_w, y0 + block_h + pad_y],
                        radius=34, fill=(16, 23, 31, 175))
    y = y0
    for l in lines:
        lw = d.textlength(l, font=font)
        d.text(((W - lw) / 2, y), l, font=font, fill=(247, 242, 230, 255))
        y += lh
    img.save(path)


def build_product_tour():
    """Product-tour rubric: every PRODUCT_TOUR_EVERY_DAYS post one raw product
    video as-is (normalised to 1080x1920) to Instagram + TikTok, alternating
    save-the-dates and websites. Runs on the days personalize doesn't."""
    import re
    import subprocess
    items = []
    products = _videos(os.path.join(ROOT, C.INPUT_TEMPLATES))
    if not products:
        return items
    today = dt.date.today()
    if today.toordinal() % C.PRODUCT_TOUR_EVERY_DAYS != 1:   # alternate with PWM days
        return items
    # alternate product type per tour day
    stds  = [p for p in products if C.product_category(p) == "save_the_date"]
    sites = [p for p in products if C.product_category(p) == "wedding_website"]
    cycle = (today.toordinal() // C.PRODUCT_TOUR_EVERY_DAYS) % 2
    pool = (stds if cycle == 0 else sites) or sites or stds or products
    clip, hook = ROT.next_single(ROOT, pool, C.PRODUCT_TOUR_HOOKS, "tour", today)
    out_dir = os.path.join(ROOT, "output", "reels")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(clip))[0]
    slug = re.sub(r"[^a-z0-9]+", "-", f"tour-{base}-{today.isoformat()}".lower()).strip("-")
    reel = os.path.join(out_dir, f"{slug}.mp4")
    cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    hook_png = os.path.join(out_dir, f"{slug}_hook.png")
    _render_hook_overlay(hook, hook_png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-i", hook_png,
                    "-filter_complex",
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,setsar=1,fps=30[v];"
                    f"[v][1:v]overlay=0:0:enable='lte(t,{C.HOOK_OVERLAY_SECONDS})'[out]",
                    "-map", "[out]", "-an",
                    "-t", str(C.PRODUCT_TOUR_MAX_S), "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", reel], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    os.remove(hook_png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", reel,
                    "-frames:v", "1", cover], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    link = RR.listing_link_from_filename(base)
    cat = C.product_category(clip)
    copy = C.PRODUCT_COPY.get(cat, C.PRODUCT_COPY["default"])
    kw = copy["keyword"]
    ig = (f"{hook} \U0001F90D\n\n{copy['value']}\n\nThis {kw} is on Etsy \u2014 link in bio.")
    tiktok = ig + "\n\n" + " ".join("#" + t for t in copy["tiktok_tags"])
    items.append({
        "id": f"REEL_{slug}",
        "channels": ["instagram_reel", "tiktok"],
        "format": "video",
        "category": cat,
        "rubric": "product_tour",
        "title": _yt_title(hook, kw),
        "video_url": raw(os.path.relpath(reel, ROOT)),
        "cover_url": raw(os.path.relpath(cover, ROOT)),
        "caption": ig,
        "caption_tiktok": tiktok,
        "yt_description": _yt_description(copy, kw, link),
        "yt_tags": copy["yt_tags"],
        "tiktok_tags": copy["tiktok_tags"],
        "link": link,
        "share_to_feed": True,
        "status": "ready",
    })
    _prune_reels(out_dir)
    return items

def main():
    os.makedirs(Q_DIR, exist_ok=True)
    pin_items = build_pins()
    car_items = build_carousels()
    reel_items = build_reels() + build_personalize() + build_product_tour()
    with open(os.path.join(Q_DIR, "pin_queue.json"), "w") as f:
        json.dump(pin_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "carousel_queue.json"), "w") as f:
        json.dump(car_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "video_queue.json"), "w") as f:
        json.dump(reel_items, f, indent=2, ensure_ascii=False)
    print(f"pins: {len(pin_items)}  carousels: {len(car_items)}  reels: {len(reel_items)}")


if __name__ == "__main__":
    main()
