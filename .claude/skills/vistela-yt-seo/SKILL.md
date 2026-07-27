---
name: vistela-yt-seo
description: >-
  Generate a complete YouTube Shorts SEO pack (3 title options, description, tags,
  hashtags, pinned comment) for a VistelaCo product video — animated save-the-dates,
  wedding invitations, and wedding-website animations that link back to an Etsy
  listing. Use whenever Diana uploads or links a product video and wants YouTube SEO,
  asks for a YouTube title/description for a save the date or wedding website, or says
  things like "youtube seo for this", "seo для ютуба", "зроби сео для цього відео",
  "title and description for youtube", or wants a product video to rank in YouTube
  search AND recommendations. Delivers the result as a copy-ready artifact.
---

# VistelaCo — YouTube Shorts SEO for product videos

VistelaCo (Etsy: `vistelaco.etsy.com`) sells animated, editable wedding stationery —
save-the-dates, wedding invitations and wedding websites (Canva templates). Before or
after publishing an Etsy listing, Diana uploads a short product video to YouTube to
showcase the product, then links that YouTube video to the Etsy listing. This skill
writes the SEO for that video so it ranks in YouTube **search and recommendations** and
drives clicks to Etsy.

This is a manual, per-video task — NOT the automated content factory (that lives in
`build.py`/`config.py` and handles the daily social reels). Do not touch those here.

## Inputs (ask only for what's missing, then proceed)

1. **The product video** — uploaded to the chat, or a link. Optional but ideal.
2. **A 1–2 sentence description** — colour/palette, and what the animation shows
   (e.g. envelope opening, text appearing, butterfly moving its wings, music).
3. **Product type** — save-the-date / wedding website / invitation. Infer it from the
   description or frames if not stated.
4. **Etsy link** — the specific listing URL if it exists; otherwise use the shop link
   `https://vistelaco.etsy.com` and add a note to swap it once the listing is live.

If the description is enough to write strong SEO, don't block on the video. If neither a
useful description nor a video is given, ask one short question, then continue.

## Step 1 — Look at the video (if a file is provided)

Extract a few frames and view them to read the real palette, animation and any on-card
text. Use the scratchpad, not the repo:

```bash
ffmpeg -y -loglevel error -i "<video>" -vf "fps=1,scale=540:-1" "<scratch>/frame_%02d.jpg"
```

Then Read 3–5 of the frames. Pull out: dominant colours, the animation beats (envelope,
butterfly, text reveal…), the style (classic / modern / editorial), and whether music is
implied. Feed these specifics into the copy — specific always beats generic.

## Step 2 — Write the SEO

Optimise for **both search and recommendations**. Search rewards the keyword in the
title and the first line of the description + relevant tags. Recommendations reward a
click-worthy title, a strong first 1–2 seconds, watch-time, and a broad+niche tag mix
so YouTube knows who to suggest it to.

Produce:

- **3 title options**, each ≤ 100 characters. Lead with the primary keyword phrase, then
  a concrete feature/hook, then `#Shorts`. Feature-specific beats generic
  ("Animated Save the Date with Butterfly Envelope Reveal + Music | Canva #Shorts").
- **Description**: first line keyword-rich (this is what search indexes); then a short
  "✨ What you get:" bullet list built from the actual features; then a clear CTA with the
  Etsy link; then a hashtag block. The first 3 hashtags render above the title, so lead
  with the strongest.
- **Tags**: ~12, broad → specific → long-tail, tuned to the real features
  (e.g. `save the date with music`, `butterfly save the date`). Keep the comma-joined
  string under 500 characters total.
- **Hashtags**: 6–7, first three strongest, always include `#shorts`.
- **Pinned comment**: one friendly line that drives to the Etsy listing and ends with a
  light engagement question (comments help recommendations).

### Keyword anchors by product type

- **save-the-date** → animated save the date, digital save the date, save the date template, canva save the date, save the date video, save the date ideas 2026
- **wedding website** → wedding website template, canva wedding website, digital wedding website, wedding rsvp website, how to make a wedding website
- **invitation** → animated wedding invitation, digital wedding invitation, canva wedding invitation, wedding invitation template, wedding invitation video

### Brand voice (do not break)

- Elegant, warm, second-person, aspirational — VistelaCo's emerald/ivory register.
- About **receiving / opening / showing** the product, never about editing (that voice
  belongs to the factory's "Personalise" rubric).
- These are product-showcase videos that link to Etsy, so a **direct Etsy link is
  correct here** (unlike the social factory's "link in bio" rule).
- Real, specific copy — no lorem, no invented names/dates unless the video shows them.

## Step 3 — Deliver as an artifact

Render the pack using the bundled template so every run looks the same and every field
has a copy button.

1. Read `template.html` in this skill folder.
2. Replace each `{{TOKEN}}`, **HTML-escaping** any `&`, `<`, `>` in the text you insert
   (the fields are `<textarea>` values):
   - `{{PRODUCT_NAME}}` — e.g. "Animated Save the Date — Butterfly & Music"
   - `{{SUBTITLE}}` — one line describing the pack
   - `{{CHIPS}}` — `<span class="chip solid">Save the date</span>` + one
     `<span class="chip">…</span>` per key feature (colour, music, envelope, etc.)
   - `{{NOTE}}` — if the listing URL isn't final, insert a
     `<div class="note">…</div>` telling her to swap the shop link for the listing URL;
     otherwise replace with an empty string.
   - `{{TITLE_1}}` `{{TITLE_2}}` `{{TITLE_3}}`, `{{DESC}}`, `{{TAGS}}`, `{{HASHTAGS}}`,
     `{{PIN}}` — the generated copy (real newlines are fine inside the textareas).
   - `{{FOOTNOTE}}` — a short brand line, e.g.
     "VistelaCo · editable wedding stationery · YouTube Shorts SEO".
3. Write the filled HTML to the scratchpad and publish with the `Artifact` tool
   (favicon `🤍`). If updating an earlier pack in the same chat, republish the same file
   path to keep the URL; otherwise a new pack is a new artifact.
4. In the chat reply, give the artifact link and a 2–3 line summary of the key choices
   (primary keyword, the hook angle). Keep the copy itself in the artifact.

## Notes

- Etsy shop link: `https://vistelaco.etsy.com`. Prefer the exact listing URL when known.
- Don't fabricate reviews, counts, or claims about the product beyond what the video and
  Diana's description support.
