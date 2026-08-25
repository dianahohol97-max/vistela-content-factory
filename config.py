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

# Wedding websites are 16:9 desktop captures. Forced into the phone screen they
# were squeezed to a 9:16 box and the page text became unreadable, so they get
# a laptop frame instead - the same footage at nearly twice the width.
LAPTOP_MOCKUP = "assets/laptop_mockup.png"
LAPTOP_SCREEN = (78, 720, 1002, 1240)          # inner screen, 924x520 (16:9)
LAPTOP_HOOK   = "IMAGINE SENDING THIS LINK"

# Opening shot for phone-reveal reels. The wedding scene is the opener: it
# sets the world the product belongs to before the device appears. Switching
# the intro to review footage was tried and rejected - it opened on a screen,
# and the reel lost the wedding entirely.
INTRO_FROM_REVIEWS = False


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
# Comment-gate CTA: competitor posts using "comment LINK" collect 350\u20131300
# comments, the strongest algorithmic signal in this niche. Appended last so it
# is the final thing read.
COMMENT_GATE = {
    "save_the_date": 'Comment "DATE" and I\'ll send you the link \U0001F48C',
    "wedding_website": 'Comment "LINK" and I\'ll send you the template \U0001F48C',
    "invitation": 'Comment "INVITE" and I\'ll send you the link \U0001F48C',
    "default": 'Comment "LINK" and I\'ll send it to you \U0001F48C',
}

