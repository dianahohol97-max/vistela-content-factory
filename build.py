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


def _prune_reels(out_dir, keep=8):
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
    products = sorted(glob.glob(os.path.join(ROOT, C.INPUT_TEMPLATES, "**", "*.mp4"), recursive=True))
    scenes = sorted(glob.glob(os.path.join(ROOT, C.INPUT_SCENES, "**", "*.mp4"), recursive=True))
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
        yt_desc = f"{copy['value']} Shop this {kw} from VistelaCo on Etsy: {link}"
        items.append({
            "id": f"REEL_{slug}",
            "channels": ["instagram_reel", "youtube_short", "tiktok"],
            "format": "video",
            "category": C.product_category(product),
            "title": hook,
            "video_url": raw(os.path.relpath(reel, ROOT)),
            "cover_url": raw(os.path.relpath(cover, ROOT)),
            "caption": ig,                 # Instagram (clean)
            "caption_tiktok": tiktok,      # TikTok (with tags)
            "yt_description": yt_desc,     # YouTube Shorts
            "yt_tags": copy["yt_tags"],
            "tiktok_tags": copy["tiktok_tags"],
            "link": link,
            "share_to_feed": True,
            "status": "ready",
        })
    _prune_reels(out_dir, keep=8)
    return items


def build_personalize():
    """Personalize-With-Me rubric: one screen-recording reel every
    PERSONALIZE_EVERY_DAYS, oldest-clip-first with a rotating hook."""
    import re
    items = []
    clips = sorted(glob.glob(os.path.join(ROOT, C.INPUT_PERSONALIZE, "**", "*.mp4"), recursive=True))
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
    yt_desc = f"{copy['value']} Shop this {kw} from VistelaCo on Etsy: {link}"
    items.append({
        "id": f"REEL_{slug}",
        "channels": ["instagram_reel", "youtube_short", "tiktok"],
        "format": "video",
        "category": C.product_category(clip),
        "rubric": "personalize_with_me",
        "title": hook,
        "video_url": raw(os.path.relpath(reel, ROOT)),
        "cover_url": raw(os.path.relpath(cover, ROOT)),
        "caption": ig,
        "caption_tiktok": tiktok,
        "yt_description": yt_desc,
        "yt_tags": copy["yt_tags"],
        "tiktok_tags": copy["tiktok_tags"],
        "link": link,
        "share_to_feed": True,
        "status": "ready",
    })
    _prune_reels(out_dir, keep=8)
    return items


def main():
    os.makedirs(Q_DIR, exist_ok=True)
    pin_items = build_pins()
    car_items = build_carousels()
    reel_items = build_reels() + build_personalize()
    with open(os.path.join(Q_DIR, "pin_queue.json"), "w") as f:
        json.dump(pin_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "carousel_queue.json"), "w") as f:
        json.dump(car_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "video_queue.json"), "w") as f:
        json.dump(reel_items, f, indent=2, ensure_ascii=False)
    print(f"pins: {len(pin_items)}  carousels: {len(car_items)}  reels: {len(reel_items)}")


if __name__ == "__main__":
    main()
