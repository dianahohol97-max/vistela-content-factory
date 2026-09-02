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
import subprocess
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
    """All video files under a folder (any supported extension), recursive.

    Clips listed in config.BLOCKED_CLIPS are filtered out here, at the single
    point every rubric reads its footage through, so a rejected clip cannot
    come back through another rubric's rotation.
    """
    files = []
    for pat in VIDEO_EXTS:
        files += glob.glob(os.path.join(folder, "**", pat), recursive=True)
    blocked = getattr(C, "BLOCKED_CLIPS", ())
    files = [f for f in files if not any(b in f for b in blocked)]
    return sorted(files)


AUDIO_EXTS = ("*.mp3", "*.m4a", "*.wav", "*.aac")


def _tracks():
    files = []
    for pat in AUDIO_EXTS:
        files += glob.glob(os.path.join(ROOT, C.INPUT_MUSIC, "**", pat), recursive=True)
    return sorted(files)


def add_music(reel, slug):
    """Replace a finished reel's audio with a track from the music folder.

    The original sound is dropped, not mixed under (Diana, 25.08.2026): the
    filmed clips carry room noise and taps, and only the Dropbox tracks should
    be heard. The track is picked by a hash of the slug, so a given reel always
    gets the same one and neighbouring reels differ. No music folder = the reel
    is left alone.

    Returns the track filename on success, so the caller can record it on the
    queue entry and never mux the same reel twice.
    """
    tracks = _tracks()
    if not tracks:
        return None
    track = tracks[int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(tracks)]
    dur = RR._dur(reel)
    fade_at = max(0.0, dur - C.MUSIC_FADE_S)
    # aformat first: a mono or 44.1k track would otherwise decide the format of
    # the whole reel's audio. loudnorm then puts every track at the same
    # measured loudness — see the note on MUSIC_LUFS in config.
    fc = (f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
          f"atrim=0:{dur},asetpts=PTS-STARTPTS,"
          f"loudnorm=I={C.MUSIC_LUFS}:TP={C.MUSIC_PEAK_DB}:LRA=11,"
          f"afade=t=out:st={fade_at}:d={C.MUSIC_FADE_S}[a]")
    tmp = reel + ".mux.mp4"
    # -map 0:v only: the source audio track is deliberately left behind
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", reel,
                        "-stream_loop", "-1", "-i", track, "-filter_complex", fc,
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "160k", "-shortest",
                        "-movflags", "+faststart", tmp], capture_output=True)
    if r.returncode != 0 or not os.path.exists(tmp):
        print(f"  ! music {os.path.basename(track)} -> {slug}: "
              f"{r.stderr.decode()[-200:]}")
        return None
    os.replace(tmp, reel)
    print(f"  ♪ {os.path.basename(track)} -> {slug}")
    return os.path.basename(track)


def build_pins():
    # The queue is also curated by hand (per-listing pin batches, SEO rewrites),
    # so regeneration must MERGE with the existing file, never overwrite it:
    # hand-written text wins for known ids, unknown ids are kept as-is.
    try:
        with open(os.path.join(Q_DIR, "pin_queue.json")) as f:
            existing = {e["id"]: e for e in json.load(f)}
    except (OSError, ValueError):
        existing = {}
    items = []
    for pal in C.PALETTES:
        rel = f"output/pins/{pal['slug']}.png"
        R.palette_pin(pal, os.path.join(ROOT, rel))
        gen = {
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
        }
        prev = existing.get(gen["id"])
        if prev:
            for k in ("title", "description", "link", "board_id", "status"):
                if prev.get(k):
                    gen[k] = prev[k]
        items.append(gen)
    known = {e["id"] for e in items}
    items += [e for e in existing.values() if e["id"] not in known]
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


# Basenames the current queue points at. On a CI checkout every file carries the
# same mtime, so the "newest" sort below is effectively arbitrary and has already
# pruned reels that had just been built — leaving the command center and Buffer
# pointing at a 404. Anything still queued is protected from pruning outright.
PROTECTED_MEDIA = set()


def _protect_queued_media(queue):
    PROTECTED_MEDIA.clear()
    for item in queue or []:
        for url in (item.get("video_url"), item.get("cover_url")):
            if url:
                PROTECTED_MEDIA.add(os.path.basename(url))


