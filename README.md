# VistelaCo — Content Factory

Automated, code-rendered content factory. Generators run on a schedule via
GitHub Actions, render on-brand media (text drawn by code = zero typos, exact
brand colours), and write a JSON **queue** that Make posters consume.

```
config.py   design tokens + palette library (add a palette = append here)
render.py   Pillow renderers — 2:3 palette pin (Pinterest), 4:5 carousel (Instagram)
build.py    renders everything + builds the queues (with anti-repeat)
output/     generated media, served free via raw.githubusercontent (CDN)
queue/      pin_queue.json + carousel_queue.json  <- Make posters read these
.github/workflows/build.yml   weekly cron + manual run
```

## What it produces
- **Pinterest palette pins** (`output/pins/`, 1000×1500 / 2:3) — one per palette.
- **Instagram carousels** (`output/carousels/CAR_*/`, 1080×1350 / 4:5) — cover + 5 palettes + CTA.
- **Queues** with the shared content-object schema and raw-CDN image URLs.

## Anti-repeat
The 10-palette library splits into two disjoint sets of 5; carousels alternate
them, so **no two consecutive carousels share a palette** (a palette returns
every 4 weeks). Add palettes to stretch the cycle.

## Handoff (Make posters — deployed by Adrián)
- **Pinterest:** read `queue/pin_queue.json`; drip ~1 pin / 3 days (2–3 / week);
  each pin once to its best board; on re-use, regenerate a fresh design variant.
- **Instagram carousel:** read `queue/carousel_queue.json`; post the next
  un-posted carousel every **14 days**; export slides as **JPEG** for IG.
  Clone the proven bloom carousel poster (Make scenario 9418390).
- Posters dedup by `id` in their own Data Store, so re-running the factory is safe.

## Run locally
```
pip install -r requirements.txt
mkdir -p fonts && curl -sSLg -o fonts/CormorantGaramond.ttf \
  "https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
python build.py
```

## Next generators (stubs to add)
- Inspiration pins: "what's in your wedding website" checklist, save-the-date timeline.
- Video assembly (Reels/TikTok/Shorts): ffmpeg wrapper over the product's own animation.
