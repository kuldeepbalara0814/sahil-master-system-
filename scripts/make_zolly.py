#!/usr/bin/env python3
"""Zolly (animated avatar) ke app-assets banata hai: ek video (mp4) se.

Kya banta hai (lab_static/ me):
  zolly_face.webp   128x128  chehra-crop, poora clip seamless LOOP (15 fps)      -> header logo, help button, chat
  zolly_body.webp   176x176  poora-badan crop, seamless LOOP (12 fps)            -> hero card, chat welcome
  zolly_poster.webp 128x128  ek saaf frame (reduced-motion, loading, chat avatar)
  zolly_icon_64.png / zolly_icon_192.png   favicon / apple-touch-icon
Awaaz hata di jati hai (-an): autoplay me awaaz waise bhi band rehti hai aur header me bajti awaaz pareshan karti.
Loop ka jhatka mitane ke liye clip ke antim d second ko shuru me crossfade karte hain (loop = T - d second).

Chalane ka tarika (ffmpeg + python3-pil chahiye):
  python3 scripts/make_zolly.py /sdcard/Download/<clip>.mp4 [--face X:Y:SIZE] [--body X:Y:SIZE] [--blend 0.6]
Default crop 720x1280 vertical clip (avatar beech me, upar neeche ghoomta) ke liye tay kiye gaye; Meta AI ka chhota nishan (neeche beech) crop se bahar rehta hai.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lab_static")


def frames(src, tmp, name, crop, size, fps, dur, d):
    x, y, c = crop
    t_end = dur
    g = (f"[0:v]fps={fps},crop={c}:{c}:{x}:{y},scale={size}:{size}:flags=lanczos,split=3[a][b][c];"
         f"[a]trim=start={t_end - d:.3f}:end={t_end:.3f},setpts=PTS-STARTPTS[tail];"
         f"[b]trim=start=0:end={d:.3f},setpts=PTS-STARTPTS[head];"
         f"[c]trim=start={d:.3f}:end={t_end - d:.3f},setpts=PTS-STARTPTS[mid];"
         f"[tail][head]xfade=transition=fade:duration={d:.3f}:offset=0[blend];[blend][mid]concat=n=2:v=1:a=0[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-an", "-filter_complex", g, "-map", "[out]", os.path.join(tmp, f"{name}_%03d.png")], check=True)
    return sorted(glob.glob(os.path.join(tmp, f"{name}_*.png")))


def save_webp(files, out, fps, q):
    ims = [Image.open(f).convert("RGB") for f in files]
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=round(1000 / fps), loop=0, quality=q, method=6)
    return len(ims), os.path.getsize(out) // 1024


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--face", default="120:170:540", help="X:Y:SIZE (square crop) chehra")
    ap.add_argument("--body", default="0:220:720", help="X:Y:SIZE poora badan")
    ap.add_argument("--blend", type=float, default=0.6)
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg nahi mila (Termux: pkg install ffmpeg)")
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", a.video]).decode().strip())
    parse = lambda s: tuple(int(v) for v in s.split(":"))
    with tempfile.TemporaryDirectory() as tmp:
        ff = frames(a.video, tmp, "face", parse(a.face), 128, 15, dur, a.blend)
        print("zolly_face.webp", save_webp(ff, os.path.join(OUT, "zolly_face.webp"), 15, 58))
        bf = frames(a.video, tmp, "body", parse(a.body), 176, 12, dur, a.blend)
        print("zolly_body.webp", save_webp(bf, os.path.join(OUT, "zolly_body.webp"), 12, 50))
        best = Image.open(ff[len(ff) // 8]).convert("RGB")                        # shuruaat ka muskuraata frame
        best.save(os.path.join(OUT, "zolly_poster.webp"), quality=82, method=6)
        for sz in (64, 192):
            best.resize((sz, sz), Image.LANCZOS).save(os.path.join(OUT, f"zolly_icon_{sz}.png"), optimize=True)
    print("ho gaya:", OUT)


if __name__ == "__main__":
    main()
