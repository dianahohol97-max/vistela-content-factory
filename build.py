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
import datetime as dt
import config as C
import render as R

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


def main():
    os.makedirs(Q_DIR, exist_ok=True)
    pin_items = build_pins()
    car_items = build_carousels()
    with open(os.path.join(Q_DIR, "pin_queue.json"), "w") as f:
        json.dump({"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "items": pin_items}, f, indent=2, ensure_ascii=False)
    with open(os.path.join(Q_DIR, "carousel_queue.json"), "w") as f:
        json.dump({"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "items": car_items}, f, indent=2, ensure_ascii=False)
    print(f"pins: {len(pin_items)}  carousels: {len(car_items)}")


if __name__ == "__main__":
    main()
