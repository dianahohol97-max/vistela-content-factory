"""Reel assembler for the VistelaCo factory.

Main format = scene -> phone reveal -> brand CTA:
  wedding scene (+hook) --xfade--> product playing in a realistic phone (on a
  blurred scene bg, full invitation with matched-cream fill) --xfade--> emerald
  brand CTA. Silent (trending audio added in-app at publish).

Screen position and the invitation's background colour are detected
automatically, so swapping assets/phone_mockup.png or the product still works.
"""
import os
import re
import subprocess
import textwrap
import numpy as np
from PIL import Image, ImageDraw
import config as C

W, H = 1080, 1920
_BBOX = None  # cached mockup screen bbox


def _hx(c): return c.replace("#", "0x")
def _wrap(t, width=24): return textwrap.wrap(t.upper(), width=width)
def _run(a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def _dur(path):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", path], capture_output=True, text=True)
        return float(r.stdout.strip())
    except (ValueError, OSError):
        pass
    # no ffprobe (imageio's bundled build ships ffmpeg only) — read the Duration
    # line ffmpeg prints to stderr
    r = subprocess.run(["ffmpeg", "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.?\d*)", r.stderr)
    if not m:
        raise RuntimeError(f"cannot read duration of {path}")
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def _dims(path):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
                           capture_output=True, text=True)
        w, h = r.stdout.strip().split("x")[:2]
        return int(w), int(h)
    except (ValueError, OSError):
        pass
    # no ffprobe (imageio's bundled build ships ffmpeg only) — read the size off
    # the stream line ffmpeg prints to stderr
    r = subprocess.run(["ffmpeg", "-i", path], capture_output=True, text=True)
    m = re.search(r"Video:.*?, (\d+)x(\d+)", r.stderr)
    return (int(m.group(1)), int(m.group(2))) if m else (1080, 1920)


def screen_bbox():
    """Enclosed transparent region of the phone mockup = the screen."""
    global _BBOX
    if _BBOX: return _BBOX
    im = Image.open(C.PHONE_MOCKUP).convert("RGBA")
    a = im.split()[3].point(lambda v: 255 if v < 12 else 0).convert("L")
    ImageDraw.floodfill(a, (0, 0), 128, thresh=0)         # mark border-connected (bg)
    arr = np.array(a); ys, xs = np.where(arr == 255)       # enclosed = screen
    _BBOX = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    return _BBOX


def _sample_cream(clip, out_dir):
    """Average edge colour of the invitation -> seamless fill for the screen."""
    tmp = os.path.join(out_dir, ".cream.jpg")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "8", "-i", clip, "-frames:v", "1", tmp])
    im = np.array(Image.open(tmp).convert("RGB"))
    edges = np.vstack([im[:20].reshape(-1, 3), im[-20:].reshape(-1, 3),
                       im[:, :20].reshape(-1, 3), im[:, -20:].reshape(-1, 3)])
    r, g, b = edges.mean(0).astype(int)
    os.remove(tmp)
    return f"0x{r:02X}{g:02X}{b:02X}"


def _hook_vf(out_dir, slug, hook, fontsize=44, y0=95, enable="1"):
    """Per-line centred hook, white + black outline (video-legible)."""
    files, parts = [], []
    for i, ln in enumerate(_wrap(hook)):
        p = os.path.join(out_dir, f".{slug}_h{i}.txt")
        open(p, "w").write(ln); files.append(p)
        y = y0 + i * int(fontsize * 1.25)
        parts.append(f"drawtext=fontfile={C.VIDEO_FONT}:textfile={p}:fontcolor=white:"
                     f"fontsize={fontsize}:borderw=5:bordercolor=black:shadowcolor=black@0.5:"
                     f"shadowx=2:shadowy=2:x=(w-text_w)/2:y={y}:enable='{enable}'")
    return ",".join(parts), files


SCENE_MAX_S = 3.5   # wedding intro is a hook, not the show


def _scene_part(scene, hook, out_dir, slug):
    out = os.path.join(out_dir, f".{slug}_scene.mp4")
    vf, tmp = _hook_vf(out_dir, slug, hook, y0=330)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", scene, "-vf",
          f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,"
          f"trim=duration={SCENE_MAX_S},{vf}",
          "-an", "-r", "30", "-pix_fmt", "yuv420p", out])
    for t in tmp: os.remove(t)
    return out, _dur(out)


