# Input clips

Drop your source video here (synced from a Dropbox folder, or committed). The
factory reads these on each build and assembles finished Reels.

```
templates/          Canva MP4 exports of animated templates  (Hook->Reveal, Before/After, This-or-that)
screen-recordings/  editing screen-recordings (Personalize-With-Me) + website scrolls
wedding-scenes/     wedding footage for scene->reveal   (source: stock-licensed / AI / UGC — tbd)
personalize/        screen recordings of editing a template (Personalise With Me rubric)
```

**Naming:** end the filename with the Etsy listing id so the caption links to the
right product, e.g. `sage-website_4491130603.mp4`. Without an id the link falls
back to the shop homepage.

Media files here are git-ignored — in production they arrive via Dropbox sync at
build time and are not committed.
