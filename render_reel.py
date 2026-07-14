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
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


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


def _scene_part(scene, hook, out_dir, slug):
    out = os.path.join(out_dir, f".{slug}_scene.mp4")
    vf, tmp = _hook_vf(out_dir, slug, hook, y0=235)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", scene, "-vf",
          f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,{vf}",
          "-an", "-r", "30", "-pix_fmt", "yuv420p", out])
    for t in tmp: os.remove(t)
    return out, _dur(out)


def _phone_part(scene, product, out_dir, slug, dur):
    sx0, sy0, sx1, sy1 = screen_bbox(); sw, sh = sx1 - sx0, sy1 - sy0
    inv_h = int(sw * 16 / 9); oy = (sh - inv_h) // 2          # fit-by-width, centred
    cream = _sample_cream(product, out_dir)
    vf, tmp = _hook_vf(out_dir, slug, C.PHONE_HOOK, y0=95)
    out = os.path.join(out_dir, f".{slug}_phone.mp4")
    fc = (
        f"[2:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"gblur=sigma=30,eq=brightness=-0.16,setsar=1,fps=30,trim=duration={dur}[obg];"
        f"color=c={cream}:s={sw}x{sh}:r=30,trim=duration={dur}[scrbg];"
        f"[0:v]trim=duration={dur},scale={sw}:{inv_h},setsar=1,fps=30[inv];"
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


def _cta_part(out_dir, slug):
    AB, CG = C.VIDEO_FONT, C.FONT
    em, iv, br = _hx(C.EMERALD), _hx(C.IVORY), _hx(C.BRASS)
    out = os.path.join(out_dir, f".{slug}_cta.mp4")
    vf = (
        f"drawbox=x=(iw-150)/2:y=946:w=150:h=2:color={br}@0.9:t=fill,"
        f"drawtext=fontfile={CG}:text='YOUR WEDDING\\, YOUR WAY':fontcolor={br}:fontsize=40:x=(w-tw)/2:y=690,"
        f"drawtext=fontfile={AB}:text='EDITABLE WEDDING':fontcolor={iv}:fontsize=62:x=(w-tw)/2:y=772,"
        f"drawtext=fontfile={AB}:text='INVITATION & WEBSITE':fontcolor={iv}:fontsize=62:x=(w-tw)/2:y=854,"
        f"drawtext=fontfile={CG}:text='@vistelaco   \u00b7   on Etsy':fontcolor={iv}:fontsize=56:x=(w-tw)/2:y=980,"
        f"drawtext=fontfile={AB}:text='E D I T   \u00b7   D O W N L O A D   \u00b7   S E N D':fontcolor={br}:fontsize=28:x=(w-tw)/2:y=1076"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
          "-i", f"color=c={em}:s={W}x{H}:d=2.6:r=30", "-vf", vf, "-pix_fmt", "yuv420p", out])
    return out


def assemble_phone_reveal(scene, product, hook, out_dir, slug):
    """scene(+hook) -> phone reveal -> brand CTA, with crossfades. Returns (reel, cover)."""
    os.makedirs(out_dir, exist_ok=True)
    reel = os.path.join(out_dir, f"{slug}.mp4"); cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    scn, sdur = _scene_part(scene, hook, out_dir, slug)
    pdur = _dur(product)
    phn = _phone_part(scene, product, out_dir, slug, pdur)
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