def _drop_dead_entries(queue, out_dir):
    """Re-render rather than advertise a missing file: an entry whose media is
    gone is dropped from the queue, which frees its source clip to come round
    again in the rubric's rotation on the next run."""
    live, dead = [], []
    for item in queue:
        name = os.path.basename(item.get("video_url") or "")
        if name and not os.path.exists(os.path.join(out_dir, name)):
            dead.append(item.get("id"))
        else:
            live.append(item)
    return live, dead


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
        if os.path.basename(f) in PROTECTED_MEDIA:
            continue
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
    # Manual re-issue: workflow_dispatch can pin the hook and narrow the product
    # pool, so a specific reel can be rebuilt without waiting for the rotation.
    force_hook = os.environ.get("FORCE_HOOK", "").strip()
    force_product = os.environ.get("FORCE_PRODUCT", "").strip().lower()
    if force_product:
        # match the whole relative path, so a folder name ("Весільні Сайти")
        # works as well as a filename fragment
        products = [p for p in products
                    if force_product in os.path.relpath(p, ROOT).lower()] or products
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

    # real hands beat stock couples as the opener (see config.INTRO_FROM_REVIEWS)
    intros = _videos(os.path.join(ROOT, C.INPUT_PHONE_REVIEW)) if C.INTRO_FROM_REVIEWS else []

    for scene, product, hook_i in jobs:
        cat = C.product_category(product)
        base = os.path.splitext(os.path.basename(product))[0]
        sbase = os.path.splitext(os.path.basename(scene))[0] if scene else "solo"
        shooks = C.hooks_for(cat, product)
        offset = int(hashlib.md5((sbase + base).encode()).hexdigest(), 16)
        hook = force_hook or shooks[(hook_i + offset) % len(shooks)]
        slug = re.sub(r"[^a-z0-9]+", "-", f"{sbase}-{base}-{today.isoformat()}".lower()).strip("-")
        if scene:
            max_s = (C.LAPTOP_REVEAL_MAX_S if cat == "wedding_website"
                     else C.PHONE_REVEAL_MAX_S)
            # the intro has to show the same product the hook promises: a
            # save-the-date clip under a "one link" website hook is the same
            # broken promise as a wax-seal hook on a design with no seal
            # an unsorted clip (no product subfolder) claims no type, so it can
            # open any reel; only a clip of a *different* known type is excluded
            same = [c for c in intros
                    if C.product_category(c) in (cat, "default")]
            intro = same[hook_i % len(same)] if same else scene
            reel, cover = RR.assemble_phone_reveal(scene, product, hook, out_dir, slug,
                                                   max_s=max_s, intro=intro)
        else:
            reel, cover = RR.assemble(product, hook, out_dir, slug)
        link = RR.listing_link_from_filename(base)
        copy = C.PRODUCT_COPY[cat]
        kw = copy["keyword"]
        # Instagram: clean, no hashtags, one natural keyword + CTA to bio
        gate = C.COMMENT_GATE.get(cat, C.COMMENT_GATE["default"])
        ig, tiktok = _captions(hook, copy, kw, gate)
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
    out_dir = os.path.join(ROOT, "output", "reels")
    pick = os.environ.get("FORCE_CLIP", "").strip().lower()
    if pick:
        clips = [c for c in clips if pick in os.path.basename(c).lower()] or clips
    clip, hook = ROT.next_single(ROOT, clips, C.PERSONALIZE_HOOKS, "pwm", today)
    hook = os.environ.get("FORCE_HOOK", "").strip() or hook
    base = os.path.splitext(os.path.basename(clip))[0]
    slug = re.sub(r"[^a-z0-9]+", "-", f"pwm-{base}-{today.isoformat()}".lower()).strip("-")
    reel, cover = RR.assemble_personalize(clip, hook, out_dir, slug)
    link = RR.listing_link_from_filename(base)
    cat = os.environ.get("FORCE_CATEGORY", "").strip() or C.product_category(clip)
    if cat not in C.PRODUCT_COPY:
        cat = "default"
    copy = C.PRODUCT_COPY[cat]
    kw = copy["keyword"]
    gate = C.COMMENT_GATE.get(cat, C.COMMENT_GATE["default"])
    ig, tiktok = _captions(hook, copy, kw, gate)
    items.append({
        "id": f"REEL_{slug}",
        "channels": ["instagram_reel", "youtube_short", "tiktok"],
        "format": "video",
        "category": cat,
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




def _captions(hook, copy, kw, gate):
    """(instagram, tiktok) captions: hook -> benefit -> keyword sentence -> shop
    -> comment gate -> tag stack. Instagram and TikTok both index caption text
    for search, so the product's search terms have to appear as normal words,
    not only as hashtags. Each platform gets its own tag stack."""
    body = [f"{hook} \U0001F90D", copy["value"]]
    if copy.get("ig_seo"):
        body.append(copy["ig_seo"])
    body += [f"This {kw} is on Etsy — link in bio.", gate]

    def with_tags(tags):
        t = " ".join("#" + x for x in tags)
        return "\n\n".join(body + [t]) if t else "\n\n".join(body)

    # Instagram runs without a hashtag block (Diana, 25.08.2026) — the search
    # terms are already in the body sentences, which is what IG indexes. TikTok
    # keeps its stack.
    return "\n\n".join(body), with_tags(copy["tiktok_tags"])


def _render_hook_overlay(hook, path):
    """Render the hook as a transparent 1080x1920 PNG, matching the phone-reveal
    style exactly: brand video font, white fill, heavy black outline, no
    background box, wrapped and centred in the top third. Both text styles used
    to coexist (a dark pill here, an outline in render_reel), which read as two
    different accounts in one feed."""
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1080, 1920
    SIZE, STROKE, Y0 = 58, 7, 300
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(ROOT, C.VIDEO_FONT), SIZE)
    words, lines, cur = hook.upper().split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= W - 200:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    y = Y0
    for line in lines:
        lw = d.textlength(line, font=font)
        d.text(((W - lw) / 2, y), line, font=font, fill=(255, 255, 255, 255),
               stroke_width=STROKE, stroke_fill=(0, 0, 0, 255))
        y += int(SIZE * 1.25)
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
    # alternate product type per tour day
    stds  = [p for p in products if C.product_category(p) == "save_the_date"]
    sites = [p for p in products if C.product_category(p) == "wedding_website"]
    cycle = (today.toordinal() // C.PRODUCT_TOUR_EVERY_DAYS) % 2
    pool = (stds if cycle == 0 else sites) or sites or stds or products
    clip, hook = ROT.next_single(ROOT, pool, C.PRODUCT_TOUR_HOOKS, "tour", today)
    hook = os.environ.get("FORCE_HOOK", "").strip() or hook
    out_dir = os.path.join(ROOT, "output", "reels")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(clip))[0]
    slug = re.sub(r"[^a-z0-9]+", "-", f"tour-{base}-{today.isoformat()}".lower()).strip("-")
    reel = os.path.join(out_dir, f"{slug}.mp4")
    cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    hook_png = os.path.join(out_dir, f"{slug}_hook.png")
    _render_hook_overlay(hook, hook_png)
    # A 16:9 desktop capture cropped to 9:16 loses both sides of the page — the
    # title gets cut and the browser chrome stays. Landscape footage goes into
    # the laptop frame instead, letterboxed, exactly like the reveal reels do.
    pw, ph = RR._dims(clip)
    if pw > ph:
        sx0, sy0, sx1, sy1 = C.LAPTOP_SCREEN
        sw, sh = sx1 - sx0, sy1 - sy0
        cream = RR._sample_cream(clip, out_dir)
        inputs = ["-i", clip, "-i", C.LAPTOP_MOCKUP, "-i", hook_png]
        fc = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "gblur=sigma=30,eq=brightness=-0.16,setsar=1,fps=30[bg];"
            f"[0:v]scale={sw}:{sh}:force_original_aspect_ratio=decrease,"
            f"pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color={cream},setsar=1,fps=30[screen];"
            "color=c=black@0.0:s=1080x1920:r=30,format=rgba[tb];"
            f"[tb][screen]overlay={sx0}:{sy0}[pl];"
            "[pl][1:v]overlay=0:0[laptop];"
            "[bg][laptop]overlay=0:0[v];"
            f"[v][2:v]overlay=0:0:enable='lte(t,{C.HOOK_OVERLAY_SECONDS})'[out]"
        )
    else:
        inputs = ["-i", clip, "-i", hook_png]
        fc = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
              "crop=1080:1920,setsar=1,fps=30[v];"
              f"[v][1:v]overlay=0:0:enable='lte(t,{C.HOOK_OVERLAY_SECONDS})'[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                    "-filter_complex", fc,
                    "-map", "[out]", "-map", "0:a?",
                    "-t", str(C.PRODUCT_TOUR_MAX_S), "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", reel], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    os.remove(hook_png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", reel,
                    "-frames:v", "1", cover], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    link = RR.listing_link_from_filename(base)
    cat = os.environ.get("FORCE_CATEGORY", "").strip() or C.product_category(clip)
    if cat not in C.PRODUCT_COPY:
        cat = "default"
    copy = C.PRODUCT_COPY[cat]
    kw = copy["keyword"]
    gate = C.COMMENT_GATE.get(cat, C.COMMENT_GATE["default"])
    ig, tiktok = _captions(hook, copy, kw, gate)
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

