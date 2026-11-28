#!/usr/bin/env python3
"""3-2-1 backup: ek zip jisme poori git history (sab branch), data, AI ke notes aur wapas laane ke kadam.
  python scripts/backup.py                 # phone par Download/SahilBackup/ me
  python scripts/backup.py --out FOLDER
Zip ko Google Drive (aur chaaho to PC / pen drive) par bhi rakho. Isme koi key/PIN/SSH key nahi hoti."""
import argparse
import datetime as dt
import hashlib
import os
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = "/root/.claude/projects/-root-myproject/memory"
KEEP = 8
SECRET_NAME = (".env", ".pem", ".key", ".p12")
RESTORE = """# Sahil Lab wapas kaise laayein
1. Zip kholo. `sahil-lab.bundle` me poori git history hai.
2. git clone sahil-lab.bundle sahil && cd sahil          (GitHub zinda ho to seedha: git clone https://github.com/kuldeepbalara0814/sahil-master-system-.git)
3. git branch -a    (jo kaam push nahi hua tha wo bhi branch me hai)
4. CLAUDE.md padho. pip install -r requirements.txt ; python -m lab.update --no-fetch ; python lab_server.py
5. Naya GitHub repo ho to push karo; Render par repo jodo (render.yaml) aur env dobara daalo (naam: patterns/SAMAJH.md bhag 7).
6. `notes/` me AI ke yaad rakhe notes hain: naye AI ko dikha do.
Keys / PIN / SSH key backup me NAHI hain - unhe alag (diary) me rakho.
"""


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, check=True).stdout.strip()


def make(out_dir, notes=NOTES, now=None):
    """-> zip ka path (jaanch kar). Gadbad ho to exception."""
    os.makedirs(out_dir, exist_ok=True)
    now = now or dt.datetime.now()
    path = os.path.join(out_dir, f"sahil-lab-backup-{now:%Y%m%d-%H%M}.zip")
    with tempfile.TemporaryDirectory() as tmp:
        bundle = os.path.join(tmp, "sahil-lab.bundle")
        git("bundle", "create", bundle, "--all")
        git("bundle", "verify", bundle)
        with open(bundle, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        info = f"bana: {now:%d-%m-%Y %H:%M}\nHEAD: {git('log', '-1', '--format=%h %s')}\nbranches:\n{git('branch', '-a', '--format=%(refname:short)')}\nbundle sha256: {digest}\n"
        dirty = git("status", "--porcelain")
        if dirty:
            info += "DHYAN: bina commit ke badlav is backup me NAHI:\n" + dirty + "\n"
        with zipfile.ZipFile(path + ".tmp", "w", zipfile.ZIP_DEFLATED) as z:
            z.write(bundle, "sahil-lab.bundle")
            z.writestr("RESTORE.md", RESTORE)
            z.writestr("INFO.txt", info)
            if notes and os.path.isdir(notes):
                for n in sorted(os.listdir(notes)):
                    if n.endswith(".md") and not n.endswith(SECRET_NAME):
                        z.write(os.path.join(notes, n), "notes/" + n)
    with zipfile.ZipFile(path + ".tmp") as z:
        if z.testzip() is not None:
            raise RuntimeError("zip kharab bani")
    os.replace(path + ".tmp", path)
    old = sorted(x for x in os.listdir(out_dir) if x.startswith("sahil-lab-backup-") and x.endswith(".zip"))
    for x in old[:-KEEP]:
        os.remove(os.path.join(out_dir, x))
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sahil Lab backup")
    ap.add_argument("--out", default="/sdcard/Download/SahilBackup" if os.path.isdir("/sdcard/Download") else os.path.join(ROOT, "..", "SahilBackup"))
    a = ap.parse_args(argv)
    p = make(a.out)
    print(f"backup bana aur jaanch liya: {p} ({os.path.getsize(p) // 1024} KB)")
    print("Ab ise Google Drive par bhi daalo (File manager -> Share -> Drive).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
