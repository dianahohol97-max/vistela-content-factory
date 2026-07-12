"""Reel assembler. Wraps a source clip (your Canva MP4 export) into a finished
1080x1920 Reel: normalises to 9:16 with cream padding, burns a video-legible
hook on the open (bold Archivo Black, white + black outline on a soft dark
band), appends a CTA end-card, and grabs a cover frame. Silent by design —
trending audio is added in-app at publish (that's what earns reach)."""
import os
import re
import subprocess
import textwrap
import config as C

W, H = 1080, 1920


def _hx(c):
    return c.replace("#", "0x")


def _wrap(text, width=22):
    return "\n".join(textwrap.wrap(text.upper(), width=width))


def _run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def assemble(input_clip, hook, out_dir, slug):
    """Returns (reel_path, cover_path)."""
    os.makedirs(out_dir, exist_ok=True)
    AB, CG = C.VIDEO_FONT, C.FONT
    cream, ink, muted = _hx(C.BG), _hx(C.INK), _hx(C.MUTED)
    reel = os.path.join(out_dir, f"{slug}.mp4")
    cover = os.path.join(out_dir, f"{slug}_cover.jpg")
    hook_f = os.path.join(out_dir, f".{slug}_hook.txt")
    part_a = os.path.join(out_dir, f".{slug}_a.mp4")
    cta = os.path.join(out_dir, f".{slug}_cta.mp4")

    with open(hook_f, "w") as f:
        f.write(_wrap(hook))

    # Part A — normalise + video-legible hook overlay (first 3s)
    vf_a = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={cream},"
        f"drawtext=fontfile={AB}:textfile={hook_f}:fontcolor=white:fontsize=54:"
        f"line_spacing=18:borderw=6:bordercolor=black:shadowcolor=black@0.4:"
        f"shadowx=2:shadowy=2:box=1:boxcolor=black@0.30:boxborderw=30:"
        f"x=(w-tw)/2:y=250:enable='lt(t,3.0)'"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", input_clip, "-vf", vf_a,
          "-r", "30", "-pix_fmt", "yuv420p", part_a])

    # CTA end-card (2.4s) on cream
    vf_cta = (
        f"drawtext=fontfile={CG}:text='YOUR WEDDING\\, YOUR WAY':fontcolor={muted}:fontsize=40:x=(w-tw)/2:y=690,"
        f"drawtext=fontfile={AB}:text='EDITABLE WEDDING':fontcolor={ink}:fontsize=66:x=(w-tw)/2:y=770,"
        f"drawtext=fontfile={AB}:text='INVITATION & WEBSITE':fontcolor={ink}:fontsize=66:x=(w-tw)/2:y=856,"
        f"drawtext=fontfile={CG}:text='@vistelaco   \u00b7   on Etsy':fontcolor={ink}:fontsize=54:x=(w-tw)/2:y=1000,"
        f"drawtext=fontfile={AB}:text='EDIT  \u00b7  DOWNLOAD  \u00b7  SEND':fontcolor={muted}:fontsize=30:x=(w-tw)/2:y=1085"
    )
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
          "-i", f"color=c={cream}:s={W}x{H}:d=2.4:r=30", "-vf", vf_cta,
          "-pix_fmt", "yuv420p", cta])

    # concat A + CTA
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", part_a, "-i", cta,
          "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]",
          "-r", "30", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20", reel])

    # cover frame (hook visible)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.3", "-i", reel,
          "-frames:v", "1", cover])

    for t in (hook_f, part_a, cta):
        try:
            os.remove(t)
        except OSError:
            pass
    return reel, cover


def listing_link_from_filename(filename):
    """`sage-website_4491130603.mp4` -> Etsy listing link; else shop homepage."""
    m = re.search(r"(\d{8,})", filename)
    return f"{C.ETSY_SHOP}/listing/{m.group(1)}" if m else C.ETSY_SHOP