def _build_review(rubric, folder, hooks, max_s, prefix, extra=None):
    """Footage-driven reel: a clip filmed/generated outside the factory,
    normalised to 1080x1920 with the hook burned into the first seconds and its
    own audio kept. Used by the phone-review and AI-presenter rubrics."""
    import re
    items = []
    clips = _videos(os.path.join(ROOT, folder))
    pick = os.environ.get("FORCE_CLIP", "").strip().lower()
    if pick:
        clips = [c for c in clips if pick in os.path.basename(c).lower()] or clips
    if not clips:
        return items
    today = dt.date.today()
    clip, hook = ROT.next_single(ROOT, clips, hooks, prefix, today)
    hook = os.environ.get("FORCE_HOOK", "").strip() or hook
    out_dir = os.path.join(ROOT, "output", "reels")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(clip))[0]
    slug = re.sub(r"[^a-z0-9]+", "-", f"{prefix}-{base}-{today.isoformat()}".lower()).strip("-")
    reel = os.path.join(out_dir, f"{slug}.mp4")
    cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    hook_png = os.path.join(out_dir, f"{slug}_hook.png")
    _render_hook_overlay(hook, hook_png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-i", hook_png,
                    "-filter_complex",
                    "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
                    "crop=1080:1920,setsar=1,fps=30[v];"
                    f"[v][1:v]overlay=0:0:enable='lte(t,{C.HOOK_OVERLAY_SECONDS})'[out]",
                    "-map", "[out]", "-map", "0:a?",
                    "-t", str(max_s), "-c:v", "libx264", "-preset", "medium",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", reel], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    os.remove(hook_png)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1", "-i", reel,
                    "-frames:v", "1", cover], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    link = RR.listing_link_from_filename(base)
    # Camera filenames carry no product type, so a clip dropped in the folder
    # root falls back to generic stationery copy. Put it in a "Save The Date" /
    # "Wedding Websites" subfolder (or pass FORCE_CATEGORY) to get the exact
    # keyword and the right comment gate.
    cat = os.environ.get("FORCE_CATEGORY", "").strip() or C.product_category(clip)
    if cat not in C.PRODUCT_COPY:
        cat = "default"
    copy = C.PRODUCT_COPY[cat]
    kw = copy["keyword"]
    gate = C.COMMENT_GATE.get(cat, C.COMMENT_GATE["default"])
    ig, tiktok = _captions(hook, copy, kw, gate)
    item = {
        "id": f"REEL_{slug}",
        "channels": ["instagram_reel", "tiktok"],
        "format": "video",
        "category": cat,
        "rubric": rubric,
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
    }
    item.update(extra or {})
    items.append(item)
    _prune_reels(out_dir)
    return items


