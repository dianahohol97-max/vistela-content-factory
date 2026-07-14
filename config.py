import os
"""Design tokens + palette library for the VistelaCo content factory.

Everything the generators need lives here. To add a palette, append to
PALETTES — the renderers and the queue builder pick it up automatically.
"""

REPO = "dianahohol97-max/vistela-content-factory"
RAW  = f"https://raw.githubusercontent.com/{REPO}/main"   # CDN for generated media

# --- brand / design tokens -------------------------------------------------
BG      = "#F7F3EC"   # cream background
INK     = "#3A322C"   # warm near-black text
MUTED   = "#8B7D6E"   # muted taupe (labels, hex)
HAIR    = "#C9BBAA"   # hairline rules
FONT    = "fonts/CormorantGaramond.ttf"   # fetched at build time (see workflow)
BRAND   = "VISTELACO"
TAGLINE = "EDITABLE WEDDING STATIONERY  \u00b7  ETSY"
ETSY_SHOP = "https://vistelaco.etsy.com"

PIN_SIZE      = (1000, 1500)  # 2:3  -> Pinterest (required ratio)
CAROUSEL_SIZE = (1080, 1350)  # 4:5  -> Instagram carousel

# Palette pins default to the existing "Wedding Color Palettes 2025 2026" board.
# Per-colour boards are pending the boards-cleanup decision, then swap per palette.
PALETTE_BOARD_ID = "1092756365776030629"

def _L(listing_id):
    return f"{ETSY_SHOP}/listing/{listing_id}"

# slug = filename + queue id. link = where the pin/caption should drive (a real
# product, not the shop homepage). Verify/adjust links as the catalogue changes.
PALETTES = [
    {"slug": "burgundy-merlot",  "name": "Burgundy & Merlot",   "trend": "Rooted Romance",
     "colors": ["#5C1A2B", "#7B2D3A", "#A34452", "#C98B7A", "#E4CDBF"], "link": _L(4487341587)},
    {"slug": "plum-fig",         "name": "Plum & Fig",          "trend": "Moody & modern",
     "colors": ["#3B2A36", "#5E3B4D", "#8A5A5E", "#B98A6E", "#E0D2BE"], "link": _L(4487325089)},
    {"slug": "sage-olive",       "name": "Sage & Olive",        "trend": "Garden & natural",
     "colors": ["#4E5A45", "#6E7C55", "#93A177", "#BEC7A4", "#E2E3D0"], "link": _L(4491130603)},
    {"slug": "emerald-ivory",    "name": "Emerald & Ivory",     "trend": "Rich & classic",
     "colors": ["#1F3B32", "#2F5D4E", "#5A8271", "#A9C1B0", "#EDE8DA"], "link": _L(4491097978)},
    {"slug": "dusty-blue",       "name": "Dusty Blue",          "trend": "Ethereal blue",
     "colors": ["#3F5A6E", "#6E8CA0", "#9CB6C9", "#C4D3DE", "#E6E2D6"], "link": _L(4485722500)},
    {"slug": "navy-silver",      "name": "Navy & Silver",       "trend": "Chrome & cool",
     "colors": ["#20304A", "#3C5169", "#6E86A0", "#AEC0CE", "#E4E6E2"], "link": _L(4487982365)},
    {"slug": "blush-neutral",    "name": "Blush & Neutral",     "trend": "Soft & timeless",
     "colors": ["#B06A57", "#CE9683", "#E1BBA9", "#EAD9CC", "#D9CBBA"], "link": _L(4485801145)},
    {"slug": "dusty-rose-mauve", "name": "Dusty Rose & Mauve",  "trend": "Quiet romance",
     "colors": ["#7A4A52", "#A9707A", "#C99AA0", "#E1C4C4", "#EFE2DC"], "link": _L(4485801145)},
    {"slug": "black-ivory",      "name": "Black & Ivory",       "trend": "Editorial",
     "colors": ["#1A1A1A", "#3D3A36", "#6E665C", "#B6AA97", "#EFEADE"], "link": _L(4485820230)},
    {"slug": "champagne-gold",   "name": "Champagne & Gold",    "trend": "Old money",
     "colors": ["#8A6D3B", "#B08D57", "#CDB07E", "#E3D2AE", "#F1E9D6"], "link": ETSY_SHOP},
]

# Caption template for the biweekly palette carousel. {a}/{b}/{c} = 3 palette names.
CAPTION_TEMPLATE = (
    "Five wedding colour palettes trending for 2026 \U0001F90D\n"
    "Which is your vibe \u2014 {a}, {b} or {c}?\n\n"
    "Every palette here comes to life as an animated, editable wedding "
    "invitation & website \u2014 change the names, dates and colours in minutes, "
    "no designer needed.\n\n"
    "\U0001F4CC Save this for your moodboard.\n"
    "\U0001F517 Shop your palette \u2192 link in bio (@vistelaco on Etsy)\n\n"
    "Which number is yours? \U0001F447\n\n"
    "#weddingcolorpalette #2026weddingtrends #weddinginvitation "
    "#digitalweddinginvitation #animatedsavethedate #weddingwebsite "
    "#weddingstationery #modernbride #weddingplanning2026"
)


# --- Reels (video) ---------------------------------------------------------
VIDEO_FONT = "fonts/ArchivoBlack.ttf"   # bold sans for video-legible captions