PRODUCT_COPY = {
    "save_the_date": {
        "keyword": "animated save the date",
        "value": "An animated save the date your guests will actually open \u2014 editable in Canva, ready in minutes.",
        "tiktok_tags": ["savethedate", "animatedsavethedate", "weddingtiktok", "savethedateideas", "2026wedding"],
        # YouTube search tags: broad -> specific -> long-tail (drives Shorts search + suggested)
        "yt_tags": ["animated save the date", "digital save the date", "save the date template",
                    "canva save the date", "wedding save the date", "save the date video",
                    "save the date ideas 2026", "electronic save the date", "modern save the date",
                    "save the date template canva", "animated wedding invitation", "wedding stationery"],
        # First 3 render above the Shorts title, so lead with the strongest search terms.
        "yt_hashtags": ["savethedate", "animatedsavethedate", "shorts", "weddingsavethedate", "weddingplanning2026"],
        # Instagram indexes caption words for search, so one natural keyword
        # sentence goes in the body; the tag stack goes last.
        "ig_seo": ("Animated save the date video — a digital save the date template you edit in "
                   "Canva, download and send. No printing, no postage, no designer. "
                   "Made for 2026 and 2027 brides."),
        "ig_hashtags": ["savethedate", "animatedsavethedate", "digitalsavethedate",
                        "savethedatevideo", "savethedateideas", "weddingstationery",
                        "weddinginvitations", "2026bride", "2027bride", "bridetobe",
                        "weddingplanning", "weddingtok"],
    },
    "wedding_website": {
        "keyword": "wedding website template",
        "value": "A wedding website template with RSVP built in \u2014 invitation, schedule and love story on one link, editable in Canva.",
        "tiktok_tags": ["weddingwebsite", "weddingwebsitedesign", "weddingtiktok", "weddingplanning2026", "rsvp"],
        "yt_tags": ["wedding website template", "canva wedding website", "digital wedding website",
                    "wedding rsvp website", "wedding website design", "how to make a wedding website",
                    "wedding website canva", "wedding website ideas 2026", "editable wedding website",
                    "online wedding invitation", "wedding planning 2026", "wedding stationery"],
        "yt_hashtags": ["weddingwebsite", "weddingwebsitedesign", "shorts", "weddingplanning2026", "rsvp"],
        "ig_seo": ("Wedding website template with RSVP — an editable Canva wedding website you "
                   "personalise yourself and share as one link. Digital invitation, schedule "
                   "and guest info in one place. For 2026 and 2027 weddings."),
        "ig_hashtags": ["weddingwebsite", "weddingwebsitedesign", "weddingwebsitetemplate",
                        "rsvp", "digitalinvites", "weddingstationery", "weddinginvitations",
                        "2026bride", "2027bride", "bridetobe", "weddingplanning", "weddingtok"],
    },
    "invitation": {
        "keyword": "animated wedding invitation",
        "value": "An animated wedding invitation you edit in Canva \u2014 change names, dates and colours in minutes.",
        "tiktok_tags": ["weddinginvitation", "digitalweddinginvitation", "animatedinvitation", "weddingtiktok"],
        "yt_tags": ["animated wedding invitation", "digital wedding invitation", "canva wedding invitation",
                    "wedding invitation template", "wedding invitation video", "editable wedding invitation",
                    "modern wedding invitation", "wedding invitation ideas 2026", "evite wedding invitation",
                    "wedding invitation canva", "wedding planning 2026", "wedding stationery"],
        "yt_hashtags": ["weddinginvitation", "digitalweddinginvitation", "shorts", "animatedinvitation", "weddingplanning2026"],
        "ig_seo": ("Animated wedding invitation — a digital wedding invitation template editable "
                   "in Canva. Change the names, dates and colours, download and send it the "
                   "same evening. Made for 2026 and 2027 brides."),
        "ig_hashtags": ["weddinginvitation", "weddinginvitations", "digitalweddinginvitation",
                        "animatedinvitation", "digitalinvites", "weddingstationery",
                        "savethedate", "2026bride", "2027bride", "bridetobe",
                        "weddingplanning", "weddingtok"],
    },
    "default": {
        "keyword": "editable wedding stationery",
        "value": "Editable wedding stationery, animated and ready to send \u2014 personalise it in minutes, no designer needed.",
        "tiktok_tags": ["wedding", "weddingstationery", "weddingtiktok", "canvatemplate", "2026wedding"],
        "yt_tags": ["wedding stationery", "canva wedding template", "digital wedding invitation",
                    "animated save the date", "wedding website template", "editable wedding invitation",
                    "wedding invitation template", "wedding planning 2026", "modern wedding stationery",
                    "etsy wedding", "canva wedding", "wedding reels"],
        "yt_hashtags": ["wedding", "weddingstationery", "shorts", "canvatemplate", "weddingplanning2026"],
        "ig_seo": ("Editable wedding stationery in Canva — animated save the dates, digital "
                   "wedding invitations and wedding website templates you personalise yourself "
                   "and send the same day. For 2026 and 2027 weddings."),
        "ig_hashtags": ["weddingstationery", "weddinginvitations", "savethedate",
                        "weddingwebsite", "digitalinvites", "canvatemplate",
                        "2026bride", "2027bride", "bridetobe", "engaged",
                        "weddingplanning", "weddingtok"],
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
PERSONALIZE_EVERY_DAYS = 2                    # legacy; the cycle below drives it now
PERSONALIZE_TARGET_S = 14                     # target length after speed-up
PERSONALIZE_SPEED = 5                         # legacy; target length drives it now
# Canva screen recordings were the single best-performing format in the
# competitor set (5.7K / 4.2K / 3.7K hearts vs 44-164 for finished-product
# posts), so these hooks carry the price claim, not just the process.
PERSONALIZE_HOOKS = [
    "Watch me personalize this in 60 seconds",
    "Type your names. Add your date. Send it.",
    "POV: a wedding invite you can edit yourself",
    "No designer needed \u2014 just add your details",
    "Turning this template into our wedding invitation",
    "Here's how easy it is to make it yours",
    "I made our save the date for under $10",
    "Making a $400 save the date for $9",
    "This took me 6 minutes, not $400",
    "POV: you saved $400 by editing it yourself",
]

# --- Phone-review reels (a real phone filmed by a second camera) -----------
# The competitors' reels look alive because nothing is composited: a real
# device is filmed from the side while the animation plays. Hand movement,
# screen glare and room light are the point - do not clean them up.
INPUT_PHONE_REVIEW = "input/phone-reviews"   # Dropbox folder "\u041e\u0433\u043b\u044f\u0434\u0438 \u041d\u0430 \u0410\u0439\u043f\u0430\u0434\u0456"
PHONE_REVIEW_MAX_S = 15
# The footage is a real device on a desk or in a hand, so the hook has to match
# what is on the screen. "This arrives in your messages" over a Canva editor is
# the same broken promise as a wax-seal hook on a design with no seal.
PHONE_REVIEW_HOOKS = [
    "I made this instead of $400 of paper",
    "This cost $9. Paper would be $400.",
    "My $9 save the date, filmed unedited",
    "POV: this is what $9 gets you",
    "I edited this on my iPad in 6 minutes",
    "Watch what my guests actually receive",
    "Tap the seal and watch it open",
    "2027 brides, this is what they get",
]

# --- AI-presenter review reels ---------------------------------------------
# A generated presenter reviewing the product. Must be labelled as AI on
# Instagram and TikTok - both platforms require it for realistic synthetic
# people, and an unlabelled one risks the reach the reel is made for.
INPUT_AI_REVIEW = "input/ai-reviews"         # Dropbox folder "\u0430\u0456 \u0431\u043b\u043e\u0433\u0435\u0440\u0438"
AI_REVIEW_MAX_S = 22
AI_REVIEW_LABEL = "AI-generated presenter \u00b7 real product"

# Music baked into every reel (Diana, 25.08.2026). Tracks come from the Dropbox
# folder "Elements/Audio". One is picked per reel from a hash of its slug, so a
# reel always gets the same track and neighbouring reels differ. A reel that
# already carries its own sound keeps it, with the music underneath.
INPUT_MUSIC = "input/music"
# Targets, not attenuations: a fixed dB cut lands wherever the track happened
# to sit, and the first pass measured -29 LUFS against the ~-14 Instagram and
# TikTok normalise to, so the music was barely audible. loudnorm drives every
# track to the same measured loudness whatever its own level.
MUSIC_LUFS = -16.0        # music-only reels, just under platform normalisation
MUSIC_UNDER_LUFS = -20.0  # music under existing sound, before the mix is normalised
MUSIC_PEAK_DB = -1.5      # true-peak ceiling, keeps the encoder from clipping
MUSIC_FADE_S = 1.5        # fade out at the end so it never stops mid-note

AI_REVIEW_HOOKS = [
    "I reviewed a $9 wedding save the date",
    "Wedding stationery under $10 - honest look",
    "I tested the $9 save the date everyone sends",
    "Is a $15 wedding website actually good?",
    "Reviewing the save the date from your feed",
    "2027 brides keep asking about this one",
]

# The daily feed is one phone-reveal reel plus one reel from this cycle, so
# every rubric gets a turn and no format repeats two days running. A rubric
# with no footage yet is skipped and the next one in the cycle takes the slot.
SECOND_SLOT_CYCLE = ["personalize", "phone_review", "product_tour", "ai_review"]


def second_slot_order(today):
    """Today's rubric preference order for the second daily reel."""
    i = today.toordinal() % len(SECOND_SLOT_CYCLE)
    return SECOND_SLOT_CYCLE[i:] + SECOND_SLOT_CYCLE[:i]


# Showcase hooks for the phone-reveal format (product shown on a phone, not
# edited). These set up the "imagine opening this on your phone" reveal, so they
# must be about receiving/opening/showing the product — never about editing
# (that language belongs to PERSONALIZE_HOOKS).
SHOWCASE_HOOKS = {
    # Descriptive openers ("the save the date your guests will screenshot",
    # "imagine sending THIS") are deliberately gone: they describe the product
    # instead of making a claim, so there is nothing to keep watching for.
    # Every hook here carries a number, a POV or a year call-out - the three
    # patterns that outperformed in docs/competitor-research-2026-08.md
    # (price hooks beat aesthetic ones ~30x).
    "save_the_date": [
        # money math - strongest lever in this niche
        "Paper save the dates: $400. This one: under $10.",
        "How I sent 120 save the dates for under $10",
        "Stop paying $4 per save the date",
        "I paid $9 instead of $400. Here's what I sent",
        "This is what a $10 save the date looks like",
        "Can a $10 save the date really wow people?",
        "A $10 save the date that actually wows people",
        "Budget tip: send it, don't print it",
        # first person, past tense - a bride's experience, not a brand claim
        "I stopped paying $4 per save the date",
        "I didn't print a single save the date",
        "I sent 120 save the dates from my phone",
        "I skipped $400 of printing and sent this",
        # POV
        "POV: you skipped $400 of printing",
        "POV: you refuse to send a boring save the date",
        "POV: your save the date plays your song",
        # year call-out
        "2027 brides, this is the save the date you need",
        "If you're a 2027 bride, save this now",
        # interaction
        "Tap the wax seal and watch what happens",
    ],
    "wedding_website": [
        # money math
        "Printed invites: $500. This website: under $15.",
        "Your whole wedding in one link, under $15",
        "Budget tip: your website IS the invitation",
        "A wedding website for less than $15",
        # first person, past tense
        "I skipped $500 of paper and sent one link",
        "I built our wedding website in one evening",
        "I never answered 'what's the dress code' again",
        # POV
        "POV: you sent a link instead of $500 of paper",
        "POV: your guests just opened your wedding website",
        # claim
        "One link that answers every guest question",
        "Never answer 'what's the dress code' again",
        "Let your website collect the RSVPs for you",
        # year call-out
        "2027 brides, this is the invite you need",
    ],
    "invitation": [
        "Printed invites: $500. This one: under $10.",
        "Stop paying $5 per wedding invitation",
        "I stopped paying $5 per wedding invitation",
        "I sent our invitations without printing one",
        "POV: you skipped $500 of printing",
        "POV: your guests just opened your invitation",
        "2027 brides, this is the invite you need",
        "Budget tip: send it, don't print it",
    ],
    "default": [
        "Paper stationery: $400. This one: under $10.",
        "Stop paying $4 per wedding invite",
        "I stopped paying $4 per wedding invite",
        "POV: you skipped $400 of printing",
        "POV: your guests just opened your wedding invite",
        "2027 brides, save this now",
    ],
}


# Phone-reveal reels: hard cap on the product segment. A 45s website scroll
# played at 1x made 54-second reels and completion rate (and reach) collapsed.
# Longer tours are sped up to fit, so the whole product is still shown.
PHONE_REVEAL_MAX_S = 11
# A website tour is a scroll through several pages; squeezed into the same 11
# seconds as a save-the-date animation it raced past unreadably. Websites get
# their own, longer budget so the scroll stays slow enough to follow.
LAPTOP_REVEAL_MAX_S = 20

# --- Product-tour reels (raw product video as-is, IG + TikTok) -------------
# "Просто як огляд продукту": every PRODUCT_TOUR_EVERY_DAYS the raw product
# video is posted unedited (normalised to 1080x1920/30fps), alternating between
# save-the-dates and wedding websites. Runs on the days personalize doesn't.
PRODUCT_TOUR_EVERY_DAYS = 2
PRODUCT_TOUR_MAX_S = 30
PRODUCT_TOUR_HOOKS = [
    "The reveal you've been waiting for",
    "Wait for the wax seal\u2026",
    "Turn your sound on for this one",
    "Watch me turn a template into THIS",
    "The full design, start to finish",
    "Rate this save the date 1\u201310",
    "From boring template to dream invite",
    # money math
    "This costs less than one printed invite",
    "Under $10. Watch the whole thing.",
    "Budget wedding tip: this replaces $400 of printing",
]

# Burned-in hook overlay on product-tour reels: the hook line is shown as
# on-screen text for the first HOOK_OVERLAY_SECONDS of the video (top third,
# safe margins). Half of viewers watch muted; the caption hook alone is not
# enough.
HOOK_OVERLAY_SECONDS = 3.0


# The hook is burned into the video and has ~2 seconds to be read on a muted
# scroll. Past HOOK_MAX_CHARS it wraps to three lines and stops reading as one
# thought — so an over-long hook fails the build instead of shipping unreadable.
HOOK_MAX_CHARS = 50
_too_long = sorted({h for hooks in (list(SHOWCASE_HOOKS.values())
                                    + [PERSONALIZE_HOOKS, PRODUCT_TOUR_HOOKS,
                                       PHONE_REVIEW_HOOKS, AI_REVIEW_HOOKS])
                    for h in hooks if len(h) > HOOK_MAX_CHARS})
assert not _too_long, f"hooks over {HOOK_MAX_CHARS} chars: {_too_long}"


# Hooks that promise a specific visual only work on products that actually have
# it: "tap the wax seal" on a lace-frame design is a broken promise, and the
# viewer who taps and sees no seal is the one who scrolls. Each entry lists the
# filename keywords a product must match for that hook to be eligible.
HOOK_REQUIRES = {
    "Tap the wax seal and watch what happens": ("envelope", "seal", "wax"),
    "POV: your save the date plays your song": ("music", "song", "audio"),
}


def hooks_for(category, product_path):
    """Showcase hooks eligible for this product (visual promises filtered out
    when the product can't keep them). Never returns an empty list."""
    name = os.path.basename(product_path).lower()
    hooks = SHOWCASE_HOOKS.get(category, SHOWCASE_HOOKS["default"])
    ok = [h for h in hooks
          if h not in HOOK_REQUIRES or any(k in name for k in HOOK_REQUIRES[h])]
    return ok or hooks