def build_phone_review():
    """A real phone filmed by a second camera while the product plays."""
    return _build_review("phone_review", C.INPUT_PHONE_REVIEW, C.PHONE_REVIEW_HOOKS,
                         C.PHONE_REVIEW_MAX_S, "phone")


def build_ai_review():
    """A generated presenter reviewing the product. Carries an AI label the
    publisher must switch on in the app - both IG and TikTok require it."""
    return _build_review("ai_review", C.INPUT_AI_REVIEW, C.AI_REVIEW_HOOKS,
                         C.AI_REVIEW_MAX_S, "ai",
                         extra={"ai_label": C.AI_REVIEW_LABEL})


def _last_second_rubric():
    """Rubric of the most recent second-slot reel, or None. Read from the queue
    rather than the rotation log because the log records clips, not slots."""
    try:
        with open(os.path.join(Q_DIR, "video_queue.json")) as f:
            items = json.load(f)
    except (OSError, ValueError):
        return None
    for item in reversed(items if isinstance(items, list) else []):
        rubric = item.get("rubric")
        if rubric in ("personalize", "phone_review", "product_tour", "ai_review"):
            return rubric
    return None


def build_second_reel():
    """One reel a day from SECOND_SLOT_CYCLE. Rubrics with no footage yet are
    skipped so the slot still gets filled by the next one in the cycle."""
    builders = {
        "personalize": build_personalize,
        "phone_review": build_phone_review,
        "product_tour": build_product_tour,
        "ai_review": build_ai_review,
    }
    # A folder with a single clip still counts as "has footage", so the plain
    # cycle kept handing the slot to /Personalise with me and re-rendering its
    # one file under a new hook. Thin folders now fall to the back and only
    # fill the slot when nothing deeper can.
    depth = {
        "personalize": len(_videos(os.path.join(ROOT, C.INPUT_PERSONALIZE))),
        "phone_review": len(_videos(os.path.join(ROOT, C.INPUT_PHONE_REVIEW))),
        "product_tour": len(_videos(os.path.join(ROOT, C.INPUT_TEMPLATES))),
        "ai_review": len(_videos(os.path.join(ROOT, C.INPUT_AI_REVIEW))),
    }
    forced = os.environ.get("FORCE_RUBRIC", "").strip()
    cycle = sorted(C.second_slot_order(dt.date.today()),
                   key=lambda r: depth.get(r, 0) < 2)     # stable: deep folders first
    # Whichever rubric filled the slot yesterday goes to the back. The date-based
    # cycle alone did not stop repeats: rubrics that return nothing are skipped,
    # so the same one kept winning the slot day after day and the grid filled with
    # near-identical thumbnails of the same footage.
    last = _last_second_rubric()
    if last in cycle and len(cycle) > 1:
        cycle = [r for r in cycle if r != last] + [last]
    order = [forced] if forced in builders else cycle
    for rubric in order:
        items = builders[rubric]()
        if items:
            return items
    return []