# Input folders (synced from Dropbox by the workflow, or committed manually).
INPUT_TEMPLATES = "input/templates"          # Canva MP4 exports (Hook->Reveal etc.)
INPUT_SCREEN    = "input/screen-recordings"  # Personalize-With-Me / website scroll
INPUT_SCENES    = "input/wedding-scenes"      # for scene->reveal (source tbd)

# Hook rotation for Hook->Reveal. One template -> a different hook each week
# (anti-repeat on the template x hook combo).
REEL_HOOKS = [
    "POV: you found a wedding invitation you can personalize in minutes",
    "Watch this template become your wedding invitation",
    "Imagine sending this to your guests instead of a paper card",
    "Type your names. Add your date. Send it to your guests.",
    "Your wedding invitation, ready in under 10 minutes",
    "POV: you refuse to send a boring save the date",
    "The invitation your guests will actually remember",
    "No designer. No waiting. Just add your details.",
]

REEL_HASHTAGS = ("#weddinginvitation #digitalweddinginvitation #animatedsavethedate "
                 "#weddingwebsite #weddingtiktok #modernbride #weddingplanning2026")


# --- Brand palette (per brand book) + phone-reveal assets ------------------
EMERALD = "#1E4736"; IVORY = "#F5EFE2"; BRASS = "#C7A76B"; SAGE = "#8AA184"
PHONE_MOCKUP = "assets/phone_mockup.png"       # realistic phone, transparent screen
PHONE_HOOK   = "IMAGINE OPENING THIS ON YOUR PHONE"


# Rotating hashtag sets (vary per reel so captions aren't identical).
REEL_HASHTAG_SETS = [
    "#weddinginvitation #digitalweddinginvitation #animatedsavethedate #weddingwebsite #weddingtiktok #modernbride #weddingplanning2026",
    "#savethedate #weddingstationery #canvatemplate #weddinginspo #engaged #weddinginvites #2026wedding",
    "#weddinginvitation #weddingreels #bridetobe #weddingideas #etsywedding #digitalinvite #weddinginspiration",
]
REELS_PER_RUN = 1   # 1/day while phone-reveal is the only reel type


# --- Per-product-type caption copy (IG clean; tags only for TikTok/Shorts) --
# Instagram hashtags are dead for reach in 2026 (the algorithm reads the content
# itself), so IG captions stay clean with 1-2 natural keywords. TikTok & YouTube
# still use tags/keywords for search.
PRODUCT_COPY = {
    "save_the_date": {
        "keyword": "animated save the date",
        "value": "An animated save the date your guests will actually open \u2014 editable in Canva, ready in minutes.",
        "tiktok_tags": ["savethedate", "animatedsavethedate", "weddingtiktok", "savethedateideas", "2026wedding"],
        "yt_tags": ["animated save the date", "digital save the date", "wedding save the date template", "canva save the date"],
    },
    "wedding_website": {
        "keyword": "wedding website template",
        "value": "Your invitation, RSVP, schedule and love story in one link \u2014 an editable wedding website in Canva.",
        "tiktok_tags": ["weddingwebsite", "weddingwebsitedesign", "weddingtiktok", "weddingplanning2026", "rsvp"],
        "yt_tags": ["wedding website template", "canva wedding website", "digital wedding website", "wedding rsvp website"],
    },
    "invitation": {
        "keyword": "animated wedding invitation",
        "value": "An editable, animated wedding invitation \u2014 change names, dates and colours in minutes.",
        "tiktok_tags": ["weddinginvitation", "digitalweddinginvitation", "animatedinvitation", "weddingtiktok"],
        "yt_tags": ["animated wedding invitation", "digital wedding invitation", "canva wedding invitation"],
    },
    "default": {
        "keyword": "editable wedding stationery",
        "value": "Editable, animated wedding stationery \u2014 personalise it in minutes, no designer needed.",
        "tiktok_tags": ["wedding", "weddingstationery", "weddingtiktok", "canvatemplate", "2026wedding"],
        "yt_tags": ["wedding stationery", "canva wedding template", "digital wedding"],
    },
}


def product_category(path):
    """Detect product type from its folder or filename (works for EN + UA)."""
    s = (os.path.basename(os.path.dirname(path)) + " " + os.path.basename(path)).lower()
    if any(k in s for k in ["save-the-date", "save the date", "savethedate", "std", "save", "\u0434\u0430\u0442\u0430"]):
        return "save_the_date"
    if any(k in s for k in ["website", "site", "\u0441\u0430\u0439\u0442"]):
        return "wedding_website"
    if any(k in s for k in ["invitation", "invite", "rsvp", "\u0437\u0430\u043f\u0440\u043e\u0448"]):
        return "invitation"
    return "default"


# --- Personalize-With-Me reels (screen recordings of editing) --------------
INPUT_PERSONALIZE = "input/personalize"      # Dropbox folder "Personalise with me"
PERSONALIZE_EVERY_DAYS = 2                    # post one every 2 days
PERSONALIZE_SPEED = 5                         # speed up the editing recording 5x
PERSONALIZE_HOOKS = [
    "Watch me personalize this in 60 seconds",
    "Type your names. Add your date. Send it.",
    "POV: you found a wedding invitation you can edit yourself",
    "No designer needed \u2014 just add your details",
    "Turning this template into our wedding invitation",
    "Here's how easy it is to make it yours",
]