def _phone_part(scene, product, out_dir, slug, dur, speed=1.0):
    sx0, sy0, sx1, sy1 = screen_bbox(); sw, sh = sx1 - sx0, sy1 - sy0
    inv_h = int(sw * 16 / 9); oy = (sh - inv_h) // 2          # fit-by-width, centred
    cream = _sample_cream(product, out_dir)
    vf, tmp = _hook_vf(out_dir, slug, C.PHONE_HOOK, y0=140)
    out = os.path.join(out_dir, f".{slug}_phone.mp4")
    fc = (
        f"[2:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"gblur=sigma=30,eq=brightness=-0.16,setsar=1,fps=30,trim=duration={dur}[obg];"
        f"color=c={cream}:s={sw}x{sh}:r=30,trim=duration={dur}[scrbg];"
        f"[0:v]setpts=PTS/{speed:.4f},trim=duration={dur},setpts=PTS-STARTPTS,"
        f"scale={sw}:{inv_h},setsar=1,fps=30[inv];"
        f"[scrbg][inv]overlay=0:{oy}[screen];"
        f"color=c=black@0.0:s={W}x{H}:r=30,trim=duration={dur},format=rgba[tb];"
        f"[tb][screen]overlay={sx0}:{sy0}[pl];"
        f"[pl][1:v]overlay=0:0[phone];"
        f"[phone]scale=864:1536,setsar=1[phs];"
        f"[obg][phs]overlay=108:250[c1];"
        f"[c1]{vf}[v]"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", product, "-loop", "1", "-i", C.PHONE_MOCKUP,
          "-stream_loop", "-1", "-i", scene, "-filter_complex", fc, "-map", "[v]",
          "-t", str(dur), "-r", "30", "-pix_fmt", "yuv420p", out])
    for t in tmp: os.remove(t)
    return out


def _laptop_part(scene, product, out_dir, slug, dur, speed=1.0):
    """The website playing in a laptop on a blurred scene background. The clip
    keeps its own aspect and is letterboxed on its sampled edge colour, so a
    desktop capture is never stretched."""
    sx0, sy0, sx1, sy1 = C.LAPTOP_SCREEN
    sw, sh = sx1 - sx0, sy1 - sy0
    cream = _sample_cream(product, out_dir)
    vf, tmp = _hook_vf(out_dir, slug, C.LAPTOP_HOOK, y0=430)
    out = os.path.join(out_dir, f".{slug}_laptop.mp4")
    fc = (
        f"[2:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"gblur=sigma=30,eq=brightness=-0.16,setsar=1,fps=30,trim=duration={dur}[obg];"
        f"[0:v]setpts=PTS/{speed:.4f},trim=duration={dur},setpts=PTS-STARTPTS,"
        f"scale={sw}:{sh}:force_original_aspect_ratio=decrease,"
        f"pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color={cream},setsar=1,fps=30[screen];"
        f"color=c=black@0.0:s={W}x{H}:r=30,trim=duration={dur},format=rgba[tb];"
        f"[tb][screen]overlay={sx0}:{sy0}[pl];"
        f"[pl][1:v]overlay=0:0[laptop];"
        f"[obg][laptop]overlay=0:0[c1];"
        f"[c1]{vf}[v]"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", product, "-loop", "1", "-i", C.LAPTOP_MOCKUP,
          "-stream_loop", "-1", "-i", scene, "-filter_complex", fc, "-map", "[v]",
          "-t", str(dur), "-r", "30", "-pix_fmt", "yuv420p", out])
    for t in tmp: os.remove(t)
    return out

def _plain_part(scene, product, out_dir, slug, dur, speed=1.0):
    """The product filling the frame, no device mockup (Diana, 25.08.2026).

    The clips are now filmed devices — a real iPad on a table — so wrapping
    them in a drawn phone or laptop put a device inside a device and boxed the
    footage in with grey bars. Anything that does not fill 9:16 sits on a
    blurred copy of itself rather than on a flat pad.
    """
    vf, tmp = _hook_vf(out_dir, slug, C.PHONE_HOOK, y0=140)
    out = os.path.join(out_dir, f".{slug}_plain.mp4")
    fc = (
        f"[0:v]setpts=PTS/{speed:.4f},trim=duration={dur},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"gblur=sigma=30,eq=brightness=-0.10,setsar=1,fps=30[bg];"
        f"[0:v]setpts=PTS/{speed:.4f},trim=duration={dur},setpts=PTS-STARTPTS,"
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,setsar=1,fps=30[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[c1];"
        f"[c1]{vf}[v]"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", product,
          "-filter_complex", fc, "-map", "[v]",
          "-t", str(dur), "-r", "30", "-pix_fmt", "yuv420p", out])
    for t in tmp: os.remove(t)
    return out