def _merge_reels(path, fresh, keep=30):
    """Reels are built twice a week but reach the content plan only when the
    command center imports them, so overwriting this file dropped any build
    nobody imported in between — every rubric except the newest disappeared
    that way. Keep a short backlog, newest last, deduped by id."""
    old = []
    if os.path.exists(path):
        try:
            with open(path) as f:
                old = json.load(f)
        except (ValueError, OSError):
            old = []
    by_id = {}
    for item in list(old) + list(fresh):
        if isinstance(item, dict) and item.get("id"):
            by_id[item["id"]] = item
    return list(by_id.values())[-keep:]


def build_daily_reels():
    """Two reels a day (Diana, 25.08.2026).

    Slot 1 is the scene->phone-reveal, which draws on the product animation
    library — by far the deepest folder and the one that keeps growing. Slot 2
    rotates the footage-driven rubrics through SECOND_SLOT_CYCLE.

    The previous plan (iPad review daily + personalise every other day) rested
    on the two thinnest folders — five clips and one — so the same footage came
    round every few days while two dozen product animations went unused."""
    if os.environ.get("FORCE_RUBRIC", "").strip():
        return build_second_reel()
    return build_reels() + build_second_reel()


def main():
    os.makedirs(Q_DIR, exist_ok=True)
    today = dt.date.today()
    video_path_early = os.path.join(Q_DIR, "video_queue.json")
    try:
        with open(video_path_early) as f:
            _protect_queued_media(json.load(f))
    except (OSError, ValueError):
        pass
    # Only reels went daily. Pins and carousels keep the Mon+Thu cadence they
    # were tuned for: generating them every day would flood the Pinterest queue,
    # and writing their files on a day nothing was built would blank them.
    static_day = today.weekday() in (0, 3) or os.environ.get("FORCE_STATIC")
    pin_items = build_pins() if static_day else None
    car_items = build_carousels() if static_day else None
    reel_items = build_daily_reels()
    video_path = os.path.join(Q_DIR, "video_queue.json")
    reel_queue = _merge_reels(video_path, reel_items)
    reel_queue, dead = _drop_dead_entries(reel_queue, os.path.join(ROOT, "output", "reels"))
    if dead:
        print(f"⚠ media missing, dropped from queue (will re-render): {', '.join(dead)}")
    # Music goes on here rather than inside each rubric — one place, and after
    # the cover has been grabbed (a still, so muxing cannot affect it). It runs
    # over the whole live queue, not just today's builds: a reel rendered before
    # any track existed would otherwise stay silent forever. The `music` key
    # records which track went on, so a reel is never muxed twice.
    for item in reel_queue:
        if item.get("music"):
            continue
        name = os.path.basename(item.get("video_url") or "")
        path = os.path.join(ROOT, "output", "reels", name)
        if name and os.path.exists(path):
            track = add_music(path, item.get("id", name))
            if track:
                item["music"] = track
    if pin_items is not None:
        with open(os.path.join(Q_DIR, "pin_queue.json"), "w") as f:
            json.dump(pin_items, f, indent=2, ensure_ascii=False)
    if car_items is not None:
        with open(os.path.join(Q_DIR, "carousel_queue.json"), "w") as f:
            json.dump(car_items, f, indent=2, ensure_ascii=False)
    with open(video_path, "w") as f:
        json.dump(reel_queue, f, indent=2, ensure_ascii=False)
    print(
        f"pins: {'skipped' if pin_items is None else len(pin_items)}  "
        f"carousels: {'skipped' if car_items is None else len(car_items)}  "
        f"reels: {len(reel_items)} new, {len(reel_queue)} in queue"
    )


if __name__ == "__main__":
    main()
