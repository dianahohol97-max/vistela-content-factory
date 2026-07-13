"""Reel assembler. Two formats:
- assemble(): Hook -> Reveal  (product clip + hook)
- assemble_scene_reveal(): wedding scene (+hook) -> product reveal -> CTA
Hook text is centred, no box, white with black outline + shadow (video-legible)."""
import os
import re
import subprocess
import textwrap
import config as C

W, H = 1080, 1920


def _hx(c):
    return c.replace("#", "0x")


def _wrap(t, width=24):
    return textwrap.wrap(t.upper(), width=width)


def _run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def _norm(mode):
    """cover = fill+crop (for footage); pad = contain on cream (for designs)."""
    cream = _hx(C.BG)
    if mode == "cover":
        return f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"
    return (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={cream},setsar=1")


def _hook_filters(out_dir, slug, hook, fontsize=42, y0=230, enable="lt(t,3.0)"):
    """Per-line centred hook (each line in its own textfile => true centring),
    no box, white + black outline + soft shadow."""
    lines = _wrap(hook)
    lh = int(fontsize * 1.42)
    files, parts = [], []
    for i, ln in enumerate(lines):
        p = os.path.join(out_dir, f".{slug}_h{i}.txt")
        with open(p, "w") as f:
            f.write(ln)
        files.append(p)
        y = y0 + i * lh
        parts.append(
            f"drawtext=fontfile={C.VIDEO_FONT}:textfile={p}:fontcolor=white:"
            f"fontsize={fontsize}:borderw=5:bordercolor=black:shadowcolor=black@0.55:"
            f"shadowx=2:shadowy=2:x=(w-text_w)/2:y={y}:enable='{enable}'")
    return ",".join(parts), files


def _cta(out_dir, slug):
    AB, CG = C.VIDEO_FONT, C.FONT
    cream, ink, muted = _hx(C.BG), _hx(C.INK), _hx(C.MUTED)
    cta = os.path.join(out_dir, f".{slug}_cta.mp4")
    vf = (
        f"drawtext=fontfile={CG}:text='YOUR WEDDING\\, YOUR WAY':fontcolor={muted}:fontsize=40:x=(w-tw)/2:y=690,"
        f"drawtext=fontfile={AB}:text='EDITABLE WEDDING':fontcolor={ink}:fontsize=62:x=(w-tw)/2:y=770,"
        f"drawtext=fontfile={AB}:text='INVITATION & WEBSITE':fontcolor={ink}:fontsize=62:x=(w-tw)/2:y=852,"
        f"drawtext=fontfile={CG}:text='@vistelaco   \u00b7   on Etsy':fontcolor={ink}:fontsize=54:x=(w-tw)/2:y=992,"
        f"drawtext=fontfile={AB}:text='EDIT  \u00b7  DOWNLOAD  \u00b7  SEND':fontcolor={muted}:fontsize=28:x=(w-tw)/2:y=1078"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
          "-i", f"color=c={cream}:s={W}x{H}:d=2.4:r=30", "-vf", vf, "-pix_fmt", "yuv420p", cta])
    return cta


def _concat(parts, out):
    inputs = []
    for p in parts:
        inputs += ["-i", p]
    n = len(parts)
    fc = "".join(f"[{i}:v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    _run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc,
          "-map", "[v]", "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20", out])


def _cover(reel, out, ss="1.2"):
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", ss, "-i", reel, "-frames:v", "1", out])


def assemble(input_clip, hook, out_dir, slug):
    """Hook -> Reveal: product clip with hook on the open + CTA."""
    os.makedirs(out_dir, exist_ok=True)
    reel = os.path.join(out_dir, f"{slug}.mp4")
    cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    hookf, tmp = _hook_filters(out_dir, slug, hook, enable="lt(t,3.0)")
    part_a = os.path.join(out_dir, f".{slug}_a.mp4")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", input_clip, "-vf",
          f"{_norm('pad')},{hookf}", "-r", "30", "-pix_fmt", "yuv420p", "-an", part_a])
    cta = _cta(out_dir, slug)
    _concat([part_a, cta], reel)
    _cover(reel, cover)
    for t in tmp + [part_a, cta]:
        try:
            os.remove(t)
        except OSError:
            pass
    return reel, cover


def assemble_scene_reveal(scene_clip, product_clip, hook, out_dir, slug):
    """Scene -> Reveal: wedding footage (+hook) -> product reveal -> CTA."""
    os.makedirs(out_dir, exist_ok=True)
    reel = os.path.join(out_dir, f"{slug}.mp4")
    cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    hookf, tmp = _hook_filters(out_dir, slug, hook, enable="1")  # hook over the whole scene
    part_s = os.path.join(out_dir, f".{slug}_s.mp4")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", scene_clip, "-vf",
          f"{_norm('cover')},{hookf}", "-r", "30", "-pix_fmt", "yuv420p", "-an", part_s])
    part_p = os.path.join(out_dir, f".{slug}_p.mp4")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", product_clip, "-vf",
          _norm('pad'), "-r", "30", "-pix_fmt", "yuv420p", "-an", part_p])
    cta = _cta(out_dir, slug)
    _concat([part_s, part_p, cta], reel)
    _cover(reel, cover, ss="1.0")
    for t in tmp + [part_s, part_p, cta]:
        try:
            os.remove(t)
        except OSError:
            pass
    return reel, cover


def listing_link_from_filename(filename):
    m = re.search(r"(\d{8,})", filename)
    return f"{C.ETSY_SHOP}/listing/{m.group(1)}" if m else C.ETSY_SHOP