def _cta_part(out_dir, slug):
    AB, CG = C.VIDEO_FONT, C.FONT
    em, iv, br = _hx(C.EMERALD), _hx(C.IVORY), _hx(C.BRASS)
    out = os.path.join(out_dir, f".{slug}_cta.mp4")
    vf = (
        f"drawbox=x=(iw-150)/2:y=946:w=150:h=2:color={br}@0.9:t=fill,"
        f"drawtext=fontfile={CG}:text='YOUR WEDDING\\, YOUR WAY':fontcolor={br}:fontsize=40:x=(w-tw)/2:y=690,"
        f"drawtext=fontfile={AB}:text='EDITABLE WEDDING':fontcolor={iv}:fontsize=62:x=(w-tw)/2:y=772,"
        f"drawtext=fontfile={AB}:text='INVITATION & WEBSITE':fontcolor={iv}:fontsize=62:x=(w-tw)/2:y=854,"
        f"drawtext=fontfile={CG}:text='Shop on Etsy   \u00b7   link in bio':fontcolor={iv}:fontsize=56:x=(w-tw)/2:y=980,"
        f"drawtext=fontfile={AB}:text='E D I T   \u00b7   D O W N L O A D   \u00b7   S E N D':fontcolor={br}:fontsize=28:x=(w-tw)/2:y=1076"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
          "-i", f"color=c={em}:s={W}x{H}:d=2.6:r=30", "-vf", vf, "-pix_fmt", "yuv420p", out])
    return out


def assemble_phone_reveal(scene, product, hook, out_dir, slug, max_s=None, intro=None):
    """scene(+hook) -> device reveal -> brand CTA, with crossfades. `device` is
    "phone" for vertical products and "laptop" for wedding websites, which are
    recorded as 16:9 desktop captures. Returns (reel, cover)."""
    os.makedirs(out_dir, exist_ok=True)
    reel = os.path.join(out_dir, f"{slug}.mp4"); cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    scn, sdur = _scene_part(intro or scene, hook, out_dir, slug)
    src = _dur(product)
    # long product tours kill completion rate — fit the whole tour into
    # PHONE_REVEAL_MAX_S by speeding it up instead of cutting it off mid-scroll
    # The frame follows the footage, not the product type: websites re-recorded
    # on a phone are portrait and belong in the phone; only landscape desktop
    # captures go in the laptop. Guessing from the category alone put a vertical
    # phone capture in a laptop, letterboxed with white on both sides.
    pw, ph = _dims(product)
    device = ("plain" if not C.REVEAL_IN_DEVICE_FRAME
              else "laptop" if pw > ph else "phone")
    # Length is a property of the product (a website scroll needs time to be
    # followed), the frame is a property of the footage. They are set apart on
    # purpose: a website filmed on a phone is portrait but still a long scroll.
    cap = max_s or C.PHONE_REVEAL_MAX_S
    pdur = min(src, cap)
    part = {"plain": _plain_part, "laptop": _laptop_part}.get(device, _phone_part)
    phn = part(scene, product, out_dir, slug, pdur, speed=max(1.0, src / pdur))
    cta = _cta_part(out_dir, slug)
    f1 = round(sdur - 0.5, 2)
    f2 = round(sdur + pdur - 0.5 - 0.5, 2)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", scn, "-i", phn, "-i", cta, "-filter_complex",
          f"[0:v][1:v]xfade=transition=fade:duration=0.5:offset={f1}[a];"
          f"[a][2:v]xfade=transition=fade:duration=0.5:offset={f2}[v]",
          "-map", "[v]", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20",
          "-movflags", "+faststart", reel])
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.4", "-i", reel, "-frames:v", "1", cover])
    for t in (scn, phn, cta):
        try: os.remove(t)
        except OSError: pass
    return reel, cover


def listing_link_from_filename(filename):
    m = re.search(r"(\d{8,})", filename)
    return f"{C.ETSY_SHOP}/listing/{m.group(1)}" if m else C.ETSY_SHOP


def assemble_personalize(clip, hook, out_dir, slug):
    """Personalize-With-Me: a screen recording of editing the template -> hook ->
    brand CTA. The recording fills 9:16 (cover-crop)."""
    os.makedirs(out_dir, exist_ok=True)
    reel = os.path.join(out_dir, f"{slug}.mp4"); cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    vf, tmp = _hook_vf(out_dir, slug, hook, y0=200, enable="lt(t,4)")
    # A fixed 5x multiplier turned a 32-second recording into 6 seconds - too
    # fast to read what is being typed, which is the whole point of the format.
    # Speed is derived from the source so the result always lands near the
    # target length, whatever the recording's length.
    speed = max(1.0, _dur(clip) / C.PERSONALIZE_TARGET_S)
    part = os.path.join(out_dir, f".{slug}_p.mp4")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-vf",
          f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"setpts=PTS/{speed:.4f},fps=30,setsar=1,{vf}",
          "-an", "-r", "30", "-pix_fmt", "yuv420p", part])
    cta = _cta_part(out_dir, slug)
    pdur = _dur(part)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", part, "-i", cta, "-filter_complex",
          f"[0:v][1:v]xfade=transition=fade:duration=0.5:offset={round(pdur - 0.5, 2)}[v]",
          "-map", "[v]", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20",
          "-movflags", "+faststart", reel])
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", reel, "-frames:v", "1", cover])
    for t in tmp + [part, cta]:
        try:
            os.remove(t)
        except OSError:
            pass
    return reel, cover
