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


def build_reels():
    """Hook->Reveal: one reel per template clip, with a weekly-rotating hook so
    the same template never repeats the same hook (anti-repeat). Reads clips from
    input/templates/ (synced from Dropbox by the workflow, or committed)."""
    items = []
    clips = sorted(glob.glob(os.path.join(ROOT, C.INPUT_TEMPLATES, "*.mp4")))
    if not clips:
        return items
    week = dt.date.today().isocalendar()[1]
    out_dir = os.path.join(ROOT, "output", "reels")
    import re
    for clip in clips:
        base = os.path.splitext(os.path.basename(clip))[0]
        slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
        h = int(hashlib.md5(base.encode()).hexdigest(), 16)
        hook = C.REEL_HOOKS[(week + h) % len(C.REEL_HOOKS)]
        reel, cover = RR.assemble(clip, hook, out_dir, slug)
        link = RR.listing_link_from_filename(base)
        caption = (f"{hook} \U0001F90D\n\n"
                   f"Editable in Canva, instant download \u2014 change names, dates & "
                   f"colours in minutes, no designer needed.\n\U0001F517 {link}\n\n"
                   f"{C.REEL_HASHTAGS}")
        items.append({
            "id": f"REEL_{slug}_w{week}",
            "channels": ["instagram_reel", "youtube_short", "tiktok"],
            "format": "video",
            "title": hook,
            "video_url": raw(os.path.relpath(reel, ROOT)),
            "cover_url": raw(os.path.relpath(cover, ROOT)),
            "caption": caption,
            "tags": [t.lstrip("#") for t in C.REEL_HASHTAGS.split()],
            "link": link,
            "share_to_feed": True,
            "status": "ready",
        })
    return items


def main():
    os.makedirs(Q_DIR, exist_ok=True)
    pin_items = build_pins()
    car_items = build_carousels()
    reel_items = build_reels()
    with open(os.path.join(Q_DIR, "pin_queue.json"), "w") as f:
        json.dump(pin_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "carousel_queue.json"), "w") as f:
        json.dump(car_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "video_queue.json"), "w") as f:
        json.dump(reel_items, f, indent=2, ensure_ascii=False)
    print(f"pins: {len(pin_items)}  carousels: {len(car_items)}  reels: {len(reel_items)}")


if __name__ == "__main__":
    main()
