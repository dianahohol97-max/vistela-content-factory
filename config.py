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
# Native Instagram look for every reel (Diana's decision, see studio/CLAUDE.md):
# white Open Sans Bold with a soft shadow, hook at the top for the first
# seconds, the comment trigger over the last seconds of the footage itself.
# No text bands, no brand end card. The font ships with the repo (studio/fonts).
NATIVE_FONT = "studio/fonts/OpenSans.ttf"
CTA_TEXT = "Comment DATE for the link"
CTA_SECONDS = 2.5
# Second line, shown between the hook and the trigger (Diana, 11.10.2026).
MID_TEXT = "Everything's ready. Just edit your details in Canva."
MID_WINDOW = (4.0, 10.0)   # seconds; skipped on reels too short to hold it

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

# Show the product itself after the wedding opening, not a drawn phone or
# laptop around it (Diana, 25.08.2026). The clips are filmed devices now — a
# real iPad on a table — so a mockup put a device inside a device and boxed the
# footage in with grey bars. Set True to bring the frames back.
REVEAL_IN_DEVICE_FRAME = False


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
# One trigger on every reel (Diana, 11.10.2026): DATE. Several words split the
# automation and the stats, and LINK / INVITE drew freebie hunters, not buyers.
COMMENT_GATE = {
    "default": 'Comment "DATE" and I\'ll send you the link \U0001F48C',
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
    "halloween_envelope": {
        "keyword": "animated halloween envelope",
        "value": "An animated Halloween envelope with a transparent background \u2014 your own invitation opens inside it. Edit in free Canva and use it again and again.",
        "tiktok_tags": ["halloweenparty", "halloweeninvitation", "animatedenvelope", "halloween2026", "partyinvite"],
        "yt_tags": ["animated envelope", "halloween envelope", "envelope opening video", "animated halloween envelope",
                    "halloween invitation video", "digital envelope", "envelope reveal", "canva envelope",
                    "halloween party invitation", "transparent background envelope", "halloween 2026", "party invitation video"],
        "yt_hashtags": ["halloween", "animatedenvelope", "shorts", "halloweeninvitation", "envelopereveal"],
        "ig_seo": ("Animated Halloween envelope video with a transparent background: drop in your own "
                   "invitation and it opens inside the envelope. Edit in free Canva, send by text."),
        "ig_hashtags": [],
    },
    "halloween": {
        "keyword": "halloween party invitation",
        "value": "An animated Halloween party invitation your guests open on their phone \u2014 already designed, just add your party details in free Canva.",
        "tiktok_tags": ["halloweenparty", "halloweeninvitation", "halloween2026", "partyinvite", "halloweenideas"],
        "yt_tags": ["halloween party invitation", "animated halloween invitation", "halloween invitation video",
                    "digital halloween invitation", "halloween party invite", "kids halloween party",
                    "halloween invitation template", "canva halloween invitation", "halloween 2026",
                    "spooky party invitation", "halloween evite", "party invitation video"],
        "yt_hashtags": ["halloween", "halloweenparty", "shorts", "halloweeninvitation", "halloween2026"],
        "ig_seo": ("Animated Halloween party invitation \u2014 a digital invitation video you send by "
                   "text or WhatsApp. Already designed: add the date and address in free Canva and send "
                   "it tonight. No printing, no postage."),
        "ig_hashtags": [],
    },
    "christmas": {
        "keyword": "christmas party invitation",
        "value": "An animated Christmas party invitation your guests open on their phone \u2014 already designed, just add your details in free Canva.",
        "tiktok_tags": ["christmasparty", "christmasinvitation", "christmas2026", "holidayparty", "partyinvite"],
        "yt_tags": ["christmas party invitation", "animated christmas invitation", "christmas invitation video",
                    "digital christmas invitation", "holiday party invitation", "christmas evite",
                    "christmas invitation template", "canva christmas invitation", "christmas 2026",
                    "christmas dinner invitation", "holiday party invite", "party invitation video"],
        "yt_hashtags": ["christmas", "christmasparty", "shorts", "christmasinvitation", "holidayparty"],
        "ig_seo": ("Animated Christmas party invitation \u2014 a digital holiday invitation video you "
                   "send by text or WhatsApp. Already designed: add the date and address in free Canva. "
                   "No printing, no postage."),
        "ig_hashtags": [],
    },
    "birthday": {
        "keyword": "birthday party invitation",
        "value": "An animated birthday invitation your guests open on their phone \u2014 already designed, just add the name, date and place in free Canva.",
        "tiktok_tags": ["birthdayparty", "birthdayinvitation", "partyinvite", "birthdayideas", "30thbirthday"],
        "yt_tags": ["birthday party invitation", "animated birthday invitation", "birthday invitation video",
                    "digital birthday invitation", "birthday evite", "30th birthday invitation",
                    "40th birthday invitation", "birthday invitation template", "canva birthday invitation",
                    "adult birthday party", "party invitation video", "birthday invite ideas"],
        "yt_hashtags": ["birthday", "birthdayparty", "shorts", "birthdayinvitation", "partyideas"],
        "ig_seo": ("Animated birthday invitation \u2014 a digital party invitation video you send by "
                   "text or WhatsApp. Already designed: add the name, date and place in free Canva. "
                   "No printing, no postage."),
        "ig_hashtags": [],
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
    folder = os.path.basename(os.path.dirname(path)).lower()
    # Envelope-only products (transparent background, the buyer's invite opens
    # inside) live in their own folder, e.g. "Halloween envelope". Invitation
    # file names often say "envelope" too, so only the folder decides.
    if "envelope" in folder or "\u043a\u043e\u043d\u0432\u0435\u0440\u0442" in folder:
        return "halloween_envelope" if "halloween" in folder else "envelope"
    if any(k in s for k in ["halloween", "\u0445\u0435\u043b\u043e\u0432\u0456\u043d", "\u0445\u0435\u043b\u043b\u043e\u0432\u0456\u043d"]):
        return "halloween"
    if any(k in s for k in ["christmas", "xmas", "\u0440\u0456\u0437\u0434\u0432", "\u043d\u043e\u0432\u043e\u0440\u0456\u0447"]):
        return "christmas"
    if any(k in s for k in ["birthday", "bday", "\u0434\u0435\u043d\u044c \u043d\u0430\u0440\u043e\u0434\u0436", "\u0434\u043d \u043d\u0430\u0440"]):
        return "birthday"
    if any(k in s for k in ["save-the-date", "save the date", "savethedate", "std", "save", "\u0434\u0430\u0442\u0430"]):
        return "save_the_date"
    if any(k in s for k in ["website", "site", "\u0441\u0430\u0439\u0442"]):
        return "wedding_website"
    if any(k in s for k in ["invitation", "invite", "rsvp", "\u0437\u0430\u043f\u0440\u043e\u0448"]):
        return "invitation"
    return "default"


# Holiday products only run in their selling window: a Halloween invite in
# November is a dead post. Birthdays and weddings sell all year.
HOLIDAYS = ("halloween", "halloween_envelope", "christmas")
SEASONS = {
    # Diana, 11.10.2026: no Halloween posts after 24 October
    "halloween": ((9, 10), (10, 24)),
    "halloween_envelope": ((9, 10), (10, 24)),
    # Christmas party invites start selling early (Diana, 11.10.2026)
    "christmas": ((10, 1), (12, 24)),
}
# What the page alternates between, one reel each in turn (Diana, 11.10.2026).
# A theme with no footage or out of season is skipped.
THEME_CYCLE = ["wedding", "christmas", "halloween"]
THEME_CATEGORIES = {
    "wedding": ("save_the_date", "wedding_website", "invitation", "default"),
    "christmas": ("christmas",),
    "halloween": ("halloween", "halloween_envelope"),
}
# Inside the wedding theme the format rotates too: scene reveal, real iPad
# review, plain template.
WEDDING_FORMATS = ["reveal", "phone_review", "product_tour"]
REELS_PER_DAY = 2
WEDDING_CATEGORIES = ("save_the_date", "wedding_website", "invitation", "default")


def in_season(category, day):
    """True if this product type should be posted on `day`."""
    if category not in SEASONS:
        return True
    (m0, d0), (m1, d1) = SEASONS[category]
    return (m0, d0) <= (day.month, day.day) <= (m1, d1)


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
    # Real iPad footage of wedding products (save the dates and websites), so
    # no price: the website is not under $10. Rewritten 11.10.2026.
    "Real iPad, real template. Your names go here.",
    "This is the whole thing. Just change the names.",
    "Engaged? This one is already designed",
    "What your guests see when they tap the link",
    "No design skills? This is already made for you",
    "You don't need a designer. Just change the names.",
    "POV: your wedding invite is ready in minutes",
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
# original audio is dropped, not mixed under: only these tracks are heard.
# Clips Diana has ruled out — matched as a substring of the path, so a whole
# folder or a single file can be blocked. Uploaded by mistake or unusable:
# the factory never picks them, whatever rubric they sit in.
BLOCKED_CLIPS = [
    "18 06 32",   # iPad review: opens on three seconds of blank white canvas
    "18-06-32",   # same clip after the sync renames it
]

INPUT_MUSIC = "input/music"
# Targets, not attenuations: a fixed dB cut lands wherever the track happened
# to sit, and the first pass measured -29 LUFS against the ~-14 Instagram and
# TikTok normalise to, so the music was barely audible. loudnorm drives every
# track to the same measured loudness whatever its own level.
MUSIC_LUFS = -16.0        # music-only reels, just under platform normalisation
MUSIC_PEAK_DB = -1.5      # true-peak ceiling, keeps the encoder from clipping
MUSIC_FADE_S = 1.5        # fade out at the end so it never stops mid-note
# Halloween product videos keep their own sound (Diana, 11.10.2026): no track
# is muxed over them.
KEEP_ORIGINAL_AUDIO = ("halloween", "halloween_envelope")

AI_REVIEW_HOOKS = [
    "Is a digital save the date worth it?",
    "Honest look: animated wedding invitations",
    "Reviewing the save the date from your feed",
    "2027 brides keep asking about this one",
    "Would your guests open this?",
    "No printing, no postage. Does it work?",
]

# The daily feed is one phone-reveal reel plus one reel from this cycle, so
# every rubric gets a turn and no format repeats two days running. A rubric
# with no footage yet is skipped and the next one in the cycle takes the slot.
# "Personalise with me" is out (Diana, 11.10.2026): an editing screen in Canva
# brought creators asking for tutorials, not buyers.
SECOND_SLOT_CYCLE = ["phone_review", "product_tour", "ai_review"]


def second_slot_order(today):
    """Today's rubric preference order for the second daily reel."""
    i = today.toordinal() % len(SECOND_SLOT_CYCLE)
    return SECOND_SLOT_CYCLE[i:] + SECOND_SLOT_CYCLE[:i]


# Showcase hooks for the phone-reveal format (product shown on a phone, not
# edited). These set up the "imagine opening this on your phone" reveal, so they
# must be about receiving/opening/showing the product — never about editing
# (that language belongs to PERSONALIZE_HOOKS).
SHOWCASE_HOOKS = {
    # Rewritten 11.10.2026 for buyers, not creators: "your guests" and "already
    # made for you", never "I made / I edited / I sent 120 / my guests".
    # Prices only where they are true: the save the dates, invitations and
    # party invites are $7.99 on Etsy, so "under $10" holds. The wedding
    # website costs more, so its hooks carry no price.
    # Wedding hooks rewritten again 11.10.2026 (Diana: fresh hooks for weddings).
    "save_the_date": [
        "Just engaged? This is your save the date",
        "Engaged? Your save the dates are already done",
        "The save the date your guests actually open",
        "Your guests will screenshot this save the date",
        "POV: your save the date arrives by text",
        "Change the names. Send it tonight.",
        "No designer. No printer. Just your names.",
        "2027 wedding? Send this before the paper ones",
        "Save the date for the price of 2 coffees",
        "Under $10. No printing. No postage.",
        "Cheaper than stamps. Prettier than paper.",
        "I almost paid $400 for paper. Then I found this.",
        "Tap the wax seal and watch what happens",
    ],
    "wedding_website": [
        "Your guests' questions, answered in one link",
        "RSVPs, schedule and map in one link",
        "The wedding website your guests will actually use",
        "Engaged? Your wedding website is already built",
        "Stop answering 'what time is the ceremony?'",
        "POV: your guests RSVP from their phone",
        "Change the names. Your website is ready.",
    ],
    "invitation": [
        "Your wedding invite, opened on their phone",
        "POV: your wedding invitation arrives by text",
        "Already designed. Just add your names.",
        "Change the names. Send it tonight.",
        "The invite your guests will replay",
        "Under $10. No printing. No postage.",
    ],
    "halloween_envelope": [
        "Already have an invite? Put it in this envelope",
        "Your invite, opening from an animated envelope",
        "Make any Halloween invite open like this",
        "Tap. The envelope opens. Your invite appears.",
        "One envelope. Use it for every party.",
    ],
    "halloween": [
        "Your Halloween party invite is already designed",
        "Halloween party? Your invites can go out tonight",
        "Your guests tap. The party starts.",
        "Last-minute Halloween party? This is ready.",
        "No printing. Send your Halloween invite by text.",
        "Halloween invites under $10. No printing.",
        "Kids' Halloween party? The invite is ready.",
        "Halloween invites your guests open on their phone",
        "Spooky invites, sent by text. No printing.",
    ],
    "christmas": [
        "Your Christmas party invite is already designed",
        "Hosting Christmas? Your invites are ready.",
        "Your guests tap. The Christmas party starts.",
        "Christmas party invites under $10",
        "No printing. No postage. Just send the link.",
        "Send your Christmas invites tonight",
    ],
    "birthday": [
        "They tap. It opens. Birthday invite sent.",
        "Your birthday invite, sent by text in minutes",
        "Already designed. Just add the name and date.",
        "Birthday invites under $10. No printing.",
        "No printing. No postage. Just send the link.",
        "Your guests will open this on their phone",
    ],
    "default": [
        "Your guests will open this on their phone",
        "Already designed. Just change the names.",
        "POV: your guests just opened your invite",
        "No printing. No postage. Just send the link.",
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
    # Wedding tours (party products use their own SHOWCASE_HOOKS list).
    "Watch it open the way your guests will",
    "This is what lands in your guests' messages",
    "Engaged? Your invites are already designed",
    "Rate this save the date 1\u201310",
    "Would you send this to your guests?",
    "No printing. No postage. Just send it.",
    "Change the names. Send it tonight.",
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
